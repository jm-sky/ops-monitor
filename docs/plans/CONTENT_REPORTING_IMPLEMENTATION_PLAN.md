# Plan Implementacji: Raportowanie nieodpowiednich treści

## 📋 Przegląd

Plan implementacji systemu raportowania nieodpowiednich treści dla publicznych kontenerów zgodnie z wymaganiami z ROADMAP_ONLINE.md. System umożliwia:
- **Raportowanie publicznych kontenerów** przez zalogowanych użytkowników
- **Automatyczne ukrywanie z widoków publicznych** po osiągnięciu ≥3 zgłoszeń
- **Panel administracyjny** do przeglądania i weryfikacji zgłoszeń
- **Automatyczne przywracanie widoczności** po weryfikacji przez admina (dismissed/OK)

## 🎯 Cele

1. **Backend**: Tabela `content_reports` z raportami dla kontenerów
2. **Backend**: Pole `is_hidden_by_reports` w modelu kontenera
3. **Backend**: Endpointy API do raportowania (`POST /gear/containers/{id}/report`)
4. **Backend**: Endpointy admina do zarządzania raportami (`GET /admin/reports`, `PATCH /admin/reports/{id}`)
5. **Backend**: Logika auto-hide po 3+ zgłoszeniach i auto-unhide po weryfikacji
6. **Frontend**: Przycisk "Zgłoś" w widokach publicznych kontenerów
7. **Frontend**: Dialog raportowania z kategoriami powodów
8. **Frontend**: Panel admina do przeglądania i obsługi zgłoszeń
9. **Frontend**: Alert dla właściciela kontenera ukrytego przez raporty

## 🔍 Analiza Obecnego Stanu

### Backend

**Istniejące modele:**
- `GearContainerDB` w `backend/app/modules/gear/db_models.py`
- Brak tabeli `content_reports`
- Brak pola `is_hidden_by_reports` w `GearContainerDB`

**Istniejące endpointy:**
- `GET /gear/public/containers` - pobieranie publicznych kontenerów
- `GET /gear/public/containers/{id}` - pobieranie publicznego kontenera
- `GET /gear/containers` - pobieranie kontenerów użytkownika

**Brakujące:**
- Tabela `content_reports`
- Pole `is_hidden_by_reports` w kontenerze
- Endpointy do raportowania i zarządzania raportami
- Logika auto-hide/unhide

### Frontend

**Istniejące komponenty:**
- `PublicContainerCard.vue` - karta kontenera w galerii
- `PublicContainerDetailPage.vue` - strona szczegółów publicznego kontenera
- `PublicContainerHeader.vue` - nagłówek publicznego kontenera
- `ContainerDetailPage.vue` - strona szczegółów własnego kontenera

**Brakujące:**
- Komponent dialogu raportowania (`ReportContentDialog.vue`)
- Przycisk "Zgłoś" w widokach publicznych
- Panel admina do raportów (`ContentReportsPage.vue`)
- Alert dla właściciela ukrytego kontenera

## 📊 Kategorie Powodów Zgłoszeń

System używa następujących kategorii powodów (enum w backendzie, select w frontendzie):

1. **Spam / Oszustwa** (`spam_fraud`)
2. **Przemoc** (`violence`) - w tym mowa nienawiści, groźby, nawoływanie do przemocy
3. **Treści seksualne** (`sexual_content`)
4. **Wulgaryzmy** (`profanity`)
5. **Inne** (`other`) - z opcjonalnym polem tekstowym "Dodatkowe informacje"

## 🗄️ Model Danych

### Tabela `content_reports`

```sql
CREATE TABLE content_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    container_id UUID NOT NULL REFERENCES gear_containers(id) ON DELETE CASCADE,
    reporter_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reason VARCHAR(50) NOT NULL, -- enum: spam_fraud, violence, sexual_content, profanity, other
    additional_info TEXT, -- opcjonalne pole tekstowe
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending, reviewed, dismissed, action_taken
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    reviewed_by UUID REFERENCES users(id) ON DELETE SET NULL,
    UNIQUE(container_id, reporter_user_id) -- jeden raport per użytkownik per kontener
);
```

