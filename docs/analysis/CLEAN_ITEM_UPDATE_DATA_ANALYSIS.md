# Analiza problemu z `cleanItemUpdateData` w `gearItemApiService.ts`

## Problem

Funkcja `cleanItemUpdateData` w `src/modules/gear/services/gearItemApiService.ts` (linie 84-153) wymaga ręcznego dodawania każdego nowego pola z `IUpdateItemDto`. To powoduje:

1. **Ryzyko błędów**: Łatwo zapomnieć dodać nowe pole (np. `showOnContainer` jest w typie, ale brakuje w funkcji!)
2. **Duplikacja kodu**: Podobna logika w `cleanItemData` dla create
3. **Trudność w utrzymaniu**: Każda zmiana w `IUpdateItemDto` wymaga aktualizacji funkcji
4. **Niespójność**: Różnice między `cleanItemData` a `cleanItemUpdateData`

## Przepływ danych (Flow)

### 1. Formularz (`ItemFormPage.vue`)
- Używa `vee-validate` z `itemSchema` (zod) z `validation.ts`
- Typ formularza: `ItemFormData` (wszystkie pola wymagane lub opcjonalne)
- W `onSubmit` (linia 192): dane są rzutowane na `ICreateItemDto | IUpdateItemDto`
- Dla edycji: `await updateItem(itemId, data as IUpdateItemDto)`

### 2. Composable (`useGear.ts`)
- `updateItem()` (linia 63): przekazuje `IUpdateItemDto` do `gearItemService().updateItem()`

### 3. Service Factory (`gearItemService.ts`)
- Dla API: wywołuje `gearItemApiService.updateItem(itemId, data)`
- Dla localStorage: wywołuje `gearItemLocalService.updateItem(itemId, data)`

### 4. API Service (`gearItemApiService.ts`)
- `updateItem()` (linia 174): wywołuje `cleanItemUpdateData(data)` przed wysłaniem
- `cleanItemUpdateData()` (linia 87): ręcznie filtruje i czyści każde pole
- Wysyła przez `apiClient.patch()` do backendu

### 5. Backend (`backend/app/modules/gear/schemas.py`)
- `ItemUpdate` (linia 172): Pydantic schema z wszystkimi polami opcjonalnymi (`Field(None)`)
- Używa `exclude_unset=True` w `model_dump()` (linia 373 w `repository.py`)
- **WAŻNE**: Pydantic NIE akceptuje `undefined` - JSON nie ma takiej wartości
- Opcjonalne pole w Pydantic oznacza: pole może być `null` lub mieć wartość, ale NIE może być `undefined`
- Jeśli pole nie jest w JSON → Pydantic używa wartości domyślnej (`None`)
- Jeśli pole jest w JSON jako `null` → Pydantic akceptuje to jako `None`
- Jeśli pole jest w JSON jako `undefined` → **Pydantic wyrzuci błąd walidacji**

## Jak działa obsługa `undefined` vs `null` w przepływie danych

### Frontend (TypeScript/JavaScript)
- `undefined`: wartość nie jest ustawiona (brak wartości)
- `null`: wartość jest jawnie ustawiona na `null` (brak wartości, ale świadomie)

### Serializacja JSON (Axios)
- **Axios automatycznie pomija pola z `undefined`** podczas serializacji (standardowe zachowanie `JSON.stringify`)
- Pola z wartością `null` są wysyłane jako `"field": null` w JSON
- **Wniosek**: Jeśli pole ma `undefined`, nie trafi do JSON (pole nie będzie w obiekcie)

### Backend (Pydantic)
- **JSON nie ma wartości `undefined`** - tylko `null` lub brak pola
- **Pydantic NIE akceptuje `undefined`** - jeśli pole jest w JSON jako `undefined` (co jest niemożliwe), Pydantic wyrzuci błąd walidacji
- **Opcjonalne pole w Pydantic** (`Field(None)`):
  - Jeśli pole **nie jest w JSON** → Pydantic używa wartości domyślnej (`None`)
  - Jeśli pole **jest w JSON jako `null`** → Pydantic akceptuje to jako `None`
  - Jeśli pole **jest w JSON z wartością** → Pydantic waliduje i przypisuje wartość
