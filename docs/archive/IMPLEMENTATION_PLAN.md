# Plan Implementacji - Gear Stack

## 📋 Przegląd

Aplikacja do zarządzania sprzętem survivalowym z pełną funkcjonalnością client-side używającą localStorage.

**Struktura modułu:** `src/modules/gear/`

---

## 🏗️ Architektura Modułu

Moduł `gear` będzie zorganizowany w następującej strukturze:

```
src/modules/gear/
├── types/           # TypeScript types i interfaces
├── services/        # CRUD operations i logika biznesowa
├── store/           # Pinia store (tylko storage/persistence)
├── composables/     # Composable functions (używa store + service)
├── components/      # Komponenty Vue
├── pages/           # Strony Vue
├── utils/           # Helper functions
├── routes.ts        # Routing configuration
└── validation/      # Zod schemas (opcjonalnie w utils/)
```

---

## 📁 Struktura Plików

### 1. Types (`src/modules/gear/types/`)

#### `src/modules/gear/types/gear.types.ts`

```typescript
import type { TUUID, TDateTime } from '@/shared/types/base.type'

// Typ kontenera
export type TGearContainerType = 'bugOutBag' | 'edc' | 'getHomeBag' | 'custom'

// Status przedmiotu
export type TGearItemStatus = 'owned' | 'missing' | 'toBuy'

// Priorytet przedmiotu
export type TGearItemPriority = 'critical' | 'high' | 'medium' | 'low'

// Kategoria przedmiotu
export type TGearItemCategory = 
  | 'water'
  | 'food'
  | 'shelter'
  | 'fire'
  | 'firstAid'
  | 'tools'
  | 'navigation'
  | 'communication'
  | 'clothing'
  | 'hygiene'
  | 'other'

// Pojedynczy przedmiot
export interface IGearItem {
  id: TUUID
  name: string
  category: TGearItemCategory
  quantity: number
  weight: number // w gramach
  notes?: string
  expirationDate?: TDateTime // ISO date string
  priority: TGearItemPriority
  status: TGearItemStatus
  createdAt: TDateTime
  updatedAt: TDateTime
}

// Kontener (plecak/zestaw)
export interface IGearContainer {
  id: TUUID
  name: string
  description?: string
  type: TGearContainerType
  items: IGearItem[]
  createdAt: TDateTime
  updatedAt: TDateTime
}

// DTO dla tworzenia kontenera
export interface ICreateContainerDto {
  name: string
  description?: string
  type: TGearContainerType
}

// DTO dla aktualizacji kontenera
export interface IUpdateContainerDto {
  name?: string
  description?: string
  type?: TGearContainerType
}

// DTO dla tworzenia przedmiotu
export interface ICreateItemDto {
  name: string
  category: TGearItemCategory
  quantity: number
  weight: number
  notes?: string
  expirationDate?: TDateTime
  priority: TGearItemPriority
  status: TGearItemStatus
}

// DTO dla aktualizacji przedmiotu
export interface IUpdateItemDto {
  name?: string
  category?: TGearItemCategory
  quantity?: number
  weight?: number
  notes?: string
  expirationDate?: TDateTime
  priority?: TGearItemPriority
  status?: TGearItemStatus
}
```

---

### 2. Services (`src/modules/gear/services/`)

#### `src/modules/gear/services/gearService.ts`

**Odpowiedzialność:** Wszystkie operacje CRUD i logika biznesowa

