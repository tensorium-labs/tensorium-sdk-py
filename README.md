# tensorium-sdk-py

Python SDK for the [Tensorium](https://tensoriumlabs.com) Proof-of-Work chain.

## Install

```bash
pip install tensorium-sdk
```

## Quick Start

```python
from tensorium_sdk import TxmRPC, TxmWallet, send

rpc = TxmRPC("https://rpc.tensoriumlabs.com")
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

## Publish To PyPI

Local publish path:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]' build twine
.venv/bin/python -m build
.venv/bin/python -m twine check dist/*
.venv/bin/python -m twine upload dist/*
```

GitHub Actions publish path:

1. Open the GitHub repo settings for `tensorium-labs/tensorium-sdk-py`
2. Add repository secret `PYPI_API_TOKEN`
3. Run the `Publish PyPI` workflow manually from the Actions tab
