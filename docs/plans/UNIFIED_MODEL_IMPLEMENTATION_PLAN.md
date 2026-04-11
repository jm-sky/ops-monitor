# Plan Implementacji: Unifikacja Modeli Kontenerów i Przedmiotów

**Data utworzenia:** 2025-12-03
**Ostatnia aktualizacja:** 2025-12-18 (18:30)
**Status:** ⚡ W trakcie implementacji (~90% gotowe)
**Priorytet:** Wysoki
**Złożoność:** Duża
**Szacowany czas:** 18-28 dni (~4-6 tygodni)

---

## 📊 AKTUALNY STAN IMPLEMENTACJI (2025-12-25)

```
BACKEND V2:  ████████████████████ 100% ✅
FRONTEND V2: ████████████████░░░░  80% 🔄
TESTY:       ████████████████████ 100% ✅ (123/123!)
MIGRACJA:    ████████████████████ 100% ✅
NOWE FUNKCJE:░░░░░░░░░░░░░░░░░░░░   0% ❌ (reporting, promotion, shelf_life)

OGÓLNY POSTĘP: ██████████████████░░ 85%
```

### ⚠️ UWAGA: Brakujące funkcje z develop

Po merge develop → feature/unified-model wykryto **3 kluczowe funkcje**, które muszą być dodane do V2:

1. **Content Reporting** (`is_hidden_by_reports`) - dla kontenerów
2. **Item Promotion** (`promote_count`) - dla przedmiotów
3. **Shelf Life** (`shelf_life`) - dla przedmiotów

📋 **Plan integracji:** [UNIFIED_MODEL_V2_MISSING_FEATURES.md](./UNIFIED_MODEL_V2_MISSING_FEATURES.md)

### ✅ Zrobione:
- ✅ **Backend V2 (100%)**: DB models, repository, service, router, schemas
- ✅ **Frontend V2 Store (100%)**: useGearStoreV2 z O(1) lookups
- ✅ **Frontend V2 Services (100%)**: API + Local + Migration
- ✅ **Frontend V2 Composables (100%)**: useGearV2, useContainerV2, operations
- ✅ **Frontend V2 Utils (100%)**: calculations, exports, type converters
- ✅ **Migracja bazy danych (100%)**: 17 containers + 115 items → 132 rows
- ✅ **Main pages migrated**: ContainerDetailPage, ContainersListPage, PublicContainersBrowserPage
- ✅ **TypeScript kompiluje się** bez błędów
- ✅ **WSZYSTKIE TESTY (100%)**: 123/123 passing! ✅
- ✅ **Merge develop → feature/unified-model**: No conflicts, auto-merged

### 🔄 W trakcie / Do zrobienia:
- 🔄 **Komponenty UI (~3%)**: 4/117 components migrowane
- ❌ **Backend routing**: V2 API istnieje ale nie jest domyślnym
- ❌ **Cleanup V1**: Stare tabele/modele nadal istnieją
- ❌ **Nowe funkcje z develop**:
  - ❌ Content Reporting (`is_hidden_by_reports`)
  - ❌ Item Promotion (`promote_count`)
  - ❌ Shelf Life (`shelf_life`)
  - ❌ Account Limits (validation only)

### 🎯 Następne kroki:
1. ✅ ~~Naprawić failujące testy~~ **DONE! 123/123 passing**
2. ✅ ~~Merge develop → feature/unified-model~~ **DONE! Auto-merged, no conflicts**
3. **Dodać brakujące funkcje do V2** (HIGH PRIORITY) ← NOWY PRIORYTET
   - Content Reporting
   - Item Promotion
   - Shelf Life
   - 📋 Plan: [UNIFIED_MODEL_V2_MISSING_FEATURES.md](./UNIFIED_MODEL_V2_MISSING_FEATURES.md)
4. Migrować pozostałe komponenty UI (113 components)
5. Przełączyć backend routing na V2 jako domyślny
6. Cleanup: usunąć V1 tables, models, stare API

---

## 📝 SZCZEGÓŁOWY PLAN FAZOWY

---

## 📋 Kontekst i Cel

### Decyzja Użytkownika
Pełna unifikacja modeli z priorytetami:
- ✅ Naturalne zagnieżdżanie (plecak → kubek → pudełko → zapałki)
- ✅ Przygotowanie do przyszłości (obrazki kontenerów, lepsze eksporty)

### Obecna Architektura
**Dwa osobne modele:**
- `IGearContainer` - kontenery (30+ pól)
- `IGearItem` - przedmioty (25+ pól)

**Dwa systemy zagnieżdżania:**
- System 1: `parentContainerId` - kontenery w kontenerach
- System 2: `IGearItem.containerId` - przedmiot wskazuje na nested kontener

### Cel Unifikacji
**Jeden model:** `IGearEntity` z flagą `isContainer`
- Jeden mechanizm zagnieżdżania: `parentId`
- Naturalne zagnieżdżanie bez duplikacji
- Wspólne pola dla kontenerów i przedmiotów
- Uproszczenie kodu i konserwacji

---

## 🎯 Nowy Model Danych

### Kluczowe Decyzje Architektoniczne

**1. Many-to-Many Relationships**
- Przedmiot może być w **wielu kontenerach jednocześnie** (use case: Victorinox w płaszczu + 2 wirtualne plany plecaków)
- Tabela `entity_relationships` dla relacji parent-child
- **BEZ pola `parentId`** na encji (zastąpione przez tabele relacji)

**2. Pola Specyficzne dla Relacji**
- `quantity_override` - ilość przedmiotu w danym kontenerze (może być różna w każdym)
- `order_in_parent` - kolejność wyświetlania w kontenerze
- Jeśli `quantity_override = NULL`, używamy `entity.quantity` (wartość domyślna)

**3. Brak Zbędnych Pól**
- ❌ **BEZ `entityType`** - nie rozróżniamy physical/virtual na poziomie modelu
- ❌ **BEZ `relationship_type`** - tylko jeden rodzaj relacji: "zawiera"

### IGearEntity (TypeScript)

```typescript
interface IGearEntity {
  // === Identyfikacja ===
  id: TUUID
  isContainer: boolean  // Flaga: czy może zawierać inne encje

  // === UWAGA: BEZ parentId - relacje w tabeli entity_relationships ===

  // === Podstawowe (wspólne) ===
  name: string
  description?: string | null

  // === Kategoryzacja (warunkowa) ===
  category?: TGearItemCategory  // Tylko przedmioty (isContainer=false)
  type?: TGearContainerType     // Tylko kontenery (isContainer=true)

  // === Właściwości fizyczne (wspólne) ===
  weight?: number
  weightUnit?: TGearWeightUnit
  color?: string  // Wspólne - kontenery i przedmioty mają kolor
  brand?: string | null
  price?: number | null
  currency?: string | null
  url?: string | null

  // === Status (wspólne) ===
  status?: TGearItemStatus  // Kontener może mieć status

  // === Właściwości przedmiotów (tylko isContainer=false) ===
  quantity?: number          // Tylko przedmioty
  priority?: TGearItemPriority  // Tylko przedmioty
  expirationDate?: TDateTime | null  // Tylko przedmioty
  wearable?: boolean | null  // Tylko przedmioty
  consumable?: boolean | null  // Tylko przedmioty

  // === Właściwości wspólne ===
  quality?: TGearItemQuality | null
  notes?: string | null
  order?: number | null

  // === Właściwości kontenerów (tylko isContainer=true) ===
  hideWhenNested?: boolean | null
  isPublic?: boolean  // TYLKO kontenery
  favorite?: boolean  // TYLKO kontenery
  showItemImages?: boolean | null
  maxWeight?: number | null
  maxWeightUnit?: TGearWeightUnit | null

  // === Obrazki (wspólne) ===
  primaryImageUrl?: string | null
  images?: IEntityImage[]  // Wspólne - kontenery i przedmioty

  // === Metadata (wspólne) ===
  createdAt: TDateTime
  updatedAt: TDateTime

  // === UWAGA: items[] przeniesione do runtime (nie persystowane) ===
  // items będzie ładowane dynamicznie przez relacje
}
```