### Rozszerzenie `gear_containers`

```sql
ALTER TABLE gear_containers ADD COLUMN is_hidden_by_reports BOOLEAN NOT NULL DEFAULT FALSE;
```

### Enum Powodów (Backend Python)

```python
class ReportReason(str, Enum):
    SPAM_FRAUD = "spam_fraud"
    VIOLENCE = "violence"
    SEXUAL_CONTENT = "sexual_content"
    PROFANITY = "profanity"
    OTHER = "other"

class ReportStatus(str, Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    DISMISSED = "dismissed"
    ACTION_TAKEN = "action_taken"
```

## 🔧 Implementacja Backend

### 1. Migracja bazy danych

**Plik:** `backend/app/db/migrations/XXXX_add_content_reports.py`

- Utworzenie tabeli `content_reports` z wszystkimi polami
- Dodanie kolumny `is_hidden_by_reports` do `gear_containers`
- Utworzenie indeksów: `idx_content_reports_container_id`, `idx_content_reports_reporter_user_id`, `idx_content_reports_status`

### 2. Modele ORM

**Plik:** `backend/app/modules/gear/db_models.py`

- Dodanie modelu `ContentReportDB` z relacjami do `GearContainerDB` i `UserDB`
- Rozszerzenie `GearContainerDB` o pole `is_hidden_by_reports`

### 3. Schematy Pydantic

**Plik:** `backend/app/modules/gear/schemas.py`

- `ContentReportCreate` - schemat do tworzenia raportu
- `ContentReportResponse` - schemat odpowiedzi z raportem
- `ContentReportUpdate` - schemat do aktualizacji statusu raportu
- `ContentReportListResponse` - schemat listy raportów z paginacją

### 4. Repository

**Plik:** `backend/app/modules/gear/repository.py`

Metody:
- `create_container_report(container_id, reporter_user_id, reason, additional_info)` - tworzenie raportu
- `get_reports_for_container(container_id)` - pobieranie raportów dla kontenera
- `count_active_reports_for_container(container_id)` - liczenie aktywnych raportów (pending + action_taken)
- `get_all_reports(status=None, container_id=None, reporter_user_id=None, limit, offset)` - lista raportów z filtrami
- `update_report_status(report_id, status, reviewed_by)` - aktualizacja statusu raportu
- `set_container_hidden_by_reports(container_id, is_hidden)` - ustawienie flagi ukrycia kontenera

### 5. Service

**Plik:** `backend/app/modules/gear/service.py`

Metody:
- `report_container(container_id, reporter_user_id, reason, additional_info)`:
  - Walidacja: kontener istnieje, jest publiczny, użytkownik nie jest właścicielem (opcjonalnie)
  - Sprawdzenie czy użytkownik już zgłosił (unique constraint)
  - Utworzenie raportu
  - Sprawdzenie liczby aktywnych raportów
  - Jeśli ≥ 3 → ustawienie `is_hidden_by_reports = True`
  - Zwrócenie utworzonego raportu

- `get_reports(status=None, container_id=None, limit=50, offset=0)`:
  - Pobranie listy raportów z filtrami
  - Agregacja liczby raportów per kontener (dla widoku admina)

- `update_report_status(report_id, status, reviewer_id)`:
  - Aktualizacja statusu raportu
  - Jeśli status = `dismissed` → sprawdzenie czy wszystkie raporty dla kontenera są dismissed/reviewed
  - Jeśli tak → ustawienie `is_hidden_by_reports = False` (auto-unhide)

### 6. Router - Endpointy Gear

**Plik:** `backend/app/modules/gear/router.py`

- `POST /gear/containers/{container_id}/report`:
  - Wymaga: zalogowany użytkownik (`CurrentUser`)
  - Body: `{ reason: ReportReason, additional_info?: string }`
  - Wywołanie: `gear_service.report_container(...)`
  - Zwraca: `ContentReportResponse`

