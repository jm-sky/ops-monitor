# Stripe Implementation - Pattern Verification

**Data:** 2025-12-18
**Status:** Verified Against Codebase
**Purpose:** Weryfikacja zgodności planu implementacji z rzeczywistymi wzorcami projektu

## Executive Summary

Przeprowadzono szczegółową analizę istniejących modułów projektu Gear Stack w celu zweryfikowania, że plan implementacji Stripe jest w 100% zgodny z używanymi wzorcami architektonicznymi. Dokument ten zawiera kluczowe ustalenia i wymagane dostosowania do planu.

---

## Backend Pattern Verification

### 1. Module Structure ✅

**Zweryfikowany wzorzec:** Wszystkie moduły (`feature_limits/`, `auth/`, `gear/`) używają identycznej struktury:

```
backend/app/modules/{module_name}/
├── __init__.py              # Module metadata (minimal)
├── db_models.py             # SQLAlchemy ORM models
├── schemas.py               # Pydantic request/response models
├── router.py                # FastAPI endpoints
├── service.py               # Business logic layer
├── repository.py            # Data access layer
├── dependencies.py          # FastAPI dependency injection (optional)
├── exceptions.py            # Module-specific exceptions (optional)
└── types/                   # TypeScript-like typing (optional)
```

**Plan billing module:** ✅ Zgodny - używa tej samej struktury

**Dodatkowe ustalenia:**
- `stripe_client.py` można dodać jako wrapper SDK (analogicznie do innych zewnętrznych integracji)
- `webhook_handler.py` jako specjalistyczny handler (pattern podobny do `auth/decorators.py`)

---

### 2. Database Models Pattern ✅

**Kluczowe konwencje z `feature_limits/db_models.py` i `auth/db_models.py`:**

```python
from datetime import UTC, datetime
from uuid import UUID, uuid4
from sqlalchemy import BigInteger, DateTime, String, Text, CheckConstraint, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class SubscriptionDB(Base):
    """SQLAlchemy model for subscriptions."""

    __tablename__ = "subscriptions"

    # Primary Key - UUID (not ULID for new tables)
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    # Foreign Keys
    user_id: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        nullable=False,
        index=True
    )  # ULID format for user compatibility

    # Stripe IDs
    stripe_customer_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True
    )
    stripe_subscription_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
        index=True
    )
    stripe_price_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Enums as string fields with CheckConstraint
    plan_tier: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='free',
        index=True
    )
    billing_interval: Mapped[str | None] = mapped_column(String(10), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='active',
        index=True
    )

    # Timestamps - CRITICAL: Always with UTC timezone
    current_period_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    current_period_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    cancel_at_period_end: Mapped[bool] = mapped_column(default=False, nullable=False)
    canceled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Standard timestamps (REQUIRED on all models)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Grandfathered flag (new requirement)
    is_grandfathered: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "plan_tier IN ('free', 'pro', 'pro_plus')",
            name="valid_plan_tier"
        ),
        CheckConstraint(
            "billing_interval IN ('month', 'year')",
            name="valid_billing_interval"
        ),
        CheckConstraint(
            "status IN ('active', 'canceled', 'past_due', 'unpaid', 'incomplete', 'trialing')",
            name="valid_status"
        ),
    )
```

**Kluczowe zmiany do planu:**
1. ✅ Używaj `datetime.now(UTC)` zamiast `datetime.utcnow()` (deprecated)
2. ✅ `DateTime(timezone=True)` dla wszystkich pól datetime
3. ✅ CheckConstraint dla enum-like fields (NOT SQLAlchemy Enum type)
4. ✅ Dodaj `is_grandfathered: Mapped[bool]` do SubscriptionDB
5. ✅ Indexes na frequently queried fields: `user_id`, `plan_tier`, `status`, `stripe_customer_id`

---

### 3. Pydantic Schemas Pattern ✅

**Wzorzec z `feature_limits/schemas.py`:**