- **`exclude_unset=True` w `model_dump()`**:
  - Pomija pola, które nie były ustawione w modelu (czyli nie były w oryginalnym JSON)
  - Używane do partial update - tylko ustawione pola są aktualizowane

### Praktyczne implikacje
1. **Frontend wysyła pole z `undefined`** → Axios pomija pole → Pole nie trafia do JSON → Backend używa wartości domyślnej (`None`) → ✅ OK
2. **Frontend wysyła pole z `null`** → Axios wysyła `"field": null` → Backend akceptuje jako `None` → ✅ OK
3. **Frontend wysyła pole z wartością** → Axios wysyła wartość → Backend waliduje i przypisuje → ✅ OK
4. **Frontend wysyła pole z pustym stringiem `""`** → Axios wysyła `"field": ""` → Backend może zaakceptować, ale lepiej wysłać `null` → ⚠️ Wymaga konwersji

**Wniosek**: Funkcja `cleanItemUpdateData` jest potrzebna nie po to, żeby usuwać `undefined` (Axios to robi automatycznie), ale po to, żeby:
- Konwertować puste stringi na `null` (backend oczekuje `null`, nie pustych stringów)
- Filtrować nieobsługiwane wartości (np. `weightUnit: 'oz'` → pomijamy pole)
- Zapewnić, że tylko ustawione pola są wysyłane (partial update)

## Obecny stan typów

### Frontend: `IUpdateItemDto`
```typescript
export interface IUpdateItemDto {
  name?: string | null
  category?: TGearItemCategory | null
  quantity?: number | null
  weight?: number | null
  weightUnit?: TGearWeightUnit | null
  notes?: string | null
  expirationDate?: TDateTime | null
  priority?: TGearItemPriority | null
  status?: TGearItemStatus | null
  containerId?: TUUID | null
  price?: number | null
  currency?: string | null
  url?: string | null
  brand?: string | null
  color?: string | null
  quality?: TGearItemQuality | null
  wearable?: boolean | null
  consumable?: boolean | null
  order?: number | null
  showOnContainer?: boolean | null  // ⚠️ BRAKUJE w cleanItemUpdateData!
}
```

### Backend: `ItemUpdate`
```python
class ItemUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    category: GearItemCategory | None = None
    quantity: int | None = Field(None, ge=1)
    weight: float | None = Field(None, ge=0)
    weightUnit: GearWeightUnit | None = None
    notes: str | None = None
    expirationDate: datetime | None = Field(None, alias="expirationDate")
    priority: GearItemPriority | None = None
    status: GearItemStatus | None = None
    containerId: str | None = Field(None, alias="containerId")
    price: float | None = Field(None, ge=0)
    currency: str | None = Field(None, max_length=10)
    url: str | None = None
    brand: str | None = Field(None, max_length=255)
    color: str | None = Field(None, max_length=50)
    quality: GearItemQuality | None = None
    linkedItemId: str | None = Field(None, alias="linkedItemId")
    wearable: bool | None = None
    consumable: bool | None = None
    order: int | None = Field(None, ge=0)
    showOnContainer: bool | None = Field(None, alias="showOnContainer")
```

## Zidentyfikowane problemy

### 1. Brakujące pole w `cleanItemUpdateData`
- `showOnContainer` jest w `IUpdateItemDto` i `ItemUpdate`, ale **brakuje w `cleanItemUpdateData`**
- To oznacza, że pole nigdy nie zostanie wysłane do API, nawet jeśli jest w formularzu

### 2. Ręczna obsługa każdego pola
- 20+ pól wymaga ręcznego dodania
- Łatwo zapomnieć o nowym polu
- Trudne do utrzymania

