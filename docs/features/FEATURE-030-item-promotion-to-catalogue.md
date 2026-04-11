# FEATURE-030: Item Promotion to Catalogue (Promocja Przedmiotu do Katalogu)

**Status:** ✅ Completed  
**Priority:** Medium  
**Category:** 🗂️ Global Catalogue / Community  
**Related:** ROADMAP_ONLINE.md - Promocja przedmiotu do katalogu globalnego

---

## 📋 Overview

Mechanizm pozwalający użytkownikom na promowanie swoich przedmiotów do globalnego katalogu, gdzie mogą być używane przez innych użytkowników. Przedmioty są promowane przez społeczność (licznik promocji) i automatycznie dodawane do katalogu po osiągnięciu progu.

---

## 🎯 Goals

1. **System promocji** - możliwość promowania przedmiotów przez użytkowników
2. **Wymagania** - tylko zarejestrowani użytkownicy z kontem > 1 miesiąc mogą promować
3. **Licznik promocji** - śledzenie liczby promocji per przedmiot
4. **Automatyczna promocja** - dodanie do katalogu po osiągnięciu progu (np. 10 promocji)
5. **UI informacyjne** - wyświetlanie statusu promocji i progress bar

---

## 🔍 Current State

### Globalny katalog istnieje
- ✅ Globalny katalog przedmiotów już zaimplementowany
- ✅ Przedmioty mogą być dodawane do katalogu (admin/manual)
- ❌ Brak mechanizmu społecznościowej promocji
- ❌ Brak licznika promocji
- ❌ Brak wymagań dla promujących użytkowników

---

## 📝 Implementation Plan

### Phase 1: Backend - Database & Models

#### Step 1.1: Dodanie pola `promote_count` do przedmiotów

**File:** `backend/app/modules/gear/db_models.py`

Dodaj pole do modelu `GearItemDB`:

```python
promote_count: Mapped[int] = mapped_column(
    Integer,
    default=0,
    nullable=False,
    server_default="0"
)
```

#### Step 1.2: Tabela historii promocji

**File:** `backend/app/modules/gear/db_models.py`

Utwórz nowy model:

```python
class ItemPromotionDB(Base):
    """SQLAlchemy model for item promotions to catalogue.
    
    Attributes:
        id: Unique identifier (ULID format)
        item_id: Promoted item ID
        user_id: User who promoted the item
        created_at: Promotion timestamp
    """
    
    __tablename__ = "item_promotions"
    
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
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    item: Mapped["GearItemDB"] = relationship("GearItemDB", back_populates="promotions")
    user: Mapped["UserDB"] = relationship("UserDB")
    
    # Unique constraint: user can promote item only once
    __table_args__ = (
        UniqueConstraint("item_id", "user_id", name="unique_item_user_promotion"),
    )
```

Dodaj relację w `GearItemDB`:

```python
promotions: Mapped[list["ItemPromotionDB"]] = relationship(
    "ItemPromotionDB",
    back_populates="item",
    cascade="all, delete-orphan"
)
```

#### Step 1.3: Migracja bazy danych

**File:** `backend/alembic/versions/XXXX_add_item_promotion.py`

Utwórz migrację:
1. Dodanie kolumny `promote_count` do `gear_items`
2. Utworzenie tabeli `item_promotions`
3. Utworzenie indeksów i constraintów

#### Step 1.4: Konfiguracja progu promocji

**File:** `backend/app/modules/gear/config.py`

```python
PROMOTION_THRESHOLD = 10  # Number of promotions needed to add to catalogue
```

---

### Phase 2: Backend - Service Layer

#### Step 2.1: Service do promocji przedmiotów

**File:** `backend/app/modules/gear/services/promotion_service.py`

```python
from datetime import datetime, timedelta
from app.modules.auth.db_models import UserDB
from app.modules.gear.db_models import GearItemDB, ItemPromotionDB
from app.modules.gear.config import PROMOTION_THRESHOLD

class PromotionService:
    @staticmethod
    async def can_promote(user: UserDB) -> tuple[bool, str]:
        """Check if user can promote items.
        
        Returns:
            (can_promote: bool, reason: str)
        """
        if not user.created_at:
            return False, "User account creation date not found"
        
        # Check if account is older than 1 month
        one_month_ago = datetime.now(user.created_at.tzinfo) - timedelta(days=30)
        if user.created_at > one_month_ago:
            days_remaining = (one_month_ago - user.created_at).days
            return False, f"Account must be at least 1 month old. {abs(days_remaining)} days remaining."
        
        return True, ""
    
    @staticmethod
    async def promote_item(
        item: GearItemDB,
        user: UserDB,
        promotion_repo: "ItemPromotionRepository"
    ) -> GearItemDB:
        """Promote item to catalogue.
        
        Returns:
            Updated item with incremented promote_count
        """
        # Check if user already promoted this item
        existing_promotion = await promotion_repo.get_by_item_and_user(
            item_id=item.id,
            user_id=user.id
        )
        if existing_promotion:
            raise ValueError("User has already promoted this item")
        
        # Check if user can promote
        can_promote, reason = await PromotionService.can_promote(user)
        if not can_promote:
            raise ValueError(reason)
        
        # Create promotion record
        promotion = ItemPromotionDB(
            id=generate_ulid(),
            item_id=item.id,
            user_id=user.id
        )
        await promotion_repo.create(promotion)
        
        # Increment promote_count
        item.promote_count += 1
        
        # Check if threshold reached
        if item.promote_count >= PROMOTION_THRESHOLD:
            # Add to catalogue (if not already there)
            if not item.catalogue_item_id:
                # Create catalogue item or link to existing
                # This depends on catalogue implementation
                pass
        
        return item
    
    @staticmethod
    async def get_promotion_status(
        item: GearItemDB
    ) -> dict:
        """Get promotion status for item."""
        return {
            "promote_count": item.promote_count,
            "threshold": PROMOTION_THRESHOLD,
            "remaining": max(0, PROMOTION_THRESHOLD - item.promote_count),
            "percentage": (item.promote_count / PROMOTION_THRESHOLD) * 100,
            "in_catalogue": item.catalogue_item_id is not None,
        }
```

