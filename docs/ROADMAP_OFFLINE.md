# Roadmap Offline - Gear Stack

<!-- 
AI_METADATA:
- Type: Offline roadmap (localStorage-based)
- Requirements: localStorage only, no backend/DB/auth needed
- Status: Active development
- Related: See ROADMAP_ONLINE.md for online/backend features
- Total Features: ~50+ features
-->

Lista planowanych funkcjonalności i ulepszeń aplikacji - **offline features** (działające z localStorage, bez potrzeby backendu, bazy danych lub autoryzacji).

> 📋 **Zobacz też:** 
> - [ROADMAP.md](./ROADMAP.md) - główny indeks roadmap
> - [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md) - funkcjonalności wymagające backendu/DB/auth
> - [Features Implementation Plans](./features/README.md) - szczegółowe plany implementacji

---

## 📊 Status Overview

- ✅ **Completed** - Zaimplementowane i przetestowane
- 🚧 **In Progress** - W trakcie implementacji
- 🔄 **Planned** - Zaplanowane, nie rozpoczęte
- ⏸️ **On Hold** - Tymczasowo wstrzymane
- ❌ **Cancelled** - Anulowane

---

## 🌐 Internacjonalizacja

### ✅ Wykrywanie języka (locale) z ustawień przeglądarki
**Status:** ✅ Completed | **Priority:** Medium | **Feature:** [FEATURE-001](./features/FEATURE-001-locale-detection.md)

- ✅ Automatyczne wykrywanie języka użytkownika na podstawie ustawień przeglądarki
- ✅ Fallback do domyślnego języka (np. polski)
- ✅ Możliwość ręcznej zmiany języka w ustawieniach
- ✅ HTML lang attribute automatycznie ustawiany na podstawie wykrytego języka
- ✅ Wykryty język zapisywany w localStorage

### ✅ Preferowana jednostka wagi
**Status:** ✅ Completed | **Priority:** Medium

- ✅ Użytkownik może ustawić preferowaną jednostkę wagi w ustawieniach (g lub kg)
- ✅ Wszystkie wyświetlane wagi na dashboard, w tabelach i kartach będą konwertowane do preferowanej jednostki
- ✅ Formularze nadal mogą używać różnych jednostek, ale wyświetlanie będzie spójne
- ✅ Ustawienie zapisywane w localStorage i synchronizowane w całej aplikacji

### ✅ Dodatkowe jednostki wagi (oz, lb)
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Medium

- ✅ Dodanie jednostek imperialnych: uncje (oz) i funty (lb)
- ✅ Rozszerzenie typu `TGearWeightUnit` o `'oz'` i `'lb'`
- ✅ Aktualizacja funkcji konwersji w `formatWeight.ts`:
  - ✅ Konwersja oz → g (1 oz = 28.3495 g)
  - ✅ Konwersja lb → g (1 lb = 453.592 g)
  - ✅ Konwersja g → oz i g → lb
- ✅ Aktualizacja formularzy (ItemFormFields, ContainerFormFields) - dodanie opcji oz i lb
- ✅ Aktualizacja preferowanej jednostki wagi w ustawieniach - dodanie oz i lb jako opcji
- ✅ Aktualizacja tłumaczeń (PL/EN) dla nowych jednostek
- ✅ Aktualizacja parsera markdown import - rozpoznawanie oz i lb w eksporcie/impocie
- ✅ Aktualizacja walidacji (zod schemas) - dodanie oz i lb do enum
- ✅ Wszystkie wyświetlane wagi będą konwertowane do preferowanej jednostki (w tym oz/lb)

### ✅ Automatyczny wybór jednostki wagi (auto) i formatowanie z separatorem tysięcznym
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Small

- ✅ Dodanie opcji `auto` dla preferowanej jednostki wagi w ustawieniach (`auto-g-kg`, `auto-oz-lb`)
- ✅ Logika automatycznego wyboru jednostki:
  - Jeśli waga < 1 kg → wyświetlanie w `g` (dla systemu metrycznego) lub `oz` (dla systemu imperialnego)
  - Jeśli waga ≥ 1 kg → wyświetlanie w `kg` (dla systemu metrycznego) lub `lb` (dla systemu imperialnego)
- ✅ Obsługa dwóch wariantów auto:
  - `auto g/kg` - automatyczny wybór między gramami a kilogramami
  - `auto oz/lb` - automatyczny wybór między uncjami a funtami
- ✅ Formatowanie liczby z separatorem tysięcznym:
  - Dodanie separatorów tysięcy w wyświetlanych wagach (np. `1 500 g` zamiast `1500 g`)
  - Uwzględnienie lokalizacji użytkownika (separator zależny od ustawień języka)
