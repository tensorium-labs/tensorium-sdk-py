from __future__ import annotations

import hashlib


def bytes_to_hex(data: bytes) -> str:
    return data.hex()


def hex_to_bytes(value: str) -> bytes:
    if len(value) % 2 != 0:
        raise ValueError("Invalid hex string")
    try:
        return bytes.fromhex(value)
    except ValueError as exc:
        raise ValueError("Invalid hex string") from exc


def double_sha256(data: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def le32(number: int) -> bytes:
    return int(number).to_bytes(4, "little", signed=False)


def le64(number: int) -> bytes:
    return int(number).to_bytes(8, "little", signed=False)

