---
name: Remote server actions
overview: "Tak — da się to zrobić. Wymaga rozszerzenia agenta o autoryzowane endpointy POST, warstwy akcji w backendzie z logiem audytowym oraz UI z potwierdzeniem (admin). Implementacja fazowa: reboot → aktualizacje security → pełny upgrade → operacje masowe."
todos:
  - id: phase1-agent
    content: "Agent: POST /actions/reboot, AGENT_ACTIONS_ENABLED, mutex, dokumentacja systemd/Docker"
    status: pending
  - id: phase1-backend
    content: "Backend: site_action_logs, ActionService, router reboot, migracja DB, derive URL z system_url"
    status: pending
  - id: phase1-frontend
    content: "Frontend: reboot w SiteDetailSystemCard, ConfirmDialog, action logs card, monitorService + typy"
    status: pending
  - id: phase2-security
    content: "Agent + backend + UI: POST /actions/upgrade scope=security"
    status: pending
  - id: phase3-full
    content: Upgrade scope=all z ostrzeżeniem w UI
    status: pending
  - id: phase4-bulk
    content: Bulk API + checkbox selection na MonitorPage + dialog masowy
    status: pending
isProject: false
---

# Moduł akcji na monitorowanych serwerach

| Pole | Wartość |
|---|---|
| **ID** | `003` |
| **Data** | 2026-07-01 |
| **Status** | `planned` |
| **Moduł** | `monitor`, `agent` (backend, frontend) |

## Odpowiedź krótka

**Tak, da się to zrobić**, ale to nie jest „dodanie guzika” — obecny system jest **pull-only i read-only**. Agent (`agent/agent.py`) ma tylko `GET /health` i `GET /system`; backend w [`backend/app/modules/monitor/service.py`](backend/app/modules/monitor/service.py) wykonuje wyłącznie `GET`. Jedyna „akcja” dziś to admin `POST .../poll` (ponowne odczytanie stanu).

Akcje reboot/upgrade wymagają nowej ścieżki: **dashboard → backend (admin + audit) → agent POST → host (root)**.

```mermaid
sequenceDiagram
    participant UI as Vue_Dashboard
    participant API as FastAPI_Backend
    participant DB as PostgreSQL
    participant Agent as Agent_na_serwerze
    participant Host as OS_host

    UI->>API: POST /sites/{id}/actions/reboot (admin JWT)
    API->>DB: Zapis action_job pending + audit
    API->>Agent: POST /actions/reboot (Bearer token)
    Agent->>Host: shutdown -r +1 / apt upgrade
    Agent-->>API: 202 accepted + job_id
    API->>DB: status running/completed
    API-->>UI: ActionJobResponse
    Note over API,Agent: Po zakończeniu: poll_site_now()
```

## Ograniczenia i założenia

| Temat | Decyzja |
|-------|---------|
| Które serwery | Tylko site'y z `system_url` (agent). Same `health_url` bez agenta — brak akcji OS |
| OS | Debian/Ubuntu (agent już używa APT i `/var/run/reboot-required`) |
| Uprawnienia agenta | Agent musi działać jako root lub mieć sudo na `reboot` / `apt` (zmiana unit systemd / Docker) |
| Bezpieczeństwo | `AdminUser` + `ConfirmDialog` + tabela audytu (bez dodatkowego 2FA) |
| Zakres faz | 1) reboot → 2) security upgrade → 3) full upgrade → 4) masowe |

## Faza 1 — Reboot (MVP)

### 1. Agent — nowe endpointy akcji

Rozszerzyć [`agent/agent.py`](agent/agent.py):

- `POST /actions/reboot` — planowany restart (`shutdown -r +1` lub `systemctl reboot`)
- Flaga `AGENT_ACTIONS_ENABLED` (domyślnie `false`) — bez niej endpointy zwracają 403
- Ten sam `verify_token()` co `/system`
- **Mutex in-process** — odrzucenie równoległych akcji na jednym hoście
- Odpowiedź synchroniczna: `{ "status": "scheduled", "message": "..." }` (reboot rozłącza po ~60s)

Opcjonalnie na przyszłość: `GET /actions/status` — na MVP wystarczy audit po stronie centralnej + `poll_now` po czasie.

