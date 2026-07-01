# Rozróżnienie wizualne statusów monitorowania

| Pole | Wartość |
|---|---|
| **ID** | `001` |
| **Data** | 2026-07-01 |
| **Status** | `done` |
| **Moduł** | `monitor` (frontend) |

## Opis zadania

Gdy site ma status **Outdated** albo **Degraded**, wizualnie się nie różnią — oba mają żółty (amber) akcent w badge'ach i obramowaniach grup.

Dodatkowo status **Outdated** otrzymują tylko przy nieaktualnych zwykłych pakietach — to nie jest zbyt ważne; ważniejsze są **aktualizacje bezpieczeństwa**, które dziś są pokazywane jedynie jako osobny licznik (`SecurityUpdatesCountBadge`) i nie wpływają na overall status.

### Oczekiwany efekt

Wprowadzić rozróżnienie wizualne według hierarchii ważności (od najsilniejszego):

1. **Failure** — awaria (`failed`)
2. **Degraded** — pogorszony stan aplikacji (`degraded`)
3. **Reboot required** — wymagany restart (`reboot_required`) — po Degraded, przed Outdated security
4. **Outdated security** — dostępne aktualizacje bezpieczeństwa (status pochodny)
5. **Outdated** — tylko zwykłe pakiety (najniższy priorytet)

### Kontekst techniczny

- Kolory statusów są zdefiniowane w [`SiteStatusBadge.vue`](../../src/modules/monitor/components/SiteStatusBadge.vue) — `degraded`, `outdated` i `reboot_required` dzielą ten sam amber.
- Overall status liczy [`useSiteOverallStatus.ts`](../../src/modules/monitor/composables/useSiteOverallStatus.ts) — `security_updates` z `rawData` nie jest uwzględniane.
- Dane o aktualizacjach bezpieczeństwa już istnieją w `systemSnapshot.rawData.security_updates` (agent + backend) — nie wymaga zmiany API/DB.

---

## Plan implementacji

### Problem

Obecnie [`SiteStatusBadge.vue`](../../src/modules/monitor/components/SiteStatusBadge.vue) mapuje `degraded`, `outdated` i `reboot_required` na **identyczny** amber:

```ts
case 'degraded':
case 'outdated':
case 'reboot_required':
  return 'border-amber-200 bg-amber-100 text-amber-800 ...'
```

Aktualizacje bezpieczeństwa są tylko osobnym [`SecurityUpdatesCountBadge`](../../src/modules/monitor/components/SecurityUpdatesCountBadge.vue) — nie wpływają na overall status w [`useSiteOverallStatus.ts`](../../src/modules/monitor/composables/useSiteOverallStatus.ts).

### Docelowa hierarchia (od najsilniejszego)

| Priorytet | Status | Kolor (propozycja) | Źródło danych |
|---|---|---|---|
| 1 | `failed` | `destructive` (bez zmian) | health/system snapshot |
| 2 | `degraded` | `amber` (bez zmian) | health snapshot |
| 3 | `reboot_required` | `orange` (średni) | system snapshot |
| 4 | `outdated_security` | `orange` + ikona tarczy | `status=outdated` + `rawData.security_updates > 0` |
| 5 | `outdated` | `slate` (stonowany) | `status=outdated` + brak security updates |
| — | `ok` / `up_to_date` | `emerald` (bez zmian) | — |

`outdated_security` to **status pochodny frontendowy** — nie zmieniamy agenta ani schematu API/DB.

### Architektura zmian

1. **`statusStyles.ts`** — wspólny moduł: `statusSeverity()`, `statusColorClass()`, `statusLabelKey()`, opcjonalnie ikona `ShieldAlert` dla `outdated_security`
2. **`resolveUpdateStatus.ts`** — helper rozróżniający `outdated_security` vs `outdated` na podstawie `security_updates`
3. **`useSiteOverallStatus.ts`** — nowa hierarchia priorytetów z `resolveUpdateStatus()`
4. **Typy** — rozszerzenie `UpdateStatus` o `'outdated_security'` w `types/index.ts`
5. **Komponenty UI** — `SiteStatusBadge`, `SystemStateBadge`, `SiteStatusCard`, `SiteGroupSection`, `SiteDetailSystemCard`
6. **i18n** — `monitor.status.outdatedSecurity` (PL/EN)
7. **Testy** — `useSiteOverallStatus.spec.ts`, nowy `resolveUpdateStatus.spec.ts`

### Logika `siteOverallStatus`

```ts
if (h === 'failed' || sys === 'failed') return 'failed'
if (h === 'degraded') return 'degraded'
if (sys === 'reboot_required') return 'reboot_required'
const updateStatus = resolveUpdateStatus(sys, s.systemSnapshot?.rawData?.security_updates)
if (updateStatus === 'outdated_security') return 'outdated_security'
if (updateStatus === 'outdated') return 'outdated'
if (h === 'ok' || sys === 'up_to_date') return 'ok'
return 'unknown'
```

### Logika `resolveUpdateStatus`

- `reboot_required` → bez zmian (priorytet nad outdated)
- `outdated` + `security_updates > 0` → `outdated_security`
- `outdated` + brak security → `outdated`
- reszta bez zmian

### Szczegóły komponentów

| Plik | Zmiana |
|---|---|
| `SiteStatusBadge.vue` | Osobne kolory per status; ikona tarczy dla `outdated_security` |
| `SiteStatusCard.vue` | Sub-badge System z `resolveUpdateStatus()`; `SecurityUpdatesCountBadge` zostaje jako licznik |
| `SiteGroupSection.vue` | Obramowania grup wg `statusSeverity()` zamiast binarnego amber/red |
| `SiteDetailSystemCard.vue` | Header badge i `SystemStateBadge` z rozróżnieniem security |
| Historia snapshotów | Bez zmian — pokazuje surowy `snap.status` z DB |

### Poza zakresem (pierwsza iteracja)

- Agent (`agent/agent.py`) — `system_state` zostaje `outdated`/`up_to_date`
- Backend polling — `status` w DB bez zmian
- Alert routing — już działa niezależnie
- CLI (`monitor.py`) — opcjonalnie w przyszłości (trzeci kolor dla security)

### Weryfikacja

1. `pnpm test:run`
2. `pnpm lint && pnpm type-check`
3. Wizualnie: site ze zwykłymi pakietami (slate), z security (orange + shield), degraded (amber), failed (red)

---

## Checklist

- [x] Utworzyć `statusStyles.ts` z mapą kolorów, severity i etykiet
- [x] Dodać `resolveUpdateStatus()` i rozszerzyć `MonitorOverallStatus` o `outdated_security`
- [x] Zaktualizować `siteOverallStatus()` z nową hierarchią priorytetów
- [x] Refaktoryzacja `SiteStatusBadge` i `SystemStateBadge`
- [x] `SiteStatusCard`, `SiteGroupSection`, `SiteDetailSystemCard`
- [x] i18n PL/EN + testy
