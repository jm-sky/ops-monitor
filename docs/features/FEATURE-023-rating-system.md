# FEATURE-023: Rating System (System Ocen)

**Status:** 🔄 Planned  
**Priority:** Medium  
**Category:** 📊 User Feedback / ⭐ Ratings  
**Related:** ROADMAP.md - System ocen

---

## 📋 Overview

Implementacja systemu ocen dla przedmiotów i kontenerów:
- Usunięcie pola "półka cenowa / jakość" (`quality`) z przedmiotów
- Dodanie oceny autora (1-5) dla przedmiotów i kontenerów
- Dodanie ocen użytkowników (1-5) jako relacji w bazie danych dla przedmiotów i kontenerów

---

## 🎯 Goals

1. **Usunięcie pola `quality`** z przedmiotów (backend + frontend)
2. **Dodanie `authorRating`** (1-5) do przedmiotów i kontenerów
3. **Dodanie relacji `userRatings`** w bazie danych:
   - Tabela `item_ratings` dla ocen przedmiotów
   - Tabela `container_ratings` dla ocen kontenerów
   - Każdy użytkownik może ocenić przedmiot/kontener raz (upsert)
   - Wyświetlanie średniej oceny użytkowników

---

## 🔍 Current State

### Pole `quality` (do usunięcia)

**Backend:**
- `backend/app/modules/gear/schemas.py`: `GearItemQuality = Literal["low", "medium", "high"]`
- `backend/app/modules/gear/db_models.py`: `quality: Mapped[str | None]` w `GearItemDB`
- Używane w schemas: `ItemCreate`, `ItemUpdate`, `ItemResponse`

**Frontend:**
- `src/modules/gear/types/gear.types.ts`: `TGearItemQuality = 'low' | 'medium' | 'high'`
- `src/modules/gear/components/ItemFormFields.vue`: Formularz z polem quality
- `src/modules/gear/pages/ItemDetailPage.vue`: Wyświetlanie quality
- `src/modules/gear/pages/PublicItemDetailPage.vue`: Wyświetlanie quality
- `src/modules/gear/i18n/index.ts`: Tłumaczenia dla quality
- `src/modules/gear/services/`: Używane w serwisach (API, localStorage, migration)

### Rating system (do dodania)

**Brak implementacji** - wymaga pełnej implementacji od zera.

---

## 📝 Implementation Plan

### Phase 1: Backend - Database Models & Migrations

#### Step 1.1: Utworzenie modeli dla ocen użytkowników

**File:** `backend/app/modules/gear/db_models.py`

Dodaj nowe modele:

```python
class ItemRatingDB(Base):
    """SQLAlchemy model for user ratings of gear items.
    
    Attributes:
        id: Unique identifier (ULID format, 36 chars)
        item_id: Rated item ID
        user_id: User who gave the rating
        rating: Rating value (1-5)
        created_at: Rating timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = "item_ratings"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    item_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("gear_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False
    )
    
    # Relationships
    item: Mapped["GearItemDB"] = relationship("GearItemDB", back_populates="ratings")
    user: Mapped["UserDB"] = relationship("UserDB", foreign_keys=[user_id])
    
    # Unique constraint: one rating per user per item
    __table_args__ = (
        UniqueConstraint('item_id', 'user_id', name='uq_item_rating_user'),
    )


class ContainerRatingDB(Base):
    """SQLAlchemy model for user ratings of gear containers.
    
    Attributes:
        id: Unique identifier (ULID format, 36 chars)
        container_id: Rated container ID
        user_id: User who gave the rating
        rating: Rating value (1-5)
        created_at: Rating timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = "container_ratings"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    container_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("gear_containers.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False
    )
    
    # Relationships
    container: Mapped["GearContainerDB"] = relationship("GearContainerDB", back_populates="ratings")
    user: Mapped["UserDB"] = relationship("UserDB", foreign_keys=[user_id])
    
    # Unique constraint: one rating per user per container
    __table_args__ = (
        UniqueConstraint('container_id', 'user_id', name='uq_container_rating_user'),
    )
```

Dodaj relacje do istniejących modeli:

```python
# W GearItemDB
ratings: Mapped[list["ItemRatingDB"]] = relationship(
    "ItemRatingDB",
    back_populates="item",
    cascade="all, delete-orphan"
)

# W GearContainerDB
ratings: Mapped[list["ContainerRatingDB"]] = relationship(
    "ContainerRatingDB",
    back_populates="container",
    cascade="all, delete-orphan"
)
```