```typescript
import type { 
  IGearContainer, 
  IGearItem,
  ICreateContainerDto,
  IUpdateContainerDto,
  ICreateItemDto,
  IUpdateItemDto
} from '../types/gear.types'
import { useGearStore } from '../store/useGearStore'

class GearService {
  // ========== Containers CRUD ==========
  
  createContainer(data: ICreateContainerDto): IGearContainer {
    // Logika tworzenia + wywołanie store
  }
  
  updateContainer(id: TUUID, data: IUpdateContainerDto): IGearContainer {
    // Logika aktualizacji + wywołanie store
  }
  
  deleteContainer(id: TUUID): void {
    // Logika usuwania + wywołanie store
  }
  
  getContainerById(id: TUUID): IGearContainer | undefined {
    // Pobranie z store
  }
  
  getAllContainers(): IGearContainer[] {
    // Pobranie wszystkich z store
  }
  
  // ========== Items CRUD ==========
  
  createItem(containerId: TUUID, data: ICreateItemDto): IGearItem {
    // Logika tworzenia + wywołanie store
  }
  
  updateItem(containerId: TUUID, itemId: TUUID, data: IUpdateItemDto): IGearItem {
    // Logika aktualizacji + wywołanie store
  }
  
  deleteItem(containerId: TUUID, itemId: TUUID): void {
    // Logika usuwania + wywołanie store
  }
  
  getItemById(containerId: TUUID, itemId: TUUID): IGearItem | undefined {
    // Pobranie z store
  }
  
  // ========== Business Logic ==========
  
  calculateTotalWeight(containerId: TUUID): number {
    // Obliczanie całkowitej wagi
  }
  
  calculateReadinessPercentage(containerId: TUUID): number {
    // Obliczanie % gotowości (owned items / total items)
  }
  
  getItemsByStatus(containerId: TUUID, status: TGearItemStatus): IGearItem[] {
    // Filtrowanie po statusie
  }
  
  getExpiredItems(containerId: TUUID): IGearItem[] {
    // Przedmioty z przeterminowaną datą
  }
  
  getExpiringSoonItems(containerId: TUUID, days: number = 30): IGearItem[] {
    // Przedmioty wygasające wkrótce
  }
  
  moveItem(containerId: TUUID, itemId: TUUID, newContainerId: TUUID): void {
    // Przenoszenie przedmiotu między kontenerami
  }
  
  // ========== Import/Export ==========
  
  exportData(): string {
    // Eksport do JSON
  }
  
  importData(json: string): void {
    // Import z JSON
  }
}

export const gearService = new GearService()
```

---

### 3. Store (`src/modules/gear/store/`)

#### `src/modules/gear/store/useGearStore.ts`

**Odpowiedzialność:** Tylko storage/persistence - synchronizacja z localStorage

**Uwaga:** Można użyć `useStorage` z VueUse do automatycznej synchronizacji z localStorage

```typescript
import { defineStore } from 'pinia'
import { useStorage } from '@vueuse/core'
import type { IGearContainer } from '../types/gear.types'

interface IGearStoreState {
  containers: IGearContainer[]
}

const STORAGE_KEY = 'gear-stack:containers'

export const useGearStore = defineStore('gear', {
  state: (): IGearStoreState => ({
    // Użycie useStorage dla automatycznej synchronizacji
    // Alternatywnie: ręczna implementacja z loadFromStorage/saveToStorage
    containers: useStorage<IGearContainer[]>(STORAGE_KEY, []).value,
  }),
  
  getters: {
    // Proste getters do dostępu do danych
    getContainerById: (state) => (id: TUUID) => {
      return state.containers.find(c => c.id === id)
    },
    
    getAllContainers: (state) => {
      return state.containers
    },
  },
  
  actions: {
    // Tylko operacje na state - bez logiki biznesowej
    setContainers(containers: IGearContainer[]): void {
      this.containers = containers
      // Jeśli używamy useStorage, automatycznie zapisze się do localStorage
      // W przeciwnym razie wywołać saveToStorage()
    },
    
    addContainer(container: IGearContainer): void {
      this.containers.push(container)
    },
    
    updateContainer(container: IGearContainer): void {
      const index = this.containers.findIndex(c => c.id === container.id)
      if (index !== -1) {
        this.containers[index] = container
      }
    },
    
    removeContainer(id: TUUID): void {
      this.containers = this.containers.filter(c => c.id !== id)
    },
    
    // Synchronizacja z localStorage (jeśli nie używamy useStorage)
    loadFromStorage(): void {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        try {
          this.containers = JSON.parse(stored)
        } catch (error) {
          console.error('Error loading from storage:', error)
        }
      }
    },
    
    saveToStorage(): void {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(this.containers))
      } catch (error) {
        console.error('Error saving to storage:', error)
      }
    },
  },
})
```