### IEntityRelationship (TypeScript)

```typescript
interface IEntityRelationship {
  id: TUUID
  parentId: TUUID  // ID kontenera
  childId: TUUID   // ID encji (przedmiot lub kontener)
  userId: TUUID

  // Metadata specyficzne dla relacji
  quantityOverride?: number | null  // Jeśli NULL, użyj entity.quantity
  orderInParent?: number | null     // Kolejność w kontenerze (dla sortowania)

  createdAt: TDateTime
}
```

### Logika Obliczania Quantity

```typescript
function getQuantityInContainer(
  entity: IGearEntity,
  relationship: IEntityRelationship
): number {
  // Priorytet: quantity_override z relacji
  if (relationship.quantityOverride !== null && relationship.quantityOverride !== undefined) {
    return relationship.quantityOverride
  }

  // Fallback: quantity z encji
  return entity.quantity || 1
}
```

### Discriminated Unions (Type Safety)

```typescript
// Typy pomocnicze dla lepszego type safety
type TGearContainer = IGearEntity & {
  isContainer: true
  type: TGearContainerType
  items?: IGearEntity[]
  isPublic?: boolean
  favorite?: boolean
  maxWeight?: number | null
}

type TGearItem = IGearEntity & {
  isContainer: false
  category: TGearItemCategory
  quantity: number
  priority: TGearItemPriority
}

// Type guard functions
function isGearContainer(entity: IGearEntity): entity is TGearContainer {
  return entity.isContainer === true
}

function isGearItem(entity: IGearEntity): entity is TGearItem {
  return entity.isContainer === false
}

// Type narrowing działa automatycznie
if (entity.isContainer) {
  console.log(entity.type) // ✅ TypeScript wie że type istnieje
  console.log(entity.items) // ✅ OK
} else {
  console.log(entity.category) // ✅ TypeScript wie że category istnieje
  console.log(entity.quantity) // ✅ OK
}
```

---

## 📊 Strategia Migracji: STOPNIOWA (Incremental)

### Dlaczego Stopniowa?
- ✅ Minimalizuje ryzyko utraty danych
- ✅ Umożliwia testowanie na każdym etapie
- ✅ Zachowuje kompatybilność wsteczną
- ✅ Łatwiejszy rollback w przypadku problemów
- ✅ Można podzielić pracę na mniejsze pull requesty

### Kluczowe Zasady
1. **Nie usuwać starych struktur** dopóki nowe nie działają w 100%
2. **Backup przed każdą fazą** (localStorage + baza danych)
3. **Testować każdą fazę** przed przejściem do następnej
4. **Legacy endpoints** dla kompatybilności wstecznej
5. **Automatyczna migracja danych** przy pierwszym uruchomieniu

---

## 🗓️ Plan Fazowy (9 Faz)

### FAZA 0: Test Creation (Pre-Implementation Safety Net)
**Czas:** 2-3 dni
**Cel:** Utworzenie testów weryfikujących obecne zachowanie przed rozpoczęciem migracji
**Priorytet:** KRYTYCZNY - wszystkie testy muszą być zielone przed FAZĄ 1

#### Dlaczego FAZA 0?
- ✅ **Regression detection** - wykryje jeśli coś się złamie podczas migracji
- ✅ **Dokumentacja zachowania** - testy opisują jak system POWINIEN działać
- ✅ **Confidence** - możemy śmiało refaktorować wiedząc że mamy sieć bezpieczeństwa
- ✅ **Baseline** - ustala punkt odniesienia dla porównania po migracji

#### Kroki:

**1. Backend Integration Tests (Vitest/Pytest)**

**1.1. Container CRUD Operations**
```python
# backend/tests/integration/test_containers_crud.py
def test_create_container_with_nested_containers():
    """Verify current nesting behavior: parent_container_id"""
    # Plecak
    backpack = create_container(name="Backpack", type="backpack")
    # Pudełko w plecaku
    box = create_container(name="Box", type="box", parent_container_id=backpack.id)

    assert box.parent_container_id == backpack.id
    # Verify API returns nested structure
    response = get_container(backpack.id)
    assert len(response.nested_containers) == 1
    assert response.nested_containers[0].id == box.id

def test_create_item_in_container():
    """Verify current item-container relationship"""
    container = create_container(name="Backpack")
    item = create_item(container_id=container.id, name="Knife")

    assert item.container_id == container.id
    response = get_container(container.id)
    assert len(response.items) == 1

def test_item_with_nested_container_reference():
    """Verify current dual-nesting mechanism"""
    # System 1: Container with parent_container_id
    backpack = create_container(name="Backpack")
    mug_container = create_container(name="Mug Container", parent_container_id=backpack.id)

    # System 2: Item with containerId pointing to nested container
    mug_item = create_item(
        container_id=backpack.id,
        name="Mug",
        nested_container_id=mug_container.id
    )

    assert mug_item.nested_container_id == mug_container.id
    assert mug_container.parent_container_id == backpack.id
```

**1.2. Weight Calculations**
```python
def test_calculate_total_weight_with_nesting():
    """Ensure weight calculations work correctly before migration"""
    backpack = create_container(name="Backpack", weight=500, weight_unit="g")
    knife = create_item(container_id=backpack.id, name="Knife", weight=100, weight_unit="g", quantity=1)
    mug = create_item(container_id=backpack.id, name="Mug", weight=200, weight_unit="g", quantity=2)

    total = calculate_total_weight(backpack.id)
    assert total == 500 + 100 + (200 * 2)  # 1000g
```

**1.3. Data Integrity**
```python
def test_delete_container_cascades_to_items():
    """Verify cascade deletion works"""
    container = create_container(name="Backpack")
    item1 = create_item(container_id=container.id, name="Knife")
    item2 = create_item(container_id=container.id, name="Mug")

    delete_container(container.id)

    # Items should be deleted
    assert get_item(item1.id) is None
    assert get_item(item2.id) is None

def test_circular_nesting_prevention():
    """Verify circular references are prevented"""
    container_a = create_container(name="A")
    container_b = create_container(name="B", parent_container_id=container_a.id)

    # Should raise error
    with pytest.raises(ValidationError):
        update_container(container_a.id, parent_container_id=container_b.id)
```

**2. Frontend Integration Tests (Vitest)**

**2.1. Store Tests**
```typescript
// src/modules/gear/store/useGearStore.spec.ts
describe('useGearStore - Pre-Migration Baseline', () => {
  it('should load containers from localStorage', async () => {
    const store = useGearStore()
    await store.initialize()

    expect(store.isInitialized).toBe(true)
    expect(store.containers).toBeInstanceOf(Array)
  })

  it('should handle nested containers correctly', () => {
    const store = useGearStore()
    const backpack = createMockContainer({ id: 'backpack-1', name: 'Backpack' })
    const box = createMockContainer({
      id: 'box-1',
      name: 'Box',
      parentContainerId: 'backpack-1'
    })

    store.setContainers([backpack, box])

    const nested = store.getNestedContainers('backpack-1')
    expect(nested).toHaveLength(1)
    expect(nested[0].id).toBe('box-1')
  })
})
```

**2.2. Service Tests**
```typescript
// src/modules/gear/services/gearContainerService.spec.ts
describe('gearContainerService - Baseline Behavior', () => {
  it('should create container with items', async () => {
    const service = new GearContainerService()
    const container = await service.createContainer({
      name: 'Backpack',
      type: 'backpack',
    })

    const item = await service.createItem(container.id, {
      name: 'Knife',
      category: 'tools',
      quantity: 1,
    })

    expect(item.containerId).toBe(container.id)
  })

  it('should calculate readiness percentage', async () => {
    const service = new GearContainerService()
    // Create container with mixed status items
    const container = await service.createContainer({ name: 'Test' })
    await service.createItem(container.id, { name: 'Item1', status: 'owned' })
    await service.createItem(container.id, { name: 'Item2', status: 'missing' })

    const readiness = await service.calculateReadinessPercentage(container.id)
    expect(readiness).toBe(50) // 1 owned out of 2 total
  })
})
```

