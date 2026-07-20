# Sekrety monitorowanych serwerów widoczne dla każdego zalogowanego użytkownika

| Pole | Wartość |
|---|---|
| **ID** | `008` |
| **Data** | 2026-07-20 |
| **Status** | `done` |
| **Moduł** | `backend/app/modules/monitor` |
| **Source** | [Security review — backend, SEC-1](../reviews/2026-07-20-security-backend.md) |
| **Severity** | High |

## Opis zadania

`SiteDB.to_response()` (`modules/monitor/db_models.py:63,70`) zwraca pole `token` (bearer token używany do pollowania `/health` + `/system` danego serwera) oraz `teamsWebhookUrl`. Endpointy `GET /monitor/sites` i `GET /monitor/site-statuses` (`modules/monitor/router.py:119-125,133-152`) są zabezpieczone tylko przez `CurrentUser` — dowolne zalogowane, zweryfikowane emailem konto.

Ponieważ `POST /auth/register` jest otwarty, **każdy, kto się zarejestruje i zweryfikuje email, może odczytać tokeny pollingu i webhooki Teams wszystkich monitorowanych serwerów** — dane, które pozwalają uderzyć bezpośrednio w wewnętrzne endpointy tych serwerów albo wysłać wiadomość na kanał Teams organizacji.

## Checklist

- [ ] Usunąć `token` i `teamsWebhookUrl` z odpowiedzi zwracanej użytkownikom bez roli admina (osobny schemat/detail view dla admina)
- [ ] Alternatywnie: zagate'ować `GET /monitor/sites` i `GET /monitor/site-statuses` za `AdminUser`
- [ ] Dodać test regresyjny: zwykły zalogowany user nie widzi `token`/`teamsWebhookUrl` w odpowiedzi

## Weryfikacja

`GET /monitor/sites` jako zwykły (nie-admin) użytkownik nie zawiera `token` ani `teamsWebhookUrl` w payloadzie.