```python
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_validator

# 1. Base Schema - shared fields
class SubscriptionBase(BaseModel):
    """Base schema for subscription."""
    plan_tier: str = Field(..., pattern="^(free|pro|pro_plus)$")
    billing_interval: str | None = Field(None, pattern="^(month|year)$")

    @field_validator("plan_tier")
    @classmethod
    def validate_plan_tier(cls, v: str) -> str:
        if v not in ['free', 'pro', 'pro_plus']:
            raise ValueError("Invalid plan tier")
        return v

# 2. Create Schema - for POST requests
class SubscriptionCreate(SubscriptionBase):
    """Schema for creating subscription."""
    user_id: str = Field(..., min_length=26, max_length=26)  # ULID format

# 3. Update Schema - optional fields for PATCH
class SubscriptionUpdate(BaseModel):
    """Schema for updating subscription."""
    status: str | None = Field(None, pattern="^(active|canceled|past_due|unpaid)$")
    cancel_at_period_end: bool | None = None

# 4. Response Schema - includes DB fields
class SubscriptionResponse(BaseModel):
    """Response schema for subscription."""
    id: UUID
    user_id: str
    stripe_customer_id: str | None
    stripe_subscription_id: str | None
    plan_tier: str
    billing_interval: str | None
    status: str
    current_period_start: datetime | None
    current_period_end: datetime | None
    cancel_at_period_end: bool
    is_grandfathered: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,  # Enable ORM mode
        "populate_by_name": True,
    }

    @classmethod
    def from_db(cls, db_model: "SubscriptionDB") -> "SubscriptionResponse":
        """Convert DB model to response schema."""
        return cls(
            id=db_model.id,
            user_id=db_model.user_id,
            stripe_customer_id=db_model.stripe_customer_id,
            stripe_subscription_id=db_model.stripe_subscription_id,
            plan_tier=db_model.plan_tier,
            billing_interval=db_model.billing_interval,
            status=db_model.status,
            current_period_start=db_model.current_period_start,
            current_period_end=db_model.current_period_end,
            cancel_at_period_end=db_model.cancel_at_period_end,
            is_grandfathered=db_model.is_grandfathered,
            created_at=db_model.created_at,
            updated_at=db_model.updated_at,
        )

# Forward reference resolution
from app.modules.billing.db_models import SubscriptionDB
SubscriptionResponse.model_rebuild()
```

**Konwencje:**
- ✅ Cztery typy schematów: Base, Create, Update, Response
- ✅ `from_db()` classmethod dla konwersji
- ✅ `model_config` z `from_attributes=True` (ORM mode)
- ✅ Forward reference handling na końcu pliku

---

### 4. Router Pattern ✅

**Wzorzec z `feature_limits/router.py`:**

```python
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import CurrentUser, AdminOrOwnerUser
from app.modules.billing.service import BillingService
from app.modules.billing.repository import BillingRepository
from app.modules.billing.schemas import (
    CheckoutSessionRequest,
    CheckoutSessionResponse,
    SubscriptionResponse,
)

router = APIRouter(prefix="/billing", tags=["billing"])

# Dependency factory
def get_billing_service(db: AsyncSession = Depends(get_db)) -> BillingService:
    """Get billing service dependency."""
    repo = BillingRepository(db)
    return BillingService(repo)

# Endpoints
@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    current_user: CurrentUser,
    service: BillingService = Depends(get_billing_service),
) -> SubscriptionResponse:
    """Get current user's subscription."""
    try:
        return await service.get_subscription(current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/checkout", response_model=CheckoutSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_checkout_session(
    data: CheckoutSessionRequest,
    current_user: CurrentUser,
    service: BillingService = Depends(get_billing_service),
) -> CheckoutSessionResponse:
    """Create Stripe Checkout session."""
    try:
        return await service.create_checkout_session(current_user, data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# Webhook endpoint - NO AUTH (signature verification only)
@router.post("/webhooks/stripe", status_code=status.HTTP_200_OK)
async def stripe_webhook(
    request: Request,
    service: BillingService = Depends(get_billing_service),
) -> dict[str, str]:
    """Handle Stripe webhook events."""
    # Get raw body and signature
    body = await request.body()
    signature = request.headers.get("stripe-signature")

    try:
        await service.handle_webhook(body, signature)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        # Return 200 even on error to prevent Stripe retries
        return {"status": "error_logged"}
```