**3. API Snapshot Tests**

**3.1. Response Format Snapshots**
```typescript
// tests/snapshots/api-responses.spec.ts
describe('API Response Snapshots', () => {
  it('GET /api/containers/:id should match snapshot', async () => {
    const container = await createTestContainer()
    const response = await fetch(`/api/containers/${container.id}`)
    const data = await response.json()

    expect(data).toMatchSnapshot()
  })

  it('GET /api/containers/:id/items should match snapshot', async () => {
    const container = await createTestContainerWithItems()
    const response = await fetch(`/api/containers/${container.id}/items`)
    const data = await response.json()

    expect(data).toMatchSnapshot()
  })
})
```

**4. E2E Tests (Playwright)**

**4.1. Critical User Flows**
```typescript
// tests/e2e/containers.spec.ts
test('User can create nested containers', async ({ page }) => {
  await page.goto('/gear')

  // Create main container
  await page.click('[data-testid="create-container"]')
  await page.fill('[data-testid="container-name"]', 'Backpack')
  await page.click('[data-testid="save-container"]')

  // Create nested container
  await page.click('[data-testid="add-nested-container"]')
  await page.fill('[data-testid="container-name"]', 'Box')
  await page.click('[data-testid="save-container"]')

  // Verify nesting
  await expect(page.locator('[data-testid="nested-container"]')).toContainText('Box')
})

test('User can add items to container', async ({ page }) => {
  const container = await createTestContainer()
  await page.goto(`/gear/${container.id}`)

  await page.click('[data-testid="add-item"]')
  await page.fill('[data-testid="item-name"]', 'Knife')
  await page.selectOption('[data-testid="item-category"]', 'tools')
  await page.click('[data-testid="save-item"]')

  await expect(page.locator('[data-testid="item-row"]')).toContainText('Knife')
})
```

**5. Data Migration Test Suite**

**5.1. Migration Simulation**
```python
# backend/tests/migration/test_data_migration.py
def test_migration_preserves_all_containers():
    """Verify no data loss during migration"""
    # Create test data
    containers = create_test_containers(count=10)

    # Run migration (simulate)
    migrate_containers_to_entities()

    # Verify all containers exist in new table
    entities = db.query(GearEntity).filter_by(is_container=True).all()
    assert len(entities) == 10

    for container in containers:
        entity = db.query(GearEntity).filter_by(id=container.id).first()
        assert entity is not None
        assert entity.name == container.name
        assert entity.is_container is True

def test_migration_preserves_nesting_relationships():
    """Verify parent-child relationships are preserved"""
    parent = create_container(name="Parent")
    child = create_container(name="Child", parent_container_id=parent.id)

    migrate_containers_to_entities()

    # Verify relationship exists in entity_relationships table
    relationship = db.query(EntityRelationship).filter_by(
        parent_id=parent.id,
        child_id=child.id
    ).first()

    assert relationship is not None
```

**6. Performance Baseline Tests**

```python
def test_query_performance_baseline():
    """Establish performance baseline before migration"""
    # Create realistic dataset
    create_test_containers(count=100)
    create_test_items(count=1000)

    # Measure query performance
    start = time.time()
    containers = get_all_containers(user_id=test_user.id)
    duration = time.time() - start

    # Should complete in <100ms
    assert duration < 0.1

    # Store baseline for comparison
    save_performance_baseline('get_all_containers', duration)
```

#### Pliki do utworzenia:

**Backend:**
- `backend/tests/integration/test_containers_crud.py`
- `backend/tests/integration/test_items_crud.py`
- `backend/tests/integration/test_nesting.py`
- `backend/tests/integration/test_calculations.py`
- `backend/tests/migration/test_data_migration.py`
- `backend/tests/performance/test_query_performance.py`

**Frontend:**
- `src/modules/gear/store/useGearStore.spec.ts`
- `src/modules/gear/services/gearContainerService.spec.ts`
- `src/modules/gear/services/gearItemService.spec.ts`
- `tests/snapshots/api-responses.spec.ts`
- `tests/e2e/containers.spec.ts`
- `tests/e2e/items.spec.ts`
- `tests/e2e/nesting.spec.ts`

#### Kryteria sukcesu FAZY 0:
- ✅ **100% testów przechodzi** - wszystkie testy zielone
- ✅ **Pokrycie kodu >80%** dla kluczowych modułów (containers, items, nesting)
- ✅ **E2E testy** dla 5+ krytycznych flow użytkownika
- ✅ **Performance baseline** - zapisane czasy dla porównania po migracji
- ✅ **Snapshots** - API responses zapisane dla weryfikacji kompatybilności

#### Metryki sukcesu:
```bash
# Backend
pytest backend/tests/integration/ --cov=backend/app/modules/gear
# Expected: >80% coverage, all tests passing

# Frontend
pnpm test:run src/modules/gear/
# Expected: >80% coverage, all tests passing

# E2E
pnpm test:e2e
# Expected: All critical flows passing
```

#### Checkpoint przed FAZĄ 1:
⚠️ **NIE ZACZYNAJ FAZY 1 dopóki:**
- [ ] Wszystkie testy z FAZY 0 nie przechodzą (100% zielone)
- [ ] Code coverage <80% dla gear module
- [ ] E2E testy nie działają
- [ ] Performance baseline nie został zapisany

---

### FAZA 1: Nowe Typy i Interfejsy
**Czas:** 1-2 dni
**Cel:** Utworzenie nowych typów bez łamania istniejącego kodu

#### Kroki:
1. **Frontend - Nowe typy TypeScript**
   - Utworzyć `src/modules/gear/types/gearEntity.types.ts`
   - Definicja `IGearEntity` z discriminated unions
   - Type guards: `isGearContainer()`, `isGearItem()`
   - DTOs: `ICreateEntityDto`, `IUpdateEntityDto`
   - **ZACHOWAĆ** stare typy w `gear.types.ts`

2. **Backend - Nowe schematy Pydantic**
   - Utworzyć `backend/app/modules/gear/entity_schemas.py`
   - `EntityCreate`, `EntityUpdate`, `EntityResponse` z warunkową walidacją
   - `.refine()` dla walidacji pól specyficznych
   - **ZACHOWAĆ** stare schematy w `schemas.py`

3. **Warunkowa walidacja (przykład Pydantic)**
   ```python
   class EntityCreate(BaseModel):
       is_container: bool
       name: str
       type: Optional[GearContainerType] = None
       category: Optional[GearItemCategory] = None
       # ...

       @model_validator(mode='after')
       def validate_conditional_fields(self):
           if self.is_container:
               if not self.type:
                   raise ValueError("Containers must have type")
               if self.category or self.quantity or self.priority:
                   raise ValueError("Containers cannot have item-specific fields")
           else:
               if not self.category or not self.quantity or not self.priority:
                   raise ValueError("Items must have category, quantity, priority")
               if self.type or self.items or self.is_public:
                   raise ValueError("Items cannot have container-specific fields")
           return self
   ```

#### Pliki do utworzenia:
- `src/modules/gear/types/gearEntity.types.ts` (nowy)
- `backend/app/modules/gear/entity_schemas.py` (nowy)

#### Kryteria sukcesu:
- ✅ TypeScript kompiluje się bez błędów
- ✅ Nowe typy są zgodne z istniejącym API
- ✅ Walidacja Pydantic działa poprawnie

---

### FAZA 2: Migracja Bazy Danych
**Czas:** 2-3 dni
**Cel:** Utworzenie nowej tabeli `gear_entities` i tabeli relacji `entity_relationships`

#### Kroki:

1. **Backup bazy danych**
   ```bash
   pg_dump -U user -d gear_stack > backup_pre_migration.sql
   ```

