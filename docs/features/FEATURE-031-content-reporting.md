# FEATURE-031: Content Reporting (Zgłaszanie Nieodpowiednich Treści)

**Status:** ✅ Completed  
**Priority:** Medium  
**Category:** 🔒 Security / Content Moderation  
**Related:** ROADMAP_ONLINE.md - Zgłaszanie nieodpowiednich treści (raportowanie)

---

## 📋 Overview

System raportowania nieodpowiednich treści przez użytkowników, umożliwiający społecznościowe moderowanie treści w aplikacji. Użytkownicy mogą zgłaszać przedmioty i kontenery, które naruszają zasady społeczności.

---

## 🎯 Goals

1. **System raportowania** - możliwość zgłaszania przedmiotów i kontenerów
2. **Powody zgłoszeń** - kategoryzacja zgłoszeń (spam, obraźliwa treść, nieprawidłowe informacje, inne)
3. **Panel admina** - przeglądanie i zarządzanie zgłoszeniami przez administratorów
4. **Ochrona przed nadużyciami** - ograniczenie liczby zgłoszeń per użytkownik
5. **Statusy zgłoszeń** - śledzenie statusu zgłoszeń (pending, reviewed, dismissed, action_taken)

---

## 🔍 Current State

### ✅ Implementacja zakończona (v2.42.0)
- ✅ System raportowania treści dla publicznych kontenerów
- ✅ Tabela `content_reports` w bazie danych
- ✅ Endpointy API do zgłaszania (`POST /gear/containers/{id}/report`)
- ✅ Panel admina do zarządzania zgłoszeniami (`ContentReportsPage`)
- ✅ Automatyczne ukrywanie kontenerów po ≥3 zgłoszeniach
- ✅ Automatyczne przywracanie widoczności po weryfikacji
- ✅ Frontend komponenty: `ReportContainerButton`, `ReportContentDialog`

---

## 📝 Implementation Plan

### Phase 1: Backend - Database & Models

#### Step 1.1: Model zgłoszeń

**File:** `backend/app/modules/gear/db_models.py`

Utwórz nowy model:

```python
class ContentReportDB(Base):
    """SQLAlchemy model for content reports.
    
    Attributes:
        id: Unique identifier (ULID format)
        reported_item_id: Reported item ID (nullable)
        reported_container_id: Reported container ID (nullable)
        reporter_user_id: User who made the report
        reason: Reason for report (spam, offensive, incorrect_info, other)
        description: Additional description (optional)
        status: Report status (pending, reviewed, dismissed, action_taken)
        reviewed_at: Review timestamp (nullable)
        reviewed_by: Admin who reviewed (nullable)
        created_at: Report timestamp
    """
    
    __tablename__ = "content_reports"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    reported_item_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("gear_items.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    reported_container_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("gear_containers.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    reporter_user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        index=True
    )
    reason: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
        server_default="pending"
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    reviewed_by: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    reported_item: Mapped["GearItemDB | None"] = relationship("GearItemDB")
    reported_container: Mapped["GearContainerDB | None"] = relationship("GearContainerDB")
    reporter: Mapped["UserDB"] = relationship("UserDB", foreign_keys=[reporter_user_id])
    reviewer: Mapped["UserDB | None"] = relationship("UserDB", foreign_keys=[reviewed_by])
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "(reported_item_id IS NOT NULL) OR (reported_container_id IS NOT NULL)",
            name="check_item_or_container"
        ),
    )
```

#### Step 1.2: Enum dla powodu zgłoszenia

**File:** `backend/app/modules/gear/schemas.py`

```python
from enum import Enum

class ReportReason(str, Enum):
    SPAM = "spam"
    OFFENSIVE = "offensive"
    INCORRECT_INFO = "incorrect_info"
    OTHER = "other"

class ReportStatus(str, Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    DISMISSED = "dismissed"
    ACTION_TAKEN = "action_taken"
```

#### Step 1.3: Migracja bazy danych

**File:** `backend/alembic/versions/XXXX_add_content_reports.py`

Utwórz migrację:
1. Utworzenie tabeli `content_reports`
2. Utworzenie indeksów i constraintów
3. Utworzenie foreign keys

---

### Phase 2: Backend - Service Layer

#### Step 2.1: Service do zgłaszania treści

**File:** `backend/app/modules/gear/services/report_service.py`

