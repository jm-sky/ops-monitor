# Roadmap Online - Gear Stack

<!-- 
AI_METADATA:
- Type: Online roadmap (backend/cloud-dependent)
- Requirements: Backend, PostgreSQL, user authentication required
- Status: Active development (auth features completed)
- Related: See ROADMAP_OFFLINE.md for offline/localStorage features
- Total Features: ~30+ features
-->

Lista planowanych funkcjonalności wymagających backendu, bazy danych i/lub autoryzacji użytkowników (online/cloud features).

> 📋 **Zobacz też:** 
> - [ROADMAP.md](./ROADMAP.md) - główny indeks roadmap
> - [ROADMAP_OFFLINE.md](./ROADMAP_OFFLINE.md) - funkcjonalności offline (localStorage)
> - [Features Implementation Plans](./features/README.md) - szczegółowe plany implementacji

---

## 📊 Status Overview

- ✅ **Completed** - Zaimplementowane i przetestowane
- 🚧 **In Progress** - W trakcie implementacji
- 🔄 **Planned** - Zaplanowane, nie rozpoczęte
- ⏸️ **On Hold** - Tymczasowo wstrzymane
- ❌ **Cancelled** - Anulowane

---

## 🔐 Autoryzacja i konta użytkowników

### ✅ Podstawowa autoryzacja
**Status:** ✅ Completed | **Priority:** High | **Complexity:** Large

- ✅ Rejestracja użytkowników (email/password)
- ✅ Logowanie/Wylogowanie
- ✅ Zarządzanie sesją użytkownika
- ✅ Reset hasła
- ✅ Zmiana hasła
- ✅ Weryfikacja email
- ✅ 2FA (TOTP + WebAuthn/Passkeys)
- ✅ Backend auth module w `backend/app/modules/auth/`
- ✅ Frontend auth module w `src/modules/auth/`

### ✅ reCAPTCHA Bot Protection
**Status:** ✅ Completed | **Priority:** High | **Feature:** [FEATURE-015](./features/FEATURE-015-recaptcha-integration.md)

- ✅ Backend reCAPTCHA service (score-based verification)
- ✅ Frontend reCAPTCHA integration (invisible v3)
- ✅ Protected endpoints: login, register, forgot-password, OAuth callback
- ✅ Auto-loads reCAPTCHA script on app startup
- ✅ Score threshold configuration (0.5 default)
- ✅ Action verification (prevents token reuse)
- ✅ Environment variable configuration fixed (v2.2.1)
- ✅ Comprehensive logging for debugging
- 📝 **Status**: Fully operational with `RECAPTCHA_ENABLED=true`

### ✅ OAuth Social Login
**Status:** ✅ Completed | **Priority:** Medium | **Feature:** [FEATURE-014](./features/FEATURE-014-oauth-authentication.md)

- ✅ Backend OAuth service with Google provider
- ✅ Database migration for OAuth fields
- ✅ Repository methods for OAuth users
- ✅ User model supports nullable passwords
- ✅ OAuth schemas and types defined
- ✅ Auth service OAuth method (`login_with_oauth`)
- ✅ OAuth router endpoints (auth-url, callback)
- ✅ Frontend OAuth integration (OAuthCallbackPage)
- ✅ OAuth button component (already existing)
- ✅ OAuth callback page with state verification
- ✅ Fixed camelCase/snake_case compatibility (v2.2.1)
- ✅ Fixed settings path and logger imports (v2.2.1)
- ✅ Enhanced error handling on frontend (v2.2.1)
- 📝 **Status**: Fully functional end-to-end with Google OAuth

### 🔐 Zarządzanie tokenami i sesjami
**Status:** 🚧 Partially Completed | **Priority:** High | **Complexity:** Medium

- ✅ **Unieważnienie tokena przy wylogowaniu** - Completed
  - Plik: `backend/app/modules/auth/router.py`
  - Linia: 204-237
  - Opis: Dodanie funkcjonalności unieważniania tokena JWT przy wylogowaniu użytkownika
  - Implementacja: Blacklist tokenów w Redis (TokenBlacklistService), weryfikacja przy każdym żądaniu
  - Status: ✅ Zaimplementowane - endpoint `/logout` blacklistuje aktualny token używając `TokenBlacklistService`

- 🔄 **Unieważnienie wszystkich sesji/tokenów przy usunięciu konta** - Częściowo zaimplementowane
  - Plik: `backend/app/modules/auth/router.py`, `backend/app/modules/auth/service.py`
  - Opis: Unieważnienie wszystkich sesji i tokenów użytkownika podczas usuwania konta
  - Status: ⚠️ Częściowo - aktualny token jest blacklistowany przy usuwaniu konta, ale `blacklist_all_user_tokens` jest placeholder (wymaga trackingu tokenów per user w Redis)
  - Uwaga: `TokenBlacklistService.blacklist_all_user_tokens()` istnieje ale nie jest zaimplementowana (zwraca 0, wymaga trackingu user_id → tokens mapping)

- ✅ **Usunięcie powiązanych danych przy usuwaniu konta** - Completed
  - Plik: `backend/app/modules/*/db_models.py` (SQLAlchemy models)
  - Opis: Usunięcie danych 2FA, passkeys i innych powiązanych danych przy usuwaniu konta
  - Implementacja: Cascade delete dla wszystkich powiązanych danych użytkownika (2FA, passkeys, gear_items, ai_settings, itp.)
  - Status: ✅ Zaimplementowane - SQLAlchemy models mają `ondelete="CASCADE"` dla powiązanych tabel (two_factor, gear_items, ai_settings, itp.)

### 🔐 Ulepszenia WebAuthn / Passkeys
**Status:** 🔄 Planned | **Priority:** High | **Complexity:** Medium

- 🔄 **Przechowywanie challenge_token w Redis**
  - Plik: `backend/app/modules/two_factor/webauthn_service.py`
  - Linia: 252
  - Opis: Przechowywanie challenge_token wraz z challenge i user_id w Redis zamiast kodowania w odpowiedzi (NIEBEZPIECZNE w produkcji)
  - Implementacja: Bezpieczne przechowywanie challenge w Redis z TTL

- 🔄 **Pobieranie challenge_data z Redis**
  - Plik: `backend/app/modules/two_factor/webauthn_service.py`
  - Linia: 304
  - Opis: Pobieranie challenge_data z Redis używając challenge_token
  - Implementacja: Walidacja challenge_token i pobieranie danych z Redis

- 🔄 **Pełna weryfikacja WebAuthn używając biblioteki webauthn**
  - Plik: `backend/app/modules/two_factor/webauthn_service.py`
  - Linia: 335
  - Opis: Implementacja pełnej weryfikacji WebAuthn używając biblioteki webauthn zamiast podstawowej walidacji
  - Implementacja: Pełna integracja z biblioteką webauthn dla bezpiecznej weryfikacji

---

## 🔒 Bezpieczeństwo i walidacja treści

### ✅ Zabezpieczenie linków w markdown (Phase 1)
**Status:** 🚧 Partially Completed (Phase 1) | **Priority:** Medium | **Complexity:** Medium | **Version:** v2.45.0

**Phase 1 - Completed (v2.45.0):**
- ✅ Frontend: Link security utilities with protocol validation and length limits
- ✅ Frontend: Post-processing of rendered markdown HTML to secure links
- ✅ Frontend: Automatic addition of `rel="noopener noreferrer"` to external links
- ✅ Frontend: Blocking of dangerous protocols (`javascript:`, `data:`, `vbscript:`, `file:`, `about:`, etc.)
- ✅ Frontend: Link length validation (max 2048 characters)
- ✅ Backend: Markdown content sanitization before saving to database
- ✅ Backend: Validators for `notes` and `description` fields in containers and items
- ✅ Backend: Automatic removal of dangerous protocol links from markdown content
- ✅ Security: Maximum markdown content length limit (50000 characters)
- ✅ Security: Visual indication of blocked links (disabled styling)

**Phase 2 - Planned:**
- 🔄 Homograph detection and normalization
- 🔄 Dialog confirmation for suspicious external links
- 🔄 Blocking external images in markdown (or lazy loading with security)

**📋 Plan implementacji:** [MARKDOWN_LINK_SECURITY_PLAN.md](./plans/MARKDOWN_LINK_SECURITY_PLAN.md)

### Zabezpieczenie przed obraźliwymi słowami i niebezpiecznymi URL
**Status:** 🔄 Planned | **Priority:** Medium | **Complexity:** Medium

**Zakres implementacji:**
- Walidacja i filtrowanie treści użytkownika w backendzie przed zapisaniem do bazy danych
- Sprawdzanie nazw kontenerów i przedmiotów pod kątem wulgaryzmów i obraźliwych treści
- Sprawdzanie opisów przedmiotów i kontenerów pod kątem nieodpowiednich treści
- Walidacja URL-ów dodawanych do przedmiotów/kontenerów:
  - Blokowanie linków do stron pornograficznych (XXX)
  - Blokowanie linków do innych nieodpowiednich treści
  - Sprawdzanie domen na czarnej liście
- Komunikaty błędów informujące użytkownika o odrzuceniu treści (bez ujawniania szczegółów filtrowania)
- Konfiguracja list słów zabronionych i domen na czarnej liście (możliwość aktualizacji przez admina)
- Opcjonalnie: automatyczna moderacja treści publicznych kontenerów

**Implementacja:**
- Backend middleware/service do walidacji treści
- Integracja z zewnętrznymi API/lista słów zabronionych (opcjonalnie)
- Walidacja na poziomie endpointów API (przed zapisaniem do DB)
- Frontend może opcjonalnie walidować po stronie klienta dla lepszego UX, ale główna walidacja w backendzie

**Zalety:**
- Ochrona przed nieodpowiednimi treściami w aplikacji
- Zgodność z regulaminem i standardami społeczności
- Lepsze doświadczenie użytkowników (brak obraźliwych treści)
- Bezpieczeństwo (ochrona przed spamem i złośliwymi linkami)