#### Step 1.2: Dodanie pola `author_rating` do modeli

**File:** `backend/app/modules/gear/db_models.py`

```python
# W GearItemDB
author_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-5

# W GearContainerDB
author_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-5
```

#### Step 1.3: Usunięcie pola `quality` z GearItemDB

**File:** `backend/app/modules/gear/db_models.py`

Usuń linię:
```python
quality: Mapped[str | None] = mapped_column(String(20), nullable=True)
```

#### Step 1.4: Utworzenie migracji

**File:** `backend/app/migrations/versions/XXXX_add_ratings_remove_quality.py`

```python
"""Add ratings system and remove quality field

Revision ID: XXXX
Revises: YYYY
Create Date: 2024-XX-XX XX:XX:XX.XXXXXX
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'XXXX'
down_revision = 'YYYY'
branch_labels = None
depends_on = None

def upgrade():
    # Create item_ratings table
    op.create_table(
        'item_ratings',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('item_id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['item_id'], ['gear_items.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('item_id', 'user_id', name='uq_item_rating_user')
    )
    op.create_index(op.f('ix_item_ratings_item_id'), 'item_ratings', ['item_id'])
    op.create_index(op.f('ix_item_ratings_user_id'), 'item_ratings', ['user_id'])
    
    # Create container_ratings table
    op.create_table(
        'container_ratings',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('container_id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['container_id'], ['gear_containers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('container_id', 'user_id', name='uq_container_rating_user')
    )
    op.create_index(op.f('ix_container_ratings_container_id'), 'container_ratings', ['container_id'])
    op.create_index(op.f('ix_container_ratings_user_id'), 'container_ratings', ['user_id'])
    
    # Add author_rating to gear_items
    op.add_column('gear_items', sa.Column('author_rating', sa.Integer(), nullable=True))
    
    # Add author_rating to gear_containers
    op.add_column('gear_containers', sa.Column('author_rating', sa.Integer(), nullable=True))
    
    # Remove quality column from gear_items
    op.drop_column('gear_items', 'quality')

def downgrade():
    # Restore quality column
    op.add_column('gear_items', sa.Column('quality', sa.String(20), nullable=True))
    
    # Remove author_rating columns
    op.drop_column('gear_containers', 'author_rating')
    op.drop_column('gear_items', 'author_rating')
    
    # Drop rating tables
    op.drop_table('container_ratings')
    op.drop_table('item_ratings')
```

---

### Phase 2: Backend - Schemas & Validation

#### Step 2.1: Aktualizacja schemas - usunięcie `quality`, dodanie `authorRating`

**File:** `backend/app/modules/gear/schemas.py`

Usuń:
```python
GearItemQuality = Literal["low", "medium", "high"]
```

Dodaj:
```python
# Rating type (1-5)
RatingValue = int  # Constrained to 1-5 in validation
```

Zaktualizuj schemas:

```python
# W ItemCreate
author_rating: int | None = Field(None, ge=1, le=5, alias="authorRating")

# W ItemUpdate
author_rating: int | None = Field(None, ge=1, le=5, alias="authorRating")

# W ItemResponse
author_rating: int | None = Field(None, alias="authorRating")
user_rating: int | None = Field(None, alias="userRating")  # Current user's rating
average_rating: float | None = Field(None, alias="averageRating")  # Average of all user ratings
rating_count: int = Field(default=0, alias="ratingCount")  # Number of user ratings

# W ContainerCreate
author_rating: int | None = Field(None, ge=1, le=5, alias="authorRating")

# W ContainerUpdate
author_rating: int | None = Field(None, ge=1, le=5, alias="authorRating")

# W ContainerResponse
author_rating: int | None = Field(None, alias="authorRating")
user_rating: int | None = Field(None, alias="userRating")  # Current user's rating
average_rating: float | None = Field(None, alias="averageRating")  # Average of all user ratings
rating_count: int = Field(default=0, alias="ratingCount")  # Number of user ratings
```

Usuń `quality` z:
- `ItemCreate`
- `ItemUpdate`
- `ItemResponse`

#### Step 2.2: Dodanie schemas dla rating endpoints

**File:** `backend/app/modules/gear/schemas.py`

```python
class ItemRatingCreate(BaseModel):
    """Schema for creating/updating item rating."""
    
    rating: int = Field(..., ge=1, le=5, description="Rating value from 1 to 5")
    
    model_config = {"populate_by_name": True}


class ContainerRatingCreate(BaseModel):
    """Schema for creating/updating container rating."""
    
    rating: int = Field(..., ge=1, le=5, description="Rating value from 1 to 5")
    
    model_config = {"populate_by_name": True}
```

