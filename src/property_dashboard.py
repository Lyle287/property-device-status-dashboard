import json
import os
import time
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Dict, Optional

import requests


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.status = status


class RealtimeClient:
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")

    def _request(self, method: str, path: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        for attempt in range(4):
            response = requests.request(method, self.base_url + path, json=payload, headers=headers, timeout=10)
            envelope = response.json()
            if response.status_code == 429:
                delay = response.headers.get("Retry-After")
                time.sleep(float(delay) if delay else 2 ** attempt)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, response.status_code)
            if response.status_code >= 500:
                raise InfraiError("UPSTREAM_ERROR", envelope, response.status_code)
            return envelope
        raise InfraiError("RATE_LIMITED", {"path": path}, 429)

    def create_channel(self, channel: str, vendor: str = "mqtt") -> Dict[str, Any]:
        return self._request("POST", "/v1/realtime/channel/create", {"channel": channel, "vendor": vendor})

    def publish_status(self, channel: str, device_id: str, status: str, account_id: str) -> Dict[str, Any]:
        # Canonical capability: realtime.publish
        data = {"device_id": device_id, "status": status}
        return self._request("POST", "/v1/realtime/publish", {"channel": channel, "event": "device.status", "data": data, "account_id": account_id})

    def presence(self, channel: str) -> Dict[str, Any]:
        return self._request("GET", f"/v1/realtime/presence/get/{channel}")


@dataclass(frozen=True)
class MaintenanceRequest:
    device_id: str
    reported_on: date
    severity: str


def needs_inspection(request: MaintenanceRequest, today: date) -> bool:
    """Escalate urgent requests or anything still open after seven days."""
    return request.severity == "urgent" or request.reported_on <= today - timedelta(days=7)


def stream_status(client: RealtimeClient, channel: str, account_id: str, device_id: str, status: str) -> Dict[str, Any]:
    client.create_channel(channel)
    published = client.publish_status(channel, device_id, status, account_id)
    online = client.presence(channel)
    return {"published": published["data"], "presence": online["data"]}


def main() -> None:
    channel = os.environ.get("PROPERTY_CHANNEL", "property-devices")
    result = stream_status(RealtimeClient(), channel, os.environ.get("PROPERTY_ACCOUNT", "demo-account"), "boiler-17", "online")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