```python
from datetime import datetime, timedelta
from app.modules.auth.db_models import UserDB
from app.modules.gear.db_models import ContentReportDB, GearItemDB, GearContainerDB
from app.modules.gear.schemas import ReportReason, ReportStatus

class ReportService:
    MAX_REPORTS_PER_DAY = 10  # Limit zgłoszeń per użytkownik per dzień
    
    @staticmethod
    async def can_report(
        user: UserDB,
        report_repo: "ContentReportRepository"
    ) -> tuple[bool, str]:
        """Check if user can make a report.
        
        Returns:
            (can_report: bool, reason: str)
        """
        # Check daily limit
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_reports = await report_repo.count_user_reports_since(
            user_id=user.id,
            since=today_start
        )
        
        if today_reports >= ReportService.MAX_REPORTS_PER_DAY:
            return False, f"Daily report limit reached ({ReportService.MAX_REPORTS_PER_DAY} reports per day)"
        
        return True, ""
    
    @staticmethod
    async def create_report(
        item_id: str | None,
        container_id: str | None,
        reporter: UserDB,
        reason: ReportReason,
        description: str | None,
        report_repo: "ContentReportRepository"
    ) -> ContentReportDB:
        """Create a content report."""
        # Validate: either item_id or container_id must be provided
        if not item_id and not container_id:
            raise ValueError("Either item_id or container_id must be provided")
        
        # Check if user can report
        can_report, reason_msg = await ReportService.can_report(reporter, report_repo)
        if not can_report:
            raise ValueError(reason_msg)
        
        # Check if user already reported this content
        existing_report = await report_repo.get_by_content_and_user(
            item_id=item_id,
            container_id=container_id,
            user_id=reporter.id
        )
        if existing_report and existing_report.status == ReportStatus.PENDING:
            raise ValueError("You have already reported this content")
        
        # Create report
        report = ContentReportDB(
            id=generate_ulid(),
            reported_item_id=item_id,
            reported_container_id=container_id,
            reporter_user_id=reporter.id,
            reason=reason.value,
            description=description,
            status=ReportStatus.PENDING.value
        )
        
        return await report_repo.create(report)
    
    @staticmethod
    async def update_report_status(
        report_id: str,
        status: ReportStatus,
        reviewer: UserDB,
        report_repo: "ContentReportRepository"
    ) -> ContentReportDB:
        """Update report status (admin only)."""
        report = await report_repo.get_by_id(report_id)
        if not report:
            raise ValueError("Report not found")
        
        report.status = status.value
        report.reviewed_by = reviewer.id
        report.reviewed_at = datetime.now()
        
        return await report_repo.update(report)
```

#### Step 2.2: Repository dla zgłoszeń

**File:** `backend/app/modules/gear/repositories/report_repository.py`

```python
from app.modules.gear.db_models import ContentReportDB
from datetime import datetime

class ContentReportRepository:
    async def create(self, report: ContentReportDB) -> ContentReportDB:
        """Create report."""
        # Implementation
        pass
    
    async def get_by_id(self, report_id: str) -> ContentReportDB | None:
        """Get report by ID."""
        # Implementation
        pass
    
    async def get_by_content_and_user(
        self,
        item_id: str | None,
        container_id: str | None,
        user_id: str
    ) -> ContentReportDB | None:
        """Get report by content and user."""
        # Implementation
        pass
    
    async def count_user_reports_since(
        self,
        user_id: str,
        since: datetime
    ) -> int:
        """Count user reports since date."""
        # Implementation
        pass
    
    async def get_all_pending(self) -> list[ContentReportDB]:
        """Get all pending reports."""
        # Implementation
        pass
    
    async def get_all(
        self,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0
    ) -> list[ContentReportDB]:
        """Get all reports with filters."""
        # Implementation
        pass
    
    async def update(self, report: ContentReportDB) -> ContentReportDB:
        """Update report."""
        # Implementation
        pass
```

---

### Phase 3: Backend - API Endpoints

#### Step 3.1: Endpoint zgłaszania przedmiotu

**File:** `backend/app/modules/gear/router.py`

