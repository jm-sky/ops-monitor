# Plan implementacji: Statystyki wyświetleń kontenerów

## Przegląd

Implementacja systemu statystyk wyświetleń kontenerów, który pozwoli właścicielom kontenerów śledzić popularność swoich kontenerów publicznych i udostępnionych. System będzie rejestrował wyświetlenia, agregował dane i prezentował je w formie dashboardu z wykresami.

## Zakres funkcjonalności

### Backend
- Tabela `container_views` do przechowywania danych o wyświetleniach
- Endpointy do rejestrowania i pobierania statystyk
- Agregacja danych (dzienne, tygodniowe, miesięczne)
- Liczniki całkowitych i unikalnych wyświetleń
- Opcjonalna geolokalizacja (anonimowa, zgodna z GDPR)

### Frontend
- Automatyczne rejestrowanie wyświetleń przy otwarciu kontenera
- Dashboard statystyk dla właściciela kontenera
- Wykresy wyświetleń w czasie
- Top kontenerów, statystyki per token
- Strona statystyk kontenera (`ContainerStatsPage`)

---

## 1. Backend - Model danych

### 1.1. Model SQLAlchemy (`backend/app/modules/gear/db_models.py`)

```python
class ContainerViewDB(Base):
    """SQLAlchemy model for container views/statistics.
    
    Tracks each view of a container (public or shared via token).
    Used to generate statistics for container owners.
    
    Attributes:
        id: Unique identifier (ULID format, 36 chars)
        container_id: Container ID being viewed
        user_id: ID of authenticated user (nullable for anonymous views)
        session_id: Browser session ID for tracking unique visitors
        share_token: Share token used to access (nullable, only for shared containers)
        viewed_at: Timestamp of the view
        ip_address: IP address (hashed or anonymized for GDPR)
        user_agent: Browser user agent string
        country: Country code from IP geolocation (optional, anonymized)
        referrer: HTTP referrer URL (optional)
    """
    
    __tablename__ = "container_views"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    container_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("gear_containers.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    user_id: Mapped[str | None] = mapped_column(
        String(36), 
        ForeignKey("users.id", ondelete="SET NULL"), 
        nullable=True, 
        index=True
    )
    session_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    share_token: Mapped[str | None] = mapped_column(
        String(255), 
        ForeignKey("container_share_tokens.token", ondelete="SET NULL"), 
        nullable=True, 
        index=True
    )
    viewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(UTC), 
        nullable=False, 
        index=True
    )
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)  # IPv6 max length
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    country: Mapped[str | None] = mapped_column(String(2), nullable=True)  # ISO 3166-1 alpha-2
    referrer: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Relationships
    container: Mapped["GearContainerDB"] = relationship("GearContainerDB", foreign_keys=[container_id])
    user: Mapped["UserDB | None"] = relationship("UserDB", foreign_keys=[user_id])
    share_token_obj: Mapped["ContainerShareTokenDB | None"] = relationship(
        "ContainerShareTokenDB", 
        foreign_keys=[share_token]
    )
    
    def __repr__(self) -> str:
        return f"<ContainerViewDB(id={self.id}, container_id={self.container_id}, viewed_at={self.viewed_at})>"
```

**Indeksy:**
- `container_id` - dla zapytań per kontener
- `viewed_at` - dla agregacji czasowej
- `session_id` - dla unikalnych wyświetleń
- `share_token` - dla statystyk per token
- Composite index: `(container_id, viewed_at)` - dla zapytań z zakresem dat

### 1.2. Migracja bazy danych

**Plik:** `backend/migrations/XXX_add_container_views.py`