### 7. Router - Endpointy Admin

**Plik:** `backend/app/modules/admin/router.py` (lub nowy `backend/app/modules/admin/reports_router.py`)

- `GET /admin/reports`:
  - Wymaga: `AdminUser`
  - Query params: `status?`, `container_id?`, `limit?`, `offset?`
  - Zwraca: `ContentReportListResponse` z agregacją liczby raportów per kontener

- `PATCH /admin/reports/{report_id}`:
  - Wymaga: `AdminUser`
  - Body: `{ status: ReportStatus }`
  - Wywołanie: `gear_service.update_report_status(...)`
  - Zwraca: `ContentReportResponse`

### 8. Filtrowanie w Publicznych Endpointach

**Plik:** `backend/app/modules/gear/router.py`

W endpointach:
- `GET /gear/public/containers` - dodać filtr `WHERE is_hidden_by_reports = FALSE`
- `GET /gear/public/containers/{id}` - zwrócić 404 jeśli `is_hidden_by_reports = TRUE`

W prywatnych endpointach (`GET /gear/containers/{id}`) - kontener zawsze zwracany, ale z informacją o ukryciu w odpowiedzi.

## 🎨 Implementacja Frontend

### 1. Typy TypeScript

**Plik:** `src/modules/gear/types/reports.ts` (nowy)

```typescript
export type ReportReason = 'spam_fraud' | 'violence' | 'sexual_content' | 'profanity' | 'other'
export type ReportStatus = 'pending' | 'reviewed' | 'dismissed' | 'action_taken'

export interface IContentReport {
  id: string
  containerId: string
  reporterUserId: string
  reason: ReportReason
  additionalInfo?: string
  status: ReportStatus
  createdAt: string
  reviewedAt?: string
  reviewedBy?: string
}

export interface ICreateReportRequest {
  reason: ReportReason
  additionalInfo?: string
}
```

### 2. API Service - Gear

**Plik:** `src/modules/gear/services/gearContainerApiService.ts`

Metody:
- `reportPublicContainer(containerId: string, reason: ReportReason, additionalInfo?: string): Promise<IContentReport>`

### 3. API Service - Admin

**Plik:** `src/modules/admin/services/adminReportsApiService.ts` (nowy)

Metody:
- `getReports(params: { status?: ReportStatus, containerId?: string, limit?: number, offset?: number }): Promise<{ reports: IContentReport[], total: number }>`
- `updateReportStatus(reportId: string, status: ReportStatus): Promise<IContentReport>`

### 4. Komponent Dialogu Raportowania

**Plik:** `src/modules/gear/components/ReportContentDialog.vue` (nowy)

**Props:**
- `containerId: string` (required)
- `open: boolean` (v-model)

**Funkcjonalność:**
- Select z kategoriami powodów (używa i18n dla labeli)
- Opcjonalne pole tekstowe "Dodatkowe informacje" (widoczne zawsze, ale nie wymagane)
- Walidacja: wymagany reason
- Przycisk "Zgłoś" → wywołanie API, toast sukcesu, zamknięcie dialogu
- Przycisk "Anuluj" → zamknięcie dialogu

**Tłumaczenia (i18n):**
- `gear.report.reasons.spam_fraud: "Spam / Oszustwa"`
- `gear.report.reasons.violence: "Przemoc"`
- `gear.report.reasons.sexual_content: "Treści seksualne"`
- `gear.report.reasons.profanity: "Wulgaryzmy"`
- `gear.report.reasons.other: "Inne"`
- `gear.report.additional_info: "Dodatkowe informacje (opcjonalnie)"`
- `gear.report.submit: "Zgłoś"`
- `gear.report.cancel: "Anuluj"`
- `gear.report.success: "Zgłoszenie zostało wysłane. Dziękujemy za zgłoszenie."`

### 5. Przycisk "Zgłoś" w Widokach Publicznych