**Konwencje:**
- ✅ Dependency injection via `Depends()`
- ✅ Separate factory function dla service
- ✅ `CurrentUser` z `app.modules.auth.dependencies`
- ✅ Proper HTTP status codes (201 for POST, 404 for not found, etc.)
- ✅ Error handling: ValueError → 404, Exception → 400

---

### 5. Migration Pattern ✅

**Wzorzec z `045_add_content_reports.py`:**

```python
"""Migration: Add billing tables and migrate existing premium users.

Usage:
    python migrations/047_add_billing_tables.py upgrade
    python migrations/047_add_billing_tables.py downgrade
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine

async def table_exists(conn, table_name: str) -> bool:
    """Check if table exists (PostgreSQL compatible)."""
    result = await conn.execute(
        text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = :table_name
            );
        """),
        {"table_name": table_name},
    )
    return result.scalar() is True

async def column_exists(conn, table_name: str, column_name: str) -> bool:
    """Check if column exists."""
    result = await conn.execute(
        text("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = :table_name
                AND column_name = :column_name
            );
        """),
        {"table_name": table_name, "column_name": column_name},
    )
    return result.scalar() is True

async def upgrade() -> None:
    """Add billing tables and migrate existing premium users."""
    print("Adding billing support...")

    async with engine.begin() as conn:
        # 1. Create subscriptions table
        if not await table_exists(conn, "subscriptions"):
            await conn.execute(text("""
                CREATE TABLE subscriptions (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id VARCHAR(36) NOT NULL UNIQUE,
                    stripe_customer_id VARCHAR(255),
                    stripe_subscription_id VARCHAR(255) UNIQUE,
                    stripe_price_id VARCHAR(255),
                    plan_tier VARCHAR(20) NOT NULL DEFAULT 'free',
                    billing_interval VARCHAR(10),
                    status VARCHAR(20) NOT NULL DEFAULT 'active',
                    current_period_start TIMESTAMP WITH TIME ZONE,
                    current_period_end TIMESTAMP WITH TIME ZONE,
                    cancel_at_period_end BOOLEAN DEFAULT FALSE,
                    canceled_at TIMESTAMP WITH TIME ZONE,
                    is_grandfathered BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    CONSTRAINT fk_subscriptions_user
                        FOREIGN KEY (user_id)
                        REFERENCES users(id)
                        ON DELETE CASCADE,
                    CONSTRAINT valid_plan_tier
                        CHECK (plan_tier IN ('free', 'pro', 'pro_plus')),
                    CONSTRAINT valid_billing_interval
                        CHECK (billing_interval IN ('month', 'year')),
                    CONSTRAINT valid_status
                        CHECK (status IN ('active', 'canceled', 'past_due', 'unpaid', 'incomplete', 'trialing'))
                )
            """))
            print("✓ Created subscriptions table")

            # Create indexes
            await conn.execute(text("CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id)"))
            await conn.execute(text("CREATE INDEX idx_subscriptions_stripe_customer_id ON subscriptions(stripe_customer_id)"))
            await conn.execute(text("CREATE INDEX idx_subscriptions_plan_tier ON subscriptions(plan_tier)"))
            await conn.execute(text("CREATE INDEX idx_subscriptions_status ON subscriptions(status)"))
            print("✓ Created indexes")

        # 2. Migrate existing premium users to grandfathered Pro
        print("Migrating existing premium users...")
        await conn.execute(text("""
            INSERT INTO subscriptions (
                user_id, plan_tier, status, is_grandfathered, created_at, updated_at
            )
            SELECT
                id,
                'pro',
                'active',
                TRUE,
                created_at,
                NOW()
            FROM users
            WHERE is_premium = TRUE
            ON CONFLICT (user_id) DO NOTHING
        """))
        print("✓ Migrated premium users to grandfathered Pro")

        # 3. Update feature_limits constraints
        if await table_exists(conn, "feature_limits"):
            # Drop old constraint
            await conn.execute(text("""
                ALTER TABLE feature_limits
                DROP CONSTRAINT IF EXISTS valid_role
            """))

            # Add new constraint with 'business' role
            await conn.execute(text("""
                ALTER TABLE feature_limits
                ADD CONSTRAINT valid_role
                CHECK (role IN ('user', 'premium', 'business', 'admin', 'owner'))
            """))
            print("✓ Updated feature_limits constraints")

            # Insert business role limits
            await conn.execute(text("""
                INSERT INTO feature_limits (role, ai_limit, storage_limit_bytes, description)
                VALUES (
                    'business',
                    50.00,
                    53687091200,
                    'Business tier: $50 AI limit, 50GB storage'
                )
                ON CONFLICT (role) DO NOTHING
            """))
            print("✓ Added business tier limits")

            # Update premium role limits (Pro tier)
            await conn.execute(text("""
                UPDATE feature_limits
                SET
                    ai_limit = 10.00,
                    storage_limit_bytes = 5368709120,
                    description = 'Pro tier: $10 AI limit, 5GB storage'
                WHERE role = 'premium'
            """))
            print("✓ Updated premium (Pro) tier limits")

        # 4. Add openrouter_api_token field to users
        if not await column_exists(conn, "users", "openrouter_api_token"):
            await conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN openrouter_api_token VARCHAR(255)
            """))
            print("✓ Added openrouter_api_token field to users")

    print("✅ Billing migration completed successfully")

async def downgrade() -> None:
    """Remove billing tables."""
    print("Removing billing support...")

    async with engine.begin() as conn:
        # Drop subscriptions table
        if await table_exists(conn, "subscriptions"):
            await conn.execute(text("DROP TABLE IF EXISTS subscriptions CASCADE"))
            print("✓ Dropped subscriptions table")

        # Revert feature_limits constraint
        if await table_exists(conn, "feature_limits"):
            await conn.execute(text("""
                ALTER TABLE feature_limits
                DROP CONSTRAINT IF EXISTS valid_role
            """))
            await conn.execute(text("""
                ALTER TABLE feature_limits
                ADD CONSTRAINT valid_role
                CHECK (role IN ('user', 'premium', 'admin', 'owner'))
            """))
            await conn.execute(text("DELETE FROM feature_limits WHERE role = 'business'"))
            print("✓ Reverted feature_limits constraints")

        # Remove openrouter_api_token field
        if await column_exists(conn, "users", "openrouter_api_token"):
            await conn.execute(text("ALTER TABLE users DROP COLUMN openrouter_api_token"))
            print("✓ Removed openrouter_api_token field")

    print("✅ Billing rollback completed successfully")

async def main() -> None:
    """Run migration."""
    import argparse

    parser = argparse.ArgumentParser(description="Billing tables migration")
    parser.add_argument("action", choices=["upgrade", "downgrade"])
    args = parser.parse_args()

    if args.action == "upgrade":
        await upgrade()
    elif args.action == "downgrade":
        await downgrade()

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
```