```python
async def upgrade() -> None:
    """Add container_views table."""
    async with engine.begin() as conn:
        await conn.execute(
            text("""
                CREATE TABLE container_views (
                    id VARCHAR(36) PRIMARY KEY,
                    container_id VARCHAR(36) NOT NULL,
                    user_id VARCHAR(36),
                    session_id VARCHAR(255) NOT NULL,
                    share_token VARCHAR(255),
                    viewed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    country VARCHAR(2),
                    referrer TEXT,
                    CONSTRAINT fk_container_views_container 
                        FOREIGN KEY (container_id) 
                        REFERENCES gear_containers(id) 
                        ON DELETE CASCADE,
                    CONSTRAINT fk_container_views_user 
                        FOREIGN KEY (user_id) 
                        REFERENCES users(id) 
                        ON DELETE SET NULL,
                    CONSTRAINT fk_container_views_share_token 
                        FOREIGN KEY (share_token) 
                        REFERENCES container_share_tokens(token) 
                        ON DELETE SET NULL
                );
            """)
        )
        
        # Create indexes
        await conn.execute(text("CREATE INDEX ix_container_views_container_id ON container_views(container_id);"))
        await conn.execute(text("CREATE INDEX ix_container_views_viewed_at ON container_views(viewed_at);"))
        await conn.execute(text("CREATE INDEX ix_container_views_session_id ON container_views(session_id);"))
        await conn.execute(text("CREATE INDEX ix_container_views_share_token ON container_views(share_token);"))
        await conn.execute(text("CREATE INDEX ix_container_views_user_id ON container_views(user_id);"))
        await conn.execute(text("CREATE INDEX ix_container_views_container_viewed_at ON container_views(container_id, viewed_at);"))
```

---

## 2. Backend - Schematy Pydantic

### 2.1. Request schemas (`backend/app/modules/gear/schemas.py`)

```python
class ContainerViewCreate(BaseModel):
    """Schema for creating a container view record."""
    
    session_id: str
    share_token: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    country: str | None = None
    referrer: str | None = None
    
    model_config = {"populate_by_name": True}


class ContainerViewResponse(BaseModel):
    """Schema for container view response."""
    
    id: str
    container_id: str
    user_id: str | None
    session_id: str
    share_token: str | None
    viewed_at: datetime
    country: str | None
    
    model_config = {"populate_by_name": True}


class ContainerStatsResponse(BaseModel):
    """Schema for container statistics response."""
    
    container_id: str
    total_views: int
    unique_views: int
    views_by_day: list[dict[str, int | str]]  # [{"date": "2024-01-01", "views": 10}]
    views_by_week: list[dict[str, int | str]]
    views_by_month: list[dict[str, int | str]]
    views_by_token: list[dict[str, int | str]]  # [{"token": "abc...", "views": 5}]
    views_by_country: list[dict[str, int | str]]  # [{"country": "PL", "views": 10}]
    first_viewed_at: datetime | None
    last_viewed_at: datetime | None
    
    model_config = {"populate_by_name": True}


class UserContainersStatsResponse(BaseModel):
    """Schema for user's all containers statistics."""
    
    containers: list[dict[str, int | str | None]]  # [{"container_id": "...", "name": "...", "total_views": 10, "unique_views": 5}]
    total_views: int
    total_unique_views: int
    
    model_config = {"populate_by_name": True}
```

---

## 3. Backend - Repository

### 3.1. Metody w `GearRepository` (`backend/app/modules/gear/repository.py`)