### 3. Specjalne przypadki
- `weightUnit`: tylko 'g' lub 'kg' (backend nie wspiera 'oz'/'lb')
- Puste stringi → `null` (dla `notes`, `expirationDate`, `url`, `brand`, `color`)
- `isSet()` helper sprawdza `!== undefined && !== null`
- **Axios automatycznie pomija pola z `undefined`** podczas serializacji JSON (standardowe zachowanie `JSON.stringify`)
- **Frontend musi upewnić się, że nie wysyła `undefined` w JSON** - Axios to robi automatycznie, ale funkcja `cleanItemUpdateData` jest potrzebna do:
  - Konwersji pustych stringów na `null`
  - Filtrowania nieobsługiwanych wartości `weightUnit`
  - Zapewnienia, że tylko ustawione pola są wysyłane (partial update)

### 4. Duplikacja z `cleanItemData`
- Podobna logika w `cleanItemData()` dla create
- Różnice w obsłudze pól (np. `currency` tylko w update)

## Propozycje rozwiązań

### Opcja 1: Automatyczne czyszczenie z użyciem TypeScript (REKOMENDOWANE)

**Idea**: Użyć TypeScript do automatycznego iterowania po polach `IUpdateItemDto` i zastosowania reguł czyszczenia.

**Zalety**:
- Automatycznie obsługuje nowe pola
- Mniej kodu do utrzymania
- Type-safe (TypeScript sprawdzi zgodność typów)
- Jedna funkcja dla wszystkich pól

**Wady**:
- Wymaga refaktoryzacji
- Trzeba obsłużyć specjalne przypadki (weightUnit, puste stringi)

**Implementacja**:
```typescript
private cleanItemUpdateData(data: IUpdateItemDto): IUpdateItemDto {
  const cleaned: Partial<IUpdateItemDto> = {}
  
  // Iteruj po wszystkich kluczach IUpdateItemDto
  for (const key in data) {
    const value = data[key as keyof IUpdateItemDto]
    
    // Pomiń undefined/null - Axios automatycznie pomija undefined podczas serializacji,
    // ale tutaj usuwamy je explicite, żeby nie wysyłać null dla nieustawionych pól
    if (!isSet(value)) {
      continue // Pomiń undefined/null
    }
    
    // Specjalne przypadki
    if (key === 'weightUnit') {
      // Tylko 'g' lub 'kg' są wspierane przez backend
      // Filtrujemy 'oz' i 'lb' - nie wysyłamy ich do API
      if (value === 'g' || value === 'kg') {
        cleaned[key] = value
      }
      // Jeśli wartość to 'oz' lub 'lb', pomijamy pole (nie wysyłamy do API)
      continue
    }
    
    // Puste stringi → null dla stringowych pól (backend oczekuje null, nie pustych stringów)
    if (typeof value === 'string' && value.trim() === '') {
      const stringFields: (keyof IUpdateItemDto)[] = ['notes', 'expirationDate', 'url', 'brand', 'color']
      if (stringFields.includes(key as keyof IUpdateItemDto)) {
        cleaned[key] = null as any
        continue
      }
    }
    
    // Dla expirationDate: puste stringi → null
    if (key === 'expirationDate' && typeof value === 'string' && value.trim() === '') {
      cleaned[key] = null as any
      continue
    }
    
    // Standardowe przypisanie - wartość jest ustawiona i nie wymaga specjalnej obsługi
    cleaned[key] = value
  }
  
  return cleaned as IUpdateItemDto
}
```

### Opcja 2: Użycie `Partial<Pick<>>` z mapowaniem

**Idea**: Stworzyć mapę reguł czyszczenia dla każdego typu pola.

**Zalety**:
- Bardziej deklaratywne
- Łatwiejsze do testowania
- Można łatwo dodać nowe reguły

**Wady**:
- Wymaga utrzymania mapy reguł
- Więcej kodu

### Opcja 3: Usunięcie opcjonalności z `IUpdateItemDto` (NIE REKOMENDOWANE)

**Idea**: Zmienić `IUpdateItemDto` tak, aby wszystkie pola były wymagane (ale z możliwością `null`).

**Problemy**:
- Backend używa `exclude_unset=True`, więc oczekuje opcjonalnych pól
- Formularz wysyła tylko zmienione pola (partial update)
- To zmieniłoby semantykę DTO (partial update → full update)