**Konwencje:**
- ✅ Raw SQL z `text()`
- ✅ `async with engine.begin()` dla transakcji
- ✅ Sprawdzanie existence przed tworzeniem/usuwaniem
- ✅ Upgrade/downgrade functions
- ✅ Progress print statements

---

## Frontend Pattern Verification

### 1. Module Structure ✅

**Zweryfikowana struktura z `settings/` i `auth/`:**

```
src/modules/billing/
├── components/              # Vue components
│   ├── PricingCard.vue
│   ├── PricingTable.vue
│   ├── SubscriptionStatusCard.vue
│   ├── BillingIntervalToggle.vue
│   └── UpgradePromptBanner.vue
├── composables/             # Vue composition functions
│   ├── useSubscription.ts
│   ├── useCheckout.ts
│   └── useBilling.ts        # Combined composable
├── pages/                   # Page components
│   ├── PricingPage.vue
│   └── BillingPage.vue
├── services/                # API services
│   └── billingApiService.ts
├── store/                   # Pinia store (optional)
│   └── useBillingStore.ts
├── types/                   # TypeScript types
│   └── billing.type.ts
├── validation/              # Zod schemas
│   ├── subscription.schema.ts
│   └── paymentMethod.schema.ts
├── utils/                   # Utilities
│   └── queryUtils.ts        # Query keys & retry
├── i18n/                    # Internationalization
│   ├── index.ts
│   └── locales/
│       ├── en.ts            # NOT .json - use .ts!
│       └── pl.ts
├── guards/                  # Route guards (optional)
│   └── billingGuard.ts
└── routes.ts                # Route definitions
```