```python
async def create_container_view(
    self,
    container_id: str,
    session_id: str,
    user_id: str | None = None,
    share_token: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    country: str | None = None,
    referrer: str | None = None,
) -> ContainerViewDB:
    """Create a container view record.
    
    Args:
        container_id: Container ID
        session_id: Browser session ID
        user_id: Authenticated user ID (optional)
        share_token: Share token used (optional)
        ip_address: IP address (optional)
        user_agent: User agent string (optional)
        country: Country code (optional)
        referrer: Referrer URL (optional)
    
    Returns:
        Created view record
    """
    view_id = generate_ulid()
    view = ContainerViewDB(
        id=view_id,
        container_id=container_id,
        user_id=user_id,
        session_id=session_id,
        share_token=share_token,
        ip_address=ip_address,
        user_agent=user_agent,
        country=country,
        referrer=referrer,
    )
    self.db.add(view)
    await self.db.commit()
    await self.db.refresh(view)
    return view


async def get_container_stats(
    self,
    container_id: str,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> dict:
    """Get aggregated statistics for a container.
    
    Args:
        container_id: Container ID
        start_date: Start date for filtering (optional)
        end_date: End date for filtering (optional)
    
    Returns:
        Dictionary with aggregated statistics
    """
    # Base query
    base_query = select(ContainerViewDB).where(ContainerViewDB.container_id == container_id)
    
    if start_date:
        base_query = base_query.where(ContainerViewDB.viewed_at >= start_date)
    if end_date:
        base_query = base_query.where(ContainerViewDB.viewed_at <= end_date)
    
    # Total views
    total_views_stmt = select(func.count(ContainerViewDB.id)).where(
        ContainerViewDB.container_id == container_id
    )
    if start_date:
        total_views_stmt = total_views_stmt.where(ContainerViewDB.viewed_at >= start_date)
    if end_date:
        total_views_stmt = total_views_stmt.where(ContainerViewDB.viewed_at <= end_date)
    
    total_result = await self.db.execute(total_views_stmt)
    total_views = total_result.scalar() or 0
    
    # Unique views (by session_id)
    unique_views_stmt = select(func.count(func.distinct(ContainerViewDB.session_id))).where(
        ContainerViewDB.container_id == container_id
    )
    if start_date:
        unique_views_stmt = unique_views_stmt.where(ContainerViewDB.viewed_at >= start_date)
    if end_date:
        unique_views_stmt = unique_views_stmt.where(ContainerViewDB.viewed_at <= end_date)
    
    unique_result = await self.db.execute(unique_views_stmt)
    unique_views = unique_result.scalar() or 0
    
    # Views by day
    views_by_day_stmt = (
        select(
            func.date(ContainerViewDB.viewed_at).label("date"),
            func.count(ContainerViewDB.id).label("views"),
        )
        .where(ContainerViewDB.container_id == container_id)
        .group_by(func.date(ContainerViewDB.viewed_at))
        .order_by(func.date(ContainerViewDB.viewed_at).desc())
    )
    if start_date:
        views_by_day_stmt = views_by_day_stmt.where(ContainerViewDB.viewed_at >= start_date)
    if end_date:
        views_by_day_stmt = views_by_day_stmt.where(ContainerViewDB.viewed_at <= end_date)
    
    day_result = await self.db.execute(views_by_day_stmt)
    views_by_day = [
        {"date": str(row.date), "views": row.views} for row in day_result.all()
    ]
    
    # Views by week (similar pattern)
    # Views by month (similar pattern)
    # Views by token
    # Views by country
    # First/last viewed dates
    
    return {
        "container_id": container_id,
        "total_views": total_views,
        "unique_views": unique_views,
        "views_by_day": views_by_day,
        "views_by_week": views_by_week,
        "views_by_month": views_by_month,
        "views_by_token": views_by_token,
        "views_by_country": views_by_country,
        "first_viewed_at": first_viewed_at,
        "last_viewed_at": last_viewed_at,
    }


async def get_user_containers_stats(
    self,
    user_id: str,
) -> dict:
    """Get statistics for all user's containers.
    
    Args:
        user_id: User ID
    
    Returns:
        Dictionary with aggregated statistics for all containers
    """
    # Get all containers owned by user
    containers_stmt = select(GearContainerDB.id, GearContainerDB.name).where(
        GearContainerDB.user_id == user_id
    )
    containers_result = await self.db.execute(containers_stmt)
    containers = containers_result.all()
    
    container_stats = []
    total_views = 0
    total_unique_views = 0
    
    for container in containers:
        stats = await self.get_container_stats(container.id)
        container_stats.append({
            "container_id": container.id,
            "name": container.name,
            "total_views": stats["total_views"],
            "unique_views": stats["unique_views"],
        })
        total_views += stats["total_views"]
        total_unique_views += stats["unique_views"]
    
    # Sort by total_views descending
    container_stats.sort(key=lambda x: x["total_views"], reverse=True)
    
    return {
        "containers": container_stats,
        "total_views": total_views,
        "total_unique_views": total_unique_views,
    }
```