**Wniosek**: To nie jest dobre rozwiązanie, bo zmienia semantykę partial update.

### Opcja 4: Uproszczenie - usunięcie `cleanItemUpdateData` (NIE REKOMENDOWANE)

**Idea**: Usunąć funkcję i polegać na Axios, który automatycznie pomija `undefined`, oraz backendzie z `exclude_unset=True`.

**Problemy**:
- **Axios automatycznie pomija pola z `undefined`** podczas serializacji (OK)
- **Backend używa `exclude_unset=True`**, więc pomija pola nieobecne w JSON (OK)
- **ALE**: Trzeba obsłużyć specjalne przypadki:
  - `weightUnit`: filtrowanie nieobsługiwanych wartości ('oz', 'lb')
  - Puste stringi → `null` (backend oczekuje `null`, nie pustych stringów)
- **Ryzyko**: Jeśli w przyszłości pojawi się pole, które wymaga specjalnej obsługi, łatwo o błąd

**Wniosek**: Możliwe, ale wymaga testów i może być ryzykowne. Obecna funkcja `cleanItemUpdateData` jest potrzebna do obsługi specjalnych przypadków, nie tylko do usuwania `undefined`.

## Rekomendacja: Opcja 1 z ulepszeniami

### Proponowane rozwiązanie

1. **Automatyczne czyszczenie** z iteracją po polach
2. **Mapa reguł specjalnych** dla pól wymagających specjalnej obsługi
3. **Wspólna funkcja** dla create i update (z różnicami w obsłudze wymaganych pól)

### Szczegóły implementacji

```typescript
// Mapa specjalnych reguł czyszczenia
const CLEANING_RULES = {
  weightUnit: (value: TGearWeightUnit | null | undefined) => {
    // Tylko 'g' lub 'kg' są wspierane przez backend
    return (value === 'g' || value === 'kg') ? value : undefined
  },
  expirationDate: (value: TDateTime | null | undefined) => {
    // Puste stringi → null
    if (typeof value === 'string' && value.trim() === '') {
      return null
    }
    return value
  },
  // String fields that should convert empty strings to null
  stringToNull: ['notes', 'url', 'brand', 'color'] as const,
} as const

private cleanItemUpdateData(data: IUpdateItemDto): IUpdateItemDto {
  const cleaned: Partial<IUpdateItemDto> = {}
  
  // Iteruj po wszystkich kluczach
  for (const key in data) {
    const typedKey = key as keyof IUpdateItemDto
    const value = data[typedKey]
    
    // Pomiń undefined/null
    if (!isSet(value)) {
      continue
    }
    
    // Specjalna obsługa weightUnit
    if (typedKey === 'weightUnit') {
      const cleanedValue = CLEANING_RULES.weightUnit(value)
      if (cleanedValue !== undefined) {
        cleaned[typedKey] = cleanedValue
      }
      continue
    }
    
    // Specjalna obsługa expirationDate
    if (typedKey === 'expirationDate') {
      cleaned[typedKey] = CLEANING_RULES.expirationDate(value) as any
      continue
    }
    
    // Puste stringi → null dla wybranych pól
    if (CLEANING_RULES.stringToNull.includes(typedKey as any)) {
      if (typeof value === 'string' && value.trim() === '') {
        cleaned[typedKey] = null as any
        continue
      }
    }
    
    // Standardowe przypisanie
    cleaned[typedKey] = value
  }
  
  return cleaned as IUpdateItemDto
}
```

### Dodatkowe ulepszenia

1. **Wspólna funkcja dla create i update**:
   - Wyodrębnić wspólną logikę
   - Różnice tylko w obsłudze wymaganych pól (create) vs opcjonalnych (update)

2. **Testy jednostkowe**:
   - Sprawdzić wszystkie pola
   - Sprawdzić specjalne przypadki
   - Sprawdzić nowe pola (automatycznie)

3. **Type safety**:
   - Użyć `keyof IUpdateItemDto` do zapewnienia zgodności typów
   - TypeScript wyłapie brakujące pola w czasie kompilacji

## Wnioski