Zaktualizować [`agent/README.md`](agent/README.md) i skrypt instalacji systemd (uprawnienia root, nowa zmienna env).

### 2. Backend — warstwa akcji + audyt

Nowe pliki w [`backend/app/modules/monitor/`](backend/app/modules/monitor/):

| Plik | Rola |
|------|------|
| `actions/db_models.py` | Tabela `site_action_logs` |
| `actions/repositories.py` | CRUD logów |
| `actions/schemas.py` | `ActionType`, `ActionStatus`, request/response |
| `actions/service.py` | `ActionService` — wywołanie agenta, zapis audytu |
| `actions/router.py` | Endpointy REST |

**Model audytu** (`site_action_logs`):

- `id`, `site_id`, `user_id`, `action_type` (`reboot` / `upgrade_security` / `upgrade_all`)
- `status` (`pending` / `running` / `completed` / `failed`)
- `request_payload`, `response_payload`, `error_message`
- `created_at`, `completed_at`

**Endpointy** (wszystkie `AdminUser`):

```
POST /api/monitor/sites/{site_id}/actions/reboot
POST /api/monitor/sites/{site_id}/actions/upgrade   # body: { scope: "security" | "all" } — faza 2/3
POST /api/monitor/actions/bulk                     # body: { siteIds[], action, scope? } — faza 4
GET  /api/monitor/actions?site_id=&limit=          # historia audytu
```

**Logika wywołania agenta** — reużyć wzorce z [`service.py`](backend/app/modules/monitor/service.py):

- `_auth_headers()`, `_resolve_url()` — URL akcji wyliczyć z `system_url` (np. zamiana `/system` → `/actions/reboot`)
- Dłuższy timeout dla upgrade (np. 300s) vs reboot (30s)
- Walidacja: site włączony, ma `system_url`, opcjonalnie `actions_enabled` per site (nowa kolumna bool, domyślnie `true`)
- Po sukcesie reboot: `asyncio.create_task` z opóźnionym `poll_site_now` (np. po 90s)

Migracja DB + wpis w `cli db migrate`.

### 3. Frontend — pojedynczy reboot

W [`src/modules/monitor/`](src/modules/monitor/):

**Typy** (`types/actions.ts`):
- `ActionType`, `ActionLog`, `BulkActionRequest`

**Serwis** (`services/monitorService.ts`):
- `rebootSite(siteId)`, `getActionLogs(...)`

**UI — miejsce guzików** (zgodnie z istniejącym wzorcem `CommonPageHeader #actions` i kart systemowej):

1. [`SiteDetailSystemCard.vue`](src/modules/monitor/components/SiteDetailSystemCard.vue) — przycisk **Reboot** widoczny gdy `reboot_required === true` (destructive outline)
2. [`SiteDetailPage.vue`](src/modules/monitor/pages/SiteDetailPage.vue) — `ConfirmDialog` z nazwą serwera + ostrzeżeniem; po sukcesie toast + invalidate queries
3. Nowa karta **`SiteDetailActionsCard.vue`** — ostatnie akcje na tym site (GET `/actions?site_id=`)

Wzorzec jak przy usuwaniu site w `SiteDetailPage` — `ConfirmDialog` + `useHandleError` + `vue-sonner`.

i18n: `src/modules/monitor/i18n/` — klucze `monitor.actions.*`.

---

## Faza 2 — Aktualizacje security

### Agent
- `POST /actions/upgrade` z body `{ "scope": "security" }`
- Wykonanie: `DEBIAN_FRONTEND=noninteractive apt-get update && apt-get upgrade -y $(apt list --upgradable 2>/dev/null | grep security ...)` lub `unattended-upgrade` / `apt upgrade` z filtrem security
- Zwraca podsumowanie: ile pakietów, czy wymaga rebootu

### Backend + UI
- Endpoint `POST .../actions/upgrade` z walidacją `scope`
- Przycisk w `SiteDetailSystemCard` gdy `security_updates > 0`
- Dłuższy spinner / status „w toku” (akcja może trwać minuty)
- Po zakończeniu: automatyczny `poll_now`

---

