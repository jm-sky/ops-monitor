# Plan implementacji Opcji D: Middleware + Uproszczona funkcja czyszczenia

## Podsumowanie

**Cel**: Zastąpić ręczne funkcje czyszczenia danych automatycznym middleware w backendzie (podobnie jak Laravel `ConvertEmptyStringsToNull`).

**Korzyści**:
- ✅ Automatyczna konwersja pustych stringów na `null` dla wszystkich endpointów
- ✅ Mniej kodu w frontendzie (uproszczone funkcje czyszczenia)
- ✅ Łatwiejsze utrzymanie (nie trzeba pamiętać o dodawaniu nowych pól)
- ✅ Spójne z podejściem Laravel (znane rozwiązanie)

**Zakres zmian**:
- **Backend**: 1 plik (middleware)
- **Frontend**: 2 pliki (serwisy API)

## Przegląd zmian

### Backend
- ✅ Dodać middleware `ConvertEmptyStringsToNoneMiddleware` w FastAPI
- ✅ Middleware automatycznie konwertuje puste stringi na `None` przed walidacją Pydantic

### Frontend
- ✅ Uprościć funkcje czyszczenia w serwisach API
- ✅ Usunąć logikę konwersji pustych stringów (middleware to obsługuje)
- ✅ Zostawić tylko specjalne przypadki (np. `weightUnit`)

## Zidentyfikowane miejsca do zmiany

### Backend

#### 1. Nowy middleware
- **Plik**: `backend/app/core/middleware.py`
- **Akcja**: Dodać `ConvertEmptyStringsToNoneMiddleware`
- **Funkcjonalność**: 
  - Konwertuje puste stringi (`""`) na `None` w request body
  - Działa dla POST, PUT, PATCH
  - Rekurencyjnie przetwarza zagnieżdżone obiekty i tablice

#### 2. Rejestracja middleware
- **Plik**: `backend/app/core/middleware.py` (funkcja `setup_middleware`)
- **Akcja**: Dodać middleware do aplikacji

### Frontend

#### 1. `gearItemApiService.ts`
- **Funkcje do zmiany**:
  - `cleanItemData()` - uprościć (usunąć konwersję pustych stringów)
  - `cleanItemUpdateData()` - uprościć (usunąć konwersję pustych stringów)
- **Co zostaje**:
  - Filtrowanie `weightUnit` (tylko 'g'/'kg')
  - Usuwanie `undefined` (dla partial update)
- **Co usuwać**:
  - Konwersja pustych stringów na `null` (middleware to obsługuje)
  - Logika `data.notes || null`, `data.url || null`, etc.

#### 2. `gearContainerApiService.ts`
- **Funkcje do zmiany**:
  - `cleanContainerData()` - uprościć (usunąć konwersję pustych stringów)
  - `cleanContainerUpdateData()` - uprościć (usunąć konwersję pustych stringów)
- **Co zostaje**:
  - Filtrowanie `weightUnit` i `maxWeightUnit` (tylko 'g'/'kg')
  - Usuwanie `undefined` (dla partial update)
- **Co usuwać**:
  - Konwersja pustych stringów na `null` (middleware to obsługuje)
  - Logika `data.description || null`, `data.url || null`, etc.

#### 3. `settingsApiService.ts` (opcjonalna zmiana)
- **Funkcja**: `sanitizeUpdateData()` - tylko usuwa `undefined`, nie konwertuje pustych stringów
- **Akcja**: Można zostawić (nie konwertuje pustych stringów) lub uprościć (middleware nie pomaga, bo tylko usuwa `undefined`)
- **Decyzja**: Zostawić bez zmian (funkcja jest prosta i nie duplikuje logiki)

#### 4. Inne serwisy API (bez zmian)
- `userApiService.ts` - ✅ Nie ma funkcji czyszczenia (wysyła dane bezpośrednio)
- `gearSettingsApiService.ts` - ✅ Nie ma funkcji czyszczenia (wysyła dane bezpośrednio)

## Szczegółowy plan implementacji

### Krok 1: Implementacja middleware w backendzie

**Plik**: `backend/app/core/middleware.py`