1. **Obecne rozwiązanie jest podatne na błędy** - łatwo zapomnieć dodać nowe pole
2. **Backend obsługuje partial update** - używa `exclude_unset=True` w `model_dump()`
3. **Pydantic NIE akceptuje `undefined`** - JSON nie ma takiej wartości, więc backend wyrzuci błąd walidacji
4. **Axios automatycznie pomija `undefined`** - podczas serializacji JSON (standardowe zachowanie)
5. **Frontend musi czyścić dane** - nie po to, żeby usuwać `undefined` (Axios to robi), ale:
   - Konwertować puste stringi na `null` (backend oczekuje `null`, nie pustych stringów)
   - Filtrować nieobsługiwane wartości `weightUnit` ('oz', 'lb')
   - Zapewnić, że tylko ustawione pola są wysyłane (partial update)
6. **Rekomendacja**: Automatyczne czyszczenie z iteracją po polach i mapą reguł specjalnych
7. **Priorytet**: Naprawić brakujące pole `showOnContainer` w `cleanItemUpdateData`

## Propozycje rozwiązań (inspirowane Laravel)

### Opcja A: Middleware w FastAPI (Backend) - REKOMENDOWANE

**Idea**: Zaimplementować middleware podobny do Laravel `ConvertEmptyStringsToNull`, który automatycznie konwertuje puste stringi na `None` przed walidacją Pydantic.

**Zalety**:
- ✅ Centralne rozwiązanie - działa dla wszystkich endpointów
- ✅ Nie trzeba pamiętać o czyszczeniu w każdym serwisie
- ✅ Spójne z podejściem Laravel (znane rozwiązanie)
- ✅ Automatycznie obsługuje wszystkie pola (nie trzeba ręcznie dodawać)
- ✅ Działa dla wszystkich modułów (gear, user, etc.)

**Wady**:
- ⚠️ Wymaga implementacji middleware
- ⚠️ Trzeba obsłużyć specjalne przypadki (np. `weightUnit` - tylko 'g'/'kg')
- ⚠️ Może wpływać na inne endpointy (ale można to kontrolować)

**Implementacja**:
```python
# backend/app/core/middleware.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import json

class ConvertEmptyStringsToNoneMiddleware(BaseHTTPMiddleware):
    """Convert empty strings to None in request body (similar to Laravel ConvertEmptyStringsToNull)."""
    
    async def dispatch(self, request: Request, call_next):
        # Only process POST, PUT, PATCH requests with JSON body
        if request.method in ("POST", "PUT", "PATCH"):
            if request.headers.get("content-type", "").startswith("application/json"):
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

# W setup_middleware():
app.add_middleware(ConvertEmptyStringsToNoneMiddleware)
```

**Uwagi**:
- Middleware działa przed walidacją Pydantic
- Można dodać wykluczenia dla konkretnych endpointów (np. przez path matching)
- Specjalne przypadki (np. `weightUnit`) nadal wymagają obsługi w serwisie lub dodatkowej logiki w middleware

### Opcja B: Axios Interceptor (Frontend)

**Idea**: Dodać request interceptor w Axios, który transformuje dane przed wysłaniem.

**Zalety**:
- ✅ Centralne rozwiązanie po stronie frontendu
- ✅ Działa dla wszystkich requestów
- ✅ Nie wymaga zmian w backendzie
- ✅ Można dodać specjalne reguły (np. `weightUnit`)

**Wady**:
- ⚠️ Transformacja po stronie frontendu (może być wolniejsza)
- ⚠️ Trzeba obsłużyć specjalne przypadki
- ⚠️ Może wpływać na inne requesty (ale można kontrolować przez URL matching)

