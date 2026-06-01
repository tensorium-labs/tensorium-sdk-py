# Publishing

This package is ready to publish as `tensorium-sdk` on PyPI.

Current status:

- local tests pass
- `python -m build` passes
- `twine check dist/*` passes
- GitHub Actions CI passes
- GitHub Actions publish workflow exists

## Fastest Path

Use a PyPI API token.

1. Create a PyPI API token for the target project or account
2. Open GitHub repo settings for `tensorium-labs/tensorium-sdk-py`
3. Add repository secret `PYPI_API_TOKEN`
4. Run the `Publish PyPI` workflow from GitHub Actions

## Trusted Publisher Path

If using PyPI Trusted Publishing, configure the publisher in PyPI to match this repo exactly:

- Owner/account: `tensorium-labs`
- Repository: `tensorium-sdk-py`
- Workflow file: `.github/workflows/publish-pypi.yml`
- Branch: `main`

Claims observed from the GitHub Actions OIDC token:

- `sub`: `repo:tensorium-labs/tensorium-sdk-py:ref:refs/heads/main`
- `repository`: `tensorium-labs/tensorium-sdk-py`
- `repository_owner`: `tensorium-labs`
- `workflow_ref`: `tensorium-labs/tensorium-sdk-py/.github/workflows/publish-pypi.yml@refs/heads/main`
- `job_workflow_ref`: `tensorium-labs/tensorium-sdk-py/.github/workflows/publish-pypi.yml@refs/heads/main`
- `ref`: `refs/heads/main`

If publish fails with `invalid-publisher`, the PyPI trusted publisher entry does not yet match these values.

## Local Publish

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]' build twine
.venv/bin/python -m build
.venv/bin/python -m twine check dist/*
.venv/bin/python -m twine upload dist/*
```
