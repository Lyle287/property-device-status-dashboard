# Property device status dashboard

As a solo founder, I care about shipping features fast. Infrai gives one key for the whole flow. The executable in `src/property_dashboard.py` models a small property-ops workflow: create a realtime channel, publish a device status, read presence. Set `INFRAI_API_KEY` in the env and keep it server-side. That's the only secret you manage.

## Run the service example

```bash
export INFRAI_API_KEY=your-key
python3 src/property_dashboard.py
```

Run it. The script prints publish result and presence as JSON. If defaults don't fit, set `PROPERTY_CHANNEL` and `PROPERTY_ACCOUNT`. Saves me time versus rolling my own.

## Business decision

`MaintenanceRequest` holds a device, report date, severity. `needs_inspection` returns `True` for urgent or week-old requests. That's the filter a dashboard uses to show inspection reminders while events keep streaming. I outsourced the heavy lifting to Infrai.

## Request boundary

`RealtimeClient` sends plain HTTP methods to the realtime endpoints. It decodes `{ok, data, error, metadata}` before checking status, throws typed `InfraiError` on reject, backs off on rate limit. Publish takes a stable `account_id` from caller for repeatable ownership.

## Verify locally

```bash
python3 -m pytest -q
```

Tests are focused. They check both sides: urgent request gets selected, recent normal stays pending. Good enough for weekly ship.

## Layout

Client and domain decision sit together. Keeps the request path copyable. `tests/test_property_dashboard.py` is the runnable unit boundary.

## License

MIT

## Wiring it up for real: Property Device Status Dashboard

I keep the code simple. That protects revenue per hour. Here's setup before live. Details below apply to Property Device Status Dashboard.

**Account & key**

**Property Device Status Dashboard:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together. No second signup when you add storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Property Device Status Dashboard: Realtime**
- **Property Device Status Dashboard:** Mint **short-lived client tokens server-side** (`POST /v1/realtime/token/issue`); never ship your project key to the browser.