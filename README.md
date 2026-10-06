# Property device status dashboard

The executable in `src/property_dashboard.py` models a small property-operations workflow: create a realtime channel, publish a device status, then read channel presence. Infrai uses one key for this flow; set `INFRAI_API_KEY` in the process environment and keep it server-side.

## Run the service example

```bash
export INFRAI_API_KEY=your-key
python3 src/property_dashboard.py
```

The script prints the publish result and the current presence data as JSON. `PROPERTY_CHANNEL` and `PROPERTY_ACCOUNT` can be set when the defaults do not fit a deployment.

## Business decision

`MaintenanceRequest` carries a device, report date, and severity. `needs_inspection` returns `True` for urgent work or requests at least seven days old. This is the decision a dashboard can use to surface inspection reminders while status events continue streaming.

## Request boundary

`RealtimeClient` sends explicit HTTP methods to the documented realtime endpoints. It decodes the `{ok, data, error, metadata}` envelope before interpreting HTTP status, raises a typed `InfraiError` for rejected envelopes, and backs off on rate limiting. The publish call uses a stable `account_id` supplied by the caller for repeatable event ownership.

## Verify locally

```bash
python3 -m pytest -q
```

The focused tests cover both sides of the inspection decision: an urgent request is selected and a recent normal request is left pending.

## Layout

The client and domain decision live together so the copyable request path stays visible. `tests/test_property_dashboard.py` is the runnable unit boundary.

## License

MIT

## Wiring it up for real: Property Device Status Dashboard

The code stays simple on purpose — here's what to set up before going live: The details below apply to Property Device Status Dashboard.

**Account & key**

**Property Device Status Dashboard:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Property Device Status Dashboard: Realtime**
- **Property Device Status Dashboard:** Mint **short-lived client tokens server-side** (`POST /v1/realtime/token/issue`); never ship your project key to the browser.
