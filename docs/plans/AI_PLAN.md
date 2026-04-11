# AI w Gear Stack — Podsumowanie

## Podstawowe zasady
- Backend korzysta tylko z **OpenRouter**.
- Użytkownik może wybierać **5–15 modeli**, różnych firm, czasem kilka modeli od tej samej firmy.
- Na razie tylko **modele tekstowe**; vision zostawiamy na później.
- Każdy użytkownik może podać **własny token**:
  - Darmowy plan → AI działa tylko z własnym tokenem.
  - Plany płatne → użytkownik wybiera jawnie: własny token lub token systemowy.
- Wybór modelu jest zawsze dowolny, niezależnie od planu.
- **Limity** dotyczą tylko użycia **systemowego tokena**.
- Endpointy są **osobne**: `/ai/chat`, `/ai/classify`, `/ai/embed`, `/ai/vision` (vision później).
- **Preferencje użytkownika** (model, token, parametry) są zapisywane w bazie.

## Zastosowania AI
1. **Rozpoznawanie właściwości przedmiotów**
   - Kategorie, brandy, kolory itp.
   - Tryby: import Markdown (opcjonalnie), tworzenie/edycja pojedynczego przedmiotu, grupowo dla wielu przedmiotów.
2. **Sugestie i optymalizacja packów**
   - Jeden kontener, kilka lub wszystkie.
   - Co dodać / usunąć, priorytety, waga.
3. **Generowanie listy gearu na podstawie scenariusza**
   - Wejście: typ bag, budżet, warunki itp.
   - Wyjście: lista rekomendowanych przedmiotów z kategoriami, wagą, ilością.

## Mechanika użycia AI
- Backend tworzy **initial prompt**, użytkownik może go zmienić.
- Dodawany jest **kontekst**: lista sprzętu wg wybranych opcji (tylko nazwy, nazwy + opisy, wagi itp.).
- Historia jest **zawsze przechowywana**:
  - Maksymalny rozmiar; po przekroczeniu kasowanie najstarszych wpisów.
  - Użytkownik może przeglądać i usuwać historię.
  - W historii zapisujemy wszystko: prompt, modyfikacje, kontekst, odpowiedź AI, model, token, czas.
- Możliwość **re-run** zapisanych interakcji (opcjonalnie).

## Interakcja użytkownika — wersja 1
- AI działa przez **okienko chatu**.
- Treść chatu może być zaimportowana, co tworzy nowe wpisy lub aktualizuje istniejące.
- Trzeba dodać obsługę **kasowania wpisów**.

## Interakcja użytkownika — wersja 2 (przyszłość)
- Wyniki działania AI mogą tworzyć **nowe przedmioty**, które są podświetlone.
- Istniejące przedmioty będą miały **przycisk wyboru alternatywnej opcji**.

---

# AI – Decyzje architektoniczne (szczegóły)

## 1. Billing / limity
- Rozliczanie dokładnie **tak jak OpenRouter** (tokeny wejściowe + wyjściowe).
- Zero ukrytych limitów, przejrzyste statystyki.
- Użytkownik widzi dokładne zużycie tokenów dla każdej operacji.

## 2. Fallback modeli
- **Brak fallbacku.**
- Jeśli model jest niedostępny — wyświetlamy komunikat użytkownikowi.
- Użytkownik sam wybiera inny model z listy dostępnych.
- Komunikat: "Model [nazwa] jest obecnie niedostępny. Wybierz inny model z listy."

## 3. Odpowiedzialność za jakość AI
- AI działa **na odpowiedzialność użytkownika**.
- Krótka informacja ostrzegawcza przy pierwszym użyciu funkcji AI.
- Disclaimer w dokumentacji: "Wyniki AI mogą być niedokładne - zawsze weryfikuj dane."

## 4. Konfiguracja parametrów modeli
- Brak ustawień typu `temperature`, `max_tokens`, `top_p` itd. w pierwszej wersji.
- System korzysta ze standardowych, sprawdzonych parametrów dla każdego typu operacji.
- W przyszłości możliwość advanced settings dla zaawansowanych użytkowników.

## 5. Kontekst sprzętu
- Użytkownik może **wybrać, które pola** idą do kontekstu:
  - Tylko nazwy przedmiotów
  - Nazwy + opisy
  - Nazwy + wagi
  - Nazwy + kategorie
  - Wszystkie dane (full context)
- Brak automatycznego skracania kontekstu.
- Jeśli kontekst przekracza limit modelu — pokazujemy komunikat:
  - "Kontekst przekracza limit modelu ([X] tokenów / [Y] max). Wybierz mniej pól lub mniej przedmiotów."