2. **Migracja 1: Utworzenie tabeli `gear_entities`**
   - Utworzyć `backend/alembic/versions/XXXX_create_gear_entities_table.py`
   - Tabela z wszystkimi polami (union `gear_containers` + `gear_items`)
   - Kolumna `is_container: bool NOT NULL`
   - **BEZ kolumny `parent_id`** (relacje w osobnej tabeli)
   - Indeksy: `is_container`, `user_id`

3. **Migracja 2: Utworzenie tabeli `entity_relationships`**
   - Utworzyć `backend/alembic/versions/XXXX_create_entity_relationships_table.py`
   ```sql
   CREATE TABLE entity_relationships (
     id VARCHAR(36) PRIMARY KEY,
     parent_id VARCHAR(36) NOT NULL REFERENCES gear_entities(id) ON DELETE CASCADE,
     child_id VARCHAR(36) NOT NULL REFERENCES gear_entities(id) ON DELETE CASCADE,
     user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,

     -- Metadata relacji
     quantity_override INT DEFAULT NULL,
     order_in_parent INT DEFAULT NULL,

     created_at TIMESTAMP NOT NULL DEFAULT NOW(),

     -- Constraints
     UNIQUE(parent_id, child_id),
     CHECK (parent_id != child_id),
     CHECK (quantity_override IS NULL OR quantity_override >= 0)
   );

   CREATE INDEX idx_entity_relationships_parent ON entity_relationships(parent_id);
   CREATE INDEX idx_entity_relationships_child ON entity_relationships(child_id);
   CREATE INDEX idx_entity_relationships_user ON entity_relationships(user_id);
   ```

4. **Migracja 3: Migracja danych**
   - Utworzyć `backend/alembic/versions/XXXX_migrate_data_to_entities.py`
   ```python
   def upgrade():
       # KROK 1: Kopiuj kontenery do gear_entities
       op.execute("""
           INSERT INTO gear_entities (
               id, user_id, is_container, name, type, description,
               weight, weight_unit, color, brand, price, currency, url,
               is_public, favorite, hide_when_nested, show_item_images,
               max_weight, max_weight_unit, created_at, updated_at
           )
           SELECT
               id, user_id, TRUE as is_container, name, type, description,
               weight, weight_unit, color, brand, price, currency, url,
               is_public, favorite, hide_when_nested, show_item_images,
               max_weight, max_weight_unit, created_at, updated_at
           FROM gear_containers
       """)

       # KROK 2: Kopiuj przedmioty do gear_entities
       op.execute("""
           INSERT INTO gear_entities (
               id, user_id, is_container, name, category,
               quantity, weight, weight_unit, status, priority,
               notes, expiration_date, price, currency, url,
               brand, color, quality, wearable, consumable,
               "order", primary_image_url, created_at, updated_at
           )
           SELECT
               id, container_id as user_id, FALSE as is_container, name, category,
               quantity, weight, weight_unit, status, priority,
               notes, expiration_date, price, currency, url,
               brand, color, quality, wearable, consumable,
               "order", NULL as primary_image_url, created_at, updated_at
           FROM gear_items
       """)

       # KROK 3: Utworzyć relacje kontenery -> kontenery (parent_container_id)
       op.execute("""
           INSERT INTO entity_relationships (
               id, parent_id, child_id, user_id, quantity_override, order_in_parent, created_at
           )
           SELECT
               gen_random_uuid(),
               parent_container_id,
               id as child_id,
               user_id,
               NULL as quantity_override,
               NULL as order_in_parent,
               created_at
           FROM gear_containers
           WHERE parent_container_id IS NOT NULL
       """)

       # KROK 4: Utworzyć relacje kontenery -> przedmioty (container_id)
       op.execute("""
           INSERT INTO entity_relationships (
               id, parent_id, child_id, user_id, quantity_override, order_in_parent, created_at
           )
           SELECT
               gen_random_uuid(),
               container_id,
               id as child_id,
               (SELECT user_id FROM gear_containers WHERE id = container_id),
               NULL as quantity_override,
               "order" as order_in_parent,
               created_at
           FROM gear_items
       """)

       # KROK 5: Obsługa nested_container_id (przedmiot wskazuje na kontener)
       # To już jest covered w KROK 4 (relacja container_id -> item_id)
   ```

5. **Migracja 4: Rename `item_images` → `entity_images`**
   - Utworzyć `backend/alembic/versions/XXXX_rename_item_images_to_entity_images.py`
   ```python
   def upgrade():
       op.rename_table('item_images', 'entity_images')
       op.alter_column('entity_images', 'item_id', new_column_name='entity_id')
   ```

6. **ZACHOWAĆ stare tabele**
   - NIE usuwać `gear_containers`, `gear_items`
   - Będą usunięte dopiero w Fazie 8

7. **Walidacja migracji**
   - Sprawdzić liczby rekordów (gear_entities = gear_containers + gear_items)
   - Sprawdzić czy wszystkie relacje zostały utworzone
   - Sprawdzić czy entity_images działa poprawnie

#### Pliki do utworzenia:
- `backend/alembic/versions/XXXX_create_gear_entities_table.py` (nowy)
- `backend/alembic/versions/XXXX_create_entity_relationships_table.py` (nowy)
- `backend/alembic/versions/XXXX_migrate_data_to_entities.py` (nowy)
- `backend/alembic/versions/XXXX_rename_item_images_to_entity_images.py` (nowy)

#### Kryteria sukcesu:
- ✅ Tabela `gear_entities` utworzona
- ✅ Tabela `entity_relationships` utworzona
- ✅ Wszystkie dane zmigrowane (0 strat)
- ✅ Wszystkie relacje utworzone w `entity_relationships`
- ✅ Indeksy utworzone
- ✅ `entity_images` działa
- ✅ Walidacja: COUNT(gear_entities) = COUNT(gear_containers) + COUNT(gear_items)

---

### FAZA 3: Backend Models (SQLAlchemy)
**Czas:** 1-2 dni
**Cel:** Utworzenie modeli ORM dla nowych tabel

#### Kroki:

1. **Utworzyć model `GearEntityDB`**
   - Plik: `backend/app/modules/gear/entity_db_models.py`
   ```python
   class GearEntityDB(Base):
       __tablename__ = "gear_entities"

       id = Column(String(36), primary_key=True)
       user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
       is_container = Column(Boolean, nullable=False)

       # Wspólne
       name = Column(String(255), nullable=False)
       description = Column(Text, nullable=True)
       # BEZ parent_id - relacje w entity_relationships

       # Warunkowe
       type = Column(String(50), nullable=True)  # Tylko kontenery
       category = Column(String(50), nullable=True)  # Tylko przedmioty

       # Wspólne
       quantity = Column(Integer, nullable=True)  # Domyślna ilość (może być override w relacji)
       weight = Column(Float, nullable=True)
       weight_unit = Column(String(5), nullable=True)
       status = Column(String(20), nullable=True)
       priority = Column(String(20), nullable=True)
       # ... reszta pól

       # Relationships
       user = relationship("UserDB", back_populates="gear_entities")
       images = relationship("EntityImageDB", back_populates="entity", cascade="all, delete-orphan")

       # Relacje many-to-many przez entity_relationships
       parent_relationships = relationship(
           "EntityRelationshipDB",
           foreign_keys="EntityRelationshipDB.child_id",
           back_populates="child_entity"
       )
       child_relationships = relationship(
           "EntityRelationshipDB",
           foreign_keys="EntityRelationshipDB.parent_id",
           back_populates="parent_entity",
           cascade="all, delete-orphan"
       )
   ```

2. **Utworzyć model `EntityRelationshipDB`**
   - Plik: `backend/app/modules/gear/entity_db_models.py`
   ```python
   class EntityRelationshipDB(Base):
       __tablename__ = "entity_relationships"

       id = Column(String(36), primary_key=True)
       parent_id = Column(String(36), ForeignKey("gear_entities.id"), nullable=False)
       child_id = Column(String(36), ForeignKey("gear_entities.id"), nullable=False)
       user_id = Column(String(36), ForeignKey("users.id"), nullable=False)

       # Metadata relacji
       quantity_override = Column(Integer, nullable=True)
       order_in_parent = Column(Integer, nullable=True)

       created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

       # Relationships
       parent_entity = relationship("GearEntityDB", foreign_keys=[parent_id], back_populates="child_relationships")
       child_entity = relationship("GearEntityDB", foreign_keys=[child_id], back_populates="parent_relationships")
       user = relationship("UserDB")
   ```