### Zgłaszanie nieodpowiednich treści (raportowanie)
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Medium | **Plan:** [CONTENT_REPORTING_IMPLEMENTATION_PLAN.md](./plans/CONTENT_REPORTING_IMPLEMENTATION_PLAN.md)

**Koncepcja:**
System raportowania nieodpowiednich treści dla publicznych kontenerów przez zalogowanych użytkowników, z automatycznym ukrywaniem z widoków publicznych po osiągnięciu ≥3 zgłoszeń oraz panelem administracyjnym do weryfikacji.

**Zakres implementacji:**
- **Backend:**
  - Tabela `content_reports` w bazie danych (container_id, reporter_user_id, reason, additional_info, status, created_at, reviewed_at, reviewed_by)
  - Pole `is_hidden_by_reports` w tabeli `gear_containers` (flaga ukrycia kontenera)
  - Endpoint `POST /gear/containers/{container_id}/report` do zgłaszania publicznych kontenerów (tylko dla zalogowanych użytkowników)
  - Endpoint `GET /admin/reports` do przeglądania zgłoszeń (tylko dla adminów) z filtrami i agregacją liczby raportów per kontener
  - Endpoint `PATCH /admin/reports/{report_id}` do aktualizacji statusu zgłoszenia (pending, reviewed, dismissed, action_taken)
  - Automatyczne ukrywanie kontenera z widoków publicznych po osiągnięciu ≥3 aktywnych zgłoszeń (pending + action_taken)
  - Automatyczne przywracanie widoczności publicznej po weryfikacji przez admina (gdy wszystkie zgłoszenia są dismissed/reviewed)
  - Filtrowanie ukrytych kontenerów w publicznych endpointach (`GET /gear/public/containers`, `GET /gear/public/containers/{id}`)

- **Frontend:**
  - Przycisk "Zgłoś" w widokach publicznych kontenerów (galeria, szczegóły publicznego kontenera) - widoczny tylko dla zalogowanych użytkowników
  - Dialog zgłaszania (`ReportContentDialog.vue`) z wyborem kategorii powodu:
    - Spam / Oszustwa
    - Przemoc (mowa nienawiści, groźby, nawoływanie do przemocy)
    - Treści seksualne
    - Wulgaryzmy
    - Inne (z opcjonalnym polem tekstowym "Dodatkowe informacje")
  - Potwierdzenie zgłoszenia (toast notification)
  - Alert dla właściciela kontenera ukrytego przez raporty (informacja o ukryciu z widoków publicznych)
  - Panel admina (`ContentReportsPage.vue`) do przeglądania i zarządzania zgłoszeniami:
    - Tabela raportów z filtrowaniem po statusie
    - Agregacja liczby raportów per kontener
    - Akcje zmiany statusu raportów (reviewed, dismissed, action_taken)

- **Walidacja:**
  - Sprawdzanie czy użytkownik już zgłosił dany kontener (unique constraint: container_id + reporter_user_id)
  - Weryfikacja czy zgłaszany kontener istnieje i jest publiczny
  - Wymagany zalogowany użytkownik (brak możliwości raportowania przez gości)

**Zalety:**
- Społecznościowa moderacja treści publicznych kontenerów
- Szybsze wykrywanie nieodpowiednich treści przez społeczność
- Automatyczna ochrona przed spamem i nieodpowiednimi treściami (auto-hide po 3 zgłoszeniach)
- Wsparcie dla adminów w moderowaniu treści (panel administracyjny)
- Lepsze doświadczenie użytkowników (brak nieodpowiednich treści w publicznych widokach)

---

## 💾 Synchronizacja i przechowywanie danych

### Synchronizacja między urządzeniami (cloud storage)
**Status:** 🚧 Partially Completed | **Priority:** Medium | **Complexity:** Large

- ✅ Cloud storage dla kontenerów i przedmiotów (PostgreSQL database)
- ✅ API endpoints dla wszystkich operacji CRUD
- ✅ Factory pattern wybierający między localStorage a API
- ✅ Migracja danych z localStorage do API
- 🔄 Automatyczna synchronizacja w tle - planowane
- 🔄 Rozwiązywanie konfliktów przy równoczesnych edycjach - planowane
- ✅ Offline-first approach z synchronizacją przy połączeniu (podstawowa implementacja)

### Wersjonowanie danych (historia zmian)
**Status:** 🔄 Planned | **Priority:** Low | **Complexity:** Large

- Historia zmian kontenerów i przedmiotów
- Możliwość cofnięcia zmian (undo/redo)
- Porównywanie wersji
- Przywracanie poprzednich wersji
- Audit log wszystkich operacji

---

## 👥 Udostępnianie i współpraca

### Udostępnianie kontenerów
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Medium

- ✅ Kontenery publiczne (`isPublic` flag)
- ✅ Publiczny link do kontenera (`/gear/public/:id`)
- ✅ Przeglądarka publicznych kontenerów (`PublicContainersBrowserPage`)
- ✅ Strona szczegółów publicznego kontenera (`PublicContainerDetailPage`)
- ✅ Publiczna strona szczegółów przedmiotu (`PublicItemDetailPage`)
- ✅ Pole `isPublic` w formularzu kontenera
- ✅ Domyślna widoczność w ustawieniach użytkownika
- ✅ **Udostępnianie kontenerów przez token** (v2.16.0+)
  - ✅ Link w formacie: `/shared/container/:token` (read-only access)
  - ✅ Token generowany przez właściciela kontenera (`ContainerShareTokensPage`)
  - ✅ Opcjonalna data wygaśnięcia tokena
  - ✅ Dostęp tylko przez token (nie wymaga container ID)
  - ✅ Wspólny komponent nagłówka (`PublicContainerHeader`) dla publicznych i udostępnionych kontenerów
  - ✅ Przycisk edycji widoczny tylko dla autora kontenera
  - ✅ Strona szczegółów udostępnionego kontenera (`SharedContainerDetailPage`)
  - ✅ Zarządzanie tokenami (tworzenie, wyświetlanie, anulowanie)
  - ✅ Kopiowanie linku do schowka
  - ✅ UI improvements for mobile (v2.17.0)
- 🔄 Uprawnienia: tylko odczyt / edycja - planowane
- 🔄 Lista osób, z którymi kontener jest udostępniony - planowane

### ✅ Galeria publiczna list/kontenerów
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Medium

- ✅ Publiczna galeria dostępnych kontenerów (`PublicContainersBrowserPage`)
- ✅ Przeglądanie kontenerów innych użytkowników
- ✅ Filtrowanie i wyszukiwanie w galerii
- ✅ Strona szczegółów publicznego kontenera (`PublicContainerDetailPage`)
- ✅ Publiczna strona szczegółów przedmiotu (`PublicItemDetailPage`)
- ✅ Backend endpoint `/gear/public/containers` dla pobierania publicznych kontenerów
- ✅ **Ocenianie (gwiazdki) kontenerów** - Completed
  - ✅ **Owner rating**: Właściciel kontenera może ocenić swój kontener (1-5 gwiazdek) - zaimplementowane
  - ✅ **User rating**: Inni użytkownicy mogą ocenić publiczne kontenera (1-5 gwiazdek) - zaimplementowane
  - ✅ Backend: Tabela `container_ratings` (container_id, user_id, rating, rating_type: 'owner' | 'user') - zaimplementowane
  - ✅ Backend: Endpointy do dodawania/aktualizacji/usuwania oceny - zaimplementowane (`POST /containers/{id}/rating`, `DELETE /containers/{id}/rating`)
  - ✅ Backend: Obliczanie średniej oceny per kontener - zaimplementowane
  - ✅ Frontend: Komponent gwiazdek do oceniania (`RatingStars.vue`, `ContainerRatingCard.vue`, `ContainerRatingSection.vue`) - zaimplementowane
  - ✅ Frontend: Wyświetlanie średniej oceny w szczegółach kontenera - zaimplementowane
  - ✅ Frontend: Rozróżnienie między owner rating a user rating w UI - zaimplementowane
  - ✅ Frontend: Możliwość zmiany własnej oceny - zaimplementowane
- 🔄 Komentarze pod kontenerami - planowane
- 🔄 Możliwość skopiowania publicznego kontenera do własnych - planowane

### System zaproszeń
**Status:** 🔄 Planned | **Priority:** Medium | **Complexity:** Large

**Zaproszenia ogólne do aplikacji:**
- Wysyłka zaproszeń na e-mail
- Generowanie unikalnego linku akceptacji dla każdego zaproszenia
- Akceptacja zaproszenia z linku (rejestracja nowego użytkownika lub dodanie do istniejącego konta)
- Lista wysłanych zaproszeń dla każdego użytkownika
- Oznaczenie statusu zaproszenia (wysłane, zaakceptowane, wygasłe)
- Możliwość anulowania zaproszenia przed akceptacją
- Opcjonalnie: limit zaproszeń per użytkownik (np. dla planów premium)

**Później: Zaproszenia do współdzielenia kontenerów**
- Wysyłka zaproszeń do współdzielenia konkretnego kontenera
- Różne poziomy uprawnień (tylko odczyt, edycja)
- Lista zaproszeń do współdzielenia kontenerów
- Zarządzanie uprawnieniami współdzielonych kontenerów
- Powiadomienia o zaproszeniach do współdzielenia

**Implementacja:**
- Backend: Tabela `invitations` w bazie danych (email, token, status, created_by, expires_at, itp.)
- Backend: Endpointy API do tworzenia, wysyłania, akceptacji i anulowania zaproszeń
- Backend: Integracja z systemem email (SMTP lub serwis zewnętrzny)
- Frontend: UI do wysyłania zaproszeń (formularz z emailem)
- Frontend: Strona akceptacji zaproszenia (landing page z linku)
- Frontend: Lista wysłanych zaproszeń w ustawieniach użytkownika
- Frontend: Zarządzanie zaproszeniami do współdzielenia kontenerów (w przyszłości)

**Zalety:**
- Kontrolowany wzrost bazy użytkowników
- Możliwość zapraszania znajomych do aplikacji
- Lepsze zarządzanie współdzieleniem kontenerów (w przyszłości)
- Historia zaproszeń i akceptacji