---

## 4. Backend - Service

### 4.1. Metody w `GearService` (`backend/app/modules/gear/service.py`)

```python
async def record_container_view(
    self,
    container_id: str,
    session_id: str,
    user_id: str | None = None,
    share_token: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    country: str | None = None,
    referrer: str | None = None,
) -> ContainerViewDB:
    """Record a container view.
    
    Args:
        container_id: Container ID
        session_id: Browser session ID
        user_id: Authenticated user ID (optional)
        share_token: Share token used (optional)
        ip_address: IP address (optional)
        user_agent: User agent string (optional)
        country: Country code (optional)
        referrer: Referrer URL (optional)
    
    Returns:
        Created view record
    
    Raises:
        ValueError: If container not found
    """
    # Verify container exists
    container = await self.repository.get_container(container_id, user_id)
    if not container:
        # For public/shared containers, check without user_id
        container = await self.repository.get_public_container(container_id)
        if not container:
            raise ValueError("Container not found")
    
    return await self.repository.create_container_view(
        container_id=container_id,
        session_id=session_id,
        user_id=user_id,
        share_token=share_token,
        ip_address=ip_address,
        user_agent=user_agent,
        country=country,
        referrer=referrer,
    )


async def get_container_statistics(
    self,
    container_id: str,
    user_id: str,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> ContainerStatsResponse:
    """Get container statistics (only for owner).
    
    Args:
        container_id: Container ID
        user_id: User ID (must be owner)
        start_date: Start date for filtering (optional)
        end_date: End date for filtering (optional)
    
    Returns:
        Container statistics
    
    Raises:
        ValueError: If container not found or user is not owner
    """
    # Verify ownership
    container = await self.repository.get_container(container_id, user_id)
    if not container:
        raise ValueError("Container not found or access denied")
    
    stats = await self.repository.get_container_stats(
        container_id=container_id,
        start_date=start_date,
        end_date=end_date,
    )
    
    return ContainerStatsResponse(**stats)


async def get_user_containers_statistics(
    self,
    user_id: str,
) -> UserContainersStatsResponse:
    """Get statistics for all user's containers.
    
    Args:
        user_id: User ID
    
    Returns:
        Statistics for all containers
    """
    stats = await self.repository.get_user_containers_stats(user_id)
    return UserContainersStatsResponse(**stats)
```

---

## 5. Backend - Router endpoints

### 5.1. Endpointy w `gear/router.py`

```python
@router.post(
    "/containers/{container_id}/view",
    status_code=status.HTTP_201_CREATED,
    summary="Record a container view",
    description="Records a view of a public or shared container. Can be called anonymously.",
)
async def record_container_view(
    container_id: str,
    data: ContainerViewCreate,
    request: Request,
    service: GearServiceDep,
    current_user: CurrentUser | None = None,  # Optional auth
) -> ContainerViewResponse:
    """Record a container view.
    
    Args:
        container_id: Container ID
        data: View data (session_id, share_token, etc.)
        request: FastAPI request object (for IP, user agent)
        service: Gear service instance
        current_user: Authenticated user (optional)
    
    Returns:
        Created view record
    """
    # Extract IP address and user agent from request
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    referrer = request.headers.get("referer")
    
    # Optional: Get country from IP (requires geolocation service)
    country = None  # TODO: Implement IP geolocation if needed
    
    view = await service.record_container_view(
        container_id=container_id,
        session_id=data.session_id,
        user_id=current_user.id if current_user else None,
        share_token=data.share_token,
        ip_address=ip_address,
        user_agent=user_agent,
        country=country,
        referrer=referrer,
    )
    
    return ContainerViewResponse(
        id=view.id,
        container_id=view.container_id,
        user_id=view.user_id,
        session_id=view.session_id,
        share_token=view.share_token,
        viewed_at=view.viewed_at,
        country=view.country,
    )


@router.get(
    "/containers/{container_id}/stats",
    response_model=ContainerStatsResponse,
    summary="Get container statistics",
    description="Get statistics for a container. Only accessible by container owner.",
)
async def get_container_stats(
    container_id: str,
    current_user: CurrentUser,
    start_date: datetime | None = Query(None, description="Start date for filtering"),
    end_date: datetime | None = Query(None, description="End date for filtering"),
    service: GearServiceDep,
) -> ContainerStatsResponse:
    """Get container statistics.
    
    Args:
        container_id: Container ID
        current_user: Authenticated user (must be owner)
        start_date: Start date for filtering (optional)
        end_date: End date for filtering (optional)
        service: Gear service instance
    
    Returns:
        Container statistics
    
    Raises:
        HTTPException: If container not found or access denied
    """
    try:
        return await service.get_container_statistics(
            container_id=container_id,
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.get(
    "/me/containers/stats",
    response_model=UserContainersStatsResponse,
    summary="Get user's containers statistics",
    description="Get statistics for all containers owned by the current user.",
)
async def get_user_containers_stats(
    current_user: CurrentUser,
    service: GearServiceDep,
) -> UserContainersStatsResponse:
    """Get user's containers statistics.
    
    Args:
        current_user: Authenticated user
        service: Gear service instance
    
    Returns:
        Statistics for all user's containers
    """
    return await service.get_user_containers_statistics(current_user.id)
```