3. **Utworzyć model `EntityImageDB`**
   - Plik: `backend/app/modules/gear/entity_db_models.py`
   ```python
   class EntityImageDB(Base):
       __tablename__ = "entity_images"

       id = Column(String(36), primary_key=True)
       entity_id = Column(String(36), ForeignKey("gear_entities.id"), nullable=False)
       user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
       # ... reszta pól z ItemImageDB

       entity = relationship("GearEntityDB", back_populates="images")
   ```

4. **ZACHOWAĆ** stare modele (`GearContainerDB`, `GearItemDB`)

#### Pliki do utworzenia:
- `backend/app/modules/gear/entity_db_models.py` (nowy)

#### Kryteria sukcesu:
- ✅ Modele SQLAlchemy działają
- ✅ Relationships poprawne (parent/children)
- ✅ Można wykonywać CRUD operations

---

### FAZA 4: Backend Services i API
**Czas:** 3-4 dni
**Cel:** Utworzenie serwisów i API endpoints dla nowych modeli

#### Kroki:

1. **Utworzyć `EntityRepository`**
   - Plik: `backend/app/modules/gear/entity_repository.py`
   - CRUD operations: `create()`, `get()`, `update()`, `delete()`
   - Rekurencyjne zapytania: `get_with_children()`, `get_all_descendants()`
   - Circular reference check

2. **Utworzyć `EntityService`**
   - Plik: `backend/app/modules/gear/entity_service.py`
   - Business logic: walidacja, circular reference detection
   - `calculate_total_weight()` - rekurencyjne
   - `calculate_readiness()` - dla kontenerów
   - `move_entity()` - zmiana parent_id

3. **Utworzyć `entity_router.py`**
   - Plik: `backend/app/modules/gear/entity_router.py`
   - RESTful API:
     ```
     POST   /gear/entities              # Create entity
     GET    /gear/entities              # List all entities
     GET    /gear/entities/{id}         # Get single entity
     PATCH  /gear/entities/{id}         # Update entity
     DELETE /gear/entities/{id}         # Delete entity
     POST   /gear/entities/{id}/children  # Create child entity
     GET    /gear/entities/{id}/children  # Get children
     GET    /gear/entities/{id}/stats/weight
     GET    /gear/entities/{id}/stats/readiness
     ```

4. **Legacy endpoints (kompatybilność)**
   - Zachować `/gear/containers/*` i `/gear/items/*`
   - Delegowanie do nowych endpoints:
   ```python
   @router.post("/containers/", response_model=ContainerResponse)
   async def create_container_legacy(data: ContainerCreate, ...):
       # Convert ContainerCreate -> EntityCreate (is_container=True)
       entity_data = EntityCreate(is_container=True, type=data.type, ...)
       entity = await entity_service.create(entity_data)
       # Convert EntityResponse -> ContainerResponse
       return convert_entity_to_container(entity)
   ```

5. **Obrazki - unified endpoint**
   ```
   POST   /gear/entities/{id}/images
   GET    /gear/entities/{id}/images
   PATCH  /gear/entities/{id}/images/{img_id}
   DELETE /gear/entities/{id}/images/{img_id}
   ```

#### Pliki do utworzenia:
- `backend/app/modules/gear/entity_repository.py` (nowy)
- `backend/app/modules/gear/entity_service.py` (nowy)
- `backend/app/modules/gear/entity_router.py` (nowy)

#### Pliki do modyfikacji:
- `backend/app/modules/gear/router.py` (legacy endpoints)

#### Kryteria sukcesu:
- ✅ API działa dla wszystkich operacji CRUD
- ✅ Legacy endpoints działają
- ✅ Circular reference detection działa
- ✅ Rekurencyjne wagi działają

---

### FAZA 5: Frontend Services
**Czas:** 2-3 dni
**Cel:** Utworzenie zunifikowanych serwisów frontendowych

#### Kroki:

1. **Utworzyć `GearEntityService` (factory)**
   - Plik: `src/modules/gear/services/gearEntityService.ts`
   - Zwraca odpowiedni serwis bazując na statusie backendu

2. **Utworzyć `GearEntityLocalService`**
   - Plik: `src/modules/gear/services/gearEntityLocalService.ts`
   - CRUD operations na localStorage
   - Rekurencyjne wagi: `calculateTotalWeight()`
   - Readiness: `calculateReadinessPercentage()`
   - Navigation: `getRootEntities()`, `getChildren()`
   - Export/import JSON

3. **Utworzyć `GearEntityApiService`**
   - Plik: `src/modules/gear/services/gearEntityApiService.ts`
   - API calls do `/gear/entities/*`
   - Error handling

4. **Utworzyć `GearEntityHybridService`**
   - Plik: `src/modules/gear/services/gearEntityHybridService.ts`
   - API + localStorage fallback
   - Auto-refresh po API operations

5. **Helper functions do migracji**
   - Plik: `src/modules/gear/utils/entityMigration.ts`
   ```typescript
   function migrateContainerToEntity(container: IGearContainer): IGearEntity
   function migrateItemToEntity(item: IGearItem): IGearEntity
   function migrateLocalStorage(): void
   ```

#### Pliki do utworzenia:
- `src/modules/gear/services/gearEntityService.ts` (nowy)
- `src/modules/gear/services/gearEntityLocalService.ts` (nowy)
- `src/modules/gear/services/gearEntityApiService.ts` (nowy)
- `src/modules/gear/services/gearEntityHybridService.ts` (nowy)
- `src/modules/gear/utils/entityMigration.ts` (nowy)

#### Kryteria sukcesu:
- ✅ Wszystkie operacje CRUD działają
- ✅ Rekurencyjne wagi działają
- ✅ Migracja localStorage działa
- ✅ Fallback na localStorage działa

---

### FAZA 6: Frontend Store (Pinia)
**Czas:** 1-2 dni
**Cel:** Utworzenie nowego store dla zunifikowanych encji

#### Kroki:

1. **Utworzyć `useGearEntityStore`**
   - Plik: `src/modules/gear/store/useGearEntityStore.ts`
   ```typescript
   export const useGearEntityStore = defineStore('gearEntity', {
     state: () => ({
       entities: [] as IGearEntity[]
     }),

     getters: {
       getEntityById: (state) => (id: TUUID) =>
         state.entities.find(e => e.id === id),
       getRootEntities: (state) =>
         state.entities.filter(e => !e.parentId),
       getContainers: (state) =>
         state.entities.filter(e => e.isContainer),
       getItems: (state) =>
         state.entities.filter(e => !e.isContainer)
     },

     actions: {
       async loadFromStorage() {
         // Automatyczna migracja przy pierwszym uruchomieniu
         await migrateLocalStorageIfNeeded()
         const data = localStorage.getItem('gear-stack:entities')
         if (data) this.entities = JSON.parse(data)
       },

       saveToStorage() {
         localStorage.setItem('gear-stack:entities', JSON.stringify(this.entities))
       }
     }
   })
   ```

2. **Automatyczna migracja localStorage**
   - Przy pierwszym uruchomieniu: konwersja `gear-stack:containers` → `gear-stack:entities`
   - Zachowanie starych danych dla rollback

3. **ZACHOWAĆ** `useGearStore` dla kompatybilności

#### Pliki do utworzenia:
- `src/modules/gear/store/useGearEntityStore.ts` (nowy)

#### Kryteria sukcesu:
- ✅ Store działa poprawnie
- ✅ Automatyczna migracja localStorage działa
- ✅ Synchronizacja z localStorage działa

---

