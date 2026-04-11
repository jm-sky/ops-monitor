# Lista zadań: Ulepszenia inspirowane LighterPack

**Data utworzenia:** 2025-01-21  
**Status:** ⏳ Oczekuje na zatwierdzenie  
**Cel:** Ulepszenie Gear Stack funkcjami inspirowanymi przez LighterPack, zachowując zaawansowane możliwości aplikacji.

---

## 📋 Lista zadań

### 1. Tryb prosty (Simple Mode)

**Status:** 🔄 Planned  
**Priorytet:** High  
**Złożoność:** Medium

**Wymagania:**
- ✅ Toggle "Tryb prosty" w ustawieniach użytkownika (zapisywane w DB/localStorage)
- ✅ Zaawansowane opcje w dropdown menu jako `Więcej... →`
- ✅ Podstawowe pola widoczne domyślnie
- ✅ Zaawansowane pola ukryte pod `Więcej` w formularzach
- ✅ W trybie prostym ukrywamy zaawansowane kolumny w tabelach (np. cena, waluta, marka, kolor)
- ✅ Zagnieżdżanie kontenerów zostaje (użytkownik kontroluje czy zagnieżdża)
- ❌ Nie robimy Wizard dla nowych użytkowników

**Szczegóły implementacji:**
- Ustawienie `simpleMode: boolean` w ustawieniach użytkownika
- Podstawowe pola przedmiotu: nazwa, waga, ilość, kategoria, notatki, status, priorytet
- Zaawansowane pola (ukryte w trybie prostym): cena, waluta, marka, kolor, URL, data ważności, shelf life, wearable, consumable
- W tabelach: ukrycie zaawansowanych kolumn w trybie prostym
- W formularzach: sekcja "Więcej opcji" z dropdown/expandable section

---

### 2. Drag & Drop

**Status:** 🔄 Planned  
**Priorytet:** High  
**Złożoność:** Medium

**Wymagania:**
- ✅ (1) Drag & drop na stronie Container Details do zmiany kolejności przedmiotów
- ✅ (2) Drag & drop do przenoszenia przedmiotów do innych kontenerów (przez sidebar menu lub inny mechanizm)
- Przy okazji rozważyć ukrycie obecnych strzałek zmiany kolejności przedmiotów. Obecnie strzałki wprowadzają wizualne zamieszanie. Można je pokazywać po naciśnięciu guzika "Zmień kolejność" jako alternatywa dla drag'n'drop.

**Szczegóły implementacji:**
- **Miejsce 1:** Tabela przedmiotów na Container Details
  - Przeciąganie wierszy do zmiany kolejności
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

---

### 3. System pomocy / Tutorial

**Status:** 🔄 Planned  
**Priorytet:** Medium  
**Złożoność:** Small-Medium

**Wymagania:**
- ✅ Małe ramki z pomocą (contextual help boxes)
- ✅ Przycisk `?` na górze który pokaże sugestie/podpowiedzi
- ✅ Możliwość dodania AI Chat jako pomoc

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

---

### 4. Kontekstowe podpowiedzi

**Status:** 🔄 Planned  
**Priorytet:** Medium  
**Złożoność:** Small

**Wymagania:**
- ✅ Tooltips przy ważnych elementach
- ✅ Empty states z sugestiami co zrobić
- ✅ Kontekstowe podpowiedzi w formularzach

**Szczegóły implementacji:**
- Tooltips dla wszystkich akcji i przycisków
- Empty states z konkretnymi sugestiami (np. "Dodaj pierwszy przedmiot", "Utwórz kontener")
- Formularze: podpowiedzi pod polami (np. "Waga w gramach", "Format daty: DD.MM.YYYY")

---

### 5. Quick Add / Inline Editing - dopracowanie

**Status:** 🔄 Planned  
**Priorytet:** High  
**Złożoność:** Medium

**Obecny stan:**
- ✅ Inline editing już istnieje dla: nazwa, ilość, waga, priorytet, status, cena, kategoria, notatki
- ✅ Edit mode toggle już istnieje
- ⚠️ Trzeba dopracować UX aby osiągnąć efekt podobny do LighterPack

**Wymagania do dopracowania:**
- ✅ Opis requirements aby osiągnąć efekt UX podobny w LighterPack
- ✅ Szybsze dodawanie przedmiotów (quick add bez otwierania formularza)
- ✅ Lepsze wizualne feedback podczas edycji
- ✅ Natychmiastowe zapisywanie zmian (debounce)
- ✅ Możliwość dodania nowego przedmiotu bezpośrednio w tabeli (pusty wiersz na końcu)

**Szczegóły implementacji:**
- Quick add: pusty wiersz na końcu tabeli w trybie edycji
- Wypełnienie podstawowych pól → automatyczne zapisanie
- Wizualne oznaczenie edytowanych wierszy
- Loading state podczas zapisywania
- Error handling z możliwością retry

