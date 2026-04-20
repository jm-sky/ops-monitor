# Health Endpoint Schema

All monitored applications must expose a `GET /health` endpoint returning JSON (could be `/api/health`, `/api/health/details` or other similar).
This document defines the expected response format consumed by ops-monitor.

> **Machine-readable schema:** `GET /api/monitor/health-schema.json` — served as JSON Schema (draft 2020-12) by the ops-monitor API.

---

## Response Structure

```json
{
  "schema_version": 1,
  "status": "ok",
  "version": "1.2.3",
  "environment": "production",
  "components": {
    "database": { "status": "ok" },
    "cache": {
      "status": "degraded",
      "reason": "High miss rate",
      "since": "2026-04-13T08:00:00Z"
    },
    "frontend": { "status": "ok" },
    "ocr": {
      "status": "ok",
      "checked_at": "2026-04-11T14:23:00Z",
      "stale": true,
      "reason": "No usage in the last 48h, status unverified"
    }
  },
  "last_activity": "2026-04-13T10:00:00Z",
  "errors": [],
  "meta": {
    "app_env": "TEST",
    "ksef_env": "DEMO"
  }
}
```

---

## Top-level Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `schema_version` | integer | yes | Always `1` for now. Increment on breaking changes. |
| `status` | string | yes | Overall app status. See [Status Values](#status-values). |
| `version` | string | no | App/release version string. |
| `environment` | string | no | Deployment environment (`production`, `staging`, etc.). |
| `components` | object | no | Per-component statuses, keyed by component name. |
| `last_activity` | string | no | ISO 8601 timestamp of the last meaningful user/system activity. |
| `errors` | array of strings | no | Active error messages contributing to a degraded/failed status. |
| `meta` | object | no | Arbitrary key-value parameters specific to this application. Values must be `string`, `number`, or `boolean`. |

The top-level `status` must reflect the worst status across all components — if any component is `failed`, the app is `failed`; if any is `degraded`, the app is at least `degraded`.

---

## Component Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `status` | string | yes | Component status. See [Status Values](#status-values). |
| `reason` | string | no | Human-readable explanation, especially for `degraded` or `failed`. |
| `since` | string | no | ISO 8601 timestamp of when this status began. |
| `checked_at` | string | no | ISO 8601 timestamp of when this status was last actually verified. |
| `stale` | boolean | no | `true` if the app considers the reported status potentially outdated. |

---

## Status Values

| Value | Meaning |
|---|---|
| `ok` | Fully operational. |
| `degraded` | Partially functional — serving requests but with reduced capability or elevated errors. |
| `failed` | Not operational — requests are failing or the component is unreachable. |

---

## Standard Component Names

Use these names for common components to ensure consistent display in ops-monitor.
Ops-monitor assigns a fixed icon to each standard name.

| Icon | Name | Description |
|---|---|---|
| 🗄️ | `database` | Primary database (PostgreSQL, MySQL, etc.). |
| ⚡ | `cache` | Cache layer (Redis, Memcached, etc.). |
| 🖥️ | `frontend` | Vue/React frontend — verified by checking for an HTTP 200 response. |
| 📬 | `queue` | Job/message queue (RabbitMQ, SQS, etc.). |
| 📦 | `storage` | File/object storage (S3, local disk, etc.). |
| 📧 | `mail` | Email delivery service. |

Any additional integration or service can be added under a descriptive name (e.g. `ocr`, `payments`, `maps`). Custom component names will use a generic 🔌 icon.

---

## Meta Fields

The optional `meta` object is an open key-value map for application-specific parameters that ops-monitor should display but not interpret. Values must be scalars (`string`, `number`, or `boolean`).

Use cases:
- An integration service reporting its own environment dimensions: `{ "app_env": "TEST", "ksef_env": "DEMO" }`
- A multi-tenant service reporting the active tenant: `{ "tenant": "acme" }`
- Feature flags or runtime modes visible in the dashboard

```json
"meta": {
  "app_env": "TEST",
  "ksef_env": "DEMO",
  "tenant": "acme"
}
```

Ops-monitor renders `meta` as a key-value table. Keys are used as labels.

### Expected Meta (ops-monitor configuration)

In the ops-monitor site configuration, you can set `expectedMeta` — a map of key-value pairs you expect the application to report. On each health poll, ops-monitor compares the received `meta` against `expectedMeta` and records any mismatches (missing keys or wrong values). Mismatches are visible in the dashboard as a warning indicator.

Example: configure `expectedMeta: { "ksef_env": "PROD" }` — if the application returns `"ksef_env": "DEMO"`, a mismatch is recorded.

---

## On-Demand / External Integrations

Services that are not continuously active (e.g. OCR, payment gateway, third-party APIs called only on user action) cannot be probed in real time. Instead:

- Report the `status` based on the **last known result** of an actual call.
- Set `checked_at` to when that call occurred.
- Set `stale: true` if the app considers the elapsed time long enough that the status is no longer reliable.

**The app defines what "stale" means for each component.** Ops-monitor stores and displays the value without reinterpreting it.

```json
"ocr": {
  "status": "ok",
  "checked_at": "2026-04-11T14:23:00Z",
  "stale": true,
  "reason": "Last successful call 48h ago"
}
```

---

## Frontend Component

If the application has a frontend, the API layer should verify it by making an internal HTTP GET request to the frontend URL and checking for an HTTP 200 response. No HTML parsing is required.

```json
"frontend": {
  "status": "ok"
}
```

```json
"frontend": {
  "status": "failed",
  "reason": "HTTP 503 from frontend origin"
}
```

This check is best-effort — if the internal request itself fails (network error, timeout), report `status: "failed"` with the error as the `reason`.

---

## Minimal Valid Response

For simple applications with no components to report:

```json
{
  "schema_version": 1,
  "status": "ok"
}
```

---

## Endpoint Authentication (Optional)

The health endpoint can be protected with an API token when public exposure is not desired.

Preferred approach is standard `Authorization: Bearer <token>` header:

- follows common HTTP auth conventions
- works out of the box with reverse proxies, API gateways, and observability tooling
- avoids custom header handling across environments

If token auth is enabled:

- use one dedicated read-only token per monitored service/environment
- keep `/health` response lightweight and non-sensitive
- rotate tokens periodically

---

## Notes for Implementers

- The endpoint must respond within **5 seconds**. Ops-monitor will treat a timeout as `failed`.
- The endpoint may be public or protected by token auth. If protected, prefer `Authorization: Bearer <token>` over custom headers.
- Avoid performing heavy operations (migrations, full DB scans) inside the health handler. Use cached/pre-computed component statuses where possible.
- `checked_at` and `stale` are optional for always-on components (database, cache) that are verified on every request cycle.