- ✅ Aktualizacja funkcji `formatWeight.ts` - dodanie logiki auto i formatowania
- ✅ Aktualizacja ustawień użytkownika - dodanie opcji `auto g/kg` i `auto oz/lb`
- ✅ Aktualizacja tłumaczeń (PL/EN) dla nowych opcji
- ✅ **Backend/API wymagania** (zobacz [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md#-automatyczny-wybór-jednostki-wagi-auto-i-formatowanie)):
  - ✅ Rozszerzenie typu `TGearWeightUnit` w backendzie o `'auto-g-kg'` i `'auto-oz-lb'`
  - ✅ Aktualizacja schematów walidacji (Pydantic) w backendzie - dodanie nowych wartości do enum
  - ✅ Aktualizacja modelu `GearSettingsDB` w bazie danych - obsługa nowych wartości jednostki wagi
  - ✅ Aktualizacja endpointów API (`/me/gear-settings`) - walidacja i zapis nowych opcji
  - ✅ Migracja bazy danych – zwiększenie długości kolumny `preferred_weight_unit` do VARCHAR(10)

### Przeniesienie ustawiania atrybutu lang do inicjalizacji aplikacji
**Status:** ✅ Completed | **Priority:** Low | **Complexity:** Small

- Przeniesienie ustawiania `document.documentElement.setAttribute('lang', ...)` z `main.ts` do bardziej odpowiedniego miejsca w inicjalizacji aplikacji
- Obecna lokalizacja: `src/main.ts` (linia 47) - TODO w komentarzu
- **Do weryfikcji:** Czy obecne miejsce jest wystarczające, czy powinno być przeniesione do dedykowanego composable/helper inicjalizacyjnego

---

## 🎨 UI/UX Ulepszenia

### 🔄 System pomocy / Tutorial (inspiracja LighterPack)
**Status:** 🔄 Planned | **Priority:** Medium | **Complexity:** Small-Medium | **Source:** [LIGHTERPACK_IMPROVEMENTS_TASKS.md](../comparison/LIGHTERPACK_IMPROVEMENTS_TASKS.md)

**Koncepcja:**
Dodanie systemu pomocy i kontekstowych podpowiedzi dla użytkowników, inspirowane prostotą LighterPack.

**Wymagania:**
- Małe ramki z pomocą (contextual help boxes)
- Przycisk `?` na górze który pokaże sugestie/podpowiedzi
- Możliwość dodania AI Chat jako pomoc

**Szczegóły implementacji:**
- **Ramki z pomocą:**
  - Tooltips przy pierwszym użyciu funkcji
  - Highlighting ważnych elementów
  - Dismissible (możliwość zamknięcia)
- **Przycisk `?`:**
  - W headerze aplikacji lub na każdej stronie
  - Dropdown/modal z sugestiami dla aktualnej strony
  - Linki do dokumentacji
- **AI Chat jako pomoc:**
  - Opcjonalna integracja z istniejącym AI Chat
  - Kontekstowe sugestie na podstawie aktualnej strony

### 🔄 Kontekstowe podpowiedzi (inspiracja LighterPack)
**Status:** 🔄 Planned | **Priority:** Medium | **Complexity:** Small | **Source:** [LIGHTERPACK_IMPROVEMENTS_TASKS.md](../comparison/LIGHTERPACK_IMPROVEMENTS_TASKS.md)

**Wymagania:**
- Tooltips przy ważnych elementach
- Empty states z sugestiami co zrobić
- Kontekstowe podpowiedzi w formularzach

**Szczegóły implementacji:**
- Tooltips dla wszystkich akcji i przycisków
- Empty states z konkretnymi sugestiami (np. "Dodaj pierwszy przedmiot", "Utwórz kontener")
- Formularze: podpowiedzi pod polami (np. "Waga w gramach", "Format daty: DD.MM.YYYY")

### ✅ Strona z listą wszystkich przedmiotów
**Status:** ✅ Completed | **Priority:** High | **Complexity:** Medium

- ✅ Nowa strona wyświetlająca listę wszystkich przedmiotów ze wszystkich kontenerów
- ✅ Dostępna jako kolejna pozycja w topbar navigation (obok "Kontenery")
- ✅ Tabela przedmiotów z kolumnami:
  - ✅ Kategoria (z ikoną)
  - ✅ Nazwa przedmiotu
  - ✅ Kontener (nazwa kontenera, z którego pochodzi przedmiot, z wizualizacją koloru)
  - ✅ Ilość
  - ✅ Waga
  - ✅ Status
  - ✅ Priorytet
  - ✅ Marka (opcjonalnie, ukryta domyślnie)
  - ✅ Kolor (opcjonalnie, ukryty domyślnie)
- ✅ Możliwość filtrowania i sortowania:
  - ✅ Filtrowanie po kategorii, statusie, priorytecie
  - ✅ Filtrowanie po kontenerze (przez wyszukiwarkę)
  - ✅ Sortowanie po dowolnej kolumnie
- ✅ Możliwość szybkiego przejścia do kontenera, w którym znajduje się przedmiot (kliknięcie w nazwę kontenera)
- ✅ Wyszukiwarka przedmiotów (globalne filtrowanie)
- ✅ Zarządzanie widocznością kolumn z zapisem w localStorage

### ✅ Zapisywanie wartości search/filtrów w localStorage
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Small

**Koncepcja:**
Na stronach z filtrami (np. AllItemsPage, ShoppingPlanningPage, ContainersListPage, PublicContainersBrowserPage), zapisywać wartości search i filtrów w localStorage, aby przy powrocie (przycisk "Wróć" lub nawigacja wstecz) użytkownik wracał dokładnie w to samo miejsce z zachowanymi filtrami.

**Implementacja:**
- Zapisywanie do localStorage:
  - Wartość pola search/wyszukiwarki
  - Wartości wszystkich aktywnych filtrów (kategorie, status, priorytet, typ kontenera, itp.)
  - Opcjonalnie: sortowanie i widoczność kolumn (jeśli jeszcze nie są zapisywane)
- Przywracanie stanu:
  - Przy montowaniu komponentu (`onMounted`) sprawdzić localStorage
  - Jeśli istnieją zapisane wartości → przywrócić je do stanu komponentu
  - Opcjonalnie: wyczyścić localStorage po załadowaniu (jednorazowe przywrócenie) lub zachować dla następnej sesji
- Klucze localStorage:
  - Unikalne klucze per strona (np. `gear-stack:all-items:filters`, `gear-stack:shopping-planning:filters`)
  - Struktura: obiekt z wartościami filtrów i search

**Strony do zaktualizowania:**
- `AllItemsPage.vue` - search, filterType, filtry kategorii/statusu/priorytetu
- `ShoppingPlanningPage.vue` - search, filtry kategorii, budget, includeExpiringSoon
- `ContainersListPage.vue` - search, filtry typu kontenera, showOnlyRootContainers
- `PublicContainersBrowserPage.vue` - search, filtry
- Inne strony z filtrami (jeśli istnieją)

**Zalety:**
- Lepsze UX - użytkownik nie traci ustawionych filtrów przy nawigacji
- Szybsze wracanie do wcześniejszego stanu wyszukiwania
- Spójność z innymi funkcjami zapisującymi stan w localStorage (np. column visibility)

### ✅ Strona planowania zakupów
**Status:** ✅ Completed | **Priority:** High | **Complexity:** Medium

- ✅ Nowa strona wyświetlająca listę przedmiotów do zakupu i z bliskim terminem ważności
- ✅ Dostępna jako pozycja w topbar navigation (obok "Kontenery" i "Wszystkie przedmioty")
- ✅ Wyświetlanie przedmiotów z statusem "To buy" oraz opcjonalnie z bliskim terminem ważności
- ✅ Sortowanie według priorytetu (critical → high → medium → low)
- ✅ Filtrowanie po kategoriach (wielokrotny wybór)
- ✅ Filtrowanie po budżecie (ogranicza listę do przedmiotów mieszczących się w budżecie)
- ✅ Możliwość dodawania/usuwania pozycji z listy zakupów
- ✅ Podsumowanie listy zakupów z liczbą przedmiotów i całkowitą ceną
- ✅ Eksport listy zakupów jako markdown (z podziałem na priorytety)
- ✅ Wszystkie teksty przetłumaczone przez i18n (PL/EN)
- ✅ Lista zakupów zapisywana w localStorage (persystencja między sesjami)

### ✅ Dedykowane ikony dla kategorii
**Status:** ✅ Completed | **Priority:** High | **Feature:** [FEATURE-002](./features/FEATURE-002-category-icons.md)

- ✅ Na liście przedmiotów - dedykowana ikona do każdej kategorii
- ✅ Ikony dla kategorii: woda, ogień, jedzenie, schronienie, pierwsza pomoc, narzędzia, nawigacja, komunikacja, odzież, higiena, światło, inne
- ✅ Spójny system ikon (Lucide Icons)
- ✅ Ikony wyświetlane w tabelach i selektorach kategorii

### ✅ Kolorowanie kontenerów
**Status:** ✅ Completed | **Priority:** Medium | **Feature:** [FEATURE-003](./features/FEATURE-003-container-colors.md)

- ✅ Możliwość przypisania koloru do kontenera
- ✅ Zestaw kolorów inspirowany realnymi kolorami sprzętu outdoor/taktycznego:
  - `default` (neutralny szary)
  - `coyote`, `khaki`, `olive`, `forestGreen`, `tan`, `brown`
  - `black`, `navy`, `jeans`, `gray`, `orange`
- ✅ Wizualne rozróżnienie kontenerów na liście (kolorowa kropka, kolor tekstu i ramki)
- ✅ Kropka (`COLOR_DOT_CLASSES`) używa custom HEX, które możliwie wiernie odwzorowują kolory materiałów (np. cordura, plecaki, odzież)
- ✅ Tekst i ramki (`COLOR_TEXT_CLASSES`, `COLOR_BORDER_CLASSES`) używają klas Tailwind dobranych tak, aby były jak najbliżej kropki, ale nadal dobrze czytelne w light/dark theme
- ✅ Kolor wyświetlany w kartach kontenerów i rozwiniętych wierszach zagnieżdżonych kontenerów

### ✅ Ulepszenie wyboru koloru kontenera (wyszukiwarka i etykiety)
**Status:** ✅ Completed | **Priority:** Low | **Complexity:** Small

**Koncepcja:**
W komponencie `ContainerColorPicker.vue` dodać funkcjonalności ułatwiające wybór koloru, szczególnie gdy jest wiele dostępnych kolorów (obecnie 12 kolorów).

**Proponowane ulepszenia:**
1. **Wyszukiwarka po nazwie koloru** - pole wyszukiwania pozwalające szybko znaleźć kolor po nazwie (np. "olive", "khaki", "coyote")
   - Filtrowanie kolorów w czasie rzeczywistym podczas wpisywania
   - Wyszukiwanie po tłumaczonej nazwie koloru (PL/EN)
   - Ukrywanie niepasujących kolorów
2. **Etykiety pod kolorami** - wyświetlanie nazw kolorów bezpośrednio pod kropkami (opcjonalnie, zamiast tylko tooltip)
   - Opcja w ustawieniach: "Pokaż nazwy kolorów" (checkbox)
   - Domyślnie: tylko tooltip (obecne zachowanie)
   - Po włączeniu: małe etykiety tekstowe pod każdą kropką

**Implementacja:**
- W `ContainerColorPicker.vue`:
  - Dodanie pola wyszukiwania nad siatką kolorów
  - Filtrowanie `CONTAINER_COLORS` na podstawie wyszukiwanej frazy
  - Opcjonalne wyświetlanie etykiet pod kropkami (zależnie od ustawienia)
- W ustawieniach (opcjonalnie):
  - Checkbox "Pokaż nazwy kolorów w selektorze" (zapis w localStorage)

**Zalety:**
- Szybsze znajdowanie konkretnego koloru (szczególnie przy większej liczbie kolorów)
- Lepsza dostępność (nazwy widoczne bez hover)
- Lepsze UX dla użytkowników, którzy nie pamiętają, jak wygląda dany kolor

### ✅ DataTable - Pinned Columns (Pin-right dla kolumny akcji)
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Small

**Koncepcja:**
Dodanie wsparcia dla pinned columns w komponencie `DataTable`, szczególnie pin-right dla kolumny akcji, aby była zawsze widoczna podczas poziomego przewijania tabeli.

**Problema:**
- Kolumna akcji (dropdown menu) może być niewidoczna podczas scrollowania poziomego
- Utrudnia to dostęp do akcji bez konieczności przewijania w prawo
- Szczególnie istotne w tabelach z wieloma kolumnami (np. CatalogueManagePage)

**Implementacja:**
1. ✅ **Rozszerzenie DataTable.vue:**
   - ✅ Dodanie wsparcia dla `meta.pinned: 'left' | 'right'` w definicji kolumny (TanStack Table v8)
   - ✅ Stylowanie pinned columns z `position: sticky` i odpowiednim `right`/`left`
   - ✅ Ustawienie odpowiedniego `z-index` i `background-color` dla sticky columns
   - ✅ Obsługa kolejności kolumn (pinned columns na początku/końcu)
   - ✅ Synchronizacja cienia pinned columns z horizontal scroll state (cień pojawia się tylko gdy jest scroll)
   - ✅ Transition dla płynnego pojawiania się/znikania cienia (200ms)
   - ✅ Composable `useHorizontalScroll` do śledzenia stanu scrolla (reusable)

2. ✅ **Użycie w CatalogueManagePage:**
   - Dodanie `meta: { pinned: 'right' }` do kolumny akcji
   - Kolumna akcji będzie zawsze widoczna po prawej stronie podczas scrollowania

3. **Użycie w innych miejscach:**
   - `AdminItemsPage.vue` - kolumna akcji
   - `AdminContainersPage.vue` - kolumna akcji
   - `AllItemsPage.vue` - jeśli ma kolumnę akcji
   - Inne strony używające DataTable z kolumną akcji

**Zalety:**
- ✅ Lepsze UX - akcje zawsze dostępne bez przewijania
- ✅ Spójność z nowoczesnymi tabelami (np. Google Sheets, Notion)
- ✅ Możliwość użycia również dla pin-left (np. dla kolumny z nazwą)
- ✅ Inteligentny cień - pojawia się tylko gdy jest scroll, z płynnym transition

### 🔄 Obrazek kontenera jako okrągły avatar w liście kontenerów
**Status:** 🔄 Planned | **Priority:** Medium | **Complexity:** Small

**Koncepcja:**
Jeżeli kontener będzie miał obrazek (primary image), wyświetlać go w nagłówku karty kontenera jako okrągły avatar zamiast ikonki `Package` i kropki koloru. Kolor kontenera powinien być wyświetlany jako border tego avatara.

**Implementacja:**
- W `ContainerCard.vue` (i `PublicContainerCard.vue`):
  - Jeśli kontener ma `primaryImageUrl` → wyświetl okrągły avatar z obrazkiem
  - Jeśli kontener nie ma obrazka → wyświetl obecną ikonkę `Package` i kropkę koloru
  - Avatar powinien mieć border w kolorze kontenera (jeśli kolor jest ustawiony)
  - Avatar powinien być okrągły (rounded-full)
  - Rozmiar avatara: podobny do obecnej ikonki (np. size-8 lub size-10)
- Fallback: Jeśli obrazek nie załaduje się, pokaż ikonkę `Package` z kropką koloru
- Wsparcie dla kontenerów bez obrazka: zachować obecne zachowanie (ikona + kropka)

**Zalety:**
- Lepsza wizualna identyfikacja kontenerów
- Wykorzystanie obrazków kontenerów (gdy będą zaimplementowane)
- Zachowanie informacji o kolorze (jako border avatara)
- Spójność z innymi miejscami, gdzie mogą być wyświetlane avatary

### Wybór primary color (brand color)
**Status:** ⏸️ On Hold | **Priority:** Low | **Complexity:** Small

- Obecny kolor "dark orange" jest zadowalający, zadanie wstrzymane
- **Uwaga:** Warianty kolorów są już przygotowane w `src/css/style.css` jako zakomentowany kod (na wypadek potrzeby zmiany w przyszłości)

### ✅ Zintegrowany input wagi z wyborem jednostki
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Small

- ✅ Komponent `<WeightInputWithUnitPicker>` łączący input wagi z wyborem jednostki w jednym elemencie UI
- ✅ Komponent łączy:
  - ✅ Input numeryczny dla wagi
  - ✅ Select/dropdown dla jednostki wagi (g, kg, oz, lb)
- ✅ Użycie w formularzach:
  - ✅ `ItemFormFields.vue` - pole wagi przedmiotu
  - ✅ `ContainerFormFields.vue` - pola wagi kontenera (weight, maxWeight)
- ✅ Korzyści:
  - ✅ Lepszy UX - wszystko w jednym miejscu
  - ✅ Spójny wygląd we wszystkich formularzach
  - ✅ Łatwiejsze zarządzanie stanem (jedna kompozycja zamiast dwóch osobnych pól)
- ✅ Obsługa wszystkich jednostek: g, kg, oz, lb

### Przycisk "Importuj z Markdown" w empty state Container List
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Small

- Na stronie Container List (`ContainersListPage.vue`), gdy nie ma żadnych kontenerów (empty state), powinien być dostępny przycisk "Importuj z Markdown"
- Obecnie w empty state są tylko przyciski:
  - "Utwórz kontener"
  - "Wygeneruj przykładowy zestaw"
- Dodanie przycisku "Importuj z Markdown" w empty state ułatwi użytkownikom szybkie rozpoczęcie pracy z aplikacją poprzez import istniejących danych
- Przycisk powinien otwierać dialog importu markdown (już istniejący `ImportMarkdownDialog`)

### ✅ Sidebar menu kompatybilny z LighterPack
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Medium

- Dodanie sidebar menu (bocznego menu) kompatybilnego z LighterPack
- Sidebar powinien wyświetlać:
  - Listę wszystkich kontenerów (z możliwością szybkiego przejścia)
  - Główne linki nawigacyjne (Kontenery, Wszystkie przedmioty, Planowanie zakupów, itp.)
- Sidebar powinien być dostępny na wszystkich stronach (lub na wybranych stronach)
- Możliwość zwijania/rozwijania sidebar (toggle)
- Wizualne oznaczenie aktywnego kontenera/strony
- Responsywność - na mobile może być ukryty lub przekształcony w drawer

### ✅ Szybka edycja nazwy kontenera na stronie Container Details
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Small

- ✅ Możliwość szybkiej edycji nazwy kontenera bezpośrednio na stronie Container Details
- ✅ Inline editing nazwy kontenera (podobnie jak inline editing przedmiotów)
- ✅ Kliknięcie w nazwę kontenera → przejście w tryb edycji
- ✅ Zapisywanie zmian po zatwierdzeniu (Enter) lub anulowanie (Escape)
- ✅ Wizualne oznaczenie trybu edycji (input field, ikona edycji)
- ✅ Implementacja w komponencie `ContainerHeaderName.vue`

### 🔄 Zwijanie sekcji statystyk i konfigurowalna kolejność sekcji na Container Details
**Status:** 🔄 Planned | **Priority:** Low | **Complexity:** Medium

- Możliwość zwijania/rozwijania sekcji statystyk na stronie Container Details
- Użytkownik może ukryć sekcje, które nie są mu potrzebne (np. wykresy, statystyki wagi)
- Konfigurowalna kolejność sekcji - możliwość zmiany kolejności wyświetlania sekcji (drag & drop lub ustawienia)
- Preferencje użytkownika zapisywane w localStorage
- Sekcje do rozważenia:
  - Statystyki kontenera (waga, ilość przedmiotów, itp.)
  - Wykresy (kategorie, cena, priorytet)
  - Lista przedmiotów
  - Opis kontenera
- Możliwość resetowania do domyślnej kolejności

### ✅ Obsługa usuwania i gwiazdkowania obrazków przedmiotu na urządzeniach mobilnych
**Status:** ✅ Completed | **Priority:** High | **Complexity:** Small

**Problem:**
Kontrolki obrazków (gwiazdkowanie, usuwanie) w `ItemImageCardControls.vue` są widoczne tylko przy hover (`group-hover:opacity-100`). Na urządzeniach mobilnych (telefony, tablety) nie ma hover, więc kontrolki są zawsze niewidoczne (`opacity-0`) i użytkownik nie może:
- Ustawić obrazka jako primary (gwiazdkowanie)
- Usunąć obrazka

**Rozwiązania do rozważenia:**
1. **Zawsze widoczne na mobile** (najprostsze)
   - Użyć media query: `md:opacity-0 md:group-hover:opacity-100`
   - Na mobile (`< md`) kontrolki zawsze widoczne
   - Na desktop zachować obecne zachowanie (hover)

2. **Long press / context menu**
   - Long press na obrazku → pokaż menu z opcjami (Set Primary, Delete)
   - Podobnie jak context menu na desktop

3. **Osobny przycisk "More" na mobile**
   - Mały przycisk w rogu obrazka (np. trzy kropki)
   - Kliknięcie → pokaż menu z opcjami
   - Widoczny tylko na mobile

4. **Touch event zamiast hover**
   - Wykrywanie touch device (`@touchstart`)
   - Po dotknięciu obrazka → pokaż kontrolki na kilka sekund
   - Automatyczne ukrycie po czasie

**Rekomendacja:**
Kombinacja opcji 1 i 2:
- Na mobile kontrolki zawsze widoczne (opcja 1)
- Dodatkowo long press → context menu z opcjami (opcja 2)
- Na desktop zachować obecne zachowanie (hover)

**Implementacja:**
- `ItemImageCardControls.vue`: Zmienić klasy CSS na responsive
  - `opacity-0 md:opacity-0 md:group-hover:opacity-100` (zawsze widoczne na mobile)
- `ItemImageCard.vue`: Dodać obsługę long press na mobile
  - `@touchstart` / `@touchend` → pokaż menu
- Opcjonalnie: Dodać wizualny wskaźnik, że obrazek ma kontrolki (np. mała ikona w rogu)

**Zalety:**
- Pełna funkcjonalność na urządzeniach mobilnych
- Zachowanie obecnego UX na desktop
- Lepsza dostępność (touch-friendly)

---

## ♿ Accessibility (Dostępność)

### ✅ Podstawowe oznaczenia ARIA i dostępność
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Medium

**Postęp (2025-01-22):**
- ✅ Dodano tooltips i aria-label do głównych przycisków z ikonami (ItemsTableRowActions, ContainerCardActions, ContainerHeader, ContainersListPageDropdown, AiChatInputSection)
- ✅ Dodano tooltips i aria-label do dodatkowych komponentów (SidebarTrigger, DarkModeToggle, LocaleToggle, ShoppingListItem, RatingStars, ItemsTableEditableNameCell, ItemsTableMoveButtons)
- ✅ Semantyka HTML i landmarky ARIA - sprawdzone i poprawne (header, nav, main, footer)
- ✅ Dodano aria-expanded i aria-label do przycisku expand/collapse w ItemsTableNameCell
- ✅ Wszystkie potrzebne translacje dodane (PL i EN)
- ⏳ Pozostały tylko testy manualne (focus management, czytnik ekranu, Lighthouse, axe DevTools)

**Zakres implementacji:**

1. **Podstawowe oznaczenia ARIA**
   - Dodanie odpowiednich atrybutów ARIA do komponentów (aria-label, aria-describedby, aria-expanded, aria-hidden, itp.)
   - Zapewnienie poprawnej semantyki HTML (użycie odpowiednich tagów: button, nav, main, itp.)
   - Poprawne oznaczenie regionów strony (landmarks)
   - Obsługa nawigacji klawiaturą (focus management, keyboard shortcuts)

2. **Tooltips na przyciskach z ikonami**
   - Użycie `v-tooltip="t(...)"` na wszystkich przyciskach zawierających tylko ikonę (bez tekstu)
   - Tooltip powinien zawierać przetłumaczoną nazwę akcji (krótki opis funkcji przycisku)
   - Tooltip powinien być dostępny zarówno przy hover jak i focus (dla użytkowników klawiatury)

3. **aria-label i tooltip z tą samą treścią**
   - Dla przycisków z ikonami: `aria-label` i tooltip mogą mieć tę samą treść
   - Zapewnia to spójność między doświadczeniem użytkowników korzystających z czytników ekranu a użytkowników korzystających z tooltipów
   - Przykład: `<Button v-tooltip="t('actions.edit')" :aria-label="t('actions.edit')">`

**Korzyści:**
- ✅ Lepsza dostępność dla użytkowników z niepełnosprawnościami
- ✅ Zgodność z wytycznymi WCAG
- ✅ Lepsze doświadczenie użytkownika dla wszystkich (tooltips pomagają zrozumieć funkcje przycisków)
- ✅ Poprawa SEO (semantyczny HTML)

**Priorytetowe obszary:**
- Przyciski akcji w tabelach (edycja, usuwanie, itp.)
- Przyciski nawigacyjne w topbar
- Przyciski w formularzach
- Dialogi i modale
- Menu i dropdowny

---

## 🔗 Relacje i Nesting

### ✅ Relacja parent-children (nesting kontenerów)
**Status:** ✅ Completed | **Priority:** High | **Feature:** [FEATURE-008](./features/FEATURE-008-container-nesting.md)

- ✅ Kontener może zawierać na liście przedmiotów inny kontener
  - Przykład: W plecaku może być Pouch, a w Pouch może być Latarka
- ✅ Kontener, który ma rodzica lub jest używany jako item, można ukryć z głównej listy kontenerów
- ✅ Opcja wyświetlania tylko kontenerów głównych (bez zagnieżdżonych)
- ✅ Wizualne oznaczenie kontenerów zagnieżdżonych (ikona, badge, klikalna nazwa)
- ✅ Rekurencyjne obliczanie wagi (waga kontenera + waga jego zawartości)
- ✅ Rozwijane wiersze w tabeli przedmiotów - możliwość zobaczenia zawartości zagnieżdżonego kontenera
- ✅ Walidacja cyklicznych referencji - zapobieganie nieskończonym pętlom
- ✅ Osobne akcje "Dodaj Przedmiot" i "Dodaj Kontener" w interfejsie

> **Uwaga:** Ta funkcjonalność jest już zaimplementowana i działa z localStorage. W przyszłości może być rozszerzona o synchronizację z backendem (zobacz [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md)).

### Oznaczanie kontenerów jako fragmentów rodzica (integral part)
**Status:** 🔄 Planned | **Priority:** Medium | **Complexity:** Medium

- Kontener może być oznaczony jako "fragment rodzica" (integral part of parent)
- Przykład: Bagażnik samochodu jest częścią samochodu i nie powinien być liczony osobno
- Przykład: Pokrywa plecaka jest częścią plecaka
- Oznaczenie kontenera jako fragmentu:
  - Kontener nie jest liczony jako osobny kontener w statystykach
  - Waga kontenera-fragmentu jest zawsze wliczana do rodzica
  - Fragment nie może być przeniesiony do innego kontenera bez rodzica
  - Wizualne oznaczenie w interfejsie (ikona, badge, tooltip)
- Użycie przypadków:
  - Części samochodu (bagażnik, schowek, konsola)
  - Części plecaka (kieszenie, pokrywy, pasy)
  - Części namiotu (stelaż, podłoga)
  - Inne kontenery, które są nierozerwalnie związane z rodzicem
- Opcja w formularzu kontenera: checkbox "Fragment rodzica" (dostępne tylko gdy kontener ma rodzica)
- Wpływ na obliczenia:
  - Waga fragmentu zawsze wliczana do rodzica
  - Fragment nie jest liczony jako osobny kontener w statystykach
  - Fragment nie może być wyświetlony jako główny kontener (jeśli opcja "Pokaż tylko główne" jest włączona)

---

## 📝 Rozszerzone pola

### ✅ Dodatkowe pola dla przedmiotów i kontenerów
**Status:** ✅ Completed | **Priority:** Medium | **Feature:** FEATURE-006 | **Complexity:** Medium

**Dla przedmiotów:**
- ✅ **Cena** - cena zakupu przedmiotu
- ✅ **Link URL** - link do produktu, recenzji, itp.
- ✅ **Półka cenowa / jakość** - niska półka, średnia półka, wyższa półka
- ✅ **Firma** - producent/marka przedmiotu (z ComboBox i sugerowanymi wartościami)
- ✅ **Kolor** - kolor przedmiotu (z ComboBox i sugerowanymi wartościami)
- ✅ **Wearable** - opcja oznaczania przedmiotu jako noszonego na sobie (np. odzież, zegarek, buty)
- ✅ **Consumable** - opcja oznaczania przedmiotu jako zużywalnego (np. jedzenie, lekarstwa, paliwo)

**Dla kontenerów:**
- ✅ **Firma** - producent/marka kontenera
- ✅ **Cena** - cena zakupu kontenera

**Ujednolicenie modelu:**
- ✅ Wspólne pola (firma, cena) zaimplementowane w modelu danych
- ✅ Wizualizacja kolorów w tabelach (kolorowa kropka)
- ✅ Zarządzanie widocznością kolumn (marka, kolor) w tabelach

> **Uwaga:** Ta funkcjonalność jest już zaimplementowana i działa z localStorage. W przyszłości może być rozszerzona o synchronizację z backendem (zobacz [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md)).

### ✅ Dodawanie własnych marek (brand)
**Status:** ✅ Completed | **Priority:** High | **Complexity:** Medium

- ✅ UI w ustawieniach do zarządzania markami (`BrandsSettingsCard.vue`) - dodawanie, edycja, usuwanie
- ✅ Marki mają strukturę `id`, `value`, `createdAt`, `updatedAt`
- ✅ Lista marek łączona: domyślne (SUGGESTED_BRANDS) + własne użytkownika
- ✅ Własne marki dostępne w:
  - ✅ Autocomplete przy wyborze marki w formularzach przedmiotów i kontenerów
  - ✅ Rozpoznawaniu parametrów przedmiotów (fuzzy matching)
- ✅ Marki zapisywane w localStorage
- ✅ Integracja z istniejącym polem `brand` w modelu danych
- ✅ Funkcja `getBrandOptions()` łącząca domyślne i własne marki

> **Uwaga:** Ta funkcjonalność działa z localStorage (front-end only). W przyszłości może być rozszerzona o synchronizację z backendem (zobacz [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md)).

### ✅ Obsługa waluty (currency)
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Medium | **Feature:** [FEATURE-017](./features/FEATURE-017-currency-support.md)

- ✅ Pole `currency` dodane do przedmiotów i kontenerów (w typach `IGearItem`, `IGearContainer`)
- ✅ Parsowanie waluty w markdown import (rozpoznawanie PLN, USD, EUR, GBP z różnych formatów)
- ✅ Obsługiwane waluty: PLN, EUR, USD, GBP
- ✅ Domyślna waluta użytkownika w ustawieniach (localStorage)
- ✅ Automatyczne rozpoznawanie domyślnej waluty na podstawie języka
- ✅ Wyświetlanie waluty:
  - ✅ W formularzach: pole wyboru waluty obok pola ceny
  - ✅ W tabelach: cena z walutą (np. "100,00 PLN")
  - ✅ W statystykach kontenera: suma cen z odpowiednimi walutami
- ✅ Formatowanie cen używając `Intl.NumberFormat`
- ✅ Logika wyboru waluty w UI

> **Uwaga:** Ta funkcjonalność działa z localStorage (front-end only). W przyszłości może być rozszerzona o synchronizację z backendem (zobacz [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md)).

### Obsługa Markdown w notatkach
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Medium

- ✅ Możliwość formatowania notatek (pole `notes`) za pomocą Markdown
- ✅ W formularzach: edytor Markdown z przełącznikiem Edit/Preview (komponent `TextareaWithMarkdownPreview`)
- ✅ W wyświetlaniu: renderowanie Markdown do HTML (linki, **pogrubienie**, *kursywa*, listy, itp.)
- ✅ Podstawowe wsparcie dla:
  - **Bold** i *italic*
  - Linki `[text](url)` i automatyczna konwersja URL-i
  - Listy (ul/ol) z odpowiednimi markerami i wcięciami
  - `code` i bloki kodu
  - Nagłówki, cytaty i inne elementy Markdown
- ✅ Obsługa dla przedmiotów (`IGearItem.notes`) i kontenerów (`IGearContainer.description`)
- ✅ Komponent `MarkdownRenderer` do wyświetlania Markdown w różnych miejscach aplikacji
- ✅ Tłumaczenia Markdown przeniesione do `shared/common` (dostępne w całej aplikacji)

---

## 🚀 Import/Export i Markdown

### ✅ Eksport i import markdown (AI-friendly format)
**Status:** ✅ Completed | **Priority:** High | **Feature:** FEATURE-009, FEATURE-011 | **Complexity:** Large

**Eksport do markdown:**
- ✅ Przycisk "Eksport do prompt (AI)" w dropdown menu kontenera
- ✅ Przycisk "Eksport do prompt (AI) - Wszystkie" dla wszystkich kontenerów na liście
- ✅ Eksport tworzy markdown z kontenerem i jego zawartością w ujednoliconym formacie
- ✅ Dialog z markdownem i przyciskiem do kopiowania
- ✅ Przycisk "Guidelines" w dialogu - kopiuje szablon formatowania dla AI
- ✅ Legenda/opis dla AI wyjaśniająca strukturę danych

**Format markdown (ujednolicony dla import/export):**
```markdown
## [Container Name] [#container-id] ([Container Type])
- **[Item Name]** x[qty] ([Brand], [Color]) [#nested-id] ([Status]) <URL> - [weight]g
```

**Cechy formatu:**
- ✅ **Nazwa przedmiotu** (bold `**text**`) - wymagane
- ✅ **Ilość** (format: `x2`, `x10`) - opcjonalne, może być wszędzie w linii
- ✅ **Marka i kolor** w pierwszych nawiasach: `(Marka, Kolor)` - opcjonalne
- ✅ **Status i expiration** w drugich nawiasach: `(Status, Expiration: DD.MM.YYYY)` - opcjonalne
- ✅ **Container ID** w formacie `[#slug-id]` - dla identyfikacji kontenerów
  - ID generowane jako slug z nazwy: "Bug-Out Bag" → `#bug-out-bag`
  - Użyte w nagłówku kontenera i referencjach do zagnieżdżonych kontenerów
- ✅ **URL** w nawiasach kątowych lub plain: `<https://example.com>` lub `https://...` lub `www...` - opcjonalne
  - Automatyczne dodawanie `https://` do linków zaczynających się od `www.`
- ✅ **Waga** na końcu: `- 500g` lub `- 2.5kg` - opcjonalne (domyślnie 100g)
- ✅ **Zagnieżdżone kontenery**:
  - Item z `[#id]` w linii przedmiotu
  - Osobna definicja kontenera z tym samym `[#id]` w nagłówku
  - Parser automatycznie tworzy relację

**Eksport do CSV:**
- ✅ Eksport kontenera do formatu CSV | **Feature:** [FEATURE-021](./features/FEATURE-021-csv-export.md) | **Version:** 2.13.0
- Kolumny: nazwa, kategoria, ilość, waga, cena, waluta, marka, kolor, status, priorytet, URL, notatki
- Opcja wyboru kolumn do eksportu
- Obsługa różnych separatorów (przecinek, średnik)
- Encoding: UTF-8 z BOM (dla Excel)
- Eksport z cenami (jeśli dostępne)

**Import z markdown:**
- ✅ Przycisk "Import z markdown" w dropdown menu na liście kontenerów
- ✅ Dialog z textarea do wklejenia markdown i przyciskiem "Preview"
- ✅ Elastyczny parser:
  - ✅ Rozpoznaje pola w dowolnej kolejności (nazwa, ilość, waga, marka, kolor, status, expiration, URL, container ID)
  - ✅ Inteligentne dopasowywanie marek (fuzzy matching z SUGGESTED_BRANDS)
  - ✅ Inteligentne dopasowywanie kolorów (z SUGGESTED_COLORS)
  - ✅ Automatyczne rozpoznawanie kategorii po słowach kluczowych
  - ✅ Domyślne wartości dla brakujących pól (waga: 100g, ilość: 1, status: owned)
  - ✅ Wyciąganie `[#id]` z nagłówków kontenerów
  - ✅ Wyciąganie `[#id]` z linii przedmiotów (dla relacji zagnieżdżonych kontenerów)
  - ✅ Obsługa różnych formatów dat expiration
  - ✅ Obsługa URL w nawiasach kątowych lub plain
- ✅ Obsługa błędów - wyświetlanie błędów parsowania z numerami linii
- ✅ Preview przed importem - podgląd kontenerów i przedmiotów przed zapisaniem

**Szablon Guidelines:**
- ✅ Kompletny szablon formatowania w markdown
- ✅ Szczegółowe zasady dla każdego pola
- ✅ Przykłady dla wszystkich możliwych formatów
- ✅ Instrukcje dla AI jak rozpoznawać i formatować dane
- ✅ Dokumentacja zagnieżdżonych kontenerów
- ✅ Przycisk kopiowania szablonu do schowka

**Opcje konfiguracji eksportu:**
- ✅ Pokazywanie UUID w eksporcie (opcjonalnie)
- ✅ Pokazywanie wagi w eksporcie (opcjonalnie)
- ✅ Pokazywanie koloru w eksporcie (opcjonalnie)
- ✅ Pokazywanie marki w eksporcie (opcjonalnie)
- ✅ Pokazywanie powiązania z kontenerem (opcjonalnie)
- ✅ Pokazywanie legendy (opcjonalnie)
- ✅ Format opisu przedmiotów (off/inline/newline) - zaimplementowane
- ✅ Pokazywanie cen przedmiotów w eksporcie (opcjonalnie) - zaimplementowane | **Feature:** [FEATURE-020](./features/FEATURE-020-price-display-in-export.md)
- ✅ Dodatkowe podsumowanie "Do kupienia" na końcu eksportu - zaimplementowane | **Feature:** [FEATURE-020](./features/FEATURE-020-price-display-in-export.md)
- 🔄 Inne opcje konfiguracji formatu (poziom szczegółowości, metadane, itp.) - planowane
- ✅ **Obsługa opisów przedmiotów w markdown** - zaimplementowane | **Feature:** [FEATURE-013](./features/FEATURE-013-item-descriptions.md)
  - ✅ Opcje formatu opisu w eksporcie: **OFF** (domyślnie), **Inline**, **New Line** - zaimplementowane
  - ✅ Dwie opcje formatu eksportu:
    - ✅ **Opcja A (Inline):** `- Nóż *(mały, składany)* - 100g` - opis w nawiasie kursywą zaraz po nazwie
    - ✅ **Opcja B (New Line):** opis w osobnej linii z wcięciem 2 spacje, od razu pod nazwą (przed wagą/marką)
  - ✅ Parsowanie opisów w imporcie markdown (automatyczne rozpoznawanie obu formatów) - zaimplementowane
  - ✅ Obsługa zagnieżdżonych nawiasów w opisach - zaimplementowane
- ✅ **Obsługa opisu kontenera w markdown import** - ZAIMPLEMENTOWANE
  - ✅ Parser markdown wykrywa opis kontenera (tekst między nagłówkiem a pierwszą listą przedmiotów)
  - ✅ Opis zapisywany w polu `description` kontenera
  - ✅ Unit tests dla parsowania opisów kontenerów
- ✅ **Obsługa ceny w markdown import** - ZAIMPLEMENTOWANE
  - ✅ Parser wykrywa ceny przedmiotów i kontenerów w różnych formatach
  - ✅ Obsługiwane formaty: `100PLN`, `10 PLN`, `10,00 PLN`, `1 000,00 PLN`, `10zł`, `$50`, `50$`
  - ✅ Automatyczne rozpoznawanie waluty (PLN, zł, $, EUR, €, GBP, £)
  - ✅ Cena zapisywana w polu `price` przedmiotu/kontenera
  - ✅ Waluta zapisywana w polu `currency`
  - ✅ Unit tests dla parsowania cen (kontenery i przedmioty)

> **Uwaga:** UUID support dla update workflow wymaga backendu/DB - zobacz [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md)

### 🔄 Obsługa różnych formatów importu
**Status:** 🔄 Planned | **Priority:** Medium | **Complexity:** Medium

**Problem:**
- Obecnie import obsługuje tylko format JSON (w `ContainerHeader.vue` linia 186-189)
- Brak obsługi importu z innych formatów (CSV, Markdown) przez ten sam interfejs

**Rozwiązania do rozważenia:**
1. **Dialog wyboru formatu** - po kliknięciu "Import" otwiera się dialog z wyborem formatu (JSON, CSV, Markdown)
2. **Osobne akcje menu** - oddzielne pozycje menu dla każdego formatu (Import JSON, Import CSV, Import Markdown)
3. **Auto-detekcja formatu** - automatyczne rozpoznawanie formatu na podstawie zawartości pliku/tekstu

**Wymagania:**
- Obsługa importu JSON (już istnieje, ale wymaga ulepszenia)
- Obsługa importu CSV (nowa funkcjonalność)
- Obsługa importu Markdown (już istnieje jako osobna akcja, ale można zintegrować)
- Spójny UX dla wszystkich formatów importu
- Walidacja i obsługa błędów dla każdego formatu

**Lokalizacja:** `src/modules/gear/components/ContainerHeader.vue:186-189`

### 🔄 Import CSV (inspiracja LighterPack)
**Status:** 🔄 Planned | **Priority:** Medium | **Complexity:** Medium | **Source:** [LIGHTERPACK_IMPROVEMENTS_TASKS.md](../comparison/LIGHTERPACK_IMPROVEMENTS_TASKS.md)

**Obecny stan:**
- ✅ CSV Export już istnieje (`ExportToCSVDialog.vue`, `exportToCSV.ts`)
- ❌ CSV Import - brak implementacji

**Wymagania:**
- Dialog importu CSV z upload pliku
- Parser CSV z obsługą różnych separatorów (przecinek, średnik)
- Mapowanie kolumn (nazwa, waga, kategoria, itp.)
- Walidacja danych przed importem
- Preview przed importem
- Obsługa błędów (nieprawidłowe dane, brakujące kolumny)

**Szczegóły implementacji:**
- Dialog importu CSV z upload pliku
- Auto-detekcja separatora (przecinek vs średnik)
- Mapowanie kolumn z interfejsu użytkownika (drag & drop lub select)
- Walidacja danych przed importem (sprawdzanie typów, wymaganych pól)
- Preview przed importem (podgląd pierwszych wierszy)
- Obsługa błędów z informacją o problematycznych wierszach
- Import do istniejącego kontenera lub tworzenie nowego

---

## ⚡ Usprawnienia dodawania przedmiotów

### ✅ Domyślne wartości dla nowych przedmiotów
**Status:** ✅ Completed | **Priority:** High | **Feature:** [FEATURE-004](./features/FEATURE-004-default-values.md)

- ✅ Nowy przedmiot ma większość pól z domyślnymi wartościami
- ✅ Domyślne wartości:
  - ✅ Waga: 0.1 kg
  - ✅ Ilość: 1
  - ✅ Status: "owned"
  - ✅ Priorytet: "medium"
  - ✅ Kategoria: "other" (lub wykryta automatycznie)
  - ✅ Jednostka wagi: kg

### ✅ Rozpoznawanie kategorii po nazwie
**Status:** ✅ Completed | **Priority:** Medium | **Feature:** [FEATURE-005](./features/FEATURE-005-category-recognition.md)

- ✅ Na podstawie słów kluczowych w nazwie dobieramy kategorię
- ✅ Przykłady:
  - ✅ `nóż`, `knife` → kategoria: narzędzia
  - ✅ `woda`, `water` → kategoria: woda
  - ✅ `zapałki`, `matches` → kategoria: ogień
  - ✅ `apteczka`, `first aid` → kategoria: pierwsza pomoc
- ✅ Podobnie dla kontenerów (rozpoznawanie typu kontenera)
- ✅ Słownik słów kluczowych dla każdej kategorii i typu kontenera
- ✅ Rozpoznawanie uruchamiane na zdarzeniu blur (po opuszczeniu pola nazwy)
- ✅ Priorytetyzacja dłuższych słów kluczowych (np. "bagażnik" zamiast "bag")

> **Uwaga:** Uczenie się na podstawie wcześniejszych wyborów użytkownika wymaga backendu/DB - zobacz [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md)

---

## 🔄 Zarządzanie kontenerami i przedmiotami

### ✅ Kopiowanie/klonowanie kontenerów
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Small | **Version:** v0.21.0

- Możliwość sklonowania całego kontenera wraz z jego zawartością
- Akcja "Duplikuj kontener" w menu akcji kontenera (dropdown na liście kontenerów)
- Klonowanie tworzy nowy kontener z:
  - Nazwą: "[Kopia] Nazwa oryginału" (edytowalna)
  - Wszystkimi przedmiotami z oryginału (głębokie kopiowanie)
  - Zagnieżdżonymi kontenerami (opcjonalnie - checkbox "Klonuj z zagnieżdżonymi kontenerami")
  - Wszystkimi metadanymi (typ, kolor, brand, opis, itp.)
- Dialog potwierdzający klonowanie z opcjami:
  - Nowa nazwa kontenera (domyślnie: "[Kopia] Original Name")
  - Checkbox: "Uwzględnij zagnieżdżone kontenery"
  - Checkbox: "Uwzględnij ceny" (dla przedmiotów)
- Klonowanie zapisuje w localStorage
- Toast potwierdzający sukces z linkiem do nowego kontenera

**Use cases:**
- Tworzenie wariantu plecaka (np. "Plecak letni" → "Plecak zimowy")
- Backup przed modyfikacją
- Tworzenie podobnych zestawów (EDC #1, EDC #2)

### ✅ Dodawanie istniejących przedmiotów do kontenera
**Status:** ✅ Completed | **Priority:** High | **Complexity:** Medium | **Feature:** [FEATURE-012](./features/FEATURE-012-add-existing-items.md) | **Completed in:** v0.22.0

- Możliwość dodania istniejącego przedmiotu z innego kontenera bez ręcznego przepisywania
- W ItemFormPage dodanie opcji wyboru:
  - **Nowy przedmiot** (obecny formularz) - domyślnie
  - **Istniejący przedmiot** (autocomplete) - nowy tryb
- Przycisk/toggle do przełączania między trybami lub dwa osobne buttony na stronie kontenera:
  - "Dodaj przedmiot" (obecny)
  - "Dodaj z katalogu" (nowy)
- **Tryb "Dodaj istniejący":**
  - Autocomplete/ComboBox z listą wszystkich przedmiotów ze wszystkich kontenerów
  - Wyświetlanie: nazwa + kontener źródłowy + ikona kategorii
  - Filtrowanie po nazwie (fuzzy search)
  - Po wybraniu przedmiotu:
    - Domyślnie: **kopia przedmiotu** (wszystkie pola + nowe UUID)
    - Opcjonalnie: edycja przed dodaniem (ilość, waga, status)
- Lista przedmiotów sortowana alfabetycznie
- Grupowanie według kontenera źródłowego (opcjonalnie)
- Podgląd szczegółów przedmiotu w dropdown (waga, marka, kolor)

**Globalny katalog przedmiotów (localStorage):**
- Funkcja w gearService: `getAllItems(): IGearItem[]` - zwraca wszystkie przedmioty ze wszystkich kontenerów
- Funkcja: `getItemsForAutocomplete()` - zwraca przedmioty w formacie dla ComboBox
- Cache w composable dla wydajności

**Use cases:**
- Dodawanie tego samego przedmiotu do wielu kontenerów (np. "Latarka" w różnych zestawach)
- Szybkie budowanie nowego kontenera na bazie istniejących przedmiotów
- Unikanie przepisywania tych samych danych

> **Uwaga:** Linkowanie przedmiotów (zmiana w jednym → zmiana w wielu) wymaga backendu/DB - zobacz [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md)

---

## ✏️ Szybka edycja

### ✅ Edycja bezpośrednio na liście (Inline Editing)
**Status:** ✅ Completed | **Priority:** High | **Feature:** FEATURE-007 | **Complexity:** Large

- ✅ **Fully Completed**: Inline editing dla wszystkich podstawowych pól
  - Edit mode toggle z persystencją w localStorage
  - Edytowalne pola w wierszu tabeli
  - Zapis z Enter lub blur, anulowanie z Escape lub X
  - Wizualne feedback i stany ładowania
- ✅ Inline editing dla wszystkich podstawowych pól:
  - ✅ Zmiana nazwy przedmiotu (edytowalne pole w wierszu) - Completed
  - ✅ Zmiana ilości (edytowalne pole w wierszu) - Completed
  - ✅ Zmiana wagi (edytowalne pole w wierszu) - Completed
  - ✅ Zmiana priorytetu (select w wierszu) - Completed
  - ✅ Zmiana statusu (select w wierszu) - Completed
  - ✅ Zmiana ceny i waluty (edytowalne pole w wierszu) - Completed
  - ✅ Zmiana kategorii (select w wierszu) - Completed
  - ✅ Zmiana notatek (edytowalne pole w wierszu) - Completed
- Szybkie akcje bezpośrednio z wiersza:
  - Upload photo (dodawanie zdjęcia do przedmiotu)
  - Add link for this item (dodawanie URL)
  - Mark as worn (oznaczenie jako worn)
  - Mark as consumable (oznaczenie jako consumable)
  - Star item (oznaczenie jako ulubiony/priorytetowy)
  - Zmiana statusu (owned, to buy, itp.)
  - Zmiana priorytetu
- Wzorzec: LighterPack - wszystkie akcje dostępne bezpośrednio z wiersza tabeli

### 🔄 Quick Add / Inline Editing - dopracowanie (inspiracja LighterPack)
**Status:** 🔄 Planned | **Priority:** Medium | **Complexity:** Medium | **Source:** [LIGHTERPACK_IMPROVEMENTS_TASKS.md](../comparison/LIGHTERPACK_IMPROVEMENTS_TASKS.md)

**Obecny stan:**
- ✅ Inline editing już istnieje dla: nazwa, ilość, waga, priorytet, status, cena, kategoria, notatki
- ✅ Edit mode toggle już istnieje
- ⚠️ Trzeba dopracować UX aby osiągnąć efekt podobny do LighterPack

**Wymagania do dopracowania:**
- Szybsze dodawanie przedmiotów (quick add bez otwierania formularza)
- Lepsze wizualne feedback podczas edycji
- Natychmiastowe zapisywanie zmian (debounce)
- Możliwość dodania nowego przedmiotu bezpośrednio w tabeli (pusty wiersz na końcu)

**Szczegóły implementacji:**
- Quick add: pusty wiersz na końcu tabeli w trybie edycji
- Wypełnienie podstawowych pól → automatyczne zapisanie
- Wizualne oznaczenie edytowanych wierszy
- Loading state podczas zapisywania
- Error handling z możliwością retry

### Szybka edycja nazwy kontenera (Inline Editing)
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Small

- Możliwość szybkiej edycji nazwy kontenera bezpośrednio na stronie Container Details
- Inline editing nazwy kontenera (podobnie jak inline editing przedmiotów)
- Kliknięcie w nazwę kontenera → przejście w tryb edycji
- Zapisywanie zmian po zatwierdzeniu (Enter) lub anulowanie (Escape)
- Wizualne oznaczenie trybu edycji (input field, ikona edycji)
- Zobacz też: [Szybka edycja nazwy kontenera na stronie Container Details](#-szybka-edycja-nazwy-kontenera-na-stronie-container-details) w sekcji UI/UX

### ✅ Kolejność przedmiotów w kontenerze
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Medium | **Feature:** [FEATURE-018](./features/FEATURE-018-item-ordering.md) | **Version:** v2.9.0

- Dodanie pola `order` (lub `sortOrder`) do przedmiotów w kontenerze
- Możliwość ręcznego układania przedmiotów w wybranej kolejności
- Dwa sposoby zmiany kolejności:
  - **Drag & drop** - przeciąganie wierszy w tabeli do zmiany kolejności (preferowane)
  - **Akcje "Do góry" / "Do dołu"** - przyciski w menu akcji przedmiotu (alternatywa, jeśli drag & drop jest zbyt skomplikowane)
- Kolejność zapisywana w localStorage i wyświetlana domyślnie w tabeli przedmiotów
- Opcja sortowania według innych kryteriów (nazwa, waga, kategoria) z możliwością powrotu do kolejności ręcznej
- Wizualne wskaźniki podczas przeciągania (highlight, placeholder)

### 🔄 Drag & Drop - rozszerzenie (inspiracja LighterPack)
**Status:** 🔄 Planned | **Priority:** Medium | **Complexity:** Medium | **Source:** [LIGHTERPACK_IMPROVEMENTS_TASKS.md](../comparison/LIGHTERPACK_IMPROVEMENTS_TASKS.md)

**Koncepcja:**
Rozszerzenie istniejącej funkcjonalności kolejności przedmiotów o pełne wsparcie drag & drop oraz przenoszenie przedmiotów między kontenerami.

**Wymagania:**
- ✅ (1) Drag & drop na stronie Container Details do zmiany kolejności przedmiotów (rozszerzenie istniejącego)
- ✅ (2) Drag & drop do przenoszenia przedmiotów do innych kontenerów (przez sidebar menu lub inny mechanizm)
- Ukrycie obecnych strzałek zmiany kolejności (obecnie wprowadzają wizualne zamieszanie)
- Strzałki można pokazać po naciśnięciu guzika "Zmień kolejność" jako alternatywa dla drag'n'drop

**Szczegóły implementacji:**
- **Miejsce 1:** Tabela przedmiotów na Container Details
  - Przeciąganie wierszy do zmiany kolejności (rozszerzenie istniejącego)
  - Wizualne feedback podczas przeciągania (highlight, placeholder)
  - Zapisywanie kolejności (pole `order` już istnieje)
  - Ukrycie strzałek zmiany kolejności (obecnie wprowadzają wizualne zamieszanie)
  - Strzałki można pokazać po naciśnięciu guzika "Zmień kolejność" jako alternatywa dla drag'n'drop
- **Miejsce 2:** Przenoszenie między kontenerami
  - Opcja A: Drag z tabeli do kontenera w sidebar menu
  - Opcja B: Drag z tabeli do dropdown "Przenieś do kontenera"
  - Opcja C: Drag handle w wierszu + dialog wyboru kontenera docelowego
- Biblioteka: `@dnd-kit/core` lub VueUse `useDraggable`
- Obsługa touch devices (mobile)

### ✅ Sortowanie w trybie batch z Alertem (ItemsTable)
**Status:** ✅ Completed | **Priority:** High | **Complexity:** Medium

- Sortowanie w ItemsTable na stronie Container Details działa w trybie batch (bez natychmiastowego zapisu)
- Po zmianie sortowania pojawia się Alert z guzikiem "Zapisz"
- Zmiany nie są zapisywane automatycznie, tylko po kliknięciu guzika w Alert
- Po kliknięciu "Zapisz" - zapis przez `batchUpdateOrder` (dla backendu i localStorage)
- Po kliknięciu "Anuluj" - przeładowanie kontenera i przywrócenie oryginalnej kolejności
- Alert pokazuje się zawsze, gdy są pending sorting changes (nie tylko dla backendu)

---

## 📊 Wizualizacje i analityka

### ✅ Wykres kołowy kategorii w kontenerze
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Medium

- ✅ Wykres kołowy (donut chart) pokazujący rozkład kategorii przedmiotów w kontenerze
- ✅ Przełącznik między dwoma trybami wyświetlania:
  - ✅ **Pod względem wagi** - Jak dużo ważą narzędzia względem całości? (procentowy udział wagi każdej kategorii)
  - ✅ **Pod względem ilości** - Jak dużo mam sztuk narzędzi względem wszystkich przedmiotów? (procentowy udział ilości przedmiotów w każdej kategorii)
- ✅ Wykres wyświetlany na stronie szczegółów kontenera
- ✅ Kolorowe segmenty odpowiadające kolorom kategorii (lub dedykowanym kolorom)
- ✅ Legenda z nazwami kategorii i wartościami procentowymi
- ✅ Uwzględnienie zagnieżdżonych kontenerów w obliczeniach (opcjonalnie)

### 🔄 Lepsze wizualizacje (inspiracja LighterPack)
**Status:** 🔄 Planned | **Priority:** Medium | **Complexity:** Small | **Source:** [LIGHTERPACK_IMPROVEMENTS_TASKS.md](../comparison/LIGHTERPACK_IMPROVEMENTS_TASKS.md)

**Koncepcja:**
Ulepszenie istniejących wykresów donut (nie zmieniamy na pie chart - donut jest lepszy) dla lepszej czytelności i użyteczności.

**Wymagania:**
- Wyświetlanie całkowitej wagi w środku donuta (obecnie tylko procenty)
- Lepsze kolory i kontrasty
- Większe, bardziej czytelne etykiety
- Lepsze tooltips z dodatkowymi informacjami

**Szczegóły implementacji:**
- Wyświetlanie całkowitej wagi w środku donuta (obecnie tylko procenty)
- Poprawa kolorów i kontrastów dla lepszej czytelności
- Większe etykiety z procentami
- Rozszerzone tooltips z wagą, ilością, ceną per kategoria

### ✅ Rozszerzenie wykresów na stronie szczegółów kontenera
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Medium | **Feature:** [FEATURE-019](./features/FEATURE-019-extended-charts.md)

- ✅ Dodanie wykresu kołowego według **ceny** (price) - rozkład kosztów według kategorii
  - ✅ Suma cen przedmiotów w każdej kategorii
  - ✅ Procentowy udział każdej kategorii w całkowitym koszcie kontenera
  - ✅ Wyświetlanie tylko dla przedmiotów z ustawioną ceną
- ✅ Dodanie wykresu kołowego według **priorytetu** (priority) - rozkład przedmiotów według priorytetu
  - ✅ Liczba przedmiotów w każdej kategorii priorytetu (critical, high, medium, low)
  - ✅ Procentowy udział każdego priorytetu w całkowitej liczbie przedmiotów
- ✅ Rozszerzenie przełącznika trybów wykresu o nowe opcje:
  - ✅ Waga (istniejące)
  - ✅ Ilość (istniejące)
  - ✅ Cena (nowe)
  - ✅ Priorytet (nowe)
- ✅ Wizualne oznaczenie brakujących danych (np. gdy przedmioty nie mają ustawionej ceny)
- ✅ Wszystkie wykresy używają spójnego systemu kolorów i stylu
- ✅ Kolory dla priorytetów: Critical (czerwony), High (pomarańczowy), Medium (żółty), Low (zielony)

### Wielowymiarowe wykresy (category x price, category x priority)
**Status:** 🔄 Planned | **Priority:** Low | **Complexity:** High

- Rozważenie implementacji wielowymiarowych wykresów pokazujących relacje między różnymi wymiarami danych
- Przykłady:
  - **Kategoria × Cena** - wykres słupkowy lub heatmap pokazujący średnią/całkowitą cenę dla każdej kategorii
  - **Kategoria × Priorytet** - wykres pokazujący rozkład priorytetów w każdej kategorii
  - **Priorytet × Cena** - wykres pokazujący rozkład cen według priorytetu
- Możliwe typy wykresów:
  - Heatmap (mapa ciepła) - dla dwóch wymiarów kategorycznych
  - Wykres słupkowy grupowany (grouped bar chart) - dla kombinacji kategorii i wartości numerycznych
  - Wykres bąbelkowy (bubble chart) - dla trzech wymiarów (x, y, rozmiar bąbelka)
- Interaktywne narzędzia do eksploracji danych (zoom, filtrowanie, tooltips)
- **Uwaga:** Ta funkcjonalność wymaga dokładniejszej analizy potrzeb użytkowników i może być zaimplementowana w późniejszej wersji

---

## ⚖️ Kontrola wagi

### ✅ Maksymalna waga kontenera (maxWeight)
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Medium | **Version:** v0.20.0

- ✅ Dodanie opcjonalnego pola `maxWeight` do kontenerów
- ✅ Możliwość ustawienia maksymalnej wagi dla kontenera (użytkownik może określić limit wagi, który jest w stanie nosić/transportować)
- ✅ Wizualne ostrzeżenia gdy waga kontenera przekracza lub zbliża się do limitu:
  - ✅ **Badge "Przekroczona waga"** - gdy totalna waga > maxWeight (czerwony, 100%+)
  - ✅ **Badge "Blisko limitu"** - ostrzeżenie (pomarańczowy, 90%+)
  - ✅ **Wskaźnik procentowy** - pokazuje procent wykorzystania limitu
  - ✅ **Kolorowanie** - zielony (0-70%), żółty (70-90%), pomarańczowy (90-100%), czerwony (100%+)
- ✅ Wyświetlanie w różnych miejscach:
  - ✅ W nagłówku kontenera (ContainerHeader) - badge i wskaźnik
  - ✅ W statystykach kontenera - wizualny wskaźnik z paskiem postępu ("15kg / 20kg")
- ✅ Ustawienie maxWeight w formularzu kontenera:
  - ✅ Pole opcjonalne z inputem numerycznym
  - ✅ Wybór jednostki wagi (g, kg, oz, lb) - zgodnie z preferowaną jednostką użytkownika
  - ✅ Automatyczna konwersja do gramów w modelu danych
- ✅ Uwzględnienie zagnieżdżonych kontenerów w obliczeniach wagi
- ✅ Uwzględnienie wagi samego kontenera w obliczeniach

**Nie zaimplementowane (future):**
- Toast/notification gdy podczas dodawania przedmiotu przekroczymy limit
- Opcjonalna blokada dodawania przedmiotów gdy limit jest przekroczony (checkbox w ustawieniach)
- Badge na karcie kontenera na liście

**Use cases:**
- Backpacking: "Nie chcę nosić więcej niż 12kg"
- Travel: "Bagaż podręczny max 8kg (limit linii lotniczej)"
- EDC: "Kieszeń max 500g"
- Survival kit: "Zestaw przetrwania max 3kg"

### ✅ Wizualizacja podziału wag (Other / Worn / Consumable)
**Status:** ✅ Completed | **Priority:** High | **Complexity:** Medium | **Feature:** [FEATURE-027](./features/FEATURE-027-weight-breakdown-visualization.md) | **Version:** v2.29.0

- ✅ Nowy tryb wykresu "weight-breakdown" w `CategoryPieChart.vue`
- ✅ Funkcja `calculateWeightBreakdown()` kategoryzująca przedmioty według flag wearable/consumable
- ✅ Wizualizacja podziału wag na trzy kategorie:
  - ✅ **Inne** - przedmioty w plecaku (nie noszone ani zużywalne)
  - ✅ **Noszone** - przedmioty noszone na sobie (wearable = true)
  - ✅ **Zużywalna** - przedmioty zużywalne (consumable = true)
- ✅ Priorytet kategoryzacji: consumable > worn > other (jeśli przedmiot ma obie flagi, traktowany jako consumable)
- ✅ Kolory: Inne (slate-400), Noszone (blue-500), Zużywalna (green-500)
- ✅ Obsługa tylko bezpośrednich przedmiotów kontenera (zagnieżdżone kontenery na razie nie uwzględniane)
- ✅ Filtrowanie pustych kategorii (nie pokazywanie kategorii z wagą = 0)
- ✅ Pełne wsparcie i18n (PL/EN) z opisowymi etykietami
- ✅ Przycisk w wykresie: "Inne / Noszone / Zużywalna" / "Other / Worn / Consumable"

### 🔄 Natychmiastowe obliczenia wagi (inspiracja LighterPack)
**Status:** 🔄 Planned | **Priority:** Medium | **Complexity:** Small | **Source:** [LIGHTERPACK_IMPROVEMENTS_TASKS.md](../comparison/LIGHTERPACK_IMPROVEMENTS_TASKS.md)

**Koncepcja:**
Obliczanie wagi w czasie rzeczywistym podczas edycji, z wizualnym feedbackiem zmian.

**Wymagania:**
- Obliczanie wagi w czasie rzeczywistym podczas edycji
- Podgląd wpływu zmian na całkowitą wagę
- Wizualne ostrzeżenia przy przekroczeniu limitu wagi

**Szczegóły implementacji:**
- Reaktywne obliczanie wagi podczas edycji inline
- Wyświetlanie zmiany wagi (np. "+50g" w kolorze zielonym/czerwonym)
- Ostrzeżenie gdy przekroczony limit wagi kontenera
- Animacja zmiany wagi

---

## 🛠️ Obsługa błędów i UX

### ✅ Strona 404 (Not Found)
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Small

- ✅ Dedykowana strona 404 dla niepasujących tras (`NotFoundPage.vue`)
- ✅ Wildcard route `*` w Vue Router łapiący wszystkie nieistniejące ścieżki
- ✅ Przyjazny dla użytkownika interfejs:
  - ✅ Komunikat "Strona nie została znaleziona"
  - ✅ Link do strony głównej
  - ✅ Sugestie dalszych kroków (Kontenery, Dashboard, Ustawienia)
- ✅ Tłumaczenia PL/EN
- ✅ Layout: `public` (dostępna dla wszystkich)

### ✅ Error handler dla chunk loading errors
**Status:** ✅ Completed | **Priority:** High | **Complexity:** Medium

- ✅ Obsługa błędu "ChunkLoadError" (błąd ładowania chunk po deploy nowej wersji)
- ✅ Wykrywanie błędów ładowania chunk w runtime
- ✅ Dialog z komunikatem (window.confirm):
  - ✅ Tytuł: "Nowa wersja aplikacji" / "New Version Available"
  - ✅ Treść: "Aplikacja została zaktualizowana. Aby kontynuować, należy odświeżyć stronę."
  - ✅ Przycisk "OK" (odświeża stronę) / "Cancel" (kontynuuje, niektóre funkcje mogą nie działać)
- ✅ Tłumaczenia PL/EN (automatyczne wykrywanie locale)
- ✅ Global error handler w `main.ts`

### ✅ Refaktoryzacja obsługi błędów - ujednolicenie użycia `useHandleError`
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Medium | **Plan:** [USE_HANDLE_ERROR_REFACTORING_PLAN.md](../plans/USE_HANDLE_ERROR_REFACTORING_PLAN.md)

- ✅ Ujednolicenie obsługi błędów w całej aplikacji poprzez użycie helpera `useHandleError`

### ✅ Poprawa przekierowania z formularza edycji przedmiotu
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Small

- ✅ Problem rozwiązany: Przekierowanie z formularza edycji przedmiotu (`ItemFormPage`) jest spójne
- ✅ Implementacja:
  - ✅ Przechowywanie `returnTo` w route query params
  - ✅ Sprawdzanie `returnTo` przed przekierowaniem po zapisaniu
  - ✅ Fallback do kontenera, jeśli brak `returnTo`
  - ✅ `ContainerDetailPage` przekazuje `returnTo: 'container'` przy edycji przedmiotu
  - ✅ `ItemDetailPage` przekazuje `returnTo: 'detail'` przy edycji przedmiotu
  - ✅ `ShoppingPlanningPage` przekazuje `returnTo: 'shopping'` przy edycji przedmiotu
- ✅ Dedykowany composable `useChunkLoadErrorHandler.ts` (opcjonalny)
- ✅ Auto-refresh po potwierdzeniu użytkownika

**Use cases:**
- Użytkownik ma otwartą aplikację
- Deploy nowej wersji następuje w tle
- Użytkownik próbuje przejść do nowej trasy
- Stara chunk jest usunięta → ChunkLoadError
- Dialog informuje użytkownika o nowej wersji i oferuje odświeżenie strony

### ✅ Refaktoryzacja systemu query parametrów (`returnTo` i `from`)
**Status:** ✅ Completed | **Priority:** High | **Complexity:** Medium | **Analysis:** [query-params-analysis.md](../analysis/query-params-analysis.md) | **Implementation:** [FEATURE-026-query-params-refactoring.md](../features/FEATURE-026-query-params-refactoring.md)

**Problem:**
- Niespójne użycie query parametrów `returnTo` i `from` w całej aplikacji
- Hardcoded stringi w URL zamiast funkcji z `routes.ts`
- Brak typowania wartości parametrów
- Rozproszona logika obsługi parametrów
- Brak automatycznego czyszczenia parametrów po użyciu

**Implementacja:**
- ✅ Utworzenie `src/modules/gear/utils/navigationParams.ts` z typami i helper functions
  - Typy: `ReturnToValue`, `FromValue`
  - Helper functions: `createNavigationQuery()`, `getReturnTo()`, `getFrom()`, `createItemEditPath()`
  - Funkcje walidacji: `isValidReturnTo()`, `isValidFrom()`
- ✅ Zastąpienie hardcoded stringów w `ShoppingListItem.vue` i `AvailableItemCard.vue`
- ✅ Refaktoryzacja `ItemFormPage.vue` do użycia helper functions
- ✅ Utworzenie composable `useNavigationReturn()` w `src/modules/gear/composables/useNavigationReturn.ts`
- ✅ Refaktoryzacja wszystkich komponentów używających query parametrów:
  - `ItemHeader.vue`, `ContainerDetailPage.vue`, `ShoppingPlanningPage.vue`
  - `AllItemsPage.vue`, `ItemsTable.vue`, `ItemsTableImageCell.vue`, `ContainerItemImageCard.vue`
- ✅ Implementacja automatycznego czyszczenia parametrów z URL po nawigacji
- ✅ Wszystkie hardcoded stringi zastąpione funkcjami z `navigationParams.ts`

**Korzyści:**
- ✅ Type safety i autocompletion w IDE
- ✅ Spójność w całej aplikacji
- ✅ Łatwość refaktoryzacji ścieżek
- ✅ Mniej duplikacji kodu
- ✅ Czyste URL-e w historii przeglądarki

**Szczegóły:** Zobacz [query-params-analysis.md](../analysis/query-params-analysis.md) i [FEATURE-026-query-params-refactoring.md](../features/FEATURE-026-query-params-refactoring.md)

---

## 📄 Informacje prawne i footer

### ✅ Strona "Informacja o ciasteczkach" i Footer
**Status:** ✅ Completed | **Priority:** Low | **Feature:** FEATURE-010 | **Complexity:** Small | **Completed in:** v0.15.0

**Strona "Informacja o ciasteczkach":**
- ✅ Strona `/cookies` z informacją o wykorzystaniu localStorage
- ✅ Sekcje: LocalStorage, Co przechowujemy, Prywatność, Przyszłość, RODO
- ✅ Zgodność z RODO - informacje o lokalnym przechowywaniu danych
- ✅ Tłumaczenia PL/EN

**Footer:**
- ✅ Footer z informacją `© [rok] DEV Made IT`
- ✅ Linki do:
  - ✅ Informacji o ciasteczkach (`/cookies`)
  - ✅ Polityki prywatności (`/privacy`)
  - ✅ Kontaktu (`/contact`)
  - ✅ GitHub/repozytorium
- ✅ Footer wyświetlany w `AuthenticatedLayout`

---

## 🤖 Funkcje AI (front-end only)


### ✅ Rozpoznawanie parametrów przedmiotów na żądanie
**Status:** ✅ Completed | **Priority:** Medium | **Complexity:** Medium | **Version:** v0.19.0

- ✅ Rozpoznawanie koloru, firmy (brand) i innych parametrów na podstawie nazwy przedmiotu
- ✅ Akcje dostępne w różnych miejscach:
  - ✅ **Formularz przedmiotu** - przycisk "Rozpoznaj parametry"
  - ✅ **Formularz kontenera** - przycisk "Rozpoznaj parametry" dla nazwy kontenera
  - ✅ **Strona kontenera z listą przedmiotów** - akcja "Rozpoznaj parametry wszystkich przedmiotów" (bulk action)
  - ✅ **Akcje wiersza przedmiotu w tabeli** - akcja "Rozpoznaj parametry" dla pojedynczego przedmiotu
- ✅ Automatyczne uzupełnianie pól: kolor, firma/brand (oraz innych jeżeli są dostępne)
- ✅ Integracja z istniejącymi słownikami sugerowanych wartości (SUGGESTED_BRANDS, SUGGESTED_COLORS)
- ✅ Fuzzy matching dla rozpoznawania brandów i kolorów
- ✅ Uzupełnianie tylko pustych pól (nie nadpisuje istniejących wartości)
- ✅ Integracja z importem markdown - automatyczne rozpoznawanie parametrów podczas importu

---

## 📈 Priorytetyzacja

### High Priority (Następne do zrobienia)
1. ✅ **Strona z listą wszystkich przedmiotów** - High priority, Medium complexity (Completed in v0.10.0)
2. ✅ **Dodawanie istniejących przedmiotów do kontenera** - High priority, Medium complexity (Completed in v0.22.0)
3. ✅ **Dodawanie własnych marek (brand)** - High priority, Medium complexity (Completed)
4. ✅ **Error handler dla chunk loading errors** - High priority, Medium complexity (Completed)
5. ✅ **Wyświetlanie kontenerów na liście wszystkich przedmiotów** - High priority, Small complexity (Completed)
6. **Edycja bezpośrednio na liście (Inline Editing)** - High priority, Large complexity

### Medium Priority
1. ✅ **Kopiowanie/klonowanie kontenerów** - Medium priority, Small complexity (Completed in v0.21.0)
2. ✅ **Maksymalna waga kontenera (maxWeight)** - Medium priority, Medium complexity (Completed in v0.20.0)
3. ✅ **Zintegrowany input wagi z wyborem jednostki** - Medium priority, Small complexity (Completed)
4. ✅ **Obsługa waluty (currency)** - Medium priority, Medium complexity (Completed)
5. ✅ **Kolejność przedmiotów w kontenerze** - Medium priority, Medium complexity (Completed)
6. ✅ **Poprawa przekierowania z formularza edycji przedmiotu** - Medium priority, Small complexity (Completed)
7. **Oznaczanie kontenerów jako fragmentów rodzica** - Medium priority, Medium complexity
8. **Obsługa Markdown w notatkach** - Medium priority, Medium complexity
9. ✅ **Rozszerzone pola** - Medium priority, Medium complexity (Completed in v0.8.0)
10. ✅ **Rozpoznawanie parametrów przedmiotów na żądanie** - Medium priority, Medium complexity (Completed in v0.19.0)

### Low Priority (Polish/Enhancement)
1. ⏸️ **Wybór primary color** - Low priority, Small complexity (On Hold - obecny kolor zadowalający)
2. ✅ **Footer i strony prawne** - Low priority, Small complexity (Completed)

---

## 📝 Uwagi dotyczące funkcjonalności wymagających backendu

Wszystkie funkcjonalności wymagające backendu, bazy danych lub autoryzacji zostały przeniesione do [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md), w tym:
- Synchronizacja między urządzeniami
- Wersjonowanie danych
- Udostępnianie i współpraca
- Globalny katalog itemów (multi-user)
- Linkowanie przedmiotów (multi-user)
- Zaawansowane funkcje AI z personalizacją
- Szablony kontenerów (z udostępnianiem)
- Statystyki i raporty (multi-user)

---

## 🐛 Znane błędy (Bugs)

### ✅ Pole notatek puste podczas edycji przedmiotu
**Status:** ✅ Completed | **Priority:** High | **Complexity:** Medium | **Bug:** [BUG_ITEM_EDIT_NOTES_EMPTY.md](./BUG_ITEM_EDIT_NOTES_EMPTY.md)

- Na stronie podglądu przedmiotu (`ItemDetailPage.vue`) pole "Notatki" wyświetla poprawną zawartość
- Na stronie edycji przedmiotu (`ItemFormPage.vue`) pole notatek jest puste
- Problem dotyczy trybu edycji - formularz nie jest poprawnie inicjalizowany danymi przedmiotu
- **Przyczyna (hipoteza):** Formularz inicjalizowany jest przed załadowaniem danych przedmiotu ze store'a
- **Kroki do reprodukcji:**
  1. Wygeneruj zestaw przykładowy "Bug Out Bag"
  2. Przejdź do kontenera "Bug Out Bag" → "Fire Pouch"
  3. Wybierz przedmiot "Morakniv Companion" (ma notatki)
  4. Na stronie podglądu widoczne są notatki
  5. Kliknij przycisk edycji - pole notatek jest puste

**Powiązane pliki:**
- `src/modules/gear/pages/ItemFormPage.vue`
- `src/modules/gear/pages/ItemDetailPage.vue`
- `src/modules/gear/composables/useItem.ts`
- `src/modules/gear/store/useGearStore.ts`

---

### ✅ Usuwanie wszystkich kontenerów - rozjazd między backend a localStorage
**Status:** ✅ Completed | **Priority:** High | **Complexity:** Medium

- ✅ Problem rozwiązany: Dodano dedykowany endpoint backendu `DELETE /gear/containers` do usuwania wszystkich kontenerów w jednej transakcji
- ✅ localStorage jest czyszczone tylko po potwierdzonym sukcesie operacji na backendzie
- ✅ Eliminacja rozjazdu między backendem a localStorage

**Rozwiązanie:**
- Backend: Dodano endpoint `DELETE /gear/containers` w `router.py`, metodę `delete_all_containers()` w `service.py` i `repository.py`
- Frontend: Zaktualizowano `gearContainerApiService.ts` i `gearContainerService.ts` do użycia nowego endpointu zamiast usuwania pojedynczo

**Powiązane pliki:**
- `backend/app/modules/gear/router.py` - endpoint `DELETE /gear/containers`
- `backend/app/modules/gear/service.py` - metoda `delete_all_containers(user_id)`
- `backend/app/modules/gear/repository.py` - implementacja usuwania wszystkich kontenerów
- `src/modules/gear/services/gearContainerApiService.ts` - metoda `deleteAllContainers()`
- `src/modules/gear/services/gearContainerService.ts` - zaktualizowana metoda `deleteAllContainers()`

---

## 📝 Notatki

- Wszystkie funkcjonalności w tym pliku działają z localStorage (front-end only)
- Wszystkie zaimplementowane features mają dokumentację w `docs/features/`
- Statusy są aktualizowane na bieżąco
- Priorytety mogą się zmieniać w zależności od potrzeb użytkowników
- Complexity: Small (1-2 dni), Medium (3-5 dni), Large (1+ tygodnie)
- Funkcjonalności wymagające backendu/DB/auth znajdują się w [ROADMAP_ONLINE.md](./ROADMAP_ONLINE.md)
