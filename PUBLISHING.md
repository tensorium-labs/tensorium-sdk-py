# Publishing

This package is published on PyPI as `tensorium-sdk`.

Current release status:

- latest release: `0.1.0`
- project URL: `https://pypi.org/project/tensorium-sdk/`
- publish method: GitHub Actions Trusted Publishing
- local tests/build/check path already verified

## Current Trusted Publisher

PyPI is configured to trust this GitHub source:

- Owner/account: `tensorium-labs`
- Repository: `tensorium-sdk-py`
- Workflow filename: `publish-pypi.yml`
- Branch: `main`
- Environment name: empty

Claims that matched the successful GitHub Actions OIDC publish:

- `sub`: `repo:tensorium-labs/tensorium-sdk-py:ref:refs/heads/main`
- `repository`: `tensorium-labs/tensorium-sdk-py`
- `repository_owner`: `tensorium-labs`
- `workflow_ref`: `tensorium-labs/tensorium-sdk-py/.github/workflows/publish-pypi.yml@refs/heads/main`
- `job_workflow_ref`: `tensorium-labs/tensorium-sdk-py/.github/workflows/publish-pypi.yml@refs/heads/main`
- `ref`: `refs/heads/main`

If a future publish fails with `invalid-publisher`, re-check the PyPI trusted publisher entry against these exact values.

## Release Flow For Next Version

1. Bump version in project metadata
2. Run local validation:
   - `python3 -m pip install -e '.[dev]'`
   - `pytest`
   - `python3 -m build`
   - `python3 -m twine check dist/*`
3. Push to `main`
4. Run the `Publish PyPI` workflow from GitHub Actions
5. Verify the new release on PyPI

## Local Publish

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]' build twine
.venv/bin/python -m build
.venv/bin/python -m twine check dist/*
.venv/bin/python -m twine upload dist/*
```