**Kluczowa zmiana:** ❗ i18n używa `.ts` zamiast `.json`!

---

### 2. Types Pattern ✅

**Wzorzec z `settings/types/settings.type.ts`:**

```typescript
import type { TULID, TDateTime } from '@/shared/types/base.type'

// Union types at top
export type PlanTier = 'free' | 'pro' | 'pro_plus'
export type BillingInterval = 'month' | 'year'
export type SubscriptionStatus =
  | 'active'
  | 'canceled'
  | 'past_due'
  | 'unpaid'
  | 'incomplete'
  | 'trialing'

// Interfaces for data structures
export interface ISubscription {
  id: string  // UUID from backend
  userId: TULID
  stripeCustomerId?: string | null
  stripeSubscriptionId?: string | null
  planTier: PlanTier
  billingInterval?: BillingInterval | null
  status: SubscriptionStatus
  currentPeriodStart?: TDateTime | null
  currentPeriodEnd?: TDateTime | null
  cancelAtPeriodEnd: boolean
  isGrandfathered: boolean
  createdAt: TDateTime
  updatedAt: TDateTime
}

export interface ISubscriptionWithLimits {
  subscription: ISubscription
  limits: {
    aiLimit: number | null  // null = unlimited
    storageLimit: number     // bytes
  }
}

export interface IPlanDetails {
  tier: PlanTier
  name: string
  monthlyPrice: number
  annualPrice: number
  features: string[]
  aiLimit: number | null
  storageLimit: number
  highlighted?: boolean
}

// Service interface for DI
export interface IBillingService {
  getSubscription(): Promise<ISubscriptionWithLimits>
  createCheckoutSession(priceId: string, planTier: PlanTier, billingInterval: BillingInterval): Promise<{ url: string }>
  createPortalSession(returnUrl: string): Promise<{ url: string }>
  cancelSubscription(cancelAtPeriodEnd: boolean): Promise<ISubscription>
}
```

**Konwencje:**
- ✅ Union types na górze pliku
- ✅ Interfaces dla struktur danych
- ✅ Prefix `I` dla interfejsów
- ✅ Import shared types (`TULID`, `TDateTime`) z `@/shared/types/base.type`
- ✅ Service interface dla dependency injection

---

### 3. Services Pattern ✅

**Wzorzec z `settings/services/settingsApiService.ts`:**

```typescript
import { apiClient } from '@/shared/services/apiClient'
import type {
  IBillingService,
  ISubscription,
  ISubscriptionWithLimits,
} from '../types/billing.type'

class BillingApiService implements IBillingService {
  async getSubscription(): Promise<ISubscriptionWithLimits> {
    const response = await apiClient.get<ISubscriptionWithLimits>('/billing/subscription')
    return response.data
  }

  async createCheckoutSession(
    priceId: string,
    planTier: string,
    billingInterval: string,
  ): Promise<{ url: string }> {
    const response = await apiClient.post<{ url: string }>('/billing/checkout', {
      priceId,
      planTier,
      billingInterval,
    })
    return response.data
  }

  async createPortalSession(returnUrl: string): Promise<{ url: string }> {
    const response = await apiClient.post<{ url: string }>('/billing/portal', {
      returnUrl,
    })
    return response.data
  }

  async cancelSubscription(cancelAtPeriodEnd: boolean = true): Promise<ISubscription> {
    const response = await apiClient.post<ISubscription>('/billing/subscription/cancel', {
      cancelAtPeriodEnd,
    })
    return response.data
  }
}

export const billingApiService = new BillingApiService()
```

**Konwencje:**
- ✅ Class-based service implementing interface
- ✅ Single exported instance
- ✅ Use `apiClient` from `@/shared/services/apiClient`
- ✅ Type all responses with generics

---

### 4. Composables Pattern (TanStack Query) ✅

**Wzorzec z `settings/composables/useSettings.ts`:**