---

### Phase 3: Backend - Repositories & Services

#### Step 3.1: Dodanie metod do repository

**File:** `backend/app/modules/gear/repository.py`

Dodaj metody do `GearRepository`:

```python
async def get_item_rating(self, item_id: str, user_id: str) -> ItemRatingDB | None:
    """Get user's rating for an item."""
    result = await self.session.execute(
        select(ItemRatingDB)
        .where(ItemRatingDB.item_id == item_id)
        .where(ItemRatingDB.user_id == user_id)
    )
    return result.scalar_one_or_none()

async def upsert_item_rating(self, item_id: str, user_id: str, rating: int) -> ItemRatingDB:
    """Create or update user's rating for an item."""
    existing = await self.get_item_rating(item_id, user_id)
    
    if existing:
        existing.rating = rating
        existing.updated_at = datetime.now(UTC)
        await self.session.flush()
        return existing
    
    new_rating = ItemRatingDB(
        id=generate_ulid(),
        item_id=item_id,
        user_id=user_id,
        rating=rating,
    )
    self.session.add(new_rating)
    await self.session.flush()
    return new_rating

async def get_item_average_rating(self, item_id: str) -> float | None:
    """Calculate average rating for an item."""
    result = await self.session.execute(
        select(func.avg(ItemRatingDB.rating))
        .where(ItemRatingDB.item_id == item_id)
    )
    avg = result.scalar()
    return float(avg) if avg is not None else None

async def get_item_rating_count(self, item_id: str) -> int:
    """Get number of ratings for an item."""
    result = await self.session.execute(
        select(func.count(ItemRatingDB.id))
        .where(ItemRatingDB.item_id == item_id)
    )
    return result.scalar() or 0

# Similar methods for containers:
async def get_container_rating(self, container_id: str, user_id: str) -> ContainerRatingDB | None
async def upsert_container_rating(self, container_id: str, user_id: str, rating: int) -> ContainerRatingDB
async def get_container_average_rating(self, container_id: str) -> float | None
async def get_container_rating_count(self, container_id: str) -> int
```

#### Step 3.2: Aktualizacja metod pobierania przedmiotów/kontenerów

**File:** `backend/app/modules/gear/repository.py`

Zaktualizuj `get_item` i `get_container` aby uwzględniały ratingi:

```python
async def get_item(self, item_id: str, user_id: str | None = None) -> GearItemDB | None:
    """Get item with ratings if user_id provided."""
    item = await self.session.get(GearItemDB, item_id)
    if item and user_id:
        # Load user's rating
        user_rating = await self.get_item_rating(item_id, user_id)
        # Calculate average rating
        avg_rating = await self.get_item_average_rating(item_id)
        rating_count = await self.get_item_rating_count(item_id)
        # Attach as attributes (will be serialized in response)
        item._user_rating = user_rating.rating if user_rating else None
        item._average_rating = avg_rating
        item._rating_count = rating_count
    return item
```

---

### Phase 4: Backend - API Endpoints

#### Step 4.1: Dodanie endpointów dla ratingów

**File:** `backend/app/modules/gear/router.py`

```python
@router.post("/items/{item_id}/rating", response_model=dict)
async def rate_item(
    item_id: str,
    rating_data: ItemRatingCreate,
    current_user: CurrentUser,
    repository: GearRepository = Depends(get_repository),
):
    """Rate an item (create or update rating)."""
    # Verify item exists
    item = await repository.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Upsert rating
    rating = await repository.upsert_item_rating(
        item_id=item_id,
        user_id=current_user.id,
        rating=rating_data.rating
    )
    
    # Get updated stats
    avg_rating = await repository.get_item_average_rating(item_id)
    rating_count = await repository.get_item_rating_count(item_id)
    
    return {
        "rating": rating.rating,
        "averageRating": float(avg_rating) if avg_rating else None,
        "ratingCount": rating_count
    }

@router.delete("/items/{item_id}/rating")
async def delete_item_rating(
    item_id: str,
    current_user: CurrentUser,
    repository: GearRepository = Depends(get_repository),
):
    """Delete user's rating for an item."""
    rating = await repository.get_item_rating(item_id, current_user.id)
    if rating:
        await repository.session.delete(rating)
        await repository.session.commit()
    
    return {"message": "Rating deleted"}

# Similar endpoints for containers:
@router.post("/containers/{container_id}/rating", response_model=dict)
@router.delete("/containers/{container_id}/rating")
```

