# tensorium-sdk-py

Python SDK for the [Tensorium](https://tensoriumlabs.com) Proof-of-Work chain.

## Install

```bash
pip install tensorium-sdk
```

## Quick Start

```python
from tensorium_sdk import TxmRPC, TxmWallet, send

rpc = TxmRPC("https://mc-rpc.tensoriumlabs.com")
wallet = TxmWallet.from_private_key_hex("YOUR_PRIVATE_KEY_HEX")

utxos = rpc.get_utxos(wallet.address)["utxos"]
balance_atoms = sum(u["value_atoms"] for u in utxos if u["mature"])
print("Balance:", balance_atoms, "atoms")

txid = send(rpc, wallet, "txm1qdestination...", 100_000_000)
print("Sent:", txid)
```

## Features

- Wallet generation and restore from private key
- Tensorium address derivation (`txm1...`)
- UTXO selection
- Raw transaction build and deterministic signing
- HTTP RPC client for `getblockcount`, `getutxos`, and `sendrawtransaction`

## Development

```bash
python3 -m pip install -e '.[dev]'
pytest
```

## Example App

A minimal CLI example is included at `examples/wallet_cli.py`.

Show wallet summary from a private key:

```bash
export TXM_PRIVATE_KEY_HEX="YOUR_PRIVATE_KEY_HEX"
export TXM_RPC_URL="https://mc-rpc.tensoriumlabs.com"
python3 examples/wallet_cli.py summary
```

Send a transaction:

```bash
export TXM_PRIVATE_KEY_HEX="YOUR_PRIVATE_KEY_HEX"
python3 examples/wallet_cli.py send --to txm1qdestination... --atoms 100000000
```

## Publish To PyPI

Current published package:

- PyPI: https://pypi.org/project/tensorium-sdk/
- Latest release: `0.1.0`

Local publish path:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]' build twine
.venv/bin/python -m build
.venv/bin/python -m twine check dist/*
.venv/bin/python -m twine upload dist/*
```

GitHub Actions publish path:

1. Push the target release commit to `main`
2. Run the `Publish PyPI` workflow manually from the Actions tab
3. Verify the uploaded version on PyPI

Detailed publish notes:

- see [PUBLISHING.md](./PUBLISHING.md)