---

### 6. Import / Export CSV i JSON

**Status:** 🔄 Planned  
**Priorytet:** Medium  
**Złożoność:** Medium

**Obecny stan:**
- ✅ CSV Export już istnieje (`ExportToCSVDialog.vue`, `exportToCSV.ts`)
- ❌ CSV Import - brak implementacji
- ✅ JSON Export - istnieje (backup/restore)
- ✅ JSON Import - istnieje (backup/restore)

**Wymagania:**
- ✅ Import CSV (nowa funkcjonalność)
- ✅ Eksport CSV (już istnieje, sprawdzić czy wymaga ulepszeń)
- ✅ Eksport JSON (już istnieje)
- ✅ Import JSON (już istnieje)

**Szczegóły implementacji:**
- **CSV Import:**
  - Dialog importu CSV z upload pliku
  - Parser CSV z obsługą różnych separatorów (przecinek, średnik)
  - Mapowanie kolumn (nazwa, waga, kategoria, itp.)
  - Walidacja danych przed importem
  - Preview przed importem
  - Obsługa błędów (nieprawidłowe dane, brakujące kolumny)
- **CSV Export:** Sprawdzić czy wymaga ulepszeń (już istnieje)
- **JSON Export/Import:** Sprawdzić czy wymaga ulepszeń (już istnieje)

---

### 7. Lepsze wizualizacje

**Status:** 🔄 Planned  
**Priorytet:** Low  
**Złożoność:** Small

**Wymagania:**
- ✅ Ulepszenie istniejących wykresów donut (nie zmieniamy na pie chart - donut jest lepszy)
- ✅ Wyświetlanie całkowitej wagi w środku donuta
- ✅ Lepsze kolory i kontrasty
- ✅ Większe, bardziej czytelne etykiety
- ✅ Lepsze tooltips z dodatkowymi informacjami

**Szczegóły implementacji:**
- Wyświetlanie całkowitej wagi w środku donuta (obecnie tylko procenty)
- Poprawa kolorów i kontrastów dla lepszej czytelności
- Większe etykiety z procentami
- Rozszerzone tooltips z wagą, ilością, ceną per kategoria
- ~~Wizualizacja wagi w headerze kontenera (duży, czytelny tekst)~~ Waga już jest czytelna.

---

### 8. Natychmiastowe obliczenia wagi

**Status:** 🔄 Planned  
**Priorytet:** Low  
**Złożoność:** Small

**Wymagania:**
- ✅ Obliczanie wagi w czasie rzeczywistym podczas edycji
- ✅ Podgląd wpływu zmian na całkowitą wagę
- ✅ Wizualne ostrzeżenia przy przekroczeniu limitu wagi

**Szczegóły implementacji:**
- Reaktywne obliczanie wagi podczas edycji inline
- Wyświetlanie zmiany wagi (np. "+50g" w kolorze zielonym/czerwonym)
- Ostrzeżenie gdy przekroczony limit wagi kontenera
- Animacja zmiany wagi

---

## 📊 Podsumowanie

| # | Zadanie | Status | Priorytet | Złożoność | Uwagi |
|---|---------|--------|-----------|-----------|-------|
| 1 | Tryb prosty | 🔄 Planned | High | Medium | Nowa funkcjonalność |
| 2 | Drag & Drop | 🔄 Planned | High | Medium | Nowa funkcjonalność |
| 3 | System pomocy | 🔄 Planned | Medium | Small-Medium | Nowa funkcjonalność |
| 4 | Kontekstowe podpowiedzi | 🔄 Planned | Medium | Small | Ulepszenie istniejących |
| 5 | Quick Add / Inline Editing | 🔄 Planned | High | Medium | Dopracowanie istniejących |
| 6 | Import/Export CSV/JSON | 🔄 Planned | Medium | Medium | CSV Import - nowe, reszta istnieje |
| 7 | Lepsze wizualizacje | 🔄 Planned | Low | Small | Ulepszenie istniejących |
| 8 | Natychmiastowe obliczenia | 🔄 Planned | Low | Small | Ulepszenie istniejących |

---

## 🎯 Priorytetyzacja

### Faza 1 (Wysoki priorytet):
1. Tryb prosty
2. Drag & Drop
3. Quick Add / Inline Editing - dopracowanie

### Faza 2 (Średni priorytet):
4. System pomocy / Tutorial
5. Kontekstowe podpowiedzi
6. Import CSV

### Faza 3 (Niski priorytet):
7. Lepsze wizualizacje
8. Natychmiastowe obliczenia wagi

---

**Ostatnia aktualizacja:** 2025-01-21