```typescript
import { computed } from 'vue'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import { billingApiService } from '../services/billingApiService'
import { billingQueryKeys, billingRetryFunction } from '../utils/queryUtils'
import type { IBillingService } from '../types/billing.type'

// Query hook
export function useSubscriptionQuery(service?: IBillingService) {
  return useQuery({
    queryKey: billingQueryKeys.subscription(),
    queryFn: () => (service ?? billingApiService).getSubscription(),
    staleTime: 5 * 60 * 1000,  // 5 minutes
    retry: billingRetryFunction,
  })
}

// Mutation hook
export function useCancelSubscription(service?: IBillingService) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (cancelAtPeriodEnd: boolean) =>
      (service ?? billingApiService).cancelSubscription(cancelAtPeriodEnd),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: billingQueryKeys.all })
    },
  })
}

// Combined composable
export function useSubscription(service?: IBillingService) {
  const queryClient = useQueryClient()
  const subscriptionQuery = useSubscriptionQuery(service)
  const cancelMutation = useCancelSubscription(service)

  const subscription = computed(() => subscriptionQuery.data?.subscription)
  const limits = computed(() => subscriptionQuery.data?.limits)
  const isLoading = subscriptionQuery.isLoading
  const isError = subscriptionQuery.isError
  const error = subscriptionQuery.error

  // Computed helpers
  const isFreeTier = computed(() => subscription.value?.planTier === 'free')
  const isProTier = computed(() => subscription.value?.planTier === 'pro')
  const isProPlusTier = computed(() => subscription.value?.planTier === 'pro_plus')
  const isGrandfathered = computed(() => subscription.value?.isGrandfathered === true)

  return {
    // Query
    subscriptionQuery,
    subscription,
    limits,
    isLoading,
    isError,
    error,

    // Computed
    isFreeTier,
    isProTier,
    isProPlusTier,
    isGrandfathered,

    // Mutations
    cancelSubscription: cancelMutation.mutateAsync,
    isCanceling: cancelMutation.isPending,

    // Refresh
    refetchSubscription: () =>
      queryClient.invalidateQueries({ queryKey: billingQueryKeys.all }),
  }
}
```

**Konwencje:**
- ✅ Separate hooks for query and mutation
- ✅ Combined composable for convenience
- ✅ Service dependency injection for testing
- ✅ Computed properties for derived state
- ✅ Proper loading/error states

---

### 5. Query Keys & Retry Utils ✅

**Wzorzec z `settings/utils/queryUtils.ts`:**

```typescript
import { isAuthError, isClientError } from '@/shared/utils/errorGuards'

export const billingQueryKeys = {
  all: ['billing'] as const,
  subscription: () => [...billingQueryKeys.all, 'subscription'] as const,
  invoices: () => [...billingQueryKeys.all, 'invoices'] as const,
  invoice: (id: string) => [...billingQueryKeys.invoices(), id] as const,
} as const

export function createBillingRetryFunction(maxAttempts = 2) {
  return (failureCount: number, error: unknown) => {
    // Don't retry auth errors (user needs to login)
    if (isAuthError(error)) return false
    // Don't retry client errors (4xx - bad request)
    if (isClientError(error)) return false
    // Retry network errors up to maxAttempts
    return failureCount < maxAttempts
  }
}

export const billingRetryFunction = createBillingRetryFunction()
```

**Konwencje:**
- ✅ Nested query key objects
- ✅ `as const` for type safety
- ✅ Retry functions that check error types
- ✅ Auth errors don't retry
- ✅ Client errors (4xx) don't retry

---

### 6. Routes Pattern ✅

**Wzorzec z `auth/config/routes.ts` i `settings/routes.ts`:**