---

## 6. Frontend - Service layer

### 6.1. Container Views API Service (`src/modules/gear/services/containerViewsService.ts`)

```typescript
import { apiClient } from '@/shared/services/apiClient'
import type { TUUID } from '@/shared/types'

export interface IContainerViewCreate {
  sessionId: string
  shareToken?: string | null
  ipAddress?: string | null
  userAgent?: string | null
  country?: string | null
  referrer?: string | null
}

export interface IContainerViewResponse {
  id: string
  containerId: string
  userId: string | null
  sessionId: string
  shareToken: string | null
  viewedAt: string
  country: string | null
}

export interface IContainerStatsResponse {
  containerId: string
  totalViews: number
  uniqueViews: number
  viewsByDay: Array<{ date: string; views: number }>
  viewsByWeek: Array<{ date: string; views: number }>
  viewsByMonth: Array<{ date: string; views: number }>
  viewsByToken: Array<{ token: string; views: number }>
  viewsByCountry: Array<{ country: string; views: number }>
  firstViewedAt: string | null
  lastViewedAt: string | null
}

export interface IUserContainersStatsResponse {
  containers: Array<{
    containerId: string
    name: string
    totalViews: number
    uniqueViews: number
  }>
  totalViews: number
  totalUniqueViews: number
}

class ContainerViewsApiService {
  /**
   * Record a container view
   */
  async recordView(
    containerId: TUUID,
    data: IContainerViewCreate
  ): Promise<IContainerViewResponse> {
    const response = await apiClient.post<IContainerViewResponse>(
      `/gear/containers/${containerId}/view`,
      data
    )
    return response.data
  }

  /**
   * Get container statistics
   */
  async getContainerStats(
    containerId: TUUID,
    startDate?: string,
    endDate?: string
  ): Promise<IContainerStatsResponse> {
    const params = new URLSearchParams()
    if (startDate) params.append('start_date', startDate)
    if (endDate) params.append('end_date', endDate)
    
    const response = await apiClient.get<IContainerStatsResponse>(
      `/gear/containers/${containerId}/stats?${params.toString()}`
    )
    return response.data
  }

  /**
   * Get user's all containers statistics
   */
  async getUserContainersStats(): Promise<IUserContainersStatsResponse> {
    const response = await apiClient.get<IUserContainersStatsResponse>(
      '/gear/me/containers/stats'
    )
    return response.data
  }
}

export const containerViewsService = new ContainerViewsApiService()
```

### 6.2. Session ID utility (`src/modules/gear/utils/sessionId.ts`)

