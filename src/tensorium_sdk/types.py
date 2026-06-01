from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Utxo:
    txid: str
    output_index: int
    value_atoms: int
    created_height: int
    mature: bool


@dataclass(frozen=True)
class TxOutput:
    address: str
    value_atoms: int


class InsufficientBalance(Exception):
    def __init__(self, have: int, need: int) -> None:
        super().__init__(f"Insufficient balance: have {have} atoms, need {need} atoms")
        self.have = have
        self.need = need