---

### 4. Composables (`src/modules/gear/composables/`)

#### `src/modules/gear/composables/useGear.ts`

**Odpowiedzialność:** Główny composable używający service + store

```typescript
import { computed } from 'vue'
import { gearService } from '../services/gearService'
import { useGearStore } from '../store/useGearStore'
import type { IGearContainer, IGearItem } from '../types/gear.types'

export function useGear() {
  const store = useGearStore()
  
  // Reactive state z store
  const containers = computed(() => store.getAllContainers)
  
  // CRUD operations przez service
  const createContainer = (data: ICreateContainerDto) => {
    return gearService.createContainer(data)
  }
  
  const updateContainer = (id: TUUID, data: IUpdateContainerDto) => {
    return gearService.updateContainer(id, data)
  }
  
  const deleteContainer = (id: TUUID) => {
    gearService.deleteContainer(id)
  }
  
  // ... podobnie dla items
  
  return {
    // State
    containers,
    
    // Actions
    createContainer,
    updateContainer,
    deleteContainer,
    // ...
  }
}
```

#### `src/modules/gear/composables/useContainer.ts`

Composable dla pojedynczego kontenera

#### `src/modules/gear/composables/useItem.ts`

Composable dla pojedynczego przedmiotu

---

### 5. Utils/Helpers (`src/modules/gear/utils/`)

#### `src/modules/gear/utils/validation.ts`

Zod schemas dla walidacji

```typescript
import { z } from 'zod'

export const containerSchema = z.object({
  name: z.string().min(1, 'Nazwa jest wymagana'),
  description: z.string().optional(),
  type: z.enum(['bugOutBag', 'edc', 'getHomeBag', 'custom']),
})

export const itemSchema = z.object({
  name: z.string().min(1, 'Nazwa jest wymagana'),
  category: z.enum(['water', 'food', 'shelter', 'fire', 'firstAid', 'tools', 'navigation', 'communication', 'clothing', 'hygiene', 'other']),
  quantity: z.number().int().min(1, 'Ilość musi być większa od 0'),
  weight: z.number().min(0, 'Waga nie może być ujemna'),
  notes: z.string().optional(),
  expirationDate: z.string().optional(),
  priority: z.enum(['critical', 'high', 'medium', 'low']),
  status: z.enum(['owned', 'missing', 'toBuy']),
})
```

#### `src/modules/gear/utils/calculations.ts`

Helper functions do obliczeń (waga, gotowość, etc.)

#### `src/modules/gear/utils/dateHelpers.ts`

Helper functions do dat (expiration, expiring soon, etc.)

**Użycie VueUse:**
- `useNow` - opcjonalnie do reactive current date/time

---

### 6. Components (`src/modules/gear/components/`)

- `ContainerCard.vue` - karta kontenera
- `ContainerStats.vue` - statystyki kontenera
- `ContainerForm.vue` - formularz kontenera
  - **VueUse:** `useFocus` - auto-focus na pierwszym polu
- `ContainerHeader.vue` - nagłówek kontenera
- `ItemsTable.vue` - tabela przedmiotów
- `ItemsFilters.vue` - filtry i sortowanie
  - **VueUse:** `useDebouncedRef` - debounce dla wyszukiwania, `useToggle` - rozwijanie filtrów
- `ItemForm.vue` - formularz przedmiotu
  - **VueUse:** `useFocus` - auto-focus na pierwszym polu