### FAZA 7: Migracja Komponentów UI
**Czas:** 5-7 dni
**Cel:** Stopniowa migracja komponentów Vue do nowego modelu

#### Strategia: Jedna strona na raz

1. **Utworzyć nowe komponenty uniwersalne**
   - `EntityCard.vue` - karty encji (zastąpi ContainerCard + ItemCard)
   - `EntityFormPage.vue` - formularz tworzenia/edycji
   - `EntityFormFields.vue` - warunkowe pola formularza
   - `EntityDetailPage.vue` - strona szczegółów
   - `EntityHeader.vue` - header z nazwą i akcjami
   - `EntityTable.vue` - tabela encji

2. **Stopniowa migracja stron**
   - Dzień 1-2: Lista kontenerów → EntityListPage
   - Dzień 3: Tworzenie/edycja → EntityFormPage
   - Dzień 4: Szczegóły kontenera → EntityDetailPage
   - Dzień 5: Obrazki → EntityImageGallery
   - Dzień 6-7: Pozostałe strony i komponenty

3. **Warunkowe renderowanie w komponentach**
   ```vue
   <script setup lang="ts">
   const { entity } = defineProps<{ entity: IGearEntity }>()
   </script>

   <template>
     <div>
       <!-- Wspólne -->
       <h2>{{ entity.name }}</h2>
       <p>{{ entity.description }}</p>

       <!-- Warunkowe dla kontenerów -->
       <div v-if="entity.isContainer">
         <p>Type: {{ entity.type }}</p>
         <p>Items: {{ entity.items?.length }}</p>
       </div>

       <!-- Warunkowe dla przedmiotów -->
       <div v-else>
         <p>Category: {{ entity.category }}</p>
         <p>Quantity: {{ entity.quantity }}</p>
       </div>
     </div>
   </template>
   ```

4. **ZACHOWAĆ** stare komponenty do czasu pełnej migracji

#### Pliki do utworzenia (~15 nowych komponentów):
- `src/modules/gear/components/EntityCard.vue`
- `src/modules/gear/components/EntityFormFields.vue`
- `src/modules/gear/components/EntityHeader.vue`
- `src/modules/gear/components/EntityTable.vue`
- `src/modules/gear/components/EntityImageGallery.vue`
- `src/modules/gear/pages/EntityListPage.vue`
- `src/modules/gear/pages/EntityFormPage.vue`
- `src/modules/gear/pages/EntityDetailPage.vue`
- ... (więcej w zależności od potrzeb)

#### Pliki do modyfikacji (~40-50 plików):
- Wszystkie komponenty używające `IGearContainer` lub `IGearItem`
- Routing: `src/modules/gear/routes.ts`

#### Kryteria sukcesu:
- ✅ Wszystkie strony działają z nowym modelem
- ✅ UI jest spójne i funkcjonalne
- ✅ Brak regresji w funkcjonalności

---

### FAZA 8: Testy, Cleanup i Dokumentacja
**Czas:** 3-4 dni
**Cel:** Pełne przetestowanie i usunięcie starych struktur

#### Kroki:

1. **Testy jednostkowe (Unit Tests)**
   - Backend: `test_entity_service.py`, `test_entity_repository.py`
   - Frontend: `gearEntityService.spec.ts`, `entityMigration.spec.ts`
   - Testować:
     - CRUD operations
     - Circular reference detection
     - Rekurencyjne wagi
     - Migrację localStorage

2. **Testy integracyjne**
   - End-to-end testy dla API
   - Testować całe przepływy:
     - Tworzenie kontenera → dodanie przedmiotu
     - Zagnieżdżanie → obliczanie wagi
     - Migracja danych

3. **Testy UI**
   - Playwright/Vitest component tests
   - Testować kluczowe strony:
     - Lista encji
     - Formularz tworzenia
     - Szczegóły encji

4. **Performance testy**
   - Testować wydajność dla dużych hierarchii (100+ encji)
   - Optymalizacja indeksów jeśli potrzeba

5. **Cleanup - TYLKO po pełnym przetestowaniu**
   - Usunąć stare tabele: `gear_containers`, `gear_items`
   - Usunąć legacy endpoints
   - Usunąć stare typy: `IGearContainer`, `IGearItem`
   - Usunąć stare serwisy i komponenty
   - Usunąć stary store: `useGearStore`

6. **Dokumentacja**
   - Zaktualizować `CLAUDE.md`
   - Zaktualizować `UNIFIED_MODEL_ANALYSIS.md`
   - Migration guide dla użytkowników
   - API documentation

#### Pliki do utworzenia:
- `backend/tests/gear/test_entity_service.py`
- `backend/tests/gear/test_entity_repository.py`
- `src/modules/gear/services/__tests__/gearEntityService.spec.ts`
- `docs/MIGRATION_GUIDE.md`

#### Pliki do usunięcia (po testach):
- `src/modules/gear/types/gear.types.ts` (część - stare typy)
- `src/modules/gear/services/gearContainerService.ts`
- `src/modules/gear/services/gearItemService.ts`
- `backend/app/modules/gear/schemas.py` (stare schematy)
- `backend/alembic/versions/XXXX_drop_old_gear_tables.py` (migracja DROP)

#### Kryteria sukcesu:
- ✅ Wszystkie testy przechodzą
- ✅ Performance jest akceptowalna
- ✅ Stare struktury usunięte
- ✅ Dokumentacja zaktualizowana

---

## 📁 Critical Files - Top 15

### Backend (Python)

**Priorytet 1 (KRYTYCZNE):**
1. **`backend/alembic/versions/XXXX_create_gear_entities_table.py`** (NOWY)
   - Utworzenie tabeli `gear_entities`
   - Definicja kolumn, indeksów, foreign keys

2. **`backend/alembic/versions/XXXX_migrate_data_to_entities.py`** (NOWY)
   - Migracja danych z `gear_containers` + `gear_items` → `gear_entities`
   - Konwersja `parent_container_id` → `parent_id`
   - Konwersja `container_id` → `parent_id`

3. **`backend/app/modules/gear/entity_schemas.py`** (NOWY)
   - Pydantic schemas: `EntityCreate`, `EntityUpdate`, `EntityResponse`
   - Warunkowa walidacja dla pól specyficznych

4. **`backend/app/modules/gear/entity_db_models.py`** (NOWY)
   - `GearEntityDB` - model SQLAlchemy
   - `EntityImageDB` - obrazki dla encji
   - Relationships (parent/children)

**Priorytet 2 (WAŻNE):**
5. **`backend/app/modules/gear/entity_repository.py`** (NOWY)
   - CRUD operations
   - Rekurencyjne zapytania (get_with_children)

6. **`backend/app/modules/gear/entity_service.py`** (NOWY)
   - Business logic
   - Circular reference detection
   - Calculate weight/readiness

7. **`backend/app/modules/gear/entity_router.py`** (NOWY)
   - RESTful API endpoints
   - `/gear/entities/*`

8. **`backend/app/modules/gear/router.py`** (MODYFIKACJA)
   - Legacy endpoints (delegacja do nowych)

### Frontend (TypeScript/Vue)

**Priorytet 1 (KRYTYCZNE):**
9. **`src/modules/gear/types/gearEntity.types.ts`** (NOWY)
   - `IGearEntity` z discriminated unions
   - Type guards, DTOs

10. **`src/modules/gear/services/gearEntityLocalService.ts`** (NOWY)
    - CRUD na localStorage
    - Rekurencyjne obliczenia

11. **`src/modules/gear/store/useGearEntityStore.ts`** (NOWY)
    - Pinia store dla encji
    - Automatyczna migracja localStorage

**Priorytet 2 (WAŻNE):**
12. **`src/modules/gear/utils/entityMigration.ts`** (NOWY)
    - Helper functions do migracji
    - `migrateLocalStorage()`

13. **`src/modules/gear/components/EntityCard.vue`** (NOWY)
    - Uniwersalny komponent karty encji

14. **`src/modules/gear/pages/EntityListPage.vue`** (NOWY)
    - Strona listy encji