```typescript
/**
 * Get or create a session ID for tracking unique views
 * Uses localStorage to persist session ID across page reloads
 */
export function getSessionId(): string {
  const STORAGE_KEY = 'gear_session_id'
  const EXPIRE_DAYS = 30 // Session expires after 30 days
  
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored) {
    const { sessionId, createdAt } = JSON.parse(stored)
    const age = Date.now() - createdAt
    const expireMs = EXPIRE_DAYS * 24 * 60 * 60 * 1000
    
    if (age < expireMs) {
      return sessionId
    }
  }
  
  // Generate new session ID
  const newSessionId = crypto.randomUUID()
  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({
      sessionId: newSessionId,
      createdAt: Date.now(),
    })
  )
  
  return newSessionId
}
```

### 6.3. Composable for tracking views (`src/modules/gear/composables/useContainerViewTracking.ts`)

```typescript
import { onMounted } from 'vue'
import { containerViewsService } from '../services/containerViewsService'
import { getSessionId } from '../utils/sessionId'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/modules/auth/store/useAuthStore'

/**
 * Composable for automatically tracking container views
 * Call this in PublicContainerDetailPage and SharedContainerDetailPage
 */
export function useContainerViewTracking(
  containerId: string,
  shareToken?: string | null
) {
  const route = useRoute()
  const authStore = useAuthStore()
  
  const trackView = async () => {
    try {
      const sessionId = getSessionId()
      
      await containerViewsService.recordView(containerId, {
        sessionId,
        shareToken: shareToken || null,
        // IP, user agent, country, referrer are handled by backend
      })
    } catch (error) {
      // Silently fail - don't interrupt user experience
      console.warn('Failed to track container view:', error)
    }
  }
  
  onMounted(() => {
    // Only track if not the owner viewing their own container
    if (authStore.isAuthenticated) {
      // TODO: Check if user is owner - if yes, skip tracking
      // For now, track all views
    }
    
    trackView()
  })
}
```

---

## 7. Frontend - Pages

### 7.1. Container Stats Page (`src/modules/gear/pages/ContainerStatsPage.vue`)