## Faza 3 — Pełny apt upgrade

- Ten sam endpoint z `scope: "all"`
- Przycisk gdy `system_state === "outdated"` i brak pilnych security (lub osobny „Upgrade all”)
- **Silniejsze ostrzeżenie** w dialogu (downtime, reboot możliwy)
- Opcjonalnie: blokada gdy `reboot_required` — najpierw reboot lub upgrade, potem reboot (kolejność w UI)

---

## Faza 4 — Operacje masowe

### Backend
- `POST /api/monitor/actions/bulk` — iteracja po `site_ids`, tworzenie osobnych wpisów audytu
- Równoległość ograniczona (np. `asyncio.Semaphore(3)`) — uniknięcie przeciążenia
- Częściowy sukces: odpowiedź `{ results: [{ siteId, status, error? }] }`

### Frontend
Na [`MonitorPage.vue`](src/modules/monitor/pages/MonitorPage.vue):

1. **Tryb zaznaczania** — checkboxy na `SiteStatusCard` (`@click.stop` żeby nie nawigować)
2. Pasek akcji w `CommonPageHeader` lub floating bar: „Reboot selected (N)”, „Upgrade security (N)”
3. Skróty kontekstowe na przefiltrowanym widoku: „Reboot all with issues” (filtr `reboot_required` / `outdated`)
4. Dialog potwierdzenia z listą nazw serwerów (max 10 + „i X więcej”)
5. Podsumowanie wyników (toast + ewentualnie modal z tabelą błędów)

Brak gotowego wzorca bulk w module — alert channels mają tylko checkboxy filtrów w [`ChannelFiltersForm.vue`](src/modules/monitor/components/ChannelFiltersForm.vue).

---

## Bezpieczeństwo (wybrany poziom)

- **Auth**: istniejący `AdminUser` z [`backend/app/modules/auth/dependencies.py`](backend/app/modules/auth/dependencies.py)
- **Potwierdzenie**: `ConfirmDialog` z wpisaniem nazwy serwera dla reboot / bulk (opcjonalnie, zalecane dla bulk)
- **Audyt**: każda akcja → `site_action_logs` z `user_id`, timestamp, payload
- **Agent**: `AGENT_ACTIONS_ENABLED=true` tylko na zaufanych hostach; token Bearer jak dziś
- **Per-site kill switch**: kolumna `actions_enabled` w `sites` — wyłączenie akcji bez usuwania monitoringu
- **Brak 2FA step-up** (zgodnie z wyborem) — można dodać później bez zmiany API

---

## Wdrożenie agenta (operacyjne)

Obecny agent nie wymaga root do odczytu metryk. Dla akcji:

- **systemd**: `User=root` lub `CapabilityBoundingSet=CAP_SYS_BOOT` + sudoers dla apt
- **Docker**: `--privileged` lub montowanie socketów + odpowiedni user; dokumentacja w `agent/README.md`
- Rolling update agentów na serwerach przed włączeniem guzików w UI

---

## Szacowany nakład

| Faza | Zakres | Szacunek |
|------|--------|----------|
| 1 Reboot | agent + backend audit + UI single | ~2–3 dni |
| 2 Security | upgrade endpoint + UI | ~1–2 dni |
| 3 Full upgrade | ten sam endpoint, inny scope | ~0.5–1 dnia |
| 4 Bulk | bulk API + selection UI | ~2 dni |

---

## Ryzyka

- **Reboot rozłącza agenta** — UI musi komunikować „zaplanowano”, nie „ukończono natychmiast”; weryfikacja przez poll po czasie
- **Upgrade trwa długo** — HTTP timeout; rozważyć `202 Accepted` + polling statusu w fazie 2 jeśli sync nie wystarczy
- **Sieć** — centralny backend musi mieć dostęp POST do agenta (ten sam co GET dziś)
- **Wersjonowanie agenta** — backend powinien obsłużyć brak endpointu (404 → czytelny błąd „zaktualizuj agenta”)

## Rekomendacja startu

Zacząć od **Fazy 1 (reboot)** end-to-end na jednym serwerze dev (docker-compose z agentem), potem rollout agenta na produkcję, dopiero potem kolejne fazy i bulk.