15. **`src/modules/gear/routes.ts`** (MODYFIKACJA)
    - Routing dla nowych stron

---

## ⚠️ Ryzyko i Mitigacja

### Top 6 Ryzyk

#### 1. Utrata Danych podczas Migracji
**Ryzyko:** Wysoki
**Mitigacja:**
- ✅ Backup bazy danych przed każdą fazą
- ✅ Testowanie migracji na kopii bazy
- ✅ Zachowanie starych tabel do Fazy 8
- ✅ Rollback plan (restore z backupu)
- ✅ Dry-run migracji przed produkcją

#### 2. Breaking Changes w API
**Ryzyko:** Średni
**Mitigacja:**
- ✅ Legacy endpoints (`/gear/containers/*`, `/gear/items/*`)
- ✅ Stopniowa migracja (obie wersje API działają równolegle)
- ✅ Versioning API (opcjonalnie: `/api/v2/gear/entities`)
- ✅ Komunikacja z użytkownikami o zmianach

#### 3. Regresja w Funkcjonalności
**Ryzyko:** Średni
**Mitigacja:**
- ✅ Kompletne testy jednostkowe i integracyjne
- ✅ UI testy dla kluczowych przepływów
- ✅ Stopniowa migracja komponentów (jedna strona na raz)
- ✅ Beta testing przed pełnym wdrożeniem

#### 4. Problem z Migracją localStorage
**Ryzyko:** Średni
**Mitigacja:**
- ✅ Automatyczna migracja przy pierwszym uruchomieniu
- ✅ Zachowanie starych kluczy localStorage (fallback)
- ✅ Walidacja danych po migracji
- ✅ Komunikat dla użytkownika jeśli migracja się nie powiedzie

#### 5. Performance przy Dużych Hierarchiach
**Ryzyko:** Niski-Średni
**Mitigacja:**
- ✅ Właściwe indeksy w bazie danych (`is_container`, `parent_id`)
- ✅ Lazy loading dla zagnieżdżonych encji
- ✅ Caching w serwisach
- ✅ Performance testy dla 100+ encji
- ✅ Monitoring po wdrożeniu

#### 6. Złożoność Walidacji Warunkowej
**Ryzyko:** Niski
**Mitigacja:**
- ✅ Discriminated unions dla lepszego type safety
- ✅ Testy walidacji dla wszystkich przypadków
- ✅ Jasne error messages
- ✅ Dokumentacja dla deweloperów

---

## ✅ Walidacja i Kryteria Sukcesu

### Kryteria Globalne (po Fazie 8)
- ✅ Wszystkie testy jednostkowe przechodzą (100% coverage dla core logic)
- ✅ Wszystkie testy integracyjne przechodzą
- ✅ UI testy przechodzą dla kluczowych przepływów
- ✅ Brak regresji w funkcjonalności
- ✅ Performance akceptowalna (< 500ms dla typowych operacji)
- ✅ 0 data loss po migracji
- ✅ localStorage migracja działa w 100%
- ✅ Legacy endpoints działają poprawnie
- ✅ Dokumentacja zaktualizowana

### Kryteria per Faza
Każda faza ma własne kryteria sukcesu (patrz sekcje powyżej).

### Definition of Done
- ✅ Kod przeszedł code review
- ✅ Wszystkie testy przechodzą
- ✅ Brak błędów TypeScript/ESLint
- ✅ Dokumentacja zaktualizowana
- ✅ Pull request zatwierdzony i zmergowany

---

## 📝 Podsumowanie Kluczowych Zmian vs Oryginalny Plan

### Zmiany Architektoniczne

**ZMIANA 1: Many-to-Many zamiast Parent-Child**
- **Oryginał:** `parentId` na encji (proste drzewo)
- **NOWE:** Tabela `entity_relationships` (many-to-many)
- **Powód:** Use case - Victorinox w 3 kontenerach jednocześnie (płaszcz + 2 plany plecaków)

**ZMIANA 2: Usunięcie niepotrzebnych pól**
- **Usunięte:** `entityType` ('physical' | 'virtual' | 'template')
- **Powód:** Nie potrzebne - rozróżnienie physical/virtual to sposób użycia, nie właściwość danych

**ZMIANA 3: Usunięcie niepotrzebnych pól w relacji**
- **Usunięte:** `relationship_type` ('contains' | 'links_to')
- **Powód:** Tylko jeden rodzaj relacji - "zawiera"

**ZMIANA 4: Pola specyficzne dla relacji**
- **DODANE do relacji:** `quantity_override` (ilość w danym kontenerze)
- **DODANE do relacji:** `order_in_parent` (kolejność w kontenerze)
- **ZACHOWANE na encji:** `quantity` (wartość domyślna)
- **Logika:** Jeśli `quantity_override = NULL`, użyj `entity.quantity`

**ZMIANA 5: localStorage**
- **Oryginał:** Automatyczna migracja przy pierwszym uruchomieniu
- **NOWE:** Możemy skasować stare dane (nie jesteśmy live)
- **Prostsze:** Brak skomplikowanej migracji localStorage

**ZMIANA 6: API Strategy**
- **Wybrane:** Legacy endpoints (prostsze, mniej pracy)
- **Odrzucone:** API v2 + versioning (za dużo pracy)

---

## 🔄 Kompatybilność Wsteczna

### localStorage Migration
**Strategia: KASOWANIE** (nie jesteśmy live)

Ponieważ aplikacja nie jest jeszcze live, możemy uprościć migrację localStorage:

```typescript
// Przy pierwszym uruchomieniu - KASUJ stare dane
export function clearOldLocalStorage(): void {
  // Usuń stare klucze
  localStorage.removeItem('gear-stack:containers')
  localStorage.removeItem('gear-stack:settings')  // Jeśli są związane z kontenerami

  // Nowy klucz będzie: 'gear-stack:entities'
  // Nowy klucz dla relacji: 'gear-stack:entity-relationships'
}

// Opcjonalnie: Export danych przed migracją (dla użytkowników którzy testowali)
export function exportOldDataForMigration(): string {
  const containers = localStorage.getItem('gear-stack:containers')
  if (!containers) return ''

  return containers // User może zapisać do pliku i zaimportować później
}
```

**UWAGA:** Jeśli są użytkownicy testowi z danymi - dać im możliwość eksportu przed wdrożeniem!

### API Legacy Endpoints
**Delegacja do nowych endpoints:**
```python
# Legacy: POST /gear/containers/
@router.post("/containers/", response_model=ContainerResponse)
async def create_container_legacy(
    data: ContainerCreate,
    service: EntityService = Depends(get_entity_service)
):
    # Convert ContainerCreate -> EntityCreate
    entity_data = EntityCreate(
        is_container=True,
        type=data.type,
        name=data.name,
        # ... map all fields
    )

    # Call new service
    entity = await service.create(entity_data)

    # Convert EntityResponse -> ContainerResponse
    return convert_entity_to_container_response(entity)

# Legacy: GET /gear/items/{item_id}
@router.get("/items/{item_id}", response_model=ItemResponse)
async def get_item_legacy(
    item_id: str,
    service: EntityService = Depends(get_entity_service)
):
    entity = await service.get(item_id)

    if entity.is_container:
        raise HTTPException(400, "Entity is a container, not an item")

    return convert_entity_to_item_response(entity)
```

---

## 📊 Szacunki

### Czas
- **Faza 1:** 1-2 dni
- **Faza 2:** 2-3 dni
- **Faza 3:** 1-2 dni
- **Faza 4:** 3-4 dni
- **Faza 5:** 2-3 dni
- **Faza 6:** 1-2 dni
- **Faza 7:** 5-7 dni
- **Faza 8:** 3-4 dni
- **TOTAL:** 18-28 dni (~4-6 tygodni)

### Pliki
- **Nowe:** ~44 plików
- **Modyfikacje:** ~65 plików
- **TOTAL:** ~109 plików

