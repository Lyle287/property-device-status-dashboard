from datetime import date

from unittest.mock import Mock, patch

from src.property_dashboard import MaintenanceRequest, RealtimeClient, needs_inspection


def test_urgent_request_is_inspection_candidate():
    request = MaintenanceRequest("boiler-17", date(2026, 9, 6), "urgent")
    assert needs_inspection(request, date(2026, 9, 6)) is True


def test_recent_normal_request_waits():
    request = MaintenanceRequest("lift-2", date(2026, 9, 3), "normal")
    assert needs_inspection(request, date(2026, 9, 6)) is False


def test_create_channel_omits_optional_type():
    client = RealtimeClient(api_key="test")
    with patch.object(client, "_request", return_value={}) as request:
        client.create_channel("test-channel")
    request.assert_called_once_with("POST", "/v1/realtime/channel/create", {"channel": "test-channel", "vendor": "mqtt"})


def test_rate_limit_retries_rejected_envelope():
    client = RealtimeClient(api_key="test")
    limited = Mock(status_code=429, headers={"Retry-After": "0"})
    limited.json.return_value = {"ok": False, "error": {"code": "RATE_LIMITED"}}
    success = Mock(status_code=200, headers={})
    success.json.return_value = {"ok": True, "data": {}}
    with patch("src.property_dashboard.requests.request", side_effect=[limited, success]) as request, patch("src.property_dashboard.time.sleep") as sleep:
        assert client.presence("test-channel") == {"ok": True, "data": {}}
    assert request.call_count == 2
    sleep.assert_called_once_with(0.0)