**Plik:** `src/modules/gear/components/PublicContainerHeader.vue` (lub odpowiedni komponent akcji)

- Dodać przycisk "Zgłoś" w menu akcji (dropdown)
- Widoczny tylko dla zalogowanych użytkowników (sprawdzenie `useAuthStore`)
- Po kliknięciu → otwarcie `ReportContentDialog`

**Plik:** `src/modules/gear/components/PublicContainerCard.vue`

- Dodać przycisk "Zgłoś" w menu akcji karty (dropdown)
- Widoczny tylko dla zalogowanych użytkowników

### 6. Alert dla Właściciela Ukrytego Kontenera

**Plik:** `src/modules/gear/pages/ContainerDetailPage.vue`

- Sprawdzenie `isHiddenByReports` w danych kontenera
- Jeśli `true` → wyświetlenie `Alert` komponentu z informacją:
  - "Ten kontener został ukryty z widoków publicznych z powodu zgłoszeń nieodpowiednich treści. Admin może go przywrócić po weryfikacji."
- Tłumaczenia: `gear.container.hidden_by_reports.alert`

### 7. Panel Admina - Strona Raportów

**Plik:** `src/modules/admin/pages/ContentReportsPage.vue` (nowy)

**Funkcjonalność:**
- Tabela raportów z kolumnami:
  - Kontener (nazwa + link do podglądu)
  - Reporter (email/username)
  - Powód (z tłumaczeniem)
  - Status (badge z kolorami)
  - Liczba raportów dla kontenera (agregacja)
  - Data utworzenia
  - Akcje (dropdown: Oznacz jako reviewed/dismissed/action_taken)
- Filtrowanie po statusie (domyślnie `pending`)
- Paginacja
- TanStack Query do pobierania danych

**Plik:** `src/modules/admin/routes.ts`

- Dodać trasę `/admin/reports` → `ContentReportsPage`

**Plik:** `src/modules/admin/components/AdminSidebar.vue` (lub odpowiedni komponent menu)

- Dodać link "Raporty treści" w menu admina

## 🔄 Logika Auto-Hide/Unhide

### Auto-Hide (≥3 zgłoszenia)

**Miejsce:** `backend/app/modules/gear/service.py` → `report_container()`

Po utworzeniu raportu:
1. Policzyć aktywne raporty: `count_active_reports_for_container(container_id)` (status: `pending` + `action_taken`)
2. Jeśli liczba ≥ 3:
   - `set_container_hidden_by_reports(container_id, is_hidden=True)`
   - Kontener automatycznie znika z widoków publicznych

### Auto-Unhide (po weryfikacji)

**Miejsce:** `backend/app/modules/gear/service.py` → `update_report_status()`

Po zmianie statusu raportu na `dismissed`:
1. Sprawdzić wszystkie raporty dla kontenera
2. Jeśli wszystkie raporty mają status `dismissed` lub `reviewed` (brak `pending` i `action_taken`):
   - `set_container_hidden_by_reports(container_id, is_hidden=False)`
   - Kontener automatycznie wraca do widoczności publicznej

## 🧪 Testy

### Backend

**Plik:** `backend/tests/modules/gear/test_content_reports.py` (nowy)

Testy:
- `test_create_report()` - tworzenie raportu
- `test_create_report_duplicate()` - próba podwójnego zgłoszenia (unique constraint)
- `test_auto_hide_on_3_reports()` - automatyczne ukrycie po 3 zgłoszeniach
- `test_auto_unhide_on_dismiss()` - automatyczne przywrócenie po weryfikacji
- `test_filter_hidden_containers_from_public()` - filtrowanie ukrytych kontenerów z publicznych endpointów
- `test_admin_get_reports()` - pobieranie raportów przez admina
- `test_admin_update_report_status()` - aktualizacja statusu przez admina

### Frontend

**Plik:** `src/modules/gear/components/__tests__/ReportContentDialog.spec.ts` (nowy)