---

## 🗂️ Globalny katalog i linkowanie

### ✅ Globalny katalog itemów
**Status:** ✅ Completed | **Priority:** High | **Complexity:** Medium

- ✅ Globalny katalog wszystkich przedmiotów (wszystkich użytkowników lub tylko własnych)
- ✅ Przeglądarka przedmiotów (globalny katalog)
- ✅ Autocomplete przy dodawaniu itemu do kontenera z globalnego katalogu
- ✅ Możliwość dodawania przedmiotów z katalogu do własnych kontenerów
- ✅ Wersjonowanie przedmiotów w katalogu

**📋 Plan implementacji:** [GLOBAL_CATALOGUE_IMPLEMENTATION_PLAN.md](./plans/GLOBAL_CATALOGUE_IMPLEMENTATION_PLAN.md)

### ✅ Wyświetlanie kontenerów na liście wszystkich przedmiotów
**Status:** ✅ Completed | **Priority:** Low | **Complexity:** Small

- ✅ Kontenery (plecaki, torby, itp.) są widoczne na liście wszystkich przedmiotów
- ✅ Plecak to też przedmiot - traktowany jako taki w katalogu
- ✅ Wizualne rozróżnienie między kontenerami a zwykłymi przedmiotami na liście (ikona Box, badge "Container")
- ✅ Możliwość filtrowania: tylko kontenery / tylko przedmioty / wszystkie
- ✅ Kontenery wyświetlane z całkowitą wagą (waga kontenera + zawartość)

### ✅ Linkowanie przedmiotów (zmiana w jednym → zmiana w wielu listach)
**Status:** ✅ Completed | **Priority:** High | **Complexity:** Large

- ✅ Przedmioty mogą być linkowane między kontenerami (przez autocomplete w ItemFormPage)
- ✅ Zmiana w jednym miejscu aktualizuje wszystkie referencje (propagacja w useGear.updateItem)
- ✅ Wizualne oznaczenie linkowanych przedmiotów (ring + ikona Link2 w ItemsTableNameCell)
- ⏸️ "Odlinkowanie" przedmiotu (tworzenie kopii) - na razie nie implementowane (usuwanie = usunięcie z kontenera)
- ⏸️ Zarządzanie referencjami - nie wymagane (uproszczona wersja)

### ✅ Pobierz obrazki z katalogu
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Medium

**Koncepcja:**
Akcja pozwalająca na pobranie obrazków z katalogu do przedmiotu, który jest już połączony z katalogiem (ma `catalogueItemId`). Obrazki z katalogu są kopiowane do galerii przedmiotu użytkownika.

**Zaimplementowane funkcjonalności:**
- ✅ **Backend:**
  - ✅ Endpoint `POST /gear/items/{item_id}/fetch-images-from-catalogue` do pobierania obrazków z katalogu
  - ✅ Pobieranie obrazków powiązanych z `catalogueItemId` przedmiotu
  - ✅ Kopiowanie obrazków z katalogu do storage użytkownika (S3 lub lokalny)
  - ✅ Zachowanie kolejności obrazków z katalogu
  - ✅ Ustawienie pierwszego obrazka jako primary (jeśli przedmiot nie ma jeszcze primary image)
  - ✅ Walidacja: sprawdzanie czy przedmiot jest połączony z katalogiem

- ✅ **Frontend:**
  - ✅ Akcja "Pobierz obrazki z katalogu" w menu akcji przedmiotu (`ItemHeaderActions.vue`)
  - ✅ Akcja widoczna tylko gdy przedmiot jest połączony z katalogiem (`isLinkedToCatalogue`)
  - ✅ Umieszczenie akcji w dropdown menu pod innymi akcjami katalogu (po "Aktualizuj z katalogu", przed "Odłącz z katalogu")
  - ✅ Loading state podczas pobierania obrazków (`isFetchingImages`)
  - ✅ Toast notification z potwierdzeniem sukcesu
  - ✅ Obsługa błędów (np. brak obrazków w katalogu, błąd pobierania)
  - ✅ Automatyczne odświeżanie kontenera po pobraniu obrazków

**Zalety:**
- Szybkie uzupełnienie galerii przedmiotu obrazkami z katalogu
- Lepsze UX - automatyczne pobieranie obrazków zamiast ręcznego uploadu
- Spójność z innymi akcjami katalogu (aktualizacja, odłącz)

### ✅ Przenoszenie przedmiotów między kontenerami
**Status:** ✅ Completed | **Priority:** High | **Complexity:** Medium

### ✅ Poprawa wyszukiwarki katalogu globalnego (lepsze dopasowanie)
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Medium

**Koncepcja:**
Poprawa wyszukiwarki w tworzeniu połączenia przedmiotu z katalogiem globalnym (`MatchWithCatalogueDialog.vue`) - lepsze dopasowywanie wyników wyszukiwania.

**Obecna implementacja:**
- Backend używa prostego `ilike` z PostgreSQL (wzorzec `%query%`)
- Wyszukiwanie w polach: `name`, `description`, `brand`, `model`
- Brak rankingowania wyników

**Proponowane ulepszenia:**
1. **Full Text Search (PostgreSQL)**
   - Użycie `to_tsvector` i `to_tsquery` dla lepszego wyszukiwania
   - Ranking wyników na podstawie relevancy (ts_rank)
   - Obsługa synonimów i stemming (dla języka angielskiego/polskiego)
   - Indeksy GIN dla wydajności

2. **Fuzzy Search (alternatywa)**
   - Użycie `pg_trgm` extension (trigram matching)
   - Funkcja `similarity()` do dopasowywania podobnych stringów
   - Lepsze radzenie sobie z literówkami i wariantami nazw

3. **Hybrydowe podejście**
   - Kombinacja Full Text Search + Fuzzy Search
   - Full Text Search dla dokładnych dopasowań
   - Fuzzy Search jako fallback dla literówek
   - Ranking uwzględniający oba metody

**Zakres implementacji:**
- **Backend:**
  - Rozszerzenie metody `get_catalogue_items()` w `GearRepository`
  - Dodanie migracji dla indeksów Full Text Search (jeśli wybrana opcja 1 lub 3)
  - Ewentualna instalacja extension `pg_trgm` (jeśli wybrana opcja 2 lub 3)
  - Ranking wyników wyszukiwania
  - Optymalizacja wydajności (indeksy)

- **Frontend:**
  - Opcjonalnie: wizualne oznaczenie trafności wyników (jeśli ranking jest dostępny)
  - Opcjonalnie: sortowanie wyników według relevancy

**Zalety:**
- Lepsze znajdowanie przedmiotów w katalogu (nawet przy literówkach)
- Lepsze UX - użytkownik szybciej znajdzie pasujący przedmiot
- Ranking wyników pomaga znaleźć najlepsze dopasowanie na górze listy

**Uwagi:**
- Full Text Search wymaga konfiguracji językowej (polski vs angielski)
- pg_trgm wymaga extension PostgreSQL
- Należy przetestować wydajność na większych zbiorach danych

**Koncepcja:**
Umożliwienie przenoszenia przedmiotów z jednego kontenera do drugiego bez konieczności usuwania i ponownego dodawania.

**Zaimplementowane funkcjonalności:**
- **Backend:**
  - ✅ Endpoint `PATCH /gear/items/{item_id}/move` do przenoszenia przedmiotu
  - ✅ Walidacja: sprawdzanie czy kontener docelowy istnieje i użytkownik ma do niego dostęp
  - ✅ Aktualizacja relacji `container_items` (zmiana `container_id`)
  - ✅ Zachowanie UUID przedmiotu przy przenoszeniu
  - ✅ Zachowanie `linked_item_id` przy przenoszeniu (przedmioty linkowane pozostają linkowane)
  - ✅ Przenoszenie tylko pojedynczego przedmiotu (nie przenosi wszystkich linkowanych)
  - ✅ Testy integracyjne dla wszystkich scenariuszy

- **Frontend:**
  - ✅ Akcja "Przenieś" w menu akcji przedmiotu (`ItemHeaderActions.vue`)
  - ✅ Dialog wyboru kontenera docelowego (`MoveItemDialog.vue`) z listą dostępnych kontenerów
  - ✅ Wizualne potwierdzenie przenoszenia (toast notification)
  - ✅ Aktualizacja UI po przenoszeniu (emit `itemUpdated`)
  - ✅ Obsługa błędów (np. kontener docelowy nie istnieje, brak uprawnień)
  - ✅ Tłumaczenia (PL/EN)

- **Edge cases:**
  - ✅ Przenoszenie przedmiotu linkowanego - zachowuje linkowanie, przenosi tylko jeden przedmiot
  - ✅ Przenoszenie przedmiotu z obrazkami - zachowuje obrazki (są powiązane z item_id)
  - ✅ Przenoszenie przedmiotu z historią - zachowuje historię (jest powiązana z item_id)

**Zalety:**
- Szybsze zarządzanie przedmiotami między kontenerami
- Lepsze UX (nie trzeba usuwać i dodawać ponownie)
- Zachowanie danych przedmiotu (UUID, historia, obrazki)

### Promocja przedmiotu do katalogu globalnego
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Medium

**Koncepcja:**
Mechanizm pozwalający użytkownikom na promowanie swoich przedmiotów do globalnego katalogu, gdzie mogą być używane przez innych użytkowników.

**Zakres implementacji:**
- **Backend:**
  - Pole `promote_count` w tabeli `items` (licznik promocji)
  - Endpoint `POST /gear/items/{item_id}/promote` do promowania przedmiotu
  - Walidacja: tylko zarejestrowani użytkownicy z kontem starszym niż 1 miesiąc mogą promować
  - Automatyczne dodanie do katalogu po osiągnięciu progu promocji (np. 10 promocji)
  - Endpoint `GET /gear/items/{item_id}/promote-status` do sprawdzania statusu promocji
  - Historia promocji (kto i kiedy promował przedmiot)