#### Step 4.2: Aktualizacja istniejących endpointów

**File:** `backend/app/modules/gear/router.py`

Zaktualizuj endpointy `get_item` i `get_container` aby uwzględniały ratingi w odpowiedzi (używając `_user_rating`, `_average_rating`, `_rating_count` z repository).

---

### Phase 5: Frontend - Types & Interfaces

#### Step 5.1: Aktualizacja typów - usunięcie `quality`, dodanie ratingów

**File:** `src/modules/gear/types/gear.types.ts`

Usuń:
```typescript
export type TGearItemQuality = 'low' | 'medium' | 'high'
```

Dodaj:
```typescript
// Rating type (1-5)
export type TRatingValue = 1 | 2 | 3 | 4 | 5
```

Zaktualizuj interfejsy:

```typescript
// W IGearItem
authorRating?: TRatingValue | null
userRating?: TRatingValue | null  // Current user's rating
averageRating?: number | null  // Average of all user ratings
ratingCount?: number  // Number of user ratings

// Usuń:
quality?: TGearItemQuality | null

// W IGearContainer
authorRating?: TRatingValue | null
userRating?: TRatingValue | null
averageRating?: number | null
ratingCount?: number

// W ICreateItemDto
authorRating?: TRatingValue | null
// Usuń: quality?: TGearItemQuality | null

// W IUpdateItemDto
authorRating?: TRatingValue | null
// Usuń: quality?: TGearItemQuality | null

// W ICreateContainerDto
authorRating?: TRatingValue | null

// W IUpdateContainerDto
authorRating?: TRatingValue | null
```

---

### Phase 6: Frontend - Components & UI

#### Step 6.1: Utworzenie komponentu Rating

**File:** `src/modules/gear/components/RatingDisplay.vue`

Komponent do wyświetlania oceny (gwiazdki lub liczba):

```vue
<script setup lang="ts">
import { computed } from 'vue'
import type { TRatingValue } from '../types/gear.types'

interface Props {
  rating?: TRatingValue | number | null
  showStars?: boolean
  showNumber?: boolean
  size?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  showStars: true,
  showNumber: false,
  size: 'md'
})

const displayRating = computed(() => {
  if (props.rating == null) return null
  return Math.round(props.rating * 10) / 10  // Round to 1 decimal
})
</script>

<template>
  <div v-if="displayRating != null" class="flex items-center gap-1">
    <div v-if="showStars" class="flex">
      <!-- Star icons -->
    </div>
    <span v-if="showNumber" class="text-sm font-medium">{{ displayRating }}</span>
  </div>
</template>
```

#### Step 6.2: Utworzenie komponentu RatingInput

**File:** `src/modules/gear/components/RatingInput.vue`

Komponent do wprowadzania oceny (gwiazdki interaktywne):

```vue
<script setup lang="ts">
import { ref } from 'vue'
import type { TRatingValue } from '../types/gear.types'

interface Props {
  modelValue?: TRatingValue | null
  disabled?: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: TRatingValue | null]
}>()

const hoveredRating = ref<TRatingValue | null>(null)

function setRating(rating: TRatingValue) {
  if (props.disabled) return
  emit('update:modelValue', rating === props.modelValue ? null : rating)
}
</script>

<template>
  <div class="flex gap-1">
    <!-- Interactive star buttons -->
  </div>
</template>
```

#### Step 6.3: Usunięcie pola `quality` z formularzy

**File:** `src/modules/gear/components/ItemFormFields.vue`

Usuń sekcję z polem `quality` (linie ~280-290).

#### Step 6.4: Dodanie pola `authorRating` do formularzy

**File:** `src/modules/gear/components/ItemFormFields.vue`

Dodaj pole `authorRating` używając `RatingInput`:

```vue
<FormField v-slot="{ value, handleChange }" name="authorRating">
  <FormItem>
    <FormLabel :label="$t('gear.item.authorRating')" />
    <FormControl>
      <RatingInput :model-value="value" @update:model-value="handleChange" />
    </FormControl>
  </FormItem>
</FormField>
```

#### Step 6.5: Aktualizacja stron szczegółów

**File:** `src/modules/gear/pages/ItemDetailPage.vue`

- Usuń sekcję wyświetlającą `quality` (linie ~260-266)
- Dodaj wyświetlanie `authorRating` i `averageRating` z `ratingCount`