#### Step 2.2: Repository dla promocji

**File:** `backend/app/modules/gear/repositories/promotion_repository.py`

```python
from app.modules.gear.db_models import ItemPromotionDB

class ItemPromotionRepository:
    async def get_by_item_and_user(
        self,
        item_id: str,
        user_id: str
    ) -> ItemPromotionDB | None:
        """Get promotion by item and user."""
        # Implementation
        pass
    
    async def create(self, promotion: ItemPromotionDB) -> ItemPromotionDB:
        """Create promotion."""
        # Implementation
        pass
    
    async def get_by_item(self, item_id: str) -> list[ItemPromotionDB]:
        """Get all promotions for item."""
        # Implementation
        pass
```

---

### Phase 3: Backend - API Endpoints

#### Step 3.1: Endpoint promocji przedmiotu

**File:** `backend/app/modules/gear/router.py`

```python
@router.post("/items/{item_id}/promote")
async def promote_item(
    item_id: str,
    current_user: CurrentUser,
    gear_repo: GearRepository = Depends(get_gear_repository),
    promotion_repo: ItemPromotionRepository = Depends(get_promotion_repository),
    promotion_service: PromotionService = Depends(get_promotion_service),
):
    """Promote item to catalogue."""
    # Get item
    item = await gear_repo.get_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Check ownership (user can only promote their own items)
    if item.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only promote your own items"
        )
    
    try:
        # Promote item
        updated_item = await promotion_service.promote_item(
            item=item,
            user=current_user,
            promotion_repo=promotion_repo
        )
        
        # Save updated item
        await gear_repo.update_item(updated_item)
        
        return {
            "success": True,
            "promote_count": updated_item.promote_count,
            "message": "Item promoted successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

#### Step 3.2: Endpoint statusu promocji

**File:** `backend/app/modules/gear/router.py`

```python
@router.get("/items/{item_id}/promote-status")
async def get_promotion_status(
    item_id: str,
    current_user: CurrentUser,
    gear_repo: GearRepository = Depends(get_gear_repository),
    promotion_service: PromotionService = Depends(get_promotion_service),
):
    """Get promotion status for item."""
    item = await gear_repo.get_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    status = await promotion_service.get_promotion_status(item)
    
    # Check if current user has already promoted
    promotion_repo = get_promotion_repository()
    user_promotion = await promotion_repo.get_by_item_and_user(
        item_id=item_id,
        user_id=current_user.id
    )
    status["user_promoted"] = user_promotion is not None
    
    return status
```

---

### Phase 4: Frontend - Types & API

#### Step 4.1: TypeScript types

**File:** `src/modules/gear/types/promotion.types.ts`

```typescript
export interface IItemPromotionStatus {
  promote_count: number
  threshold: number
  remaining: number
  percentage: number
  in_catalogue: boolean
  user_promoted: boolean
}

export interface IPromoteItemResponse {
  success: boolean
  promote_count: number
  message: string
}
```

#### Step 4.2: API service

**File:** `src/modules/gear/services/promotionApiService.ts`

```typescript
import { apiClient } from '@/shared/services/apiClient'
import type { IItemPromotionStatus, IPromoteItemResponse } from '../types/promotion.types'

export const promotionApiService = {
  async promoteItem(itemId: string): Promise<IPromoteItemResponse> {
    const response = await apiClient.post<IPromoteItemResponse>(
      `/gear/items/${itemId}/promote`
    )
    return response.data
  },
  
  async getPromotionStatus(itemId: string): Promise<IItemPromotionStatus> {
    const response = await apiClient.get<IItemPromotionStatus>(
      `/gear/items/${itemId}/promote-status`
    )
    return response.data
  },
}
```

---

### Phase 5: Frontend - UI Components

#### Step 5.1: Komponent promocji przedmiotu

**File:** `src/modules/gear/components/ItemPromotionCard.vue`

```vue
<script setup lang="ts">
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import { promotionApiService } from '../services/promotionApiService'
import { Progress } from '@/components/ui/progress'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { ThumbsUp } from 'lucide-vue-next'