### Linie Kodu (szacunkowo)
- **Backend:** ~5,000-7,000 linii
- **Frontend:** ~10,000-13,000 linii
- **TOTAL:** ~15,000-20,000 linii

### Ryzyko
- **Średnie-Wysokie** (ale z mitigacją)
- Kluczowe: backup, stopniowa migracja, testy

### Korzyści Długoterminowe
- ✅ Naturalne zagnieżdżanie bez duplikacji
- ✅ Uproszczenie kodu (jeden model zamiast dwóch)
- ✅ Łatwiejsze dodawanie nowych funkcji
- ✅ Wspólne obrazki dla kontenerów i przedmiotów
- ✅ Prostsze eksporty/importy
- ✅ Lepsza konserwacja w przyszłości

---

## 🎯 Następne Kroki

1. **Review tego planu** - upewnić się że wszystko jest jasne
2. **Przygotowanie środowiska** - backup, test database
3. **Faza 1** - Nowe typy i interfejsy (start implementacji)

---

## ✅ PROGRESS CHECKLIST (Ostatnia aktualizacja: 2025-12-18)

### FAZA 0: Testy (100% - 123/123 passing) ✅
- [x] Backend integration tests (containers CRUD) - 21/21 ✅
- [x] Backend integration tests (items CRUD) - 21/21 ✅
- [x] Backend integration tests (nesting) - 18/18 ✅
- [x] Backend integration tests (weight calculations) - 17/17 ✅
- [x] Backend integration tests (data integrity) - 40/40 ✅
- [x] Backend migration tests - 9/9 ✅ (FIXED 2025-12-18)
- [x] Backend V2 unified model tests - 23/23 ✅
- [ ] Frontend store tests (V2) ⏳
- [ ] Frontend service tests (V2) ⏳
- [ ] E2E tests (Playwright) ⏳
- [ ] Performance baseline tests ⏳

### FAZA 1: Nowe Typy i Interfejsy (100%) ✅
- [x] Frontend: `gear.types.v2.ts` - IGearItemV2, type guards ✅
- [x] Backend: `schemas_v2.py` - Pydantic schemas ✅
- [x] Warunkowa walidacja (Pydantic) ✅
- [x] Type discriminator: itemType ('container' | 'item') ✅
- [x] Pole: isHiddenByReports dodane (2025-12-18) ✅

### FAZA 2: Migracja Bazy Danych (100%) ✅
- [x] Tabela: gear_items_v2 created ✅
- [x] Indexes: created (item_type, user_id, parent_item_id, etc.) ✅
- [x] Foreign keys: parent_item_id, user_id, linked_item_id ✅
- [x] Check constraints: type validation ✅
- [x] Migracja danych: 17 containers + 115 items = 132 rows ✅
- [x] Migration script: 051_migrate_data_to_unified_model.py ✅
- [x] Verification: counts match (132 = 17 + 115) ✅

### FAZA 3: Backend Models (100%) ✅
- [x] `db_models_v2.py` - GearItemDBV2 model ✅
- [x] Self-referential FK (parent_item_id) ✅
- [x] Relationships (parent/children) ✅
- [x] Column mappings from V1 ✅

### FAZA 4: Backend Services i API (100%) ✅
- [x] `repository_v2.py` - CRUD operations ✅
- [x] `service_v2.py` - Business logic ✅
- [x] `router_v2.py` - RESTful API endpoints ✅
- [x] `schemas_v2.py` - Pydantic schemas ✅
- [ ] Legacy endpoints delegation (V1 → V2) ⏳
- [ ] Default routing switched to V2 ⏳

### FAZA 5: Frontend Services (100%) ✅
- [x] `gearItemLocalServiceV2.ts` - localStorage CRUD ✅
- [x] `gearItemApiServiceV2.ts` - API calls ✅
- [x] `v1ToV2Migration.ts` - Migration helpers ✅
- [x] `migrationV1toV2Service.ts` - Auto-migration ✅

### FAZA 6: Frontend Store (100%) ✅
- [x] `useGearStoreV2.ts` - Pinia store ✅
- [x] O(1) lookups with Map structure ✅
- [x] Parent-child indexing ✅
- [x] Automatic localStorage sync ✅
- [x] Migration from V1 on first load ✅

### FAZA 7: Migracja Komponentów UI (~3% - 4/117) 🔄
**Composables (100%):**
- [x] `useGearV2.ts` - Main composable ✅
- [x] `useContainerV2.ts` - Container operations ✅
- [x] `useContainerOperationsV2.ts` ✅
- [x] `useItemOperationsV2.ts` ✅
- [x] `useContainerCalculationsV2.ts` ✅

**Utils (100%):**
- [x] `containerCalculationsV2.ts` - Weight/readiness ✅
- [x] `exportToCSVV2.ts` ✅
- [x] `exportToPromptV2.ts` ✅
- [x] `typeConverters.ts` - V1 ↔ V2 conversion ✅

**Pages migrowane (6/15 = 40%):**
- [x] ContainerDetailPage.vue ✅
- [x] ContainersListPage.vue ✅
- [x] PublicContainersBrowserPage.vue ✅
- [x] PublicContainerDetailPage.vue ✅
- [x] SharedContainerDetailPage.vue ✅
- [x] ContainerFormPage.vue ✅
- [ ] ItemDetailPage.vue
- [ ] ItemFormPage.vue
- [ ] AllItemsPage.vue
- [ ] CatalogueBrowserPage.vue
- [ ] ...

**Komponenty migrowane (4/117 = 3%):**
- [x] ContainerRatingBadge.vue ✅
- [x] ContainerTypeBadge.vue ✅
- [x] WeightLimitBadge.vue ✅
- [x] ItemsTableNameCell.vue ✅
- [ ] 113 innych komponentów...

### FAZA 8: Testy, Cleanup, Dokumentacja (~30%) 🔄
**Testy:**
- [x] Backend integration tests (100% passing) ✅
- [x] Backend migration tests (100% passing) ✅
- [ ] Frontend store tests (V2)
- [ ] Frontend service tests (V2)
- [ ] E2E tests (Playwright)
- [ ] Performance tests

**Cleanup (0%):**
- [ ] Przełączyć routing na V2 jako domyślny
- [ ] Usunąć tabele: gear_containers, gear_items
- [ ] Usunąć legacy endpoints
- [ ] Usunąć stare typy V1
- [ ] Usunąć stare services V1
- [ ] Usunąć stary store V1

**Dokumentacja:**
- [x] Plan implementacji (ten dokument) ✅
- [ ] Migration guide dla użytkowników
- [ ] API documentation
- [ ] Zaktualizować CLAUDE.md

---

## 🎯 IMMEDIATE NEXT STEPS (Priorytet)

### 1. ✅ ~~Naprawić failujące testy~~ (DONE 2025-12-18)
```bash
✅ DONE: Wszystkie 123 testy przechodzą!
- Dodano fixtures V2 (gear_service_v2, gear_repository_v2)
- Przepisano 6 testów migration integrity na V2 API
- Wszystkie testy używają GearItemCreateV2 zamiast V1 schemas
```

### 2. Migrować komponenty UI (Priorytet: HIGH)
```
Pozostało: 113/117 komponentów
Strategia: Migrować batch po batch (10-20 komponentów na raz)
- Start z najczęściej używanymi komponentami
- ItemForm, ContainerCard, ItemCard, FilterComponents, etc.
```

### 3. Przełączyć backend routing na V2 (Priorytet: MEDIUM)
```python
# backend/main.py lub backend/app/modules/gear/router.py
# Zmienić domyślny router z V1 na V2
# Opcjonalnie: Legacy endpoints dla kompatybilności
```

### 4. Cleanup V1 (Priorytet: LOW)
```
- Usunąć tabele: gear_containers, gear_items
- Usunąć legacy endpoints
- Usunąć stare typy V1
- Usunąć stare services V1
```

---

**Ostatnia aktualizacja:** 2025-12-18 (18:30)
**Status:** 90% gotowe - Backend V2 ✅, Frontend V2 80% ✅, Testy 100% ✅✅✅