- **Frontend:**
  - Przycisk "Promuj do katalogu" w menu akcji przedmiotu
  - Wyświetlanie licznika promocji (`promote_count`) w szczegółach przedmiotu
  - Informacja o wymaganiach (konto > 1 miesiąc)
  - Wizualne oznaczenie przedmiotów w katalogu (pochodzących z promocji)
  - Progress bar pokazujący postęp do progu promocji (np. "7/10 promocji")

- **Wymagania:**
  - Tylko zarejestrowani użytkownicy mogą promować
  - Konto musi być starsze niż 1 miesiąc
  - Użytkownik może promować tylko swoje przedmioty
  - Ograniczenie: jeden użytkownik może promować dany przedmiot tylko raz

**Zalety:**
- Rozbudowa globalnego katalogu przez społeczność
- Weryfikacja jakości przedmiotów przez społeczność (promocje)
- Zachęta do tworzenia wysokiej jakości przedmiotów
- Lepsze wykorzystanie katalogu przez użytkowników

---

## 💳 Limity kont i subskrypcje

### ✅ Limity przedmiotów i kontenerów dla kont free/premium
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Medium

**Koncepcja:**
System limitów liczby przedmiotów i kontenerów w zależności od typu konta (free/premium), z możliwością opcjonalnego uwzględnienia wykorzystanej przestrzeni w bazie danych.

**Zakres implementacji:**
- **Backend:**
  - Pole `account_tier` w tabeli `users` (free, premium)
  - Konfiguracja limitów:
    - Free: 500 przedmiotów, 10 kontenerów (lub zależnie od wykorzystanej przestrzeni DB)
    - Premium: 1000 przedmiotów, 50 kontenerów (lub zależnie od wykorzystanej przestrzeni DB)
  - Endpoint `GET /me/limits` do sprawdzania limitów i wykorzystania
  - Walidacja limitów przy tworzeniu przedmiotów/kontenerów
  - Endpoint `GET /me/storage-usage` do sprawdzania wykorzystanej przestrzeni (opcjonalnie)
  - Obliczanie wykorzystanej przestrzeni DB per użytkownik (rozmiar danych w tabelach)

- **Frontend:**
  - Wyświetlanie informacji o limitach w ustawieniach użytkownika
  - Progress bar pokazujący wykorzystanie limitów (np. "450/500 przedmiotów")
  - Ostrzeżenia przy zbliżaniu się do limitu (np. przy 80% wykorzystania)
  - Blokada tworzenia nowych przedmiotów/kontenerów po przekroczeniu limitu
  - Komunikat zachęcający do upgrade do premium przy osiągnięciu limitu
  - Informacja o wykorzystanej przestrzeni DB (jeśli implementowane)

- **Opcje implementacji:**
  - **Opcja 1:** Proste limity liczbowe (500/1000 przedmiotów)
  - **Opcja 2:** Limity zależne od wykorzystanej przestrzeni DB (bardziej elastyczne)
  - **Opcja 3:** Hybrydowe podejście (limity liczbowe + monitoring przestrzeni DB)

**Zalety:**
- Kontrola wykorzystania zasobów serwera
- Zachęta do upgrade do premium
- Przewidywalne koszty infrastruktury
- Lepsze zarządzanie przestrzenią w bazie danych

---

## ⚙️ Ustawienia użytkownika (wymagające DB)

### ✅ Rozszerzone ustawienia użytkownika
**Status:** ✅ Completed | **Priority:** High | **Complexity:** Small

- ✅ **Domyślna waluta użytkownika** (zapisywana w DB) - zaimplementowane
- ✅ **Domyślna widoczność nowych kontenerów** - zaimplementowane
  - ✅ **Backend:** Pole `default_containers_public` w `UserSettingsDB` - zaimplementowane
  - ✅ **Backend:** Endpoint `/me/settings` do aktualizacji ustawienia - zaimplementowane
  - ✅ **Frontend:** Checkbox w Gear Settings (`GearPreferencesCard.vue`) - zaimplementowane
  - ✅ **Frontend:** Automatyczne ustawienie `isPublic` przy tworzeniu nowego kontenera na podstawie ustawienia użytkownika - zaimplementowane (w `ContainerFormPage.vue` i backend `create_container`)
  - ✅ **Frontend:** Możliwość nadpisania domyślnego ustawienia w formularzu kontenera - zaimplementowane
  - ✅ **Zachowanie:** Jeśli użytkownik nie ma ustawienia, domyślnie `false` (prywatne) - zaimplementowane