```typescript
import type { RouteRecordRaw } from 'vue-router'

export const BILLING_BASE_PATH = '/billing'

export const BillingRoutePaths = {
  pricing: '/pricing',  // Public pricing page
  billing: `${BILLING_BASE_PATH}`,
  subscription: `${BILLING_BASE_PATH}/subscription`,
  invoices: `${BILLING_BASE_PATH}/invoices`,
} as const

export const BillingRouteNames = {
  pricing: 'pricing',
  billing: 'billing',
  subscription: 'billing-subscription',
  invoices: 'billing-invoices',
} as const

export const billingRoutes: RouteRecordRaw[] = [
  {
    path: BillingRoutePaths.pricing,
    name: BillingRouteNames.pricing,
    component: () => import('@/modules/billing/pages/PricingPage.vue'),
    meta: {
      layout: 'public',  // Public page
      title: 'billing.pricing.title',
    },
  },
  {
    path: BillingRoutePaths.billing,
    name: BillingRouteNames.billing,
    component: () => import('@/modules/billing/pages/BillingPage.vue'),
    meta: {
      layout: 'authenticated',
      requiresAuth: true,
      title: 'billing.page.title',
    },
  },
]
```

**Konwencje:**
- ✅ Separate `RoutePaths` and `RouteNames`
- ✅ `as const` for type safety
- ✅ Meta properties: `layout`, `title`, `requiresAuth`
- ✅ Lazy-loaded components with dynamic import

---

### 7. i18n Pattern ⚠️ CRITICAL CHANGE

**WAŻNE:** Projekt używa `.ts` files, NIE `.json`!

**Wzorzec z `settings/i18n/locales/en.ts`:**

```typescript
export const billingEn = {
  billing: {
    pricing: {
      title: 'Pricing',
      subtitle: 'Choose the plan that fits your needs',
      free: {
        title: 'Free',
        price: 'Free',
        features: {
          ai: '$1 AI limit (bring your own token)',
          storage: '100 MB storage',
          models: 'All AI models available',
          processing: 'Standard quality image processing',
        },
        cta: 'Get Started',
      },
      pro: {
        title: 'Pro',
        price_monthly: '$5.00/month',
        price_annual: '$50/year',
        annual_savings: 'Save 17%',
        features: {
          ai: '$10 AI limit included',
          storage: '5 GB storage',
          models: 'All AI models available',
          processing: 'High quality image processing',
          search: 'Advanced image search',
        },
        cta: 'Upgrade to Pro',
      },
      pro_plus: {
        title: 'Pro Plus',
        price_monthly: '$15.00/month',
        price_annual: '$150/year',
        annual_savings: 'Save 17%',
        features: {
          ai: '$50 AI limit included',
          storage: '50 GB storage',
          models: 'All AI models available',
          processing: 'High quality image processing',
          search: 'Advanced image search',
        },
        cta: 'Upgrade to Pro Plus',
      },
    },
    subscription: {
      title: 'Subscription',
      current_plan: 'Current Plan',
      status: 'Status',
      grandfathered_badge: 'Lifetime Access',
      grandfathered_message: 'You have lifetime Pro access as an early supporter!',
      limits: {
        ai: 'AI Limit',
        storage: 'Storage',
      },
      actions: {
        manage: 'Manage Billing',
        upgrade: 'Upgrade Plan',
        cancel: 'Cancel Subscription',
      },
    },
  },
}
```

**i18n/index.ts:**

```typescript
export { billingEn } from './locales/en'
export { billingPl } from './locales/pl'
```

**Konwencje:**
- ⚠️ Use `.ts` files, NOT `.json`
- ✅ Export named constant (`billingEn`, `billingPl`)
- ✅ Nested object structure
- ✅ Always provide both English and Polish

---

### 8. Validation Schema Pattern ✅

**Wzorzec z `settings/validation/settings.schema.ts`:**

```typescript
import { z } from 'zod'

export const subscriptionCreateSchema = z.object({
  planTier: z.enum(['free', 'pro', 'pro_plus']),
  billingInterval: z.enum(['month', 'year']),
})

export type SubscriptionCreateFormData = z.infer<typeof subscriptionCreateSchema>

export const paymentMethodSchema = z.object({
  cardNumber: z.string().regex(/^\d{16}$/, 'Invalid card number'),
  expiryDate: z.string().regex(/^\d{2}\/\d{2}$/, 'Invalid expiry date'),
  cvv: z.string().regex(/^\d{3,4}$/, 'Invalid CVV'),
})

export type PaymentMethodFormData = z.infer<typeof paymentMethodSchema>
```

**Konwencje:**
- ✅ One schema per domain
- ✅ Export both schema and inferred type
- ✅ Use `z.enum()` for enums
- ✅ Include validation messages