## 6. Przechowywanie tokenów użytkownika
- Klucze API **encrypt-at-rest** w bazie danych (szyfrowanie).
- Użytkownik może:
  - Dodać własny token OpenRouter
  - Zmienić token w dowolnym momencie
  - Usunąć token (przejście na token systemowy lub brak dostępu do AI na darmowym planie)
- Token systemowy dostępny tylko dla płatnych planów.
- Walidacja tokena przy dodawaniu (test API call do OpenRouter).

## 7. Historia AI
- Zapisujemy pełne dane każdej interakcji:
  - **Finalny prompt** (po wszystkich modyfikacjach użytkownika)
  - Kontekst użyty w zapytaniu
  - Odpowiedź AI (pełna)
  - Metadane:
    - Model użyty (nazwa, provider)
    - Token użyty (systemowy / własny)
    - Timestamp (data i czas)
    - Liczba tokenów (input + output)
    - Koszt operacji (jeśli token systemowy)
- **Nie zapisujemy** template'u promptu (tylko finalny prompt po edycji użytkownika).
- Mechanizm limitu historii:
  - Domyślnie: 100 ostatnich wpisów
  - Po przekroczeniu: automatyczne usuwanie najstarszych
  - Użytkownik może ręcznie usuwać wpisy z historii
- Użytkownik może:
  - Przeglądać historię
  - Filtrować po dacie, modelu, typie operacji
  - Usuwać pojedyncze wpisy lub całą historię
  - Re-run zapisanych promptów (opcjonalnie w przyszłości)

## 8. Logi i monitoring
- Logujemy na backendzie:
  - Błędy API (OpenRouter down, rate limits, invalid tokens)
  - Czasy odpowiedzi (performance monitoring)
  - Zużycie tokenów per użytkownik
  - Zużycie systemowego tokena (koszty)
- Podstawowy monitoring stabilności:
  - Status OpenRouter API (health check)
  - Średnie czasy odpowiedzi per model
  - Success rate per model
- Alerty dla adminów przy problemach (opcjonalnie Sentry integration).

## 9. Cache
- Cache dla powtarzalnych operacji:
  - **Klasyfikacje przedmiotów** (nazwa → kategoria, worn, consumable)
  - **Embeddingi** (dla przyszłych funkcji semantic search)
- Strategia cache:
  - Key: hash(operation_type + input_data + model)
  - TTL: 7 dni dla klasyfikacji, 30 dni dla embedów
  - Storage: Redis lub PostgreSQL JSONB
- Korzyści:
  - Zmniejsza koszty (mniej API calls)
  - Szybsze odpowiedzi dla powtarzalnych zapytań
  - Mniejsze obciążenie OpenRouter API

## 10. Awaria OpenRouter
- Jeśli OpenRouter API jest niedostępne:
  - Pokazujemy prosty i jasny komunikat:
    - **"Usługa OpenRouter jest tymczasowo niedostępna. Spróbuj ponownie za kilka minut."**
  - Nie próbujemy fallbacków ani retry (aby nie generować kosztów).
  - Logujemy błąd dla monitoringu.
- Jeśli konkretny model jest niedostępny:
  - Komunikat: **"Model [nazwa] jest obecnie niedostępny. Wybierz inny model z listy."**

## 11. Wybór modelu
- Użytkownik wybiera **jeden aktywny model** z listy.
- Lista zawiera około **5–15 modeli**:
  - Różni providerzy (OpenAI, Anthropic, Google, Meta, Mistral, itp.)
  - Różne rozmiary (small, medium, large)
  - Różne ceny (budget, balanced, premium)
- Przykładowa lista modeli:
  - OpenAI: GPT-4o, GPT-4o-mini, GPT-3.5-turbo
  - Anthropic: Claude 3.5 Sonnet, Claude 3 Haiku
  - Google: Gemini Pro, Gemini Flash
  - Meta: Llama 3.1 70B, Llama 3.1 8B
  - Mistral: Mistral Large, Mistral Small
- Dla każdego modelu pokazujemy:
  - Nazwę i providera
  - Context window (np. 128k tokens)
  - Koszt (input / output per 1M tokens)
  - Rekomendowany use case (klasyfikacje, generowanie, analiza)
- Użytkownik może używać **własnego tokena** → brak limitów poza OpenRouter limits.
- Limity dotyczą **tylko użycia tokena systemowego** (płatne plany).