- ✅ Preferowana jednostka wagi (zapisywana w DB, nie tylko localStorage) - zaimplementowane
- ✅ **Automatyczny wybór jednostki wagi (auto) i formatowanie z separatorem tysięcznym** - zaimplementowane
  - ✅ Rozszerzenie typu jednostki wagi o opcje `auto-g-kg` i `auto-oz-lb`
  - ✅ Aktualizacja schematów walidacji (Pydantic) - dodanie nowych wartości do enum `TGearWeightUnit`
  - ✅ Aktualizacja modelu `GearSettingsDB` w bazie danych - obsługa nowych wartości jednostki wagi
  - ✅ Aktualizacja endpointów API (`/me/gear-settings`) - walidacja i zapis nowych opcji auto
  - ✅ Migracja bazy danych – zwiększenie długości kolumny `preferred_weight_unit` do VARCHAR(10)
  - ✅ Logika automatycznego wyboru jednostki (frontend):
    - Jeśli waga < 1 kg → wyświetlanie w `g` (dla systemu metrycznego) lub `oz` (dla systemu imperialnego)
    - Jeśli waga ≥ 1 kg → wyświetlanie w `kg` (dla systemu metrycznego) lub `lb` (dla systemu imperialnego)
  - ✅ Formatowanie liczby z separatorem tysięcznym w wyświetlanych wagach
  - 📍 Szczegóły implementacji: [ROADMAP_OFFLINE.md](./ROADMAP_OFFLINE.md#-automatyczny-wybór-jednostki-wagi-auto-i-formatowanie-z-separatorem-tysięcznym)
- ✅ **Dodawanie nowych kategorii** (zapisywane w DB) - zaimplementowane
- ✅ **Dodawanie firm / marek (brand)** - zapisywane w DB - zaimplementowane
- 🔄 Uczenie się na podstawie wcześniejszych wyborów użytkownika (dla kategorii) - planowane

**Zaimplementowane funkcjonalności:**
- ✅ Backend: Model `GearSettingsDB` z polem `default_currency`
- ✅ Backend: Schemas z `defaultCurrency` w response i update
- ✅ Backend: Repository i Service dla gear_settings
- ✅ Backend: Router z endpointami `GET /me/gear-settings` i `PATCH /me/gear-settings`
- ✅ Frontend: API service (`gearSettingsApiService.ts`)
- ✅ Frontend: Factory pattern w `gearSettingsService.ts` (API/localStorage)
- ✅ Frontend: Store zaktualizowany do używania factory pattern

### ✅ Profil użytkownika - link do Gravatara
**Status:** ✅ Completed | **Priority:** Low | **Complexity:** Small

- ✅ Umożliwienie zapisania URL do obrazu awatara użytkownika
- ✅ Integracja z Gravatar (automatyczne pobieranie awatara na podstawie email)
- ✅ Pole `avatar_url` w profilu użytkownika (już istnieje w DB)
- ✅ Możliwość podania własnego URL do awatara

### 🔄 Tryb prosty (Simple Mode) (inspiracja LighterPack)
**Status:** 🔄 Planned | **Priority:** Medium | **Complexity:** Medium | **Source:** [LIGHTERPACK_IMPROVEMENTS_TASKS.md](../comparison/LIGHTERPACK_IMPROVEMENTS_TASKS.md)

**Koncepcja:**
Dodanie trybu prostego dla użytkowników, którzy chcą prostszy interfejs z ukrytymi zaawansowanymi funkcjami.

**Wymagania:**
- Toggle "Tryb prosty" w ustawieniach użytkownika (zapisywane w DB)
- Zaawansowane opcje w dropdown menu jako `Więcej... →`
- Podstawowe pola widoczne domyślnie
- Zaawansowane pola ukryte pod `Więcej` w formularzach
- W trybie prostym ukrywamy zaawansowane kolumny w tabelach (np. cena, waluta, marka, kolor)
- Zagnieżdżanie kontenerów zostaje (użytkownik kontroluje czy zagnieżdża)
- Nie robimy Wizard dla nowych użytkowników

**Szczegóły implementacji:**
- Ustawienie `simpleMode: boolean` w ustawieniach użytkownika (zapisywane w DB)
- Podstawowe pola przedmiotu: nazwa, waga, ilość, kategoria, notatki, status, priorytet
- Zaawansowane pola (ukryte w trybie prostym): cena, waluta, marka, kolor, URL, data ważności, shelf life, wearable, consumable
- W tabelach: ukrycie zaawansowanych kolumn w trybie prostym
- W formularzach: sekcja "Więcej opcji" z dropdown/expandable section

### 🚧 Sekcja AI w Gear Settings
**Status:** 🚧 Partially Completed | **Priority:** High | **Complexity:** Medium

**Koncepcja:**
Dodanie sekcji ustawień AI w Gear Settings, umożliwiającej zarządzanie konfiguracją AI bezpośrednio z poziomu ustawień aplikacji.

**Zakres implementacji:**
- **Backend:**
  - ✅ Endpointy AI settings już istnieją (`/ai/settings`) - zaimplementowane
  - 🔄 Endpoint do pobierania zużycia credits/tokenów: `GET /ai/usage` lub `GET /ai/stats` - planowane
  - 🔄 Obliczanie limitu credits (jeśli używany token systemowy) - planowane
  - 🔄 Śledzenie zużycia credits per użytkownik (dla tokenów systemowych) - planowane

- **Frontend:**
  - ✅ Nowa sekcja "AI Settings" w Gear Settings (`GearSettingsPage.vue`) - zaimplementowane (`AiSettingsCard.vue`)
  - ✅ **Domyślny model:** Selektor modelu AI - zaimplementowane (używa `useAiModels` i `Select`)
  - ✅ **Własny token:** 
    - ✅ Pole do wprowadzenia własnego tokena OpenRouter - zaimplementowane
    - ✅ Przycisk "Zapisz token" / "Usuń token" - zaimplementowane
    - ✅ Walidacja tokena przy zapisie (test API call) - zaimplementowane (backend)
    - ✅ Informacja o szyfrowaniu tokena (encrypt-at-rest) - zaimplementowane (wyświetlana w UI)
  - ✅ **Limit credits:** 
    - ✅ Wyświetlanie limitu credits (tylko dla tokenów systemowych) - zaimplementowane (z `monthlyUsage` z store)
    - ✅ Informacja o braku limitu dla własnych tokenów - zaimplementowane
    - 🔄 Możliwość ustawienia limitu (opcjonalnie, dla adminów) - planowane
  - ✅ **Progress bar zużycia:**
    - ✅ Progress bar pokazujący zużycie credits w stosunku do limitu - zaimplementowane
    - ✅ Wyświetlanie: "X / Y credits użyto" lub "X credits użyto (bez limitu)" - zaimplementowane
    - ✅ Wizualne oznaczenie (zielony/żółty/czerwony) w zależności od poziomu zużycia - zaimplementowane
    - 🔄 Reset limitu (opcjonalnie, dla adminów lub przy odnowieniu subskrypcji) - planowane
  - ✅ Integracja z istniejącym `useAiStore` - zaimplementowane
  - ✅ Komunikaty błędów i sukcesu (toast notifications) - zaimplementowane (używa `useHandleError`)
  - ✅ **Premium feature:** Ustawienia AI wyłączone (disabled inputs) dla zwykłych użytkowników - zaimplementowane
  - ✅ **Premium feature:** Informacja "Only for premium users" lub "Premium feature" (`AiPremiumFeatureAlert`) - zaimplementowane

- **UI/UX:**
  - ✅ Sekcja AI Settings jako osobna karta/sekcja w Gear Settings - zaimplementowane
  - ✅ Spójny design z resztą ustawień - zaimplementowane
  - ✅ Tooltips z wyjaśnieniami (np. "Własny token pozwala na nieograniczone użycie AI") - zaimplementowane
  - ✅ Responsywny design dla urządzeń mobilnych - zaimplementowane
  - ✅ Premium feature alert i disabled inputs dla zwykłych użytkowników - zaimplementowane

**Zalety:**
- Centralne miejsce do zarządzania ustawieniami AI
- Lepsza widoczność zużycia credits
- Łatwiejsze zarządzanie tokenami
- Spójność z resztą ustawień aplikacji

**Uwagi:**
- Backend endpointy AI settings już istnieją (`/ai/settings`)
- Możliwe wykorzystanie istniejących komponentów AI (np. `AiModelSelector`)
- Integracja z istniejącym systemem śledzenia zużycia tokenów

---

## 🚀 Import/Export - rozszerzenia wymagające DB

### ✅ UUID support dla update workflow
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Medium

**Koncepcja:**
Kontenery i przedmioty już mają UUID - to ich pole `id` (typu `TUUID`). UUID support to system wykorzystujący ten istniejący UUID do identyfikacji podczas importu/eksportu, co umożliwia aktualizację istniejących danych zamiast tworzenia duplikatów.

**Zaimplementowane funkcjonalności:**
- ✅ Export markdown zawiera UUID w formacie `[uuid:xxx]` (opcjonalnie, przez `showUuid`)
- ✅ Import parsuje UUID z markdowna i używa go do identyfikacji kontenerów/przedmiotów
- ✅ Import rozpoznaje UUID i może zaktualizować istniejące kontenery/przedmioty zamiast tylko tworzyć nowe
- ✅ Jeśli UUID istnieje w systemie → aktualizacja istniejącego kontenera/przedmiotu
- ✅ Jeśli UUID nie istnieje → tworzenie nowego kontenera/przedmiotu z tym samym UUID (zachowuje UUID z eksportu)
- ✅ Opcja w import dialog: "Aktualizuj istniejące (po UUID)" vs "Twórz nowe" (już działa)
- ✅ Umożliwia cykl export → edycja w AI → import z zachowaniem relacji i aktualizacją danych
- ✅ Stabilne referencje nawet po zmianie nazw kontenerów (UUID się nie zmienia)
- ✅ Wsparcie dla UUID zarówno w localStorage (local services) jak i w backend API
- ✅ Aktualizacja wszystkich parsowanych pól podczas update (nazwa, opis, waga, URL, cena, waluta)

**Zaimplementowane zmiany techniczne:**
- ✅ Dodać opcjonalne pole `id` do `ICreateContainerDto` i `ICreateItemDto` (frontend)
- ✅ Dodać opcjonalne pole `id` do `ContainerCreate` i `ItemCreate` schemas (backend)
- ✅ Zmodyfikować `createContainer` i `createItem` w local services, aby używały podanego UUID
- ✅ Zmodyfikować backend repository, aby akceptowało opcjonalny UUID
- ✅ Zaktualizować `ImportMarkdownDialog.vue`, aby przekazywał UUID podczas tworzenia i aktualizacji
- ✅ Zaktualizować API services (`gearContainerApiService.ts`, `gearItemApiService.ts`), aby przekazywały UUID do backendu
- ✅ Dodać testy jednostkowe dla UUID support w lokalnych serwisach:
  - `gearContainerLocalService.spec.ts` - 5 testów sprawdzających użycie UUID przy tworzeniu kontenerów
  - `gearItemLocalService.spec.ts` - 5 testów sprawdzających użycie UUID przy tworzeniu przedmiotów
- ✅ Testy parsowania UUID już istnieją w `markdownImportService.spec.ts`

---

## 📊 Statystyki i raporty (multi-user)

### Statystyki i raporty
**Status:** 🔄 Planned | **Priority:** Low | **Complexity:** Medium

- Statystyki użytkownika (liczba kontenerów, przedmiotów, całkowita waga)
- Porównywanie z innymi użytkownikami (opcjonalnie)
- Raporty okresowe
- Analiza trendów w czasie

### Statystyki wyświetleń kontenerów
**Status:** 🔄 Planned | **Priority:** High | **Complexity:** Medium

**Koncepcja:**
System śledzenia wyświetleń kontenerów (publicznych i udostępnionych) z ~~dashboardem~~ małą sekcją statystyk dla właściciela.

**Zakres implementacji:**
- **Backend:**
  - Tabela `container_views` (container_id, user_id, session_id, viewed_at, ip_address, user_agent, country)
  - Endpoint `POST /gear/containers/{container_id}/view` do rejestrowania wyświetleń
  - Endpoint `GET /gear/containers/{container_id}/stats` do pobierania statystyk (tylko dla właściciela)
  - Endpoint `GET /me/containers/stats` do pobierania statystyk wszystkich kontenerów użytkownika
  - Licznik wyświetleń kontenera (ile razy ktoś obejrzał kontener)
  - Licznik unikalnych wyświetleń (tracking unikalnych użytkowników/sesji)
  - Historia wyświetleń z timestampami
  - Agregacja danych (dzienne, tygodniowe, miesięczne statystyki)
  - **Uwaga**: Na początku wystarczy nam licznik wszystkich/unikalnych wyświetleń, bez agregacji

- **Frontend:**
  - Automatyczne rejestrowanie wyświetleń przy otwarciu publicznego/udostępnionego kontenera
  - Na początek robimy małą sekcję statystyk na stronie kontenera: wszystkie i unikalne wyświetlenia
  - Na razie bez dashboard, czyli bez:
    - Dashboard ze statystykami dla właściciela kontenera:
      - Całkowita liczba wyświetleń per kontener
      - Wyświetlenia w czasie (wykresy liniowe/słupkowe)
      - Top 10 najczęściej oglądanych kontenerów
      - Statystyki wyświetleń dla udostępnionych tokenów (które tokeny były najczęściej używane)
      - Unikalne vs całkowite wyświetlenia
      - Statystyki geograficzne (opcjonalnie)
    - Strona statystyk kontenera (`ContainerStatsPage`) dostępna tylko dla właściciela
    - Link do statystyk w menu akcji kontenera (tylko dla właściciela)
  - Prywatność: statystyki widoczne tylko dla właściciela kontenera

- **Tracking:**
  - Tracking dla publicznych kontenerów (`/gear/public/:id`)
  - Tracking dla kontenerów udostępnionych przez token (`/shared/container/:token`)
  - Unikanie podwójnego liczenia (sprawdzanie sesji/cookies)

**Zalety:**
- Właściciel kontenera widzi popularność swoich kontenerów
- Możliwość analizy, które kontenery są najczęściej oglądane
- Lepsze zrozumienie użycia funkcji udostępniania

---

## 🎯 Szablony i presety

### Szablony kontenerów (predefiniowane zestawy)
**Status:** 🔄 Planned | **Priority:** Low | **Complexity:** Medium

- Predefiniowane szablony kontenerów (UL, bushcraft, EDC, itp.)
- Możliwość tworzenia własnych szablonów
- Udostępnianie szablonów między użytkownikami
- Galeria szablonów
- Tworzenie kontenera z szablonu

### Generowanie gotowych presetów (UL, bushcraft, EDC)
**Status:** 🔄 Planned | **Priority:** Low | **Complexity:** Medium

- AI-powered generowanie presetów na podstawie typu aktywności
- Zapisywanie wygenerowanych presetów jako szablonów
- Możliwość edycji i personalizacji presetów

---

## 🤖 Funkcje AI (wymagające backend)

### Infrastruktura AI
**Status:** 🚧 Partially Completed | **Priority:** Medium | **Complexity:** Large | **Version:** v2.17.3+

**Integracja z OpenRouter:**
- ✅ OpenRouter jako główny provider AI (dostęp do wielu modeli z różnych providerów) - zaimplementowane
- ✅ Użytkownik wybiera jeden aktywny model z listy dostępnych modeli - zaimplementowane (`AiModelSelector`)
- ✅ Obsługa własnych tokenów użytkownika (opcjonalnie) - zaimplementowane
- ✅ Billing dokładnie jak OpenRouter (tokeny wejściowe + wyjściowe) - zaimplementowane (`AiCostDisplay`)
- ✅ Zero ukrytych limitów, przejrzyste statystyki - zaimplementowane
- ✅ Brak fallbacku modeli - użytkownik sam wybiera inny model przy niedostępności - zaimplementowane
- 🔄 Krótka informacja ostrzegawcza przy pierwszym użyciu (AI działa na odpowiedzialność użytkownika) - planowane

**Zarządzanie tokenami:**
- ✅ Klucze encrypt-at-rest (szyfrowane w bazie danych) - zaimplementowane (Fernet encryption)
- ✅ Możliwość podmiany lub usunięcia tokena przez użytkownika - zaimplementowane (settings endpoint)
- ✅ Wsparcie dla tokenów systemowych (dla użytkowników bez własnych tokenów) - zaimplementowane
- 🔄 Limity dotyczą tylko użycia tokena systemowego - planowane
- ✅ Walidacja tokena przy dodawaniu (test API call) - zaimplementowane

**Konfiguracja kontekstu:**
- ✅ Użytkownik wybiera, które pola idą do kontekstu (nazwy, opisy, wagi, kategorie, etc.) - zaimplementowane (`AiContextConfig`)
- ✅ Opcja włączania/wyłączania danych kontenera w kontekście - zaimplementowane (checkbox w `AiChatWindow`)
- ✅ Brak automatycznego skracania kontekstu - zaimplementowane
- 🔄 Komunikat gdy kontekst przekracza limity modelu - planowane
- ✅ Brak ustawień typu temperature, max_tokens (standardowe parametry w pierwszej wersji) - zaimplementowane

**Historia AI:**
- ✅ Zapisywanie pełnych danych: finalny prompt, modyfikacje, kontekst, odpowiedź - zaimplementowane
- ✅ Metadane: model, provider, timestamp, liczba tokenów, koszt - zaimplementowane
- ✅ Nie zapisujemy template'u promptu (tylko finalny prompt) - zaimplementowane
- ✅ Backend endpoints do zarządzania historią (GET, DELETE) - zaimplementowane
- ✅ Frontend composable `useAiHistory` z funkcjami do zarządzania historią - zaimplementowane
- ✅ **Zarządzanie historią - UI:**
  - ✅ Przeglądanie historii chatów (lista konwersacji z filtrowaniem i wyszukiwaniem) - Completed
  - ✅ Powrót do konwersacji (restore conversation from history - załadowanie wiadomości z historii do chat window) - Completed
  - ✅ Kasowanie historii (UI do usuwania pojedynczych wpisów i całej historii) - Completed
  - ✅ Historia viewer page (strona z listą historii, szczegóły konwersacji) - Completed
- ✅ **Sprawdzenie i poprawa działania strony AiHistory** - Completed
  - ✅ Przywracanie konwersacji działa poprawnie
  - ✅ Sprawdzenie innych funkcjonalności strony (filtrowanie, wyszukiwanie, paginacja) - działa
- 🔄 Mechanizm limitu historii (domyślnie 100 wpisów) + automatyczne usuwanie najstarszych - planowane
- ✅ **Rozszerzenie funkcjonalności czatu AI** - zaimplementowane - [FEATURE-AI-CHAT-ENHANCEMENTS.md](../features/FEATURE-AI-CHAT-ENHANCEMENTS.md)
  - ✅ Dodanie pola container_ids do modelu historii
  - ✅ Czat z poziomu Listy Kontenerów z załączaniem przefiltrowanych kontenerów
  - ✅ Resume chat z AI History Page z automatycznym przekierowaniem
  - ✅ Panel historii w oknie czatu używając Sheet component

**Cache:**
- ✅ Cache dla powtarzalnych operacji (klasyfikacje, embeddingi) - zaimplementowane (PostgreSQL cache)
- ✅ Zmniejsza koszty oraz liczbę requestów - zaimplementowane
- ✅ TTL: 7 dni dla klasyfikacji, 30 dni dla embedów - zaimplementowane
- ✅ Storage: PostgreSQL JSONB - zaimplementowane

**Logi i monitoring:**
- ✅ Logowanie błędów, czasów odpowiedzi, zużycia tokenów - zaimplementowane
- 🔄 Podstawowy monitoring stabilności OpenRouter API - planowane
- 🔄 Health check per model (status, response times, success rate) - planowane
- 🔄 Jasne komunikaty przy awarii: "Usługa OpenRouter jest niedostępna - spróbuj ponownie później" - planowane
- ✅ Integracja z Sentry dla alertów (opcjonalnie) - zaimplementowane (jeśli Sentry włączony)

**Endpointy:**
- ✅ `/ai/chat` - Chat completions (generowanie tekstu, sugestie) - zaimplementowane
- ✅ `/ai/settings` - Zarządzanie ustawieniami użytkownika (token, model, kontekst) - zaimplementowane
- ✅ `/ai/history` - Historia interakcji AI - zaimplementowane
- ✅ `/ai/models` - Lista dostępnych modeli - zaimplementowane
- 🔄 `/ai/classify` - Klasyfikacje (kategorie, worn, consumable) - planowane
- 🔄 `/ai/embed` - Embeddingi (semantic search w przyszłości) - planowane
- 🔄 `/ai/vision` - Vision models (planowane na później) - planowane

**Frontend Components (v2.17.3):**
- ✅ `AiChatDialog` - Główny dialog chatu z AI
- ✅ `AiChatWindow` - Okno chatu z wiadomościami i inputem
- ✅ `AiChatMessage` - Komponent wyświetlający wiadomości AI
- ✅ `AiChatMessageDebugPrompt` - Debug prompt dla wiadomości asystenta
- ✅ `AiChatTemplateMsgButton` - Przyciski z szablonami wiadomości
- ✅ `AiContextConfig` - Konfiguracja pól kontekstu
- ✅ `AiModelSelector` - Selektor modelu AI
- ✅ `AiCostDisplay` - Wyświetlanie kosztów i tokenów
- ✅ Pełne wsparcie i18n (PL/EN) dla modułu AI

### Sugestie sprzętu (na podstawie pogody, aktywności itp.)
**Status:** 🔄 Planned | **Priority:** Low | **Complexity:** Large

- Integracja z API pogodowym
- Sugestie sprzętu na podstawie warunków pogodowych
- Sugestie na podstawie typu aktywności
- Personalizacja sugestii na podstawie historii użytkownika
- Wykorzystanie wybranego przez użytkownika modelu AI
- Konfigurowalny kontekst (użytkownik wybiera jakie dane wysłać)

### Analiza listy (co dodać, co usunąć, alternatywy)
**Status:** 🔄 Planned | **Priority:** Low | **Complexity:** Large

- AI-powered analiza kompletności listy
- Sugestie co dodać do kontenera
- Sugestie co można usunąć (redundancja)
- Propozycje alternatywnych przedmiotów
- Analiza wagi i optymalizacja
- Konfigurowalny kontekst (użytkownik wybiera co wysłać do AI)

### Automatyczne oznaczanie kategorii / worn / consumable
**Status:** 🔄 Planned | **Priority:** Low | **Complexity:** Medium

- AI-powered automatyczne kategoryzowanie
- Automatyczne oznaczanie przedmiotów jako "worn" lub "consumable"
- Uczenie się na podstawie wyborów użytkownika
- Zapisywanie preferencji w DB
- Cache dla powtarzalnych klasyfikacji (zmniejsza koszty)

### Konwersja: opis → gotowy kontener
**Status:** 🔄 Planned | **Priority:** Low | **Complexity:** Large

- Konwersja tekstowego opisu na gotowy kontener z przedmiotami
- Integracja przez OpenRouter (dostęp do różnych modeli)
- Zapisywanie wygenerowanych kontenerów w DB
- Historia generowania w bazie danych

---

## 📷 Media i zasoby graficzne

### Upload avatarów użytkownika (wymaga S3)
**Status:** 🔄 Planned | **Priority:** Low | **Complexity:** Medium | **Prerequisite:** S3 Storage

- Możliwość wgrywania własnych avatarów użytkownika
- Alternatywa do Gravatar - użytkownik może wgrać własny obraz
- Automatyczne skalowanie i optymalizacja obrazów
- Limity rozmiaru pliku (np. 2MB max)
- Obsługa formatów: JPG, PNG, WebP
- **Wymaga:** Wdrożenie S3 lub innego cloud storage

### ✅ Zdjęcia przedmiotów
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Medium | **Feature:** [FEATURE-017](./features/FEATURE-017-item-image-gallery-upload.md) | **Version:** v2.11.0

- ✅ Możliwość dodawania zdjęć do przedmiotów w kontenerach (admin-only)
- ✅ Wielokrotne zdjęcia per przedmiot (galeria, max 10 zdjęć)
- ✅ Limity rozmiaru pliku (10 MB default)
- ✅ Automatyczne skalowanie i kompresja (do 1920x1920, JPEG quality 85%)
- ✅ Obsługa formatów: JPG, PNG, WebP, GIF
- ✅ Storage adapter pattern (local filesystem + S3 support)
- ✅ Drag-and-drop upload z VueUse
- ✅ Primary image selection
- ✅ Image reordering (drag-and-drop)
- ✅ FileDropZone component (reusable)
- ✅ Transaction safety (rollback on failure)
- ✅ Docker volume persistence
- ✅ Frontend integration into ItemDetailPage (ItemImageGallery component)
- ✅ ContainerItemImagesGallery component (wyświetlanie obrazków przedmiotów na stronie kontenera)
- ✅ Pole `showItemImages` w kontenerze (opcja pokazywania obrazków w widoku kontenera)
- ✅ **Show from URL** - opcja dodawania obrazków z URL zamiast uploadu (v2.15.0)
  - ✅ Pole URL w formularzu dodawania obrazka (`ItemImageGalleryUrlForm`)
  - ✅ Walidacja URL i formatu obrazka
  - ✅ Pobieranie i przetwarzanie obrazka z URL
  - ✅ Alternatywa dla uploadu (szczególnie przydatne dla adminów)
  - 🔄 **Do rozważenia:** Sprawdzić obecne zachowanie - czy dodawanie obrazka przez URL ściąga obrazek do storage, czy tylko zapisuje zewnętrzny URL
    - **Obecne zachowanie:** Obrazek jest ściągany z URL i zapisywany w storage (podobnie jak upload pliku)
    - **Cel pierwotny:** Zapis zewnętrznego URL (bez ściągania do storage)
    - **Do rozważenia:** Które podejście jest lepsze?
      - **Zapis URL (pros):** Oszczędność miejsca w storage, brak duplikacji danych
      - **Zapis URL (cons):** Zależność od zewnętrznego serwera, możliwość utraty obrazka gdy URL przestanie działać
      - **Ściąganie do storage (pros):** Niezależność od zewnętrznych serwerów, kontrola nad obrazkami
      - **Ściąganie do storage (cons):** Zajmuje miejsce w storage, duplikacja danych
    - **Opcja:** Możliwość wyboru przez użytkownika (ściągnij do storage vs zapisz tylko URL)
- ✅ **Primary image w wierszu tabeli** - opcjonalne wyświetlanie miniaturki primary image w tabeli przedmiotów (v2.15.0)
  - ✅ Miniaturka primary image w tabeli (`ItemsTableImageCell`)
  - ✅ Lazy loading dla wydajności
  - ✅ Kliknięcie w miniaturkę → przejście do szczegółów przedmiotu
  - ✅ Dostępne w `ItemsTable` i `AllItemsPage`
- 🔄 Limity przestrzeni per użytkownik (nie zaimplementowane - future enhancement)
- **Wsparcie:** Local storage (development) + S3 (production ready)

### ✅ Kasowanie obrazków z S3
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Medium

**Koncepcja:**
Automatyczne usuwanie obrazków z S3 storage po usunięciu powiązanych danych (przedmiotów, kontenerów, kont użytkowników).

**Zaimplementowane funkcjonalności:**
- ✅ **Automatyczne usuwanie z S3 po usunięciu przedmiotu:**
  - ✅ Metoda `_delete_all_item_images()` w `GearService` usuwa wszystkie obrazki przedmiotu
  - ✅ Integracja z `delete_item()` - obrazy są usuwane przed usunięciem przedmiotu z bazy danych
  - ✅ Obsługa błędów (logowanie, nie blokowanie usuwania przedmiotu jeśli obrazki nie mogą być usunięte)

- ✅ **Automatyczne usuwanie z S3 po usunięciu kontenera:**
  - ✅ Integracja z `delete_container()` - obrazy wszystkich przedmiotów w kontenerze są usuwane przed usunięciem kontenera
  - ✅ Pobieranie wszystkich przedmiotów kontenera i usuwanie ich obrazków

- ✅ **Automatyczne usuwanie z S3 po usunięciu wszystkich kontenerów:**
  - ✅ Integracja z `delete_all_containers()` - obrazy wszystkich przedmiotów we wszystkich kontenerach są usuwane przed usunięciem kontenerów

- ✅ **Automatyczne usuwanie z S3 po usunięciu konta użytkownika:**
  - ✅ Metoda `delete_all_user_images()` w `GearService` usuwa wszystkie obrazy użytkownika
  - ✅ Integracja z `delete_account` endpoint w `AuthService` - obrazy są usuwane przed usunięciem konta
  - ✅ Metoda `get_all_by_user()` w `ItemImageRepository` do pobierania wszystkich obrazków użytkownika

**Implementacja:**
- ✅ **Backend:**
  - ✅ Metoda `_delete_all_item_images()` w `GearService` - usuwa obrazy pojedynczego przedmiotu
  - ✅ Metoda `delete_all_user_images()` w `GearService` - usuwa wszystkie obrazy użytkownika
  - ✅ Metoda `get_all_by_user()` w `ItemImageRepository` - pobiera wszystkie obrazy użytkownika
  - ✅ Integracja z `delete_item()`, `delete_container()`, `delete_all_containers()` w `GearService`
  - ✅ Integracja z `delete_account` endpoint w `auth/router.py` - wywołanie `delete_all_user_images()` przed usunięciem konta
  - ✅ Obsługa błędów - logowanie błędów, nie blokowanie głównej operacji jeśli usuwanie obrazków się nie powiedzie

- **Edge cases:**
  - Co jeśli obrazek nie istnieje w S3? (ignorowanie błędu 404)
  - Co jeśli operacja usuwania z S3 się nie powiedzie? (logowanie, kontynuowanie operacji)
  - Co z obrazkami używanymi przez wiele przedmiotów? (nie dotyczy - każdy przedmiot ma własne obrazy)

**Zalety:**
- Oszczędność przestrzeni w S3 (usuwanie nieużywanych obrazków)
- Lepsze zarządzanie kosztami storage
- Zgodność z RODO (usuwanie danych użytkownika)

**Uwagi:**
- Usuwanie obrazków powinno być non-blocking (nie blokować głównej operacji usuwania)
- Należy rozważyć asynchroniczne usuwanie dla większych operacji (batch delete)
- Logowanie wszystkich operacji usuwania dla audytu

### Przetwarzanie obrazków z ustawieniami użytkownika (3 tryby)
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Medium | **Feature:** [FEATURE-025](./features/FEATURE-025-image-processing-modes.md)

**Koncepcja:**
Po uploadzie obrazków automatyczne przetwarzanie (zmiana rozmiaru, kompresja) w zależności od wybranego przez użytkownika trybu. Dotyczy zarówno obrazków **przedmiotów** (items) jak i **kontenerów** (containers).

**Wymagania:**
- ✅ Obrazki przedmiotów (items) - już zaimplementowane
- 🔄 Obrazki kontenerów (containers) - do zaimplementowania
  - Galeria obrazków dla kontenerów (podobnie jak dla przedmiotów)
  - Primary image dla kontenera
  - Upload, zarządzanie, usuwanie obrazków kontenerów
  - Wyświetlanie w widoku listy kontenerów i szczegółach kontenera

**3 tryby przetwarzania:**
1. **Wysoka jakość** (High Quality)
   - Maksymalny rozmiar: 2560x2560px
   - JPEG quality: 95%
   - Minimalna kompresja, zachowanie szczegółów
   - Dla użytkowników, którzy potrzebują najlepszej jakości

2. **Zbalansowany** (Balanced) - domyślny
   - Maksymalny rozmiar: 1200x1200px
   - JPEG quality: 90%
   - Zbalansowana kompresja i jakość
   - Dla większości użytkowników (optymalne dla miniatur)

3. **Oszczędny** (Storage Saver)
   - Maksymalny rozmiar: 800x800px
   - JPEG quality: 80%
   - Maksymalna kompresja, oszczędność miejsca
   - Dla użytkowników z ograniczoną przestrzenią (optymalne dla miniatur)

**Rozszerzenie parametrów (do rozważenia):**
- Osobne ustawienia dla obrazków kontenerów vs przedmiotów
- Konfiguracja formatu wyjściowego (JPEG, WebP, AVIF)
- Zaawansowane opcje kompresji (progressive JPEG, lossless PNG)
- **🔄 Generowanie thumbnails** - automatyczne tworzenie miniatur obrazków dla szybszego ładowania w galeriach i listach
  - Thumbnails w różnych rozmiarach (np. 150x150px, 300x300px, 600x600px)
  - Lazy loading z pełnym obrazkiem na żądanie
  - Oszczędność transferu danych i czasu ładowania
  - Automatyczne generowanie przy uploadzie obrazka
- Różne parametry dla różnych typów obrazków (thumbnail vs full size)
- Opcja zachowania oryginalnego formatu dla wybranych obrazków
- Batch processing settings (przetwarzanie wielu obrazków jednocześnie)

**Implementacja:**
- ✅ Ustawienie użytkownika w profilu (zapisywane w DB)
- ✅ Backend: `ImageProcessor` z konfiguracją per użytkownik
- ✅ Frontend: UI do wyboru trybu w ustawieniach użytkownika (Gear Settings)
- ✅ Automatyczne zastosowanie wybranego trybu przy każdym uploadzie
- ✅ Możliwość zmiany trybu w dowolnym momencie (nie wpływa na już przetworzone obrazy)
- ✅ Ograniczenie dostępu do trybu "Wysoka jakość" tylko dla administratorów
- ✅ Limity rozmiaru plików: 20 MB dla zwykłych użytkowników, 50 MB dla administratorów
- 🔄 Docelowo: Ograniczenie dostępu do trybu "Wysoka jakość" w zależności od planu subskrypcji
- Wsparcie dla obrazków kontenerów (nowa tabela `ContainerImage` lub rozszerzenie istniejącej struktury)

**Zalety:**
- Użytkownik kontroluje balans między jakością a zużyciem przestrzeni
- Oszczędność miejsca dla użytkowników, którzy nie potrzebują najwyższej jakości
- Elastyczność - każdy użytkownik może wybrać odpowiedni tryb dla swoich potrzeb
- Spójność - te same ustawienia przetwarzania dla przedmiotów i kontenerów

### Automatyczne wyszukiwanie obrazków dla przedmiotów
**Status:** 🔄 Planned | **Priority:** Low | **Complexity:** Large | **Feature:** [FEATURE-016](./features/FEATURE-016-automatic-item-image-fetching.md)

- Opcja przy tworzeniu przedmiotu "Wyszukaj obrazki w web"
- Dodatkowa akcja na żądanie dla istniejących przedmiotów
- Ustawienie w ustawieniach użytkownika: "Domyślnie wyszukaj obrazków dla nowych przedmiotów"
- **Dostęp tylko dla adminów** (isAdmin) - funkcjonalność dostępna wyłącznie dla użytkowników z uprawnieniami administratora
- Konfiguracja wielu wyszukiwarek obrazków:
  - Konfiguracja zapisywana na serwerze jako relationship do item
  - Każda wyszukiwarka ma konfigurację:
    - URL sklepu (np. militaria.pl, allegro.pl)
    - Template wyszukiwania (szablon URL z parametrami)
    - Selectors HTML (gdzie w HTML znajdują się obrazki)
    - Lub czyste API (jeśli sklep ma API)
- Wyszukiwanie na podstawie nazwy przedmiotu, marki/firmy i innych parametrów
- Możliwość wyboru obrazu z wyników wyszukiwania
- Cache wyszukanych obrazów
- Fallback do domyślnych ikon gdy brak wyników

### Generowanie SVG z obrazków
**Status:** 🔄 Planned | **Priority:** Low | **Complexity:** Large

- Konwersja obrazów rastowych → SVG
- Tworzenie kompozycji wielu przedmiotów (wizualizacja zawartości plecaka)
- Generowanie layout'u z przedmiotów
- Export do SVG/PNG
- Możliwość edycji kompozycji
- Integracja z biblioteką do wektoryzacji obrazów

---

## 🔍 Monitoring i diagnostyka

### Integracja z Sentry
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Small

**Backend (Python):**
- ✅ Monitoring błędów w czasie rzeczywistym (backend)
- ✅ Automatyczne raportowanie wyjątków i błędów
- ✅ Performance monitoring (transakcje, zapytania DB)
- ✅ Release tracking i deployment notifications
- ✅ Contextualne informacje (user ID, environment, breadcrumbs)
- ✅ Opcjonalne włączenie przez zmienną środowiskową `SENTRY_ENABLED=true`
- ✅ Konfiguracja przez zmienne środowiskowe (DSN, environment, sample rates)

**Frontend (Vue.js):**
- ✅ Integracja z Sentry dla Vue.js - zaimplementowane
- 🔄 Source maps dla lepszego debugowania (frontend) - planowane
- 🔄 User feedback integration - planowane
- 🔄 Browser performance monitoring - planowane

**Konfiguracja (Backend):**
- ✅ Opcjonalne włączenie przez zmienną środowiskową `SENTRY_ENABLED=true`
- ✅ Wymagane zmienne: `SENTRY_DSN` (DSN z Sentry dashboard)
- ✅ Opcjonalne zmienne:
  - `SENTRY_ENVIRONMENT` - środowisko (development, staging, production)
  - `SENTRY_RELEASE` - wersja release (domyślnie APP_VERSION)
  - `SENTRY_TRACES_SAMPLE_RATE` - sample rate dla performance monitoring (0.0-1.0, domyślnie 1.0)
  - `SENTRY_PROFILES_SAMPLE_RATE` - sample rate dla profiling (0.0-1.0, domyślnie 1.0)
- ✅ Jeśli `SENTRY_ENABLED=false` lub brak `SENTRY_DSN`, Sentry nie jest inicjalizowane

**Korzyści:**
- Szybsze wykrywanie i diagnozowanie błędów w produkcji
- Proaktywne powiadomienia o problemach przed zgłoszeniem przez użytkowników
- Lepsze zrozumienie zachowania aplikacji w środowisku produkcyjnym
- Tracking wydajności i bottlenecków

---

## 🎨 UI/UX Improvements

### Uporządkowanie nazewnictwa komponentów autocomplete/select
**Status:** 🔄 Planned | **Priority:** Medium | **Complexity:** Small

**Problem:**
W `ItemFormFields.vue` występuje niespójność w nazewnictwie komponentów autocomplete/select. Niektóre pola używają dedykowanych komponentów, a inne używają bezpośrednio komponentów bazowych.

**Aktualny stan:**
- ✅ `ColorAutocomplete` - dedykowany komponent (OK)
- ✅ `CategorySelect` - dedykowany komponent (OK)
- ❌ `ComboBox` dla brands - powinien być dedykowany komponent (np. `BrandSelect` lub `BrandAutocomplete`)
- ❌ `Select` dla priority - powinien być dedykowany komponent (np. `PrioritySelect`)
- ❌ `Select` dla status - powinien być dedykowany komponent (np. `StatusSelect`)
- ❌ `Select` dla currency - powinien być dedykowany komponent (np. `CurrencySelect`)
- ❌ `Select` dla quality - powinien być dedykowany komponent (np. `QualitySelect`)

**Zadanie:**
- Utworzenie dedykowanych komponentów dla wszystkich pól select/autocomplete
- Ujednolicenie nazewnictwa (wszystkie jako `*Select` lub `*Autocomplete` w zależności od funkcjonalności)
- Refaktoring `ItemFormFields.vue` do użycia dedykowanych komponentów
- Zapewnienie spójności w całej aplikacji

### ✅ Uporządkowanie labeli formularzy (`<Label>` vs ręczne `<label>`)
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Small

**Problem:**
W `ItemFormPage.vue` (np. linie 325–328) oraz innych miejscach ręcznie używane są tagi `<label>` z klasami i gwiazdką wymaganego pola, zamiast spójnego komponentu `Label` z propem `required`.

**Przykład:**
- Ręczny label:
  - `ItemFormPage.vue:325-328` – zwykły `<label>` z klasami Tailwinda i `*` w treści
- Docelowo:
  - Użycie komponentu `Label` z API typu `<Label required>…</Label>`

**Zadanie:**
- ✅ Przejrzenie formularzy itemów/kontenerów (m.in. `ItemFormPage.vue`, `ItemFormFields.vue`)
- ✅ Zamiana ręcznych `<label>` na komponent `Label` tam, gdzie to ma sens
- ✅ Ustalenie i udokumentowanie wzorca: kiedy używać `FormLabel`, a kiedy `Label`
- ✅ Zapewnienie spójności wyglądu i oznaczeń pól wymaganych w całej aplikacji

### ✅ Uporządkowanie użycia translacji (`$t` → `t` + `useI18n`)
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Small

**Problem:**
W wielu komponentach używane jest `$t()` zamiast `t()` z `useI18n()`. Zgodnie z konwencjami Vue 3 Composition API, powinniśmy używać composable `useI18n()` zamiast globalnego `$t`.

**Zaimplementowane zmiany:**
- ✅ Zamiana wszystkich `$t()` na `t()` z `useI18n()` w `ItemFormFields.vue` (44 wystąpienia)
- ✅ Zamiana wszystkich `$t()` na `t()` z `useI18n()` w `ContainerFormFields.vue` (28 wystąpień)
- ✅ Zamiana wszystkich `$t()` na `t()` z `useI18n()` w `ContainerHeader.vue` (3 wystąpienia)
- ✅ Zamiana wszystkich `$t()` na `t()` z `useI18n()` w `ColorAutocomplete.vue` (1 wystąpienie)
- ✅ Dodanie `const { t } = useI18n()` w komponentach, które tego wymagały

**Korzyści:**
- ✅ Spójność z Vue 3 Composition API
- ✅ Lepsze TypeScript support
- ✅ Łatwiejsze testowanie (możliwość mockowania `useI18n`)
- ✅ Zgodność z best practices Vue 3

---

## 📱 Aplikacja mobilna

### ✅ PWA (Progressive Web App)
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Medium

- ✅ Konwersja aplikacji na PWA (`vite-plugin-pwa`)
- ✅ Manifest.json z konfiguracją PWA
- ✅ Service Worker (Workbox)
- ✅ Instalacja na urządzenia mobilne
- ✅ Offline support z cache'owaniem
- ✅ Komponent `PwaUpdatePrompt` do aktualizacji
- ✅ Runtime caching dla API, fonts, assets
- 🔄 Push notifications - opcjonalnie (planowane)
- ✅ Responsywny design dla urządzeń mobilnych

---

## 📈 Priorytetyzacja

### High Priority (Następne do zrobienia)
1. ✅ **Autoryzacja i konta użytkowników** - High priority, Large complexity (Completed)
2. ✅ **Globalny katalog itemów** - High priority, Medium complexity (Completed)
3. ✅ **Linkowanie przedmiotów** - High priority, Large complexity (Completed)
4. ✅ **Rozszerzone ustawienia użytkownika** (waluta, kategorie, marki w DB) - High priority, Small complexity (Completed)
5. ✅ **Ocenianie (gwiazdki) kontenerów** - High priority, Medium complexity (Completed)
6. ✅ **Przenoszenie przedmiotów między kontenerami** - High priority, Medium complexity (Completed)
7. ✅ **Domyślna widoczność nowych kontenerów** - High priority, Small complexity (Completed)
8. 🔄 **Statystyki wyświetleń kontenerów** - High priority, Medium complexity (Planned)
9. 🚧 **Sekcja AI w Gear Settings** - High priority, Medium complexity (Partially Completed)

### Medium Priority
1. **Synchronizacja między urządzeniami** - Medium priority, Large complexity
2. **Udostępnianie kontenerów** - Medium priority, Medium complexity
3. **System zaproszeń** - Medium priority, Large complexity
4. **Poprawa wyszukiwarki katalogu globalnego** - Medium priority, Medium complexity
5. ✅ **PWA** - Medium priority, Medium complexity (Completed)
6. ✅ **Galeria publiczna kontenerów** - Medium priority, Medium complexity (Completed)

### Low Priority
1. ✅ **Profil użytkownika - link do Gravatara** - Low priority, Small complexity (Completed)
2. **Wersjonowanie danych** - Low priority, Large complexity
3. ✅ **Galeria publiczna** - Low priority, Medium complexity (Completed - główna funkcja zaimplementowana, ocenianie i komentarze planowane)
4. **Funkcje AI** - Low priority, Large complexity
5. **Statystyki i raporty** - Low priority, Medium complexity

---

## 📝 Notatki

- Wszystkie funkcjonalności w tym pliku wymagają backendu, bazy danych i/lub autoryzacji
- Backend auth module już istnieje w `backend/app/modules/auth/`
- Complexity: Small (1-2 dni), Medium (3-5 dni), Large (1+ tygodnie)
- Priorytety mogą się zmieniać w zależności od potrzeb użytkowników