- `ItemDetail.vue` - szczegóły przedmiotu
- `ExpirationWarning.vue` - ostrzeżenie o ważności
- `QuickActions.vue` - szybkie akcje
  - **VueUse:** `useToggle` - otwieranie/zamykanie menu akcji

---

### 7. Pages (`src/modules/gear/pages/`)

- `ContainersListPage.vue` - lista kontenerów
  - **VueUse:** `useDebouncedRef` - wyszukiwanie, `useMediaQuery` - responsive grid, `useElementVisibility` - lazy loading
- `ContainerFormPage.vue` - formularz kontenera (create/edit)
- `ContainerDetailPage.vue` - widok kontenera
  - **VueUse:** `useFileDialog` - import JSON, `useDownloadFile` - export JSON, `useClipboard` - kopiowanie, `useAsyncState` - stan import/export
- `ItemFormPage.vue` - formularz przedmiotu (create/edit)
- `ItemDetailPage.vue` - widok szczegółowy przedmiotu

---

### 8. Routes (`src/modules/gear/routes.ts`)

```typescript
import type { RouteRecordRaw } from 'vue-router'

export const gearRoutes: RouteRecordRaw[] = [
  {
    path: '/gear',
    name: 'gear-containers',
    component: () => import('@/modules/gear/pages/ContainersListPage.vue'),
    meta: { layout: 'authenticated' },
  },
  {
    path: '/gear/new',
    name: 'gear-container-new',
    component: () => import('@/modules/gear/pages/ContainerFormPage.vue'),
    meta: { layout: 'authenticated' },
  },
  {
    path: '/gear/:id',
    name: 'gear-container-detail',
    component: () => import('@/modules/gear/pages/ContainerDetailPage.vue'),
    meta: { layout: 'authenticated' },
  },
  {
    path: '/gear/:id/edit',
    name: 'gear-container-edit',
    component: () => import('@/modules/gear/pages/ContainerFormPage.vue'),
    meta: { layout: 'authenticated' },
  },
  {
    path: '/gear/:containerId/items/new',
    name: 'gear-item-new',
    component: () => import('@/modules/gear/pages/ItemFormPage.vue'),
    meta: { layout: 'authenticated' },
  },
  {
    path: '/gear/:containerId/items/:itemId',
    name: 'gear-item-detail',
    component: () => import('@/modules/gear/pages/ItemDetailPage.vue'),
    meta: { layout: 'authenticated' },
  },
  {
    path: '/gear/:containerId/items/:itemId/edit',
    name: 'gear-item-edit',
    component: () => import('@/modules/gear/pages/ItemFormPage.vue'),
    meta: { layout: 'authenticated' },
  },
]
```

---

## 🔄 Flow Danych

```
Component (Vue)
    ↓
Composable (useGear, useContainer, useItem)
    ↓
Service (gearService) - logika biznesowa + CRUD
    ↓
Store (useGearStore) - tylko storage/persistence
    ↓
localStorage
```

**Przykład:**
1. Komponent wywołuje `createContainer()` z composable
2. Composable wywołuje `gearService.createContainer()`
3. Service wykonuje logikę biznesową i wywołuje `store.addContainer()`
4. Store aktualizuje state i zapisuje do localStorage

---

## 📝 Kolejność Implementacji

### Faza 1: Fundamenty
1. ✅ Utworzenie struktury katalogów `src/modules/gear/`
2. ✅ Utworzenie typów TypeScript (`types/gear.types.ts`)
3. ✅ Utworzenie schematów walidacji Zod (`utils/validation.ts`)
4. ✅ Utworzenie store Pinia (`store/useGearStore.ts`) - tylko storage
5. ✅ Utworzenie serwisu (`services/gearService.ts`) - CRUD + logika
6. ✅ Utworzenie composables (`composables/useGear.ts`)
7. ✅ Dodanie tłumaczeń i18n

