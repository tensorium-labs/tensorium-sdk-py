from __future__ import annotations

import json
from typing import Any

from ecdsa import SigningKey, util

from .encoding import bytes_to_hex, double_sha256, hex_to_bytes, le32, le64
from .rpc import TxmRPC
from .types import InsufficientBalance, TxOutput, Utxo
from .wallet import TxmWallet


def _sig_to_der(compact: bytes) -> bytes:
    r = compact[:32]
    s = compact[32:]

    def encode_int(value: bytes) -> bytes:
        trimmed = value.lstrip(b"\x00") or b"\x00"
        if trimmed[0] >= 0x80:
            trimmed = b"\x00" + trimmed
        return trimmed

    r_enc = encode_int(r)
    s_enc = encode_int(s)
    total_len = 2 + len(r_enc) + 2 + len(s_enc)
    return (
        bytes([0x30, total_len, 0x02, len(r_enc)])
        + r_enc
        + bytes([0x02, len(s_enc)])
        + s_enc
    )


def tx_id(
    inputs: list[dict[str, Any]],
    outputs: list[TxOutput],
    payload: bytes = b"",
) -> str:
    parts: list[bytes] = []
    for inp in inputs:
        parts.append(inp["previous_output"]["txid"])
        parts.append(le32(inp["previous_output"]["output_index"]))
        parts.append(inp["signature_script"])
    for output in outputs:
        parts.append(le64(output.value_atoms))
        parts.append(output.address.encode())
    parts.append(payload)
    return bytes_to_hex(double_sha256(b"".join(parts)))


def select_utxos(utxos: list[Utxo], target_atoms: int) -> list[Utxo]:
    mature = [utxo for utxo in utxos if utxo.mature]
    sorted_utxos = sorted(mature, key=lambda utxo: utxo.value_atoms, reverse=True)
    selected: list[Utxo] = []
    total = 0
    for utxo in sorted_utxos:
        selected.append(utxo)
        total += utxo.value_atoms
        if total >= target_atoms:
            return selected
    have = sum(utxo.value_atoms for utxo in mature)
    raise InsufficientBalance(have, target_atoms)


def build_and_sign(
    wallet: TxmWallet,
    utxos: list[Utxo],
    outputs: list[TxOutput],
    payload: bytes = b"",
) -> dict[str, Any]:
    unsigned_inputs = [
        {
            "previous_output": {
                "txid": hex_to_bytes(utxo.txid),
                "output_index": utxo.output_index,
            },
            "signature_script": b"",
        }
        for utxo in utxos
    ]

    total_in = sum(utxo.value_atoms for utxo in utxos)
    total_out = sum(output.value_atoms for output in outputs)
    all_outputs = list(outputs)
    if total_in > total_out:
        all_outputs.append(
            TxOutput(address=wallet.address, value_atoms=total_in - total_out)
        )

    sig_hash_hex = tx_id(unsigned_inputs, all_outputs, payload)
    sig_hash_bytes = hex_to_bytes(sig_hash_hex)

    signing_key = SigningKey.from_string(
        hex_to_bytes(wallet.private_key_hex), curve=wallet._signing_key.curve
    )
    compact_sig = signing_key.sign_digest_deterministic(
        sig_hash_bytes,
        sigencode=util.sigencode_string,
    )
    der_hex = bytes_to_hex(_sig_to_der(compact_sig))
    sig_script = json.dumps(
        {"public_key_hex": wallet.public_key_hex, "signature_hex": der_hex}
    ).encode()
    sig_script_bytes = list(sig_script)

    signed_inputs = [
        {
            "previous_output": {
                "txid": list(inp["previous_output"]["txid"]),
                "output_index": inp["previous_output"]["output_index"],
            },
            "signature_script": sig_script_bytes,
        }
        for inp in unsigned_inputs
    ]

    signed_for_id = [
        {
            "previous_output": {
                "txid": bytes(inp["previous_output"]["txid"]),
                "output_index": inp["previous_output"]["output_index"],
            },
            "signature_script": bytes(inp["signature_script"]),
        }
        for inp in signed_inputs
    ]
    final_txid = tx_id(signed_for_id, all_outputs, payload)

    return {
        "id": list(hex_to_bytes(final_txid)),
        "inputs": signed_inputs,
        "outputs": [
            {"value_atoms": output.value_atoms, "address": output.address}
            for output in all_outputs
        ],
        "payload": list(payload),
    }


def send(
    rpc: TxmRPC,
    wallet: TxmWallet,
    to: str,
    atoms: int,
    payload: bytes = b"",
) -> str:
    rpc_utxos = rpc.get_utxos(wallet.address)["utxos"]
    parsed = [
        Utxo(
            txid=utxo["txid"],
            output_index=utxo["output_index"],
            value_atoms=int(utxo["value_atoms"]),
            created_height=utxo["created_height"],
            mature=utxo["mature"],
        )
        for utxo in rpc_utxos
    ]
    selected = select_utxos(parsed, atoms)
    tx = build_and_sign(wallet, selected, [TxOutput(address=to, value_atoms=atoms)], payload)
    result = rpc.send_raw_transaction(tx)
    return result["txid"]