```python
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import json

class ConvertEmptyStringsToNoneMiddleware(BaseHTTPMiddleware):
    """
    Convert empty strings to None in request body (similar to Laravel ConvertEmptyStringsToNull).
    
    This middleware automatically converts empty strings ('') to None (null in JSON)
    before Pydantic validation, ensuring consistent handling of optional fields.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Only process POST, PUT, PATCH requests with JSON body
        if request.method in ("POST", "PUT", "PATCH"):
            content_type = request.headers.get("content-type", "")
            if content_type.startswith("application/json"):
                body = await request.body()
                if body:
                    try:
                        data = json.loads(body)
                        data = self._convert_empty_strings_to_none(data)
                        # Reconstruct request with modified body
                        async def receive():
                            return {"type": "http.request", "body": json.dumps(data).encode()}
                        request._receive = receive
                    except (json.JSONDecodeError, ValueError):
                        # If JSON parsing fails, let Pydantic handle it
                        pass
        
        response = await call_next(request)
        return response
    
    def _convert_empty_strings_to_none(self, obj):
        """Recursively convert empty strings to None."""
        if isinstance(obj, dict):
            return {k: self._convert_empty_strings_to_none(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_empty_strings_to_none(item) for item in obj]
        elif isinstance(obj, str) and obj == "":
            return None
        return obj
```

**Rejestracja w `setup_middleware()`**:
```python
# Add custom middleware here
app.add_middleware(ConvertEmptyStringsToNoneMiddleware)
```

### Krok 2: Uproszczenie `gearItemApiService.ts`

**Zmiany w `cleanItemData()`**:
- Usunąć: `cleaned.notes = data.notes || null`
- Usunąć: `cleaned.expirationDate = data.expirationDate && data.expirationDate.trim() !== '' ? data.expirationDate : null`
- Usunąć: `cleaned.url = data.url || null`
- Usunąć: `cleaned.brand = data.brand || null`
- Usunąć: `cleaned.color = data.color || null`
- Zostawić: Filtrowanie `weightUnit` (jeśli potrzebne)
- Zostawić: Usuwanie `undefined` dla opcjonalnych pól

**Zmiany w `cleanItemUpdateData()`**:
- Usunąć: `cleaned.notes = data.notes || null`
- Usunąć: `cleaned.expirationDate = data.expirationDate && data.expirationDate.trim() !== '' ? data.expirationDate : null`
- Usunąć: `cleaned.url = data.url || null`
- Usunąć: `cleaned.brand = data.brand || null`
- Usunąć: `cleaned.color = data.color || null`
- Zostawić: Filtrowanie `weightUnit` (tylko 'g'/'kg')
- Zostawić: Usuwanie `undefined` dla partial update
- **Dodać**: Brakujące pole `showOnContainer`

**Nowa uproszczona wersja**:
```typescript
private cleanItemUpdateData(data: IUpdateItemDto): IUpdateItemDto {
  const cleaned: Partial<IUpdateItemDto> = {}
  
  for (const key in data) {
    const typedKey = key as keyof IUpdateItemDto
    const value = data[typedKey]
    
    // Pomiń undefined/null (Axios automatycznie pomija undefined)
    if (!isSet(value)) {
      continue
    }
    
    // Specjalna obsługa weightUnit - tylko 'g' lub 'kg' są wspierane przez backend
    if (typedKey === 'weightUnit') {
      if (value === 'g' || value === 'kg') {
        cleaned[typedKey] = value
      }
      // Pomijamy 'oz' i 'lb' - nie wysyłamy do API
      continue
    }
    
    // Wszystkie inne pola - middleware obsługuje konwersję pustych stringów
    cleaned[typedKey] = value
  }
  
  return cleaned as IUpdateItemDto
}
```

### Krok 3: Uproszczenie `gearContainerApiService.ts`

**Zmiany w `cleanContainerData()`**:
- Usunąć: `cleaned.description = data.description || null`
- Usunąć: `cleaned.url = data.url || null`
- Usunąć: `cleaned.brand = data.brand || null`
- Zostawić: Filtrowanie `weightUnit` i `maxWeightUnit` (tylko 'g'/'kg')
- Zostawić: Usuwanie `undefined` dla opcjonalnych pól

**Zmiany w `cleanContainerUpdateData()`**:
- Usunąć: `cleaned.description = data.description || null`
- Usunąć: `cleaned.url = data.url || null`
- Usunąć: `cleaned.brand = data.brand || null`
- Zostawić: Filtrowanie `weightUnit` i `maxWeightUnit` (tylko 'g'/'kg')
- Zostawić: Usuwanie `undefined` dla partial update