---

## Configuration Updates

### Backend Config Pattern ✅

**Wzorzec z `config.py`:**

```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_base_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    case_sensitive=False,
    extra="ignore",
)

class StripeSettings(BaseSettings):
    """Stripe billing configuration."""

    model_config = _base_config

    enabled: bool = Field(default=False, validation_alias="STRIPE_ENABLED")
    secret_key: str = Field(default="", validation_alias="STRIPE_SECRET_KEY")
    publishable_key: str = Field(default="", validation_alias="STRIPE_PUBLISHABLE_KEY")
    webhook_secret: str = Field(default="", validation_alias="STRIPE_WEBHOOK_SECRET")

    # Price IDs
    pro_monthly_price_id: str = Field(default="", validation_alias="STRIPE_PRO_MONTHLY_PRICE_ID")
    pro_annual_price_id: str = Field(default="", validation_alias="STRIPE_PRO_ANNUAL_PRICE_ID")
    pro_plus_monthly_price_id: str = Field(default="", validation_alias="STRIPE_PRO_PLUS_MONTHLY_PRICE_ID")
    pro_plus_annual_price_id: str = Field(default="", validation_alias="STRIPE_PRO_PLUS_ANNUAL_PRICE_ID")

class Settings(BaseSettings):
    """Application settings."""
    model_config = _base_config

    # ... existing settings
    stripe: StripeSettings = Field(default_factory=StripeSettings)
```

**Usage:**
```python
from app.core.config import settings

stripe_key = settings.stripe.secret_key
pro_price = settings.stripe.pro_monthly_price_id
```

---

## Critical Implementation Checklist

### Backend ✅

- [x] Use UUID for primary keys (NOT ULID for new tables)
- [x] `DateTime(timezone=True)` for all datetime fields
- [x] Use `datetime.now(UTC)` (NOT `datetime.utcnow()`)
- [x] CheckConstraint for enum-like fields (NOT SQLAlchemy Enum)
- [x] Add `is_grandfathered` field to SubscriptionDB
- [x] Indexes on: `user_id`, `plan_tier`, `status`, `stripe_customer_id`
- [x] Four schema types: Base, Create, Update, Response
- [x] `from_db()` classmethod in Response schemas
- [x] Dependency injection via `Depends()`
- [x] Error handling: ValueError → 404, Exception → 400
- [x] Migration with existence checks
- [x] Both upgrade/downgrade functions

### Frontend ✅

- [x] i18n uses `.ts` files (NOT `.json`)
- [x] Types in `types/billing.type.ts`
- [x] Service implements interface
- [x] Query keys in `utils/queryUtils.ts`
- [x] Separate query/mutation hooks
- [x] Combined composable for convenience
- [x] Routes with `as const` for type safety
- [x] Validation schemas with Zod
- [x] Meta properties: `layout`, `requiresAuth`, `title`

---

## Summary of Required Changes to Implementation Plan

### ❗ Critical Changes:

1. **Backend Models:**
   - Add `is_grandfathered: Mapped[bool]` field to SubscriptionDB
   - Use `DateTime(timezone=True)` everywhere
   - Use `datetime.now(UTC)` instead of `datetime.utcnow()`
   - CheckConstraint pattern instead of Enum types

2. **Frontend i18n:**
   - Change from `.json` to `.ts` files
   - Export named constants (`billingEn`, `billingPl`)

3. **Migration:**
   - Add migration for `is_grandfathered` field
   - Add migration for `openrouter_api_token` in users table
   - Include grandfathered migration logic

4. **Pricing Updates:**
   - Pro: $5.00/mo, $50/yr
   - Pro Plus: $15.00/mo, $150/yr
   - Free: BYOK for AI

### ✅ Confirmed Patterns:

- Module structure (backend & frontend)
- Database models with timestamps
- Pydantic schemas (Base/Create/Update/Response)
- FastAPI router with dependency injection
- TanStack Query composables
- Query keys and retry logic
- Route definitions
- Validation schemas

---

**Document Version:** 1.0
**Last Updated:** 2025-12-18
**Status:** ✅ Pattern Verification Complete
**Next Step:** Update implementation plan with verified patterns