const props = defineProps<{
  itemId: string
}>()

const { t } = useI18n()
const queryClient = useQueryClient()

const { data: status, isLoading } = useQuery({
  queryKey: ['item-promotion-status', props.itemId],
  queryFn: () => promotionApiService.getPromotionStatus(props.itemId),
})

const promoteMutation = useMutation({
  mutationFn: () => promotionApiService.promoteItem(props.itemId),
  onSuccess: () => {
    toast.success(t('gear.promotion.success'))
    queryClient.invalidateQueries({ queryKey: ['item-promotion-status', props.itemId] })
  },
  onError: (error: any) => {
    toast.error(error.response?.data?.detail || t('gear.promotion.error'))
  },
})

const handlePromote = () => {
  promoteMutation.mutate()
}
</script>

<template>
  <Card v-if="status && !isLoading">
    <CardHeader>
      <CardTitle class="flex items-center gap-2">
        <ThumbsUp class="size-4" />
        {{ t('gear.promotion.title') }}
        <Badge v-if="status.in_catalogue" variant="default">
          {{ t('gear.promotion.inCatalogue') }}
        </Badge>
      </CardTitle>
    </CardHeader>
    <CardContent>
      <div class="space-y-4">
        <!-- Progress bar -->
        <div class="space-y-2">
          <div class="flex justify-between text-sm">
            <span>{{ t('gear.promotion.promotions') }}</span>
            <span>{{ status.promote_count }} / {{ status.threshold }}</span>
          </div>
          <Progress :model-value="status.percentage" />
          <p class="text-xs text-muted-foreground">
            {{ t('gear.promotion.remaining', { count: status.remaining }) }}
          </p>
        </div>
        
        <!-- Promote button -->
        <Button
          v-if="!status.user_promoted && !status.in_catalogue"
          @click="handlePromote"
          :disabled="promoteMutation.isPending"
          class="w-full"
        >
          <ThumbsUp class="size-4 mr-2" />
          {{ t('gear.promotion.promoteButton') }}
        </Button>
        
        <!-- Already promoted -->
        <div v-if="status.user_promoted" class="text-sm text-muted-foreground">
          {{ t('gear.promotion.alreadyPromoted') }}
        </div>
        
        <!-- In catalogue -->
        <div v-if="status.in_catalogue" class="text-sm text-success">
          {{ t('gear.promotion.addedToCatalogue') }}
        </div>
      </div>
    </CardContent>
  </Card>
</template>
```

#### Step 5.2: Dodanie do ItemDetailPage

**File:** `src/modules/gear/pages/ItemDetailPage.vue`

Dodaj `ItemPromotionCard` do strony szczegółów przedmiotu (tylko dla właściciela przedmiotu).

#### Step 5.3: Przycisk w menu akcji

**File:** `src/modules/gear/components/ItemHeaderActions.vue`

Dodaj opcję "Promuj do katalogu" w dropdown menu (tylko dla właściciela przedmiotu).

---

### Phase 6: Error Handling & Validation

#### Step 6.1: Walidacja wymagań

**Backend:**
- Sprawdzanie wieku konta (> 1 miesiąc)
- Sprawdzanie czy użytkownik już promował przedmiot
- Sprawdzanie czy przedmiot należy do użytkownika

**Frontend:**
- Wyświetlanie komunikatu o wymaganiach (konto > 1 miesiąc)
- Disable przycisku jeśli wymagania nie spełnione
- Informacja o już promowanym przedmiocie

---

## 🎨 UI/UX Considerations

- **Progress bar** - wizualne przedstawienie postępu do progu promocji
- **Badge "W katalogu"** - oznaczenie przedmiotów już w katalogu
- **Disabled state** - przycisk wyłączony jeśli użytkownik już promował
- **Clear messaging** - jasne komunikaty o wymaganiach i statusie promocji
- **Toast notifications** - potwierdzenie sukcesu/błędu

---

## 🔄 Future Enhancements

1. **Historia promocji** - wyświetlanie listy użytkowników, którzy promowali przedmiot
2. **Różne progi** - różne progi dla różnych typów przedmiotów
3. **Weryfikacja jakości** - dodatkowa weryfikacja przed dodaniem do katalogu
4. **Anulowanie promocji** - możliwość cofnięcia promocji (opcjonalnie)

---

## 📊 Testing

### Backend Tests

- Test wymagań promocji (konto > 1 miesiąc)
- Test unikalności promocji (użytkownik może promować tylko raz)
- Test licznika promocji
- Test automatycznego dodania do katalogu po osiągnięciu progu
- Test endpointów API

### Frontend Tests

- Test wyświetlania statusu promocji
- Test przycisku promocji
- Test progress bar
- Test komunikatów błędów
- Test disabled state

---

## 📝 Notes

- Próg promocji: 10 (konfigurowalny)
- Wymaganie: konto > 1 miesiąc
- Użytkownik może promować tylko swoje przedmioty
- Jeden użytkownik może promować dany przedmiot tylko raz
- Automatyczne dodanie do katalogu po osiągnięciu progu