**Nowa uproszczona wersja** (podobna do `cleanItemUpdateData`):
```typescript
private cleanContainerUpdateData(data: IUpdateContainerDto): IUpdateContainerDto {
  const cleaned: Partial<IUpdateContainerDto> = {}
  
  for (const key in data) {
    const typedKey = key as keyof IUpdateContainerDto
    const value = data[typedKey]
    
    // Pomiń undefined/null
    if (!isSet(value)) {
      continue
    }
    
    // Specjalna obsługa weightUnit i maxWeightUnit
    if (typedKey === 'weightUnit' || typedKey === 'maxWeightUnit') {
      if (value === 'g' || value === 'kg') {
        cleaned[typedKey] = value
      }
      continue
    }
    
    // Wszystkie inne pola - middleware obsługuje konwersję pustych stringów
    cleaned[typedKey] = value
  }
  
  return cleaned as IUpdateContainerDto
}
```

### Krok 4: Testy

#### Backend
- Test middleware: sprawdzić konwersję pustych stringów na `None`
- Test zagnieżdżonych obiektów
- Test tablic
- Test różnych typów danych (string, number, boolean, null)
- Test że middleware nie wpływa na inne requesty

#### Frontend
- Test uproszczonych funkcji czyszczenia
- Test filtrowania `weightUnit`
- Test że `undefined` jest pomijane
- Test że puste stringi są wysyłane (middleware je konwertuje)

### Krok 5: Weryfikacja

1. ✅ Sprawdzić, czy wszystkie endpointy działają poprawnie
2. ✅ Sprawdzić, czy puste stringi są konwertowane na `null` w backendzie
3. ✅ Sprawdzić, czy specjalne przypadki (weightUnit) działają
4. ✅ Sprawdzić, czy nie ma regresji w innych modułach

## Lista plików do zmiany

### Backend
1. `backend/app/core/middleware.py` - dodać middleware i rejestrację

### Frontend
1. `src/modules/gear/services/gearItemApiService.ts` - uprościć `cleanItemData()` i `cleanItemUpdateData()`
2. `src/modules/gear/services/gearContainerApiService.ts` - uprościć `cleanContainerData()` i `cleanContainerUpdateData()`

### Frontend (opcjonalne)
3. `src/modules/settings/services/settingsApiService.ts` - można uprościć `sanitizeUpdateData()`, ale nie jest konieczne (nie konwertuje pustych stringów)

## Potencjalne problemy i rozwiązania

### Problem 1: Middleware może wpływać na inne endpointy
**Rozwiązanie**: Middleware działa tylko dla POST/PUT/PATCH z JSON, co jest bezpieczne. Jeśli potrzeba wykluczeń, można dodać path matching.

### Problem 2: Konwersja pustych stringów może być niepożądana w niektórych przypadkach
**Rozwiązanie**: Dodać wykluczenia w middleware (np. przez path matching) lub flagę w request headers.

### Problem 3: Wydajność - middleware przetwarza każdy request
**Rozwiązanie**: Middleware jest lekki (tylko rekurencyjna konwersja), nie powinno być problemu z wydajnością.

## Kolejność implementacji

1. ✅ **Backend middleware** - najpierw dodać middleware, żeby frontend mógł z niego korzystać
2. ✅ **Testy middleware** - upewnić się, że działa poprawnie
3. ✅ **Frontend - gearItemApiService** - uprościć funkcje czyszczenia
4. ✅ **Frontend - gearContainerApiService** - uprościć funkcje czyszczenia
5. ✅ **Testy frontend** - sprawdzić, czy wszystko działa
6. ✅ **Integracja** - testy end-to-end
7. ✅ **Dokumentacja** - zaktualizować komentarze w kodzie

## Metryki sukcesu

- ✅ Middleware automatycznie konwertuje puste stringi na `None`
- ✅ Funkcje czyszczenia w frontendzie są uproszczone (mniej kodu)
- ✅ Nie ma regresji w istniejących funkcjach
- ✅ Wszystkie testy przechodzą
- ✅ Kod jest łatwiejszy w utrzymaniu (mniej duplikacji)

## Uwagi

- Middleware działa globalnie dla wszystkich endpointów - to jest zamierzone
- Jeśli w przyszłości pojawi się potrzeba wykluczeń, można dodać path matching
- Specjalne przypadki (np. `weightUnit`) nadal wymagają obsługi w frontendzie
- Middleware nie obsługuje `undefined` (Axios to robi automatycznie), tylko puste stringi