```python
@router.post("/items/{item_id}/report")
async def report_item(
    item_id: str,
    report_data: ReportItemRequest,
    current_user: CurrentUser,
    gear_repo: GearRepository = Depends(get_gear_repository),
    report_repo: ContentReportRepository = Depends(get_report_repository),
    report_service: ReportService = Depends(get_report_service),
):
    """Report an item."""
    # Check if item exists
    item = await gear_repo.get_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    try:
        report = await report_service.create_report(
            item_id=item_id,
            container_id=None,
            reporter=current_user,
            reason=report_data.reason,
            description=report_data.description,
            report_repo=report_repo
        )
        
        return {
            "success": True,
            "report_id": report.id,
            "message": "Item reported successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

#### Step 3.2: Endpoint zgłaszania kontenera

**File:** `backend/app/modules/gear/router.py`

```python
@router.post("/containers/{container_id}/report")
async def report_container(
    container_id: str,
    report_data: ReportContainerRequest,
    current_user: CurrentUser,
    gear_repo: GearRepository = Depends(get_gear_repository),
    report_repo: ContentReportRepository = Depends(get_report_repository),
    report_service: ReportService = Depends(get_report_service),
):
    """Report a container."""
    # Check if container exists
    container = await gear_repo.get_container_by_id(container_id)
    if not container:
        raise HTTPException(status_code=404, detail="Container not found")
    
    try:
        report = await report_service.create_report(
            item_id=None,
            container_id=container_id,
            reporter=current_user,
            reason=report_data.reason,
            description=report_data.description,
            report_repo=report_repo
        )
        
        return {
            "success": True,
            "report_id": report.id,
            "message": "Container reported successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

#### Step 3.3: Endpointy admina

**File:** `backend/app/modules/admin/router.py` (lub `gear/router.py`)

```python
@router.get("/reports")
async def get_reports(
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    current_user: AdminUser = Depends(get_admin_user),
    report_repo: ContentReportRepository = Depends(get_report_repository),
):
    """Get all reports (admin only)."""
    reports = await report_repo.get_all(
        status=status,
        limit=limit,
        offset=offset
    )
    
    return {
        "reports": reports,
        "total": len(reports)
    }

@router.patch("/reports/{report_id}")
async def update_report_status(
    report_id: str,
    update_data: UpdateReportStatusRequest,
    current_user: AdminUser = Depends(get_admin_user),
    report_repo: ContentReportRepository = Depends(get_report_repository),
    report_service: ReportService = Depends(get_report_service),
):
    """Update report status (admin only)."""
    try:
        report = await report_service.update_report_status(
            report_id=report_id,
            status=update_data.status,
            reviewer=current_user,
            report_repo=report_repo
        )
        
        return {
            "success": True,
            "report": report
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

---

### Phase 4: Frontend - Types & API

#### Step 4.1: TypeScript types

**File:** `src/modules/gear/types/report.types.ts`

```typescript
export type ReportReason = 'spam' | 'offensive' | 'incorrect_info' | 'other'

export type ReportStatus = 'pending' | 'reviewed' | 'dismissed' | 'action_taken'

export interface IReportItemRequest {
  reason: ReportReason
  description?: string
}

export interface IReportContainerRequest {
  reason: ReportReason
  description?: string
}

export interface IContentReport {
  id: string
  reported_item_id?: string
  reported_container_id?: string
  reporter_user_id: string
  reason: ReportReason
  description?: string
  status: ReportStatus
  reviewed_at?: string
  reviewed_by?: string
  created_at: string
}

export interface IReportResponse {
  success: boolean
  report_id: string
  message: string
}
```

#### Step 4.2: API service

**File:** `src/modules/gear/services/reportApiService.ts`

```typescript
import { apiClient } from '@/shared/services/apiClient'
import type {
  IReportItemRequest,
  IReportContainerRequest,
  IContentReport,
  IReportResponse,
} from '../types/report.types'

export const reportApiService = {
  async reportItem(itemId: string, data: IReportItemRequest): Promise<IReportResponse> {
    const response = await apiClient.post<IReportResponse>(
      `/gear/items/${itemId}/report`,
      data
    )
    return response.data
  },
  
  async reportContainer(containerId: string, data: IReportContainerRequest): Promise<IReportResponse> {
    const response = await apiClient.post<IReportResponse>(
      `/gear/containers/${containerId}/report`,
      data
    )
    return response.data
  },
  
  async getReports(status?: string): Promise<{ reports: IContentReport[]; total: number }> {
    const response = await apiClient.get<{ reports: IContentReport[]; total: number }>(
      '/admin/reports',
      { params: { status } }
    )
    return response.data
  },
  
  async updateReportStatus(reportId: string, status: ReportStatus): Promise<IContentReport> {
    const response = await apiClient.patch<IContentReport>(
      `/admin/reports/${reportId}`,
      { status }
    )
    return response.data
  },
}
```

---

### Phase 5: Frontend - UI Components

#### Step 5.1: Dialog zgłaszania

**File:** `src/modules/gear/components/ReportContentDialog.vue`

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { useMutation } from '@tanstack/vue-query'
import { reportApiService } from '../services/reportApiService'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import type { ReportReason } from '../types/report.types'

const props = defineProps<{
  open: boolean
  itemId?: string
  containerId?: string
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
}>()

const { t } = useI18n()

const reason = ref<ReportReason>('spam')
const description = ref('')

const reportMutation = useMutation({
  mutationFn: async () => {
    if (props.itemId) {
      return reportApiService.reportItem(props.itemId, {
        reason: reason.value,
        description: description.value || undefined,
      })
    } else if (props.containerId) {
      return reportApiService.reportContainer(props.containerId, {
        reason: reason.value,
        description: description.value || undefined,
      })
    }
    throw new Error('Either itemId or containerId must be provided')
  },
  onSuccess: () => {
    toast.success(t('gear.report.success'))
    emit('update:open', false)
    reason.value = 'spam'
    description.value = ''
  },
  onError: (error: any) => {
    toast.error(error.response?.data?.detail || t('gear.report.error'))
  },
})

const handleSubmit = () => {
  reportMutation.mutate()
}
</script>

<template>
  <Dialog :open="open" @update:open="emit('update:open', $event)">
    <DialogContent>
      <DialogHeader>
        <DialogTitle>{{ t('gear.report.title') }}</DialogTitle>
      </DialogHeader>
      
      <div class="space-y-4">
        <div>
          <Label>{{ t('gear.report.reason') }}</Label>
          <Select v-model="reason">
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="spam">{{ t('gear.report.reasons.spam') }}</SelectItem>
              <SelectItem value="offensive">{{ t('gear.report.reasons.offensive') }}</SelectItem>
              <SelectItem value="incorrect_info">{{ t('gear.report.reasons.incorrectInfo') }}</SelectItem>
              <SelectItem value="other">{{ t('gear.report.reasons.other') }}</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        <div>
          <Label>{{ t('gear.report.description') }} ({{ t('common.optional') }})</Label>
          <Textarea
            v-model="description"
            :placeholder="t('gear.report.descriptionPlaceholder')"
            rows="4"
          />
        </div>
        
        <div class="flex justify-end gap-2">
          <Button variant="outline" @click="emit('update:open', false)">
            {{ t('common.cancel') }}
          </Button>
          <Button @click="handleSubmit" :disabled="reportMutation.isPending">
            {{ t('gear.report.submit') }}
          </Button>
        </div>
      </div>
    </DialogContent>
  </Dialog>
</template>
```

#### Step 5.2: Przycisk zgłaszania w menu akcji

**File:** `src/modules/gear/components/ItemHeaderActions.vue`

Dodaj opcję "Zgłoś" w dropdown menu.

**File:** `src/modules/gear/components/ContainerHeader.vue`

Dodaj opcję "Zgłoś" w menu akcji kontenera.

#### Step 5.3: Panel admina do zarządzania zgłoszeniami

**File:** `src/modules/admin/pages/ContentReportsPage.vue`

Strona z listą zgłoszeń, filtrowaniem po statusie, i możliwością aktualizacji statusu.

---

## 🎨 UI/UX Considerations

- **Dialog zgłaszania** - prosty formularz z wyborem powodu i opcjonalnym opisem
- **Toast notifications** - potwierdzenie sukcesu/błędu
- **Panel admina** - tabela z filtrowaniem i akcjami
- **Ograniczenia** - komunikaty o limitach zgłoszeń
- **Status badges** - wizualne oznaczenie statusu zgłoszeń

---

## 🔄 Future Enhancements

1. **Automatyczne blokowanie** - automatyczne ukrycie treści po przekroczeniu progu zgłoszeń
2. **Powiadomienia** - powiadomienia dla adminów o nowych zgłoszeniach
3. **Historia zgłoszeń** - historia zgłoszeń per użytkownik
4. **Kary dla nadużyć** - system kar dla użytkowników nadużywających zgłoszeń

---

## 📊 Testing

### Backend Tests

- Test tworzenia zgłoszeń
- Test limitów zgłoszeń per użytkownik
- Test unikalności zgłoszeń (użytkownik nie może zgłosić dwa razy)
- Test endpointów API
- Test panelu admina

### Frontend Tests

- Test dialogu zgłaszania
- Test przycisków zgłaszania
- Test komunikatów błędów
- Test panelu admina

---

## 📝 Notes

- Limit zgłoszeń: 10 per użytkownik per dzień (konfigurowalny)
- Użytkownik może zgłosić daną treść tylko raz (pending)
- Statusy: pending, reviewed, dismissed, action_taken
- Panel admina dostępny tylko dla administratorów
