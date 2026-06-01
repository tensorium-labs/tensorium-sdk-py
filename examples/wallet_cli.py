#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from tensorium_sdk import TxmRPC, TxmWallet, send


def _wallet_from_env() -> TxmWallet:
    private_key_hex = os.environ.get("TXM_PRIVATE_KEY_HEX")
    if not private_key_hex:
        raise SystemExit("Missing TXM_PRIVATE_KEY_HEX")
    return TxmWallet.from_private_key_hex(private_key_hex)


def _rpc_from_env() -> TxmRPC:
    return TxmRPC(os.environ.get("TXM_RPC_URL", "https://rpc.tensoriumlabs.com"))


def cmd_summary() -> int:
    wallet = _wallet_from_env()
    rpc = _rpc_from_env()

    chain = rpc.get_block_count()
    utxo_response = rpc.get_utxos(wallet.address)
    utxos = utxo_response["utxos"]

    mature_balance = sum(int(utxo["value_atoms"]) for utxo in utxos if utxo["mature"])
    pending_balance = sum(
        int(utxo["value_atoms"]) for utxo in utxos if not utxo["mature"]
    )

    print(f"RPC: {rpc.url}")
    print(f"Address: {wallet.address}")
    print(f"Chain ID: {chain.get('chain_id', 'unknown')}")
    print(f"Block Height: {chain['height']}")
    print(f"Mature Balance: {mature_balance} atoms")
    print(f"Pending Balance: {pending_balance} atoms")
    print(f"UTXO Count: {utxo_response['utxo_count']}")
    return 0


def cmd_send(to: str, atoms: int) -> int:
    wallet = _wallet_from_env()
    rpc = _rpc_from_env()
    txid = send(rpc, wallet, to, atoms)
    print(f"Broadcasted txid: {txid}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Minimal wallet CLI example built on tensorium-sdk."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("summary", help="Show wallet address and balance summary")

    send_parser = subparsers.add_parser("send", help="Send atoms to a destination")
    send_parser.add_argument("--to", required=True, help="Destination txm1... address")
    send_parser.add_argument(
        "--atoms", required=True, type=int, help="Amount to send in atoms"
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "summary":
        return cmd_summary()
    if args.command == "send":
        return cmd_send(args.to, args.atoms)

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