### Faza 2: Lista Kontenerów
8. ✅ Utworzenie `pages/ContainersListPage.vue`
9. ✅ Utworzenie `components/ContainerCard.vue`
10. ✅ Utworzenie `pages/ContainerFormPage.vue` i `components/ContainerForm.vue`
11. ✅ Dodanie routingu (`routes.ts`)
12. ✅ Testowanie CRUD kontenerów

### Faza 3: Widok Kontenera
13. ✅ Utworzenie `pages/ContainerDetailPage.vue`
14. ✅ Utworzenie `components/ItemsTable.vue` (używa DataTable)
15. ✅ Utworzenie `components/ItemsFilters.vue`
16. ✅ Implementacja sortowania i filtrowania
17. ✅ Implementacja wyszukiwania

### Faza 4: Zarządzanie Przedmiotami
18. ✅ Utworzenie `pages/ItemFormPage.vue` i `components/ItemForm.vue`
19. ✅ Utworzenie `pages/ItemDetailPage.vue`
20. ✅ Implementacja szybkich akcji (zmiana statusu)
21. ✅ Testowanie CRUD przedmiotów

### Faza 5: Funkcjonalności Zaawansowane
22. ✅ Implementacja obliczania wagi kontenera (`utils/calculations.ts`)
23. ✅ Implementacja wskaźnika gotowości
24. ✅ Implementacja wykrywania przeterminowanych przedmiotów (`utils/dateHelpers.ts`)
25. ✅ Implementacja wykrywania wygasających przedmiotów
26. ✅ Implementacja import/export JSON

### Faza 6: UX i Polerowanie
27. ✅ Dodanie loading states
28. ✅ Dodanie error handling
29. ✅ Dodanie toast notifications
30. ✅ Dodanie potwierdzeń usuwania
31. ✅ Optymalizacja wydajności

---

## 🎨 UI/UX Wskazówki

### Kolory dla Statusów
- `owned` - zielony (success)
- `missing` - czerwony (danger)
- `toBuy` - żółty/pomarańczowy (warning)

### Kolory dla Priorytetów
- `critical` - czerwony
- `high` - pomarańczowy
- `medium` - żółty
- `low` - szary

### Wskaźnik Gotowości
- Progress bar z procentami
- Kolor zależny od %:
  - 0-50% - czerwony
  - 51-80% - żółty
  - 81-100% - zielony

### Ostrzeżenia o Ważności
- Przeterminowane - czerwony badge/alert
- Wygasające w ciągu 7 dni - żółty badge/alert
- Wygasające w ciągu 30 dni - pomarańczowy badge/alert

---

## 🔧 Narzędzia i Biblioteki

### Użyte Komponenty UI (Shadcn-Vue)
- `Button` - przyciski
- `Card` - karty kontenerów
- `Table` - tabela przedmiotów (z DataTable)
- `Form` - formularze z walidacją
- `Input` - pola tekstowe
- `Select` - listy rozwijane
- `Badge` - statusy i priorytety
- `Alert` - ostrzeżenia
- `Dialog` - modale potwierdzenia

### Użyte Biblioteki
- `@tanstack/vue-table` - zaawansowana tabela
- `vee-validate` + `zod` - walidacja formularzy
- `vue-sonner` - toast notifications
- `lucide-vue-next` - ikony

### VueUse (@vueuse/core) - Przydatne Composables

#### Storage & Persistence
- **`useStorage`** / **`useLocalStorage`** - automatyczna synchronizacja z localStorage
  - Użycie: W store do automatycznego zapisywania/ładowania danych
  - Zamiast ręcznego `loadFromStorage()` / `saveToStorage()`

#### Search & Filtering
- **`useDebounceFn`** / **`useDebouncedRef`** - debounce dla wyszukiwania
  - Użycie: W `ItemsFilters.vue` i `ContainersListPage.vue` do wyszukiwania
  - Opóźnia wyszukiwanie do momentu zakończenia wpisywania

#### File Operations
- **`useFileDialog`** - dialog wyboru pliku do importu
  - Użycie: W `ContainerDetailPage.vue` do importu JSON