Testy:
- Renderowanie dialogu z kategoriami powodów
- Walidacja wymaganego pola reason
- Wysyłanie raportu przez API
- Obsługa błędów

## 📝 Tłumaczenia (i18n)

**Plik:** `src/modules/gear/i18n/locales/pl.ts` i `en.ts`

Dodać sekcję `gear.report.*` z wszystkimi tłumaczeniami kategorii, komunikatów i labeli.

## ✅ Checklist Implementacji

### Backend
- [ ] Migracja bazy danych (tabela `content_reports`, pole `is_hidden_by_reports`)
- [ ] Modele ORM (`ContentReportDB`, rozszerzenie `GearContainerDB`)
- [ ] Schematy Pydantic (create, response, update)
- [ ] Repository methods (CRUD + liczenie raportów)
- [ ] Service methods (raportowanie + auto-hide/unhide)
- [ ] Endpointy Gear (`POST /gear/containers/{id}/report`)
- [ ] Endpointy Admin (`GET /admin/reports`, `PATCH /admin/reports/{id}`)
- [ ] Filtrowanie ukrytych kontenerów w publicznych endpointach
- [ ] Testy jednostkowe i integracyjne

### Frontend
- [ ] Typy TypeScript (`ReportReason`, `ReportStatus`, `IContentReport`)
- [ ] API service dla gear (`reportPublicContainer`)
- [ ] API service dla admin (`getReports`, `updateReportStatus`)
- [ ] Komponent `ReportContentDialog.vue`
- [ ] Przycisk "Zgłoś" w `PublicContainerHeader.vue`
- [ ] Przycisk "Zgłoś" w `PublicContainerCard.vue`
- [ ] Alert dla właściciela w `ContainerDetailPage.vue`
- [ ] Strona admina `ContentReportsPage.vue`
- [ ] Routing admina (`/admin/reports`)
- [ ] Link w menu admina
- [ ] Tłumaczenia (PL/EN)
- [ ] Testy komponentów

## 🔗 Powiązane Pliki

### Backend
- `backend/app/db/migrations/` - migracje bazy danych
- `backend/app/modules/gear/db_models.py` - modele ORM
- `backend/app/modules/gear/schemas.py` - schematy Pydantic
- `backend/app/modules/gear/repository.py` - repository methods
- `backend/app/modules/gear/service.py` - business logic
- `backend/app/modules/gear/router.py` - endpointy Gear
- `backend/app/modules/admin/router.py` - endpointy Admin (lub nowy plik)

### Frontend
- `src/modules/gear/types/reports.ts` - typy TypeScript
- `src/modules/gear/services/gearContainerApiService.ts` - API service gear
- `src/modules/admin/services/adminReportsApiService.ts` - API service admin
- `src/modules/gear/components/ReportContentDialog.vue` - dialog raportowania
- `src/modules/gear/components/PublicContainerHeader.vue` - nagłówek publicznego kontenera
- `src/modules/gear/components/PublicContainerCard.vue` - karta publicznego kontenera
- `src/modules/gear/pages/ContainerDetailPage.vue` - strona szczegółów kontenera
- `src/modules/admin/pages/ContentReportsPage.vue` - panel admina raportów
- `src/modules/admin/routes.ts` - routing admina
- `src/modules/gear/i18n/locales/pl.ts` i `en.ts` - tłumaczenia

## 📚 Dokumentacja

Po implementacji zaktualizować:
- `docs/ROADMAP_ONLINE.md` - zmienić status na "In Progress" / "Completed"
- Dokumentacja API (jeśli istnieje) - dodać endpointy raportowania

---

## Dodatkowo:
- Chcę aby niektórzy użytkownicy mogli wycofać się ze zgłoszenia kontenera, anulować swoje zgłoszenie.  
  Kto? Ustalmy. 
  - Na pewno user z rangą admin i owner (isAdmin, isOwner).
  - Ktoś jeszcze?

- Rozważmy, czy nie chcemy pokazać użytkownikom, że kontener był zgłoszony, np. zmieniając kolor flagi na czerwoną.
