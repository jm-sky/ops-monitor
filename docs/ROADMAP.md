# Roadmap Index - Gear Stack

<!-- 
AI_METADATA:
- Type: Roadmap index/overview
- Purpose: Entry point for understanding project roadmap structure
- Last Updated: 2025-01-21
-->

Ten dokument jest punktem wejścia do roadmap projektu Gear Stack. Projekt ma **2 osobne roadmapy** ze względu na architekturę aplikacji (offline-first z opcjonalnym backendem).

---

## 🎯 Nadchodzące zadania (Prioritized)

Lista zadań, którymi chcę się zająć w najbliższym czasie:

### Wysoki priorytet

1. **Bezpieczeństwo aplikacji (Security Hardening)** - 🚧 In Progress
   - 📍 Plan: [SECURITY_IMPROVEMENT_PLAN.md](./security/SECURITY_IMPROVEMENT_PLAN.md)
   - 📍 Docker Security: [SECURITY_FIX.md](./SECURITY_FIX.md)
   - ✅ **Critical:** Implementacja security headers (CSP, HSTS, X-Frame-Options) - Completed (v2.47.0)
   - 📋 **Low:** PostgreSQL SSL/TLS (opcjonalne - Docker network zapewnia izolację)
   - 🔒 **High:** Implementacja WAF (Web Application Firewall)
   - 🔒 **High:** Procedury backup/recovery bazy danych
   - 🔐 **Medium:** Migracja na httpOnly cookies (obecnie localStorage)
   - 🔐 **Medium:** Implementacja CSRF protection
   - 🛡️ **Medium:** Strict CORS configuration
   - 📋 **Low:** Procedury rotacji sekretów (secrets rotation)
   - 📊 **Low:** Security monitoring & alerting
   - Status: 🚧 In Progress | Priority: Critical | Complexity: Large
   - **Uwaga:** Wymaga zmian w backend middleware, Caddy config, i frontend auth