```vue
<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { useQuery } from '@tanstack/vue-query'
import AuthenticatedLayout from '@/layouts/AuthenticatedLayout.vue'
import { containerViewsService } from '../services/containerViewsService'
import { GearRoutePath } from '../routes'
import { useGearStore } from '../store/useGearStore'
// Import chart components (e.g., from vue-chartjs or similar)

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const gearStore = useGearStore()

const containerId = route.params.id as string

// Fetch container to verify ownership
const container = computed(() => gearStore.getContainerById(containerId))

// Fetch stats
const { data: stats, isLoading } = useQuery({
  queryKey: ['container-stats', containerId],
  queryFn: () => containerViewsService.getContainerStats(containerId),
  enabled: !!container.value,
})

// Date range filters
const dateRange = ref<'7d' | '30d' | '90d' | 'all'>('30d')

const filteredStats = computed(() => {
  if (!stats.value) return null
  
  const now = new Date()
  let startDate: Date | null = null
  
  switch (dateRange.value) {
    case '7d':
      startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
      break
    case '30d':
      startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
      break
    case '90d':
      startDate = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000)
      break
    case 'all':
      startDate = null
      break
  }
  
  // Filter viewsByDay, viewsByWeek, viewsByMonth by startDate
  // Implementation depends on chart library
  return stats.value
})
</script>

<template>
  <AuthenticatedLayout>
    <div class="container mx-auto p-6 space-y-6">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold">
            {{ t('gear.stats.title', 'Container Statistics') }}
          </h1>
          <p class="text-muted-foreground mt-1">
            {{ container?.name }}
          </p>
        </div>
        <Button @click="router.push(GearRoutePath.ContainerDetailById(containerId))">
          {{ t('common.back', 'Back') }}
        </Button>
      </div>

      <!-- Date range filter -->
      <div class="flex gap-2">
        <Button
          v-for="range in ['7d', '30d', '90d', 'all']"
          :key="range"
          :variant="dateRange === range ? 'default' : 'outline'"
          @click="dateRange = range"
        >
          {{ t(`gear.stats.range.${range}`, range) }}
        </Button>
      </div>

      <!-- Stats cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>{{ t('gear.stats.totalViews', 'Total Views') }}</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="text-3xl font-bold">{{ stats?.totalViews ?? 0 }}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{{ t('gear.stats.uniqueViews', 'Unique Views') }}</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="text-3xl font-bold">{{ stats?.uniqueViews ?? 0 }}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{{ t('gear.stats.lastViewed', 'Last Viewed') }}</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="text-sm">
              {{ stats?.lastViewedAt ? new Date(stats.lastViewedAt).toLocaleDateString() : '-' }}
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- Charts -->
      <Card>
        <CardHeader>
          <CardTitle>{{ t('gear.stats.viewsOverTime', 'Views Over Time') }}</CardTitle>
        </CardHeader>
        <CardContent>
          <!-- Line chart: views by day -->
          <!-- Implementation depends on chart library -->
        </CardContent>
      </Card>

      <!-- Views by token -->
      <Card v-if="stats?.viewsByToken && stats.viewsByToken.length > 0">
        <CardHeader>
          <CardTitle>{{ t('gear.stats.viewsByToken', 'Views by Share Token') }}</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{{ t('gear.stats.token', 'Token') }}</TableHead>
                <TableHead>{{ t('gear.stats.views', 'Views') }}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow
                v-for="tokenStat in stats.viewsByToken"
                :key="tokenStat.token"
              >
                <TableCell>{{ tokenStat.token.substring(0, 8) }}...</TableCell>
                <TableCell>{{ tokenStat.views }}</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <!-- Views by country -->
      <Card v-if="stats?.viewsByCountry && stats.viewsByCountry.length > 0">
        <CardHeader>
          <CardTitle>{{ t('gear.stats.viewsByCountry', 'Views by Country') }}</CardTitle>
        </CardHeader>
        <CardContent>
          <!-- Bar chart or table -->
        </CardContent>
      </Card>
    </div>
  </AuthenticatedLayout>
</template>
```

### 7.2. Update PublicContainerDetailPage

Dodać tracking w `src/modules/gear/pages/PublicContainerDetailPage.vue`:

```typescript
import { useContainerViewTracking } from '../composables/useContainerViewTracking'

// In setup:
useContainerViewTracking(containerId)
```

### 7.3. Update SharedContainerDetailPage

Dodać tracking w `src/modules/gear/pages/SharedContainerDetailPage.vue`:

```typescript
import { useContainerViewTracking } from '../composables/useContainerViewTracking'

// In setup:
const token = route.params.token as string
useContainerViewTracking(containerId, token)
```

---

## 8. Frontend - Routing

### 8.1. Update routes (`src/modules/gear/routes.ts`)

```typescript
export const GearRouteName = {
  // ... existing routes
  ContainerStats: 'gear-container-stats',
}

export const GearRoutePath = {
  // ... existing paths
  ContainerStats: '/gear/:id/stats',
  ContainerStatsById: (id: string) => `/gear/${id}/stats`,
}

// Add route:
{
  path: GearRoutePath.ContainerStats,
  name: GearRouteName.ContainerStats,
  component: () => import('../pages/ContainerStatsPage.vue'),
  meta: {
    requiresAuth: true,
  },
}
```

---

## 9. Frontend - UI Integration

### 9.1. Add stats link to container actions

W komponencie z akcjami kontenera (np. `ContainerActionsMenu.vue`), dodać link do statystyk (tylko dla właściciela):

```vue
<DropdownMenuItem
  v-if="isOwner"
  @click="router.push(GearRoutePath.ContainerStatsById(container.id))"
>
  <BarChart3 class="size-4" />
  {{ t('gear.actions.viewStats', 'View Statistics') }}
</DropdownMenuItem>
```

### 9.2. Dashboard with top containers

Opcjonalnie: dodać sekcję na dashboardzie użytkownika z top kontenerami (najczęściej oglądanymi).