- **`useDownloadFile`** - pobieranie plików
  - Użycie: W `ContainerDetailPage.vue` do eksportu JSON
- **`useClipboard`** - kopiowanie do schowka
  - Użycie: Opcjonalnie do szybkiego kopiowania danych JSON

#### UI State Management
- **`useToggle`** - toggle boolean state
  - Użycie: Do otwierania/zamykania dialogów, rozwijania sekcji
- **`useFocus`** - zarządzanie focusem
  - Użycie: Auto-focus na pierwszym polu w formularzach
- **`useElementVisibility`** - wykrywanie widoczności elementu
  - Użycie: Lazy loading dla dużych list przedmiotów

#### Async Operations
- **`useAsyncState`** - zarządzanie async state
  - Użycie: Do operacji import/export, które mogą trwać dłużej
- **`useTimeoutFn`** - opóźnione wykonanie funkcji
  - Użycie: Auto-save z opóźnieniem, delay dla toast notifications

#### Utilities
- **`useSortable`** - sortowanie list przez drag & drop
  - Użycie: Opcjonalnie do ręcznego sortowania przedmiotów w kontenerze
- **`useMediaQuery`** - responsive breakpoints
  - Użycie: Adaptacja UI na mobile/desktop
- **`useIntersectionObserver`** - infinite scroll / lazy loading
  - Użycie: Dla bardzo długich list przedmiotów
- **`useThrottleFn`** - throttle dla częstych operacji
  - Użycie: Do aktualizacji wagi/gotowości podczas edycji wielu przedmiotów

---

## ✅ Checklist Implementacji

### Fundamenty
- [ ] Struktura katalogów `src/modules/gear/`
- [ ] Typy TypeScript z `TUUID` i `TDateTime`
- [ ] Typ `TGearContainerType` (camelCase)
- [ ] Schematy Zod
- [ ] Store Pinia (tylko storage)
  - [ ] Rozważyć użycie `useStorage` z VueUse dla automatycznej synchronizacji
- [ ] Service (CRUD + logika biznesowa)
- [ ] Composables (używa store + service)
- [ ] Tłumaczenia i18n

### Routing
- [ ] Route dla listy kontenerów
- [ ] Route dla formularza kontenera
- [ ] Route dla widoku kontenera
- [ ] Route dla formularza przedmiotu
- [ ] Route dla widoku przedmiotu
- [ ] Integracja z głównym routerem

### Komponenty
- [ ] ContainersListPage
- [ ] ContainerCard
- [ ] ContainerForm
- [ ] ContainerDetailPage
- [ ] ItemsTable
- [ ] ItemsFilters
- [ ] ItemForm
- [ ] ItemDetail

### Funkcjonalności
- [ ] CRUD kontenerów (przez service)
- [ ] CRUD przedmiotów (przez service)
- [ ] Obliczanie wagi
- [ ] Wskaźnik gotowości
- [ ] Sortowanie i filtrowanie
- [ ] Wyszukiwanie (z `useDebouncedRef` z VueUse)
- [ ] Wykrywanie przeterminowanych
- [ ] Szybkie akcje
- [ ] Import/Export (z `useFileDialog` i `useDownloadFile` z VueUse)

### VueUse Integration
- [ ] `useStorage` / `useLocalStorage` w store
- [ ] `useDebouncedRef` dla wyszukiwania
- [ ] `useFileDialog` dla importu
- [ ] `useDownloadFile` dla eksportu
- [ ] `useFocus` w formularzach
- [ ] `useToggle` dla UI state
- [ ] `useMediaQuery` dla responsive design
- [ ] `useElementVisibility` dla lazy loading (opcjonalnie)

---

## 🚀 Gotowe do Implementacji!

Plan jest kompletny i gotowy do rozpoczęcia implementacji zgodnie z architekturą modułową. Możemy zacząć od Fazy 1 (Fundamenty).