2. ✅ **UUID support dla update workflow** - Zakończone
   - 📍 Lokalizacja: [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md#uuid-support-dla-update-workflow)
   - Wykorzystanie istniejącego UUID (`id`) do aktualizacji istniejących kontenerów/przedmiotów podczas importu markdown
   - Status: ✅ Completed | Priority: Medium | Complexity: Medium

2. ✅ **Media** - Zakończone (v2.15.0)
   - 📍 Lokalizacja: [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md#-media-i-zasoby-graficzne)
   - ✅ **Show from URL** — opcja dodawania obrazków z URL
   - ✅ **Primary image w wierszu tabeli** — opcjonalne wyświetlanie miniaturki primary image w tabeli przedmiotów
   - Status: ✅ Completed

3. ✅ **Katalog i linkowanie** - Zakończone
   - 📍 Lokalizacja: [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md#-globalny-katalog-i-linkowanie)
   - ✅ **Globalny katalog itemów** — High priority, Medium complexity (Completed)
   - 📋 **Plan implementacji:** [GLOBAL_CATALOGUE_IMPLEMENTATION_PLAN.md](./plans/GLOBAL_CATALOGUE_IMPLEMENTATION_PLAN.md)
   - ✅ **Linkowanie przedmiotów** — High priority, Large complexity (Completed)
   - Status: ✅ Completed

4. ✅ **Rozszerzone ustawienia użytkownika (waluta, widoczność, kategorie, marki w DB)** - Zakończone
   - 📍 Lokalizacja: [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md#-ustawienia-użytkownika-wymagające-db)
   - ✅ **Domyślna waluta użytkownika** (zapisywana w DB) - Completed
   - ✅ **Domyślna widoczność nowych kontenerów** - Completed
   - ✅ **Dodawanie nowych kategorii** (zapisywane w DB) - Completed
   - ✅ **Dodawanie firm/marek (brand)** — zapisywane w DB - Completed
   - Status: ✅ Completed | Priority: High | Complexity: Small

5. **Funkcje AI**
   - 📍 Lokalizacja: [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md#-funkcje-ai-wymagające-backend)
   - Infrastruktura AI (OpenRouter, zarządzanie tokenami, historia, cache)
   - Status: 🚧 Partially Completed (v2.17.3+) | Priority: Medium | Complexity: Large
   - ✅ Chat interface z AI (Phase 1 & 2)
   - ✅ Model selection, token management, context configuration
   - ✅ History tracking, cost display, template messages
  - ✅ Backend endpoints do zarządzania historią (GET, DELETE)
  - ✅ Frontend composable do zarządzania historią
  - ✅ **Zarządzanie historią - UI:** przeglądanie historii chatów, powrót do konwersacji, kasowanie historii - Completed
  - ✅ **Sprawdzenie i poprawa działania strony AiHistory** - Completed (przywracanie konwersacji działa)
  - 🔄 Classification, embeddings, vision models - planowane

6. ✅ **AI settings - Premium feature** - Zakończone
   - 📍 Lokalizacja: [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md)
   - ✅ Ustawienia AI powinny być wyłączone (disabled inputs) dla zwykłych użytkowników - Completed
   - ✅ Informacja "Only for premium users" lub "Premium feature" - Completed
   - Status: ✅ Completed | Priority: High | Complexity: Small

7. ✅ **Wskaźnik użycia S3 storage** - Zakończone
   - 📍 Lokalizacja: [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md)
   - ✅ Wyświetlanie w Settings (`StorageUsageCard.vue`)
   - ✅ Limit: 20 MB (zwykli użytkownicy), 50 MB (admin) - konfigurowalny przez zmienne środowiskowe
   - Status: ✅ Completed | Priority: High | Complexity: Medium

8. ✅ **DataTable - Pinned Columns** - Zakończone
   - 📍 Lokalizacja: [ROADMAP_OFFLINE.md](./ROADMAP_OFFLINE.md#-datatable---pinned-columns-pin-right-dla-kolumny-akcji)
   - ✅ Dodanie wsparcia dla pinned columns (pin-right dla kolumny akcji) w komponencie DataTable
   - ✅ Kolumna akcji zawsze widoczna podczas poziomego przewijania
   - ✅ Synchronizacja cienia pinned columns z horizontal scroll state
   - ✅ Transition dla płynnego pojawiania się/znikania cienia
   - ✅ Composable `useHorizontalScroll` do śledzenia stanu scrolla
   - Status: ✅ Completed | Priority: Medium | Complexity: Small

9. **Unifikacja modeli kontenerów i przedmiotów**
   - 📍 Analiza: [UNIFIED_MODEL_ANALYSIS.md](./analysis/UNIFIED_MODEL_ANALYSIS.md)
   - Połączenie modeli `IGearContainer` i `IGearItem` w jeden model `IGearEntity` z flagą `isContainer`
   - Uproszczenie zagnieżdżania (plecak → kubek → pudełko → zapałki) - jeden mechanizm `parentId`
   - Wspólne obrazki dla kontenerów i przedmiotów (jedna tabela `entity_images`)
   - Prostsze zapytania SQL (jedna tabela zamiast dwóch)
   - Status: 🔄 Analysis Complete | Priority: High | Complexity: Large
   - **Uwaga:** Wymaga migracji danych i refaktoryzacji ~80-150 plików (2-4 tygodnie pracy)

10. **Pełna analiza backend i frontend + refaktoryzacja**
   - Pełna analiza architektury backend i frontend
   - Identyfikacja problemów i obszarów do poprawy
   - Refaktoryzacja kodu zgodnie z najlepszymi praktykami
   - Status: 🚧 In Progress | Priority: High | Complexity: Large

11. ✅ **Loading state przed wczytaniem JavaScript w index.html** - Zakończone
   - Dodanie stanu ładowania w `index.html` przed załadowaniem aplikacji Vue
   - Zapobieganie białemu ekranowi podczas inicjalizacji aplikacji
   - Status: ✅ Completed | Priority: High | Complexity: Small

12. ✅ **Welcome back message and links on landing page for already logged in users**
   - Dodanie komunikatu powitalnego na stronie głównej dla zalogowanych użytkowników
   - Linki do głównych sekcji aplikacji (np. kontenery, ustawienia)
   - Status: ✅ Completed | Priority: High | Complexity: Small

13. ✅ **Nie działa zmiana ilości wierszy przedmiotów (limit) na stronie Container Details** - Zakończone
   - Naprawa funkcjonalności zmiany limitu wierszy w tabeli przedmiotów na stronie szczegółów kontenera
   - Problem: Zmiana pageSize nie propaguje się w górę do parent component (brak emit w client-side mode)
   - Status: ✅ Completed | Priority: High | Complexity: Small

### Średni priorytet

1. **Zabezpieczenie linków w markdown** - Phase 1 Completed
   - 📍 Lokalizacja: [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md#zabezpieczenie-linków-w-markdown)
   - 📋 **Plan implementacji:** [MARKDOWN_LINK_SECURITY_PLAN.md](./plans/MARKDOWN_LINK_SECURITY_PLAN.md)
   - ✅ **Phase 1 (v2.45.0):** Walidacja protokołów, limity długości, rel="noopener noreferrer", sanityzacja przed zapisem
   - 🔄 **Phase 2 (Planned):** Homograph detection, dialog potwierdzenia, blokowanie zewnętrznych obrazów
   - Status: 🚧 Partially Completed (Phase 1) | Priority: Medium | Complexity: Medium

2. ✅ **Nawigacja przycisku "Wróć"** - Zakończone
   - 📍 Lokalizacja: [FEATURE-028-back-button-navigation.md](./features/FEATURE-028-back-button-navigation.md)
   - Naprawa nawigacji przycisku "Wróć" w różnych komponentach aplikacji
   - Użycie parametru `from` zamiast `router.back()` dla przewidywalnej nawigacji
   - Status: ✅ Completed | Priority: High | Complexity: Small

3. ✅ **Przenoszenie przedmiotów między kontenerami** - Zakończone
   - 📍 Lokalizacja: [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md#-przenoszenie-przedmiotów-między-kontenerami)
   - Dialog wyboru kontenera docelowego, endpoint API, pełna implementacja backend + frontend
   - Status: ✅ Completed | Priority: High | Complexity: Medium

4. ✅ **Kasowanie obrazków z S3** - Zakończone
   - 📍 Lokalizacja: [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md)
   - ✅ Automatyczne usuwanie z S3 po usunięciu przedmiotu
   - ✅ Automatyczne usuwanie z S3 po usunięciu kontenera
   - ✅ Automatyczne usuwanie z S3 po usunięciu wszystkich kontenerów
   - ✅ Automatyczne usuwanie z S3 po usunięciu konta użytkownika
   - Status: ✅ Completed | Priority: Medium | Complexity: Medium

5. ✅ **Automatyczny wybór jednostki wagi (auto) i formatowanie z separatorem tysięcznym** - Zakończone
   - 📍 Lokalizacja: [ROADMAP_OFFLINE.md](./ROADMAP_OFFLINE.md#-automatyczny-wybór-jednostki-wagi-auto-i-formatowanie-z-separatorem-tysięcznym) | [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md#-ustawienia-użytkownika-wymagające-db)
   - Opcje `auto g/kg` i `auto oz/lb` dla preferowanej jednostki wagi
   - Automatyczny wybór jednostki w zależności od wartości wagi (< 1 kg → g/oz, ≥ 1 kg → kg/lb)
   - Formatowanie liczby z separatorem tysięcznym (np. `1 500 g`)
   - Aktualizacja backendu (API, walidacja, baza danych) i migracja kolumny `preferred_weight_unit`
   - Status: ✅ Completed | Priority: Medium | Complexity: Small

6. **Ulepszenia inspirowane LighterPack**
   - 📍 Lokalizacja: [LIGHTERPACK_IMPROVEMENTS_TASKS.md](./comparison/LIGHTERPACK_IMPROVEMENTS_TASKS.md)
   - 📋 **Tryb prosty** - [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md#-tryb-prosty-simple-mode-inspiracja-lighterpack) - toggle w ustawieniach, ukryte zaawansowane funkcje
   - 📋 **Drag & Drop** - [ROADMAP_OFFLINE.md](./ROADMAP_OFFLINE.md#-drag--drop---rozszerzenie-inspiracja-lighterpack) - rozszerzenie kolejności przedmiotów + przenoszenie między kontenerami
   - 📋 **System pomocy / Tutorial** - [ROADMAP_OFFLINE.md](./ROADMAP_OFFLINE.md#-system-pomocy--tutorial-inspiracja-lighterpack) - ramki z pomocą, przycisk `?`, AI Chat
   - 📋 **Kontekstowe podpowiedzi** - [ROADMAP_OFFLINE.md](./ROADMAP_OFFLINE.md#-kontekstowe-podpowiedzi-inspiracja-lighterpack) - tooltips, empty states, podpowiedzi w formularzach
   - 📋 **Quick Add / Inline Editing** - [ROADMAP_OFFLINE.md](./ROADMAP_OFFLINE.md#-quick-add--inline-editing---dopracowanie-inspiracja-lighterpack) - dopracowanie UX, quick add bez formularza
   - 📋 **Import CSV** - [ROADMAP_OFFLINE.md](./ROADMAP_OFFLINE.md#-import-csv-inspiracja-lighterpack) - nowa funkcjonalność (export już istnieje)
   - 📋 **Lepsze wizualizacje** - [ROADMAP_OFFLINE.md](./ROADMAP_OFFLINE.md#-lepsze-wizualizacje-inspiracja-lighterpack) - ulepszenie wykresów donut
   - 📋 **Natychmiastowe obliczenia wagi** - [ROADMAP_OFFLINE.md](./ROADMAP_OFFLINE.md#-natychmiastowe-obliczenia-wagi-inspiracja-lighterpack) - real-time podczas edycji
   - Status: 🔄 Planned | Priority: Medium | Complexity: Various

7. **Migracja z vue-i18n na Intlayer**
   - 📍 Plan: [intlayer-migration-plan.md](./intlayer-migration-plan.md)
   - Pełna migracja z vue-i18n na Intlayer (component-scoped translations)
   - Korzyści: tree-shaking, lazy loading, lepszy TypeScript support, auto-generated types
   - 9 faz implementacji: 221 komponentów, 2401 linii tłumaczeń, 7 modułów
   - Szacowany czas: 3.5-5 tygodni (17-26 dni roboczych)
   - Status: 🔄 Planned | Priority: Medium | Complexity: Large
   - **Uwaga:** Wymaga refaktoryzacji wszystkich komponentów używających `useI18n()` → `useIntlayer()`

### Obniżony priorytet (trudne zadania)

1. **Warianty kontenera**
   - 📍 Lokalizacja: [ROADMAP_OFFLINE.md](./ROADMAP_OFFLINE.md)
   - Ten sam kontener, różna zawartość
   - Status: 🔄 Planned | Priority: Low | Complexity: Medium

2. **Porównywarka kontenerów**
   - 📍 Lokalizacja: [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md)
   - Porównywanie kontenerów osobistych i publicznych
   - Status: 🔄 Planned | Priority: Low | Complexity: Large

3. **Automatyczne wyszukiwanie obrazków dla przedmiotów**
   - 📍 Lokalizacja: [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md#automatyczne-wyszukiwanie-obrazków-dla-przedmiotów)
   - Status: 🔄 Planned | Priority: Medium | Complexity: Large

4. **Generowanie SVG z obrazków**
   - 📍 Lokalizacja: [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md#generowanie-svg-z-obrazków)
   - Status: 🔄 Planned | Priority: Low | Complexity: Large

---

## 📋 Struktura Roadmap

### [ROADMAP_OFFLINE.md](./ROADMAP_OFFLINE.md) - Offline Features
**688 linii** | **~50+ funkcji**

Funkcjonalności działające z **localStorage**, bez potrzeby backendu (offline-first):
- ✅ Zarządzanie kontenerami i przedmiotami
- ✅ Eksport/import markdown (AI-friendly format)
- ✅ Wykresy i analityka (kategorie, cena, priorytet)
- ✅ Kolorowanie kontenerów
- ✅ Rozpoznawanie kategorii i parametrów
- ✅ Inline editing (częściowo zakończone - v2.25.0: edycja nazwy przedmiotu)
- ✅ Custom brand management
- ✅ Strona z listą wszystkich przedmiotów
- ✅ Strona planowania zakupów
- ✅ Dedykowane ikony dla kategorii
- ✅ Relacja parent-children (nesting kontenerów)
- ✅ Dodatkowe pola (cena, URL, marka, kolor, wearable, consumable)
- ✅ Obsługa waluty (currency)
- ✅ Kopiowanie/klonowanie kontenerów
- ✅ Dodawanie istniejących przedmiotów do kontenera
- ✅ Kolejność przedmiotów w kontenerze (drag & drop)
- ✅ Maksymalna waga kontenera (maxWeight)
- ✅ Rozpoznawanie parametrów przedmiotów na żądanie
- ✅ Strona 404 i error handling
- ✅ Footer i strony prawne
- 🔄 Oznaczanie kontenerów jako fragmentów rodzica - planowane
- ✅ Obsługa Markdown w notatkach - ukończone
- 🔄 Zwijanie sekcji statystyk - planowane
- ✅ Podstawowe oznaczenia ARIA i dostępność - ukończone

**Kiedy sprawdzać:** Gdy implementujesz funkcje działające offline lub z localStorage.

---

### [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md) - Online Features
**342 linie** | **~30+ funkcji**

Funkcjonalności wymagające **backendu, bazy danych i/lub autoryzacji** (online/cloud):
- ✅ OAuth authentication (completed)
- ✅ reCAPTCHA integration (completed)
- ✅ 2FA (completed)
- ✅ Udostępnianie kontenerów (publiczne + token sharing)
- ✅ Galeria publiczna kontenerów
- ✅ Linkowanie przedmiotów (zmiana w jednym → zmiana w wielu)
- ✅ Rozszerzone ustawienia użytkownika (waluta, widoczność, kategorie, marki w DB)
- ✅ Domyślna widoczność nowych kontenerów
- ✅ Wskaźnik użycia S3 storage
- ✅ Profil użytkownika - link do Gravatara
- ✅ UUID support dla update workflow
- ✅ Zdjęcia przedmiotów (galeria, upload, S3)
- ✅ Przetwarzanie obrazków z ustawieniami użytkownika (3 tryby)
- ✅ PWA (Progressive Web App)
- ✅ Ocenianie (gwiazdki) kontenerów - Completed
- 🚧 Infrastruktura AI (OpenRouter, chat, historia) - częściowo zakończone
- 🚧 Sekcja AI w Gear Settings - częściowo zakończone
- 🚧 Synchronizacja między urządzeniami - częściowo zakończone
- ✅ Integracja z Sentry (backend + frontend) - completed
- 🔄 Multi-device synchronization (automatyczna) - planowane
- ✅ Global item catalog - completed
- ✅ Przenoszenie przedmiotów między kontenerami - completed
- 🔄 Statystyki wyświetleń kontenerów - planowane
- 🔄 System zaproszeń - planowane
- 🔄 Szablony kontenerów - planowane
- 🔄 Wersjonowanie danych (historia zmian) - planowane
- 🔄 Automatyczne wyszukiwanie obrazków dla przedmiotów - planowane

**Kiedy sprawdzać:** Gdy implementujesz funkcje wymagające serwera, bazy danych lub systemu użytkowników.

---

## 🎯 Jak używać z AI Agentem

### Dla funkcji offline:
```
Sprawdź: docs/ROADMAP_OFFLINE.md
Filtruj: Szukaj sekcji z tagiem "offline" lub "localStorage"
```

### Dla funkcji online:
```
Sprawdź: docs/ROADMAP_ONLINE.md
Filtruj: Szukaj sekcji z tagiem "Backend/DB/Auth Required" lub "online"
```

### Dla pełnego obrazu:
```
Sprawdź: Oba pliki (ROADMAP_OFFLINE.md + ROADMAP_ONLINE.md)
Uwaga: Większość funkcji jest w ROADMAP_OFFLINE.md (offline-first approach)
```

---

## 📊 Statystyki

| Plik | Linie | Funkcje | Status |
|------|-------|---------|--------|
| ROADMAP_OFFLINE.md | 688 | ~50+ | ✅ Aktywny |
| ROADMAP_ONLINE.md | 342 | ~30+ | ✅ Aktywny |
| **Razem** | **1030** | **~80+** | - |

---

## 🔍 Szybkie wyszukiwanie

### Offline Features (ROADMAP_OFFLINE.md):
- Kategorie: 🌐 Internacjonalizacja, 🎨 UI/UX, 🔗 Relacje, 📝 Pola, 🚀 Import/Export, ⚡ Usprawnienia, ✏️ Edycja, 📊 Wizualizacje, ⚖️ Kontrola wagi, 🛠️ Obsługa błędów

### Online Features (ROADMAP_ONLINE.md):
- Kategorie: 🔐 Autoryzacja, 💾 Synchronizacja, 👥 Udostępnianie, 🗂️ Katalog, ⚙️ Ustawienia, 🚀 Import/Export, 📊 Statystyki, 🎯 Szablony, 🤖 AI, 📷 Media, 📱 PWA

---

## 💡 Uwagi dla AI

1. **Zawsze sprawdzaj oba pliki** jeśli nie jesteś pewien, gdzie szukać
2. **ROADMAP_OFFLINE.md jest głównym** - większość funkcji jest tam (offline-first approach)
3. **ROADMAP_ONLINE.md jest uzupełnieniem** - tylko funkcje wymagające backendu/cloud
4. **Statusy są aktualizowane na bieżąco** - sprawdź emoji (✅ Completed, 🔄 Planned, 🚧 In Progress)
5. **Każda funkcja ma link do szczegółowego planu** w `docs/features/`

---

**Ostatnia aktualizacja:** 2025-12-29