**File:** `src/modules/gear/pages/PublicItemDetailPage.vue`

- Podobne zmiany jak w `ItemDetailPage.vue`
- Dodaj możliwość oceniania przez użytkowników (jeśli zalogowani)

#### Step 6.6: Aktualizacja strony szczegółów kontenera

**File:** `src/modules/gear/pages/ContainerDetailPage.vue` (lub odpowiedni plik)

- Dodaj wyświetlanie `authorRating` i `averageRating` z `ratingCount`
- Dodaj możliwość oceniania przez użytkowników (jeśli publiczny kontener)

---

### Phase 7: Frontend - Services & API

#### Step 7.1: Aktualizacja serwisów - usunięcie `quality`

**Files:**
- `src/modules/gear/services/gearItemApiService.ts`
- `src/modules/gear/services/gearItemLocalService.ts`
- `src/modules/gear/services/gearContainerApiService.ts`
- `src/modules/gear/services/gearContainerLocalService.ts`

Usuń wszystkie referencje do `quality` i dodaj obsługę `authorRating`.

#### Step 7.2: Dodanie metod API dla ratingów

**File:** `src/modules/gear/services/gearItemApiService.ts`

```typescript
async rateItem(itemId: string, rating: TRatingValue): Promise<{
  rating: TRatingValue
  averageRating: number | null
  ratingCount: number
}> {
  const response = await apiClient.post(`/gear/items/${itemId}/rating`, { rating })
  return response.data
}

async deleteItemRating(itemId: string): Promise<void> {
  await apiClient.delete(`/gear/items/${itemId}/rating`)
}
```

**File:** `src/modules/gear/services/gearContainerApiService.ts`

Podobne metody dla kontenerów.

#### Step 7.3: Aktualizacja walidacji

**File:** `src/modules/gear/utils/validation.ts`

Usuń:
```typescript
quality: z.enum(['low', 'medium', 'high']).optional(),
```

Dodaj:
```typescript
authorRating: z.number().int().min(1).max(5).nullable().optional(),
```

---

### Phase 8: Frontend - i18n

#### Step 8.1: Aktualizacja tłumaczeń

**File:** `src/modules/gear/i18n/index.ts`

Usuń:
```typescript
quality: 'Quality / Price Tier',
qualities: {
  low: 'Low',
  medium: 'Medium',
  high: 'High'
}
```

Dodaj:
```typescript
authorRating: 'Author Rating',
userRating: 'Your Rating',
averageRating: 'Average Rating',
ratingCount: 'ratings',
rateItem: 'Rate Item',
rateContainer: 'Rate Container',
deleteRating: 'Delete Rating',
```

---

### Phase 9: Data Migration & Cleanup

#### Step 9.1: Aktualizacja migracji danych

**File:** `src/modules/gear/services/dataMigrationService.ts`

Usuń mapowanie `quality` podczas migracji z localStorage do API.

#### Step 9.2: Aktualizacja przykładowych danych

**File:** `src/modules/gear/services/exampleSets.ts`

Usuń wszystkie referencje do `quality` i dodaj przykładowe `authorRating`.

**File:** `src/modules/gear/services/sampleSetGenerator.ts`

Podobne zmiany.

#### Step 9.3: Aktualizacja importu/eksportu Markdown

**File:** `src/modules/gear/services/markdownImportService.ts`

Usuń parsowanie `quality` z markdown i dodaj parsowanie `authorRating`.

**File:** `src/modules/gear/utils/exportToPrompt.ts`

Usuń eksport `quality` i dodaj eksport `authorRating`.

---

## 📁 Files to Modify

### Backend

- `backend/app/modules/gear/db_models.py` - Modele, relacje, usunięcie `quality`, dodanie `author_rating`
- `backend/app/modules/gear/schemas.py` - Schemas, walidacja, usunięcie `quality`, dodanie ratingów
- `backend/app/modules/gear/repository.py` - Metody dla ratingów
- `backend/app/modules/gear/router.py` - Endpointy dla ratingów
- `backend/app/migrations/versions/XXXX_add_ratings_remove_quality.py` - Migracja bazy danych

### Frontend

