from __future__ import annotations

import json
from typing import Any, Callable
from urllib import parse, request


RequestFn = Callable[[str, str, dict[str, Any] | None], dict[str, Any]]


class TxmRPC:
    def __init__(self, url: str, request_fn: RequestFn | None = None) -> None:
        self.url = url.rstrip("/")
        self._request_fn = request_fn

    def _request(
        self, method: str, path: str, body: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        if self._request_fn is not None:
            return self._request_fn(method, f"{self.url}{path}", body)

        payload = None if body is None else json.dumps(body).encode()
        req = request.Request(
            f"{self.url}{path}",
            data=payload,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        with request.urlopen(req) as resp:
            return json.loads(resp.read().decode())

    def get_block_count(self) -> dict[str, Any]:
        return self._request("GET", "/getblockcount")

    def get_utxos(self, address: str) -> dict[str, Any]:
        encoded = parse.quote(address, safe="")
        return self._request("GET", f"/getutxos/{encoded}")

    def send_raw_transaction(self, tx: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/sendrawtransaction", tx)