**Implementacja**:
```typescript
// src/shared/services/dataTransform.interceptor.ts
import type { InternalAxiosRequestConfig } from 'axios'

export function dataTransformInterceptor(config: InternalAxiosRequestConfig): InternalAxiosRequestConfig {
  // Only transform JSON requests
  if (config.data && typeof config.data === 'object' && config.headers['Content-Type']?.includes('application/json')) {
    // Only for gear endpoints (optional - can be removed for global transform)
    if (config.url?.includes('/gear/')) {
      config.data = transformGearData(config.data)
    }
  }
  return config
}

function transformGearData(data: any): any {
  if (Array.isArray(data)) {
    return data.map(transformGearData)
  }
  if (data && typeof data === 'object') {
    const transformed: any = {}
    for (const [key, value] of Object.entries(data)) {
      // Convert empty strings to null
      if (value === '') {
        transformed[key] = null
      }
      // Filter unsupported weightUnit values
      else if (key === 'weightUnit' && value !== 'g' && value !== 'kg') {
        // Skip this field (don't send to API)
        continue
      }
      // Recursively transform nested objects
      else if (value && typeof value === 'object') {
        transformed[key] = transformGearData(value)
      }
      else {
        transformed[key] = value
      }
    }
    return transformed
  }
  return data
}

// W apiClient.ts:
apiClient.interceptors.request.use(dataTransformInterceptor)
```

### Opcja C: Ulepszona funkcja `cleanItemUpdateData` (Obecne rozwiązanie, ale automatyczne)

**Idea**: Ulepszyć obecną funkcję, aby automatycznie iterowała po wszystkich polach (jak w Opcji 1 z analizy).

**Zalety**:
- ✅ Nie wymaga zmian w backendzie
- ✅ Kontrola nad transformacją w serwisie
- ✅ Można łatwo dodać specjalne reguły

**Wady**:
- ⚠️ Trzeba pamiętać o użyciu funkcji w każdym serwisie
- ⚠️ Duplikacja logiki między create i update
- ⚠️ Nie działa automatycznie dla innych modułów

**Implementacja**: (Zobacz Opcję 1 w sekcji "Propozycje rozwiązań" powyżej)

### Opcja D: Kombinacja - Middleware (Backend) + Uproszczona funkcja (Frontend)

**Idea**: Middleware w backendzie obsługuje konwersję pustych stringów na `None`, a frontend tylko filtruje specjalne przypadki (np. `weightUnit`).

**Zalety**:
- ✅ Najlepsze z obu światów
- ✅ Backend automatycznie obsługuje puste stringi
- ✅ Frontend tylko filtruje specjalne przypadki
- ✅ Mniej kodu w frontendzie

**Wady**:
- ⚠️ Wymaga implementacji middleware
- ⚠️ Nadal trzeba obsłużyć specjalne przypadki w frontendzie

**Implementacja**:
- Backend: Middleware jak w Opcji A
- Frontend: Uproszczona funkcja, która tylko filtruje `weightUnit` i usuwa `undefined`

## Rekomendacja: Opcja D (Kombinacja)

**Dlaczego**:
1. **Middleware w backendzie** rozwiązuje problem z pustymi stringami globalnie (wszystkie moduły)
2. **Uproszczona funkcja w frontendzie** obsługuje tylko specjalne przypadki (np. `weightUnit`)
3. **Mniej kodu** - większość logiki w jednym miejscu (middleware)
4. **Spójne z Laravel** - znane i sprawdzone rozwiązanie
5. **Automatyczne** - nie trzeba pamiętać o czyszczeniu w każdym serwisie

**Plan implementacji**:
1. Dodać middleware `ConvertEmptyStringsToNoneMiddleware` w backendzie
2. Uprościć `cleanItemUpdateData` - tylko specjalne przypadki (weightUnit, etc.)
3. Usunąć logikę konwersji pustych stringów z frontendu (middleware to obsługuje)
4. Dodać testy dla middleware
5. Dodać testy dla uproszczonej funkcji czyszczenia

## Plan działania

1. ✅ Analiza problemu (ten dokument)
2. ⏳ Implementacja middleware w backendzie (Opcja D)
3. ⏳ Uproszczenie `cleanItemUpdateData` w frontendzie (tylko specjalne przypadki)
4. ⏳ Dodanie brakującego pola `showOnContainer`
5. ⏳ Refaktoryzacja `cleanItemData` do użycia wspólnej logiki
6. ⏳ Testy jednostkowe (middleware + funkcje czyszczenia)
7. ⏳ Weryfikacja z backendem