- `src/modules/gear/types/gear.types.ts` - Typy, usunięcie `TGearItemQuality`, dodanie `TRatingValue`
- `src/modules/gear/components/ItemFormFields.vue` - Usunięcie pola `quality`, dodanie `authorRating`
- `src/modules/gear/components/RatingDisplay.vue` - **NOWY** - Komponent wyświetlania oceny
- `src/modules/gear/components/RatingInput.vue` - **NOWY** - Komponent wprowadzania oceny
- `src/modules/gear/pages/ItemDetailPage.vue` - UI dla ratingów
- `src/modules/gear/pages/PublicItemDetailPage.vue` - UI dla ratingów
- `src/modules/gear/pages/ContainerDetailPage.vue` - UI dla ratingów kontenerów
- `src/modules/gear/services/gearItemApiService.ts` - API metody dla ratingów
- `src/modules/gear/services/gearContainerApiService.ts` - API metody dla ratingów
- `src/modules/gear/services/gearItemLocalService.ts` - Usunięcie `quality`
- `src/modules/gear/services/gearContainerLocalService.ts` - Dodanie `authorRating`
- `src/modules/gear/services/dataMigrationService.ts` - Migracja danych
- `src/modules/gear/services/exampleSets.ts` - Przykładowe dane
- `src/modules/gear/services/sampleSetGenerator.ts` - Generator danych
- `src/modules/gear/services/markdownImportService.ts` - Import markdown
- `src/modules/gear/utils/exportToPrompt.ts` - Eksport markdown
- `src/modules/gear/utils/validation.ts` - Walidacja
- `src/modules/gear/i18n/index.ts` - Tłumaczenia

---

## ✅ Acceptance Criteria

### Backend

- [ ] Tabele `item_ratings` i `container_ratings` utworzone z odpowiednimi constraintami
- [ ] Pole `author_rating` dodane do `gear_items` i `gear_containers`
- [ ] Pole `quality` usunięte z `gear_items`
- [ ] Endpointy POST/DELETE dla ratingów przedmiotów działają
- [ ] Endpointy POST/DELETE dla ratingów kontenerów działają
- [ ] Endpointy GET przedmiotów/kontenerów zwracają `userRating`, `averageRating`, `ratingCount`
- [ ] Walidacja ratingów (1-5) działa poprawnie
- [ ] Unique constraint zapobiega duplikatom ratingów (jeden użytkownik = jedna ocena)

### Frontend

- [ ] Pole `quality` usunięte ze wszystkich formularzy i widoków
- [ ] Pole `authorRating` dostępne w formularzach przedmiotów i kontenerów
- [ ] Komponent `RatingDisplay` wyświetla oceny poprawnie
- [ ] Komponent `RatingInput` pozwala na wprowadzanie ocen (1-5)
- [ ] Strony szczegółów wyświetlają `authorRating` i `averageRating` z `ratingCount`
- [ ] Użytkownicy mogą oceniać publiczne przedmioty/kontenery
- [ ] Użytkownicy mogą aktualizować swoje oceny
- [ ] Użytkownicy mogą usuwać swoje oceny
- [ ] Migracja danych z localStorage do API działa (bez `quality`)
- [ ] Import/eksport markdown działa z `authorRating` zamiast `quality`
- [ ] Tłumaczenia zaktualizowane (usunięte `quality`, dodane ratingi)

### Testing

- [ ] Testy jednostkowe dla repository methods (ratingi)
- [ ] Testy integracyjne dla endpointów ratingów
- [ ] Testy E2E dla oceniania przedmiotów/kontenerów
- [ ] Testy migracji danych (usunięcie `quality`)

---

## 🔗 Related Features

- Public containers/items (FEATURE-014) - Ratingi będą szczególnie przydatne dla publicznych zasobów
- User profiles - Możliwość wyświetlania średnich ocen użytkownika

---

## 📝 Notes

- **Rating scale:** 1-5 (gwiazdki)
- **Author rating:** Ocenę autora może ustawić tylko właściciel przedmiotu/kontenera
- **User ratings:** Każdy użytkownik może ocenić przedmiot/kontener raz (upsert)
- **Public visibility:** Ratingi użytkowników widoczne tylko dla publicznych przedmiotów/kontenerów
- **Migration:** Pole `quality` zostanie całkowicie usunięte - nie ma mapowania na ratingi
- **Backward compatibility:** Stare dane z `quality` zostaną utracone podczas migracji (celowe usunięcie)

---

## 🚀 Future Enhancements

- Komentarze do ocen (opcjonalne)
- Filtrowanie/sortowanie po ocenach
- Statystyki ocen w profilu użytkownika
- Powiadomienia o nowych ocenach
- Weryfikacja zakupów (tylko użytkownicy, którzy kupili przedmiot mogą ocenić)