---

## 10. Internationalization

### 10.1. Translation keys (`src/modules/gear/i18n/locales/pl.ts`)

```typescript
export default {
  gear: {
    stats: {
      title: 'Statystyki kontenera',
      totalViews: 'Całkowite wyświetlenia',
      uniqueViews: 'Unikalne wyświetlenia',
      lastViewed: 'Ostatnie wyświetlenie',
      viewsOverTime: 'Wyświetlenia w czasie',
      viewsByToken: 'Wyświetlenia według tokenu',
      viewsByCountry: 'Wyświetlenia według kraju',
      token: 'Token',
      views: 'Wyświetlenia',
      range: {
        '7d': '7 dni',
        '30d': '30 dni',
        '90d': '90 dni',
        all: 'Wszystkie',
      },
    },
    actions: {
      viewStats: 'Zobacz statystyki',
    },
  },
}
```

---

## 11. Testy

### 11.1. Backend tests

- Test tworzenia view record
- Test agregacji statystyk
- Test autoryzacji (tylko właściciel może zobaczyć statystyki)
- Test filtrowania po dacie
- Test unikalnych wyświetleń (session_id)

### 11.2. Frontend tests

- Test trackowania wyświetleń
- Test wyświetlania statystyk
- Test filtrowania po zakresie dat
- Test session ID persistence

---

## 12. Optymalizacje i uwagi

### 12.1. Performance

- **Indeksy bazy danych**: Zapewnić odpowiednie indeksy dla zapytań agregacyjnych
- **Caching**: Rozważyć cache dla statystyk (np. Redis) dla często oglądanych kontenerów
- **Batch inserts**: Dla wysokiego ruchu, rozważyć batch inserts zamiast pojedynczych insertów

### 12.2. Privacy & GDPR

- **Anonimizacja IP**: Rozważyć hashowanie IP addresses przed zapisem
- **Retention policy**: Określić politykę przechowywania danych (np. usuwanie starszych niż X miesięcy)
- **User consent**: Rozważyć informowanie użytkowników o trackingu (opcjonalne)

### 12.3. Rate limiting

- Ograniczyć liczbę wywołań `POST /containers/{id}/view` per IP/session (np. max 1 na minutę)

### 12.4. Geolokalizacja (opcjonalne)

- Integracja z serwisem geolokalizacji IP (np. MaxMind GeoIP2, ipapi.co)
- Pamiętać o zgodzie z GDPR (anonimowe dane, tylko kraj, nie konkretna lokalizacja)

---

## 13. Kolejność implementacji

1. **Backend - Model i migracja** (kroki 1-2)
2. **Backend - Repository i Service** (kroki 3-4)
3. **Backend - Router endpoints** (krok 5)
4. **Frontend - Service layer** (krok 6)
5. **Frontend - Tracking w istniejących stronach** (krok 7.2-7.3)
6. **Frontend - Container Stats Page** (krok 7.1)
7. **Frontend - Routing i UI integration** (kroki 8-9)
8. **Internationalization** (krok 10)
9. **Testy** (krok 11)

---

## 14. Zależności

### Backend
- SQLAlchemy (już w projekcie)
- FastAPI (już w projekcie)
- Pydantic (już w projekcie)

### Frontend
- Vue 3 (już w projekcie)
- TanStack Query (już w projekcie)
- Biblioteka do wykresów (np. `vue-chartjs`, `recharts-vue`, `chart.js` z wrapperem Vue)
- `crypto.randomUUID()` (natywne API przeglądarki)

---

## 15. Uwagi końcowe

- System powinien działać zarówno dla kontenerów publicznych, jak i udostępnionych przez token
- Właściciel kontenera nie powinien zwiększać licznika wyświetleń podczas przeglądania własnego kontenera (opcjonalnie)
- Statystyki powinny być dostępne tylko dla właściciela kontenera
- System powinien być odporny na błędy - niepowodzenie trackingu nie powinno przerywać działania aplikacji

