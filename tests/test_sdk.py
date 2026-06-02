import json

import pytest

from tensorium_sdk import (
    InsufficientBalance,
    TxOutput,
    TxmRPC,
    TxmWallet,
    build_and_sign,
    select_utxos,
    tx_id,
)
from tensorium_sdk.types import Utxo

TEST_PRIV = "0101010101010101010101010101010101010101010101010101010101010101"
TEST_PUB = "031b84c5567b126440995d3ed5aaba0565d71e1834604819ff9c17f5e9d5dd078f"
TEST_ADDR = "txm178gjqyjqdwr6lvnldhgk4s98dlx6540dtczms0"
TX_VECTOR = "f1502ea322ee70ca9761b78cec26c14986c67bfbea11e8435c5441d527893f7a"


def test_generate_wallet_has_expected_shapes():
    wallet = TxmWallet.generate()
    assert wallet.address.startswith("txm1")
    assert len(wallet.private_key_hex) == 64
    assert len(wallet.public_key_hex) == 66


def test_restore_wallet_matches_vector():
    wallet = TxmWallet.from_private_key_hex(TEST_PRIV)
    assert wallet.address == TEST_ADDR
    assert wallet.public_key_hex == TEST_PUB
    assert wallet.private_key_hex == TEST_PRIV


def test_tx_id_matches_vector():
    inputs = [
        {
            "previous_output": {"txid": bytes(32), "output_index": 0},
            "signature_script": b"",
        }
    ]
    outputs = [TxOutput(address="txm1qtest", value_atoms=100_000_000)]
    assert tx_id(inputs, outputs) == TX_VECTOR


def test_select_utxos_skips_immature():
    utxos = [
        Utxo("a" * 64, 0, 50_000_000, 1, True),
        Utxo("b" * 64, 0, 80_000_000, 2, True),
        Utxo("c" * 64, 0, 20_000_000, 3, False),
    ]
    selected = select_utxos(utxos, 100_000_000)
    assert all(utxo.mature for utxo in selected)
    assert sum(utxo.value_atoms for utxo in selected) >= 100_000_000


def test_select_utxos_raises_when_short():
    utxos = [Utxo("a" * 64, 0, 50_000_000, 1, True)]
    with pytest.raises(InsufficientBalance):
        select_utxos(utxos, 200_000_000)


def test_build_and_sign_returns_expected_shape():
    wallet = TxmWallet.from_private_key_hex(TEST_PRIV)
    utxos = [Utxo("a" * 64, 0, 200_000_000, 1, True)]
    outputs = [TxOutput(address=TEST_ADDR, value_atoms=100_000_000)]
    tx = build_and_sign(wallet, utxos, outputs)

    assert len(tx["id"]) == 32
    assert len(tx["inputs"]) == 1
    assert len(tx["outputs"]) == 2

    sig_script = json.loads(bytes(tx["inputs"][0]["signature_script"]).decode())
    assert sig_script["public_key_hex"] == TEST_PUB
    assert all(ch in "0123456789abcdef" for ch in sig_script["signature_hex"])


def test_rpc_methods_call_expected_paths():
    calls = []

    def request_fn(method, url, body):
        calls.append((method, url, body))
        if url.endswith("/getblockcount"):
            return {"height": 100, "chain_id": "tensorium-mainnet-candidate-0"}
        if url.endswith("/getutxos/txm1qtest"):
            return {"tip_height": 100, "utxo_count": 0, "utxos": []}
        if url.endswith("/sendrawtransaction"):
            return {"txid": "abc123"}
        raise AssertionError(url)

    rpc = TxmRPC("https://rpc.example.com", request_fn=request_fn)
    assert rpc.get_block_count()["height"] == 100
    rpc.get_utxos("txm1qtest")
    assert rpc.send_raw_transaction({"id": [], "inputs": [], "outputs": [], "payload": []})["txid"] == "abc123"

    assert calls[0] == ("GET", "https://rpc.example.com/getblockcount", None)
    assert calls[1] == ("GET", "https://rpc.example.com/getutxos/txm1qtest", None)
    assert calls[2][0] == "POST"
    assert calls[2][1] == "https://rpc.example.com/sendrawtransaction"
