from __future__ import annotations

import hashlib
import os

from bech32 import bech32_encode, convertbits
from ecdsa import SECP256k1, SigningKey

from .encoding import bytes_to_hex, hex_to_bytes

ADDRESS_HRP = "txm"


def _compressed_pubkey(signing_key: SigningKey) -> bytes:
    point = signing_key.verifying_key.pubkey.point
    prefix = b"\x02" if point.y() % 2 == 0 else b"\x03"
    return prefix + point.x().to_bytes(32, "big")


def _pubkey_to_address(compressed_pubkey: bytes) -> str:
    payload = hashlib.sha256(compressed_pubkey).digest()[:20]
    words = convertbits(payload, 8, 5, True)
    if words is None:
        raise ValueError("Failed to encode address")
    return bech32_encode(ADDRESS_HRP, words)


class TxmWallet:
    def __init__(self, private_key_bytes: bytes) -> None:
        signing_key = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
        compressed = _compressed_pubkey(signing_key)
        self._signing_key = signing_key
        self.private_key_hex = bytes_to_hex(private_key_bytes)
        self.public_key_hex = bytes_to_hex(compressed)
        self.address = _pubkey_to_address(compressed)

    @classmethod
    def generate(cls) -> "TxmWallet":
        while True:
            candidate = os.urandom(32)
            try:
                return cls(candidate)
            except Exception:
                continue

    @classmethod
    def from_private_key_hex(cls, value: str) -> "TxmWallet":
        return cls(hex_to_bytes(value))

