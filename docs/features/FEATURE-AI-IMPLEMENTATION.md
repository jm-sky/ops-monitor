# FEATURE-AI - AI Integration with OpenRouter

**Status:** 🔄 Planned
**Priority:** High
**Complexity:** Large
**Version:** TBD
**Access:** Admin users only (initial release)
**Related:** [ROADMAP_ONLINE.md](../ROADMAP_ONLINE.md), [AI_PLAN.md](../plans/AI_PLAN.md)

---

## 📋 Overview

Integracja funkcji AI w Gear Stack poprzez OpenRouter API. System umożliwia:
- Automatyczną klasyfikację przedmiotów (kategorie, worn, consumable)
- Analizę i optymalizację packów (sugestie co dodać/usunąć)
- Generowanie list gearu na podstawie scenariusza
- Rozpoznawanie parametrów przedmiotów z opisów tekstowych

---

## 🎯 Goals

1. **Infrastruktura AI:**
   - Integracja z OpenRouter jako głównym providerem
   - Zarządzanie tokenami użytkownika (encrypt-at-rest)
   - Wybór modelu z listy dostępnych modeli
   - Historia wszystkich interakcji AI
   - Cache dla powtarzalnych operacji (PostgreSQL)
   - **Dostęp tylko dla adminów** w pierwszej wersji

2. **Główny flow - Chat z aktualizacją danych:**
   - Chat interface: użytkownik pisze do AI
   - AI zwraca strukturalny JSON z danymi
   - System automatycznie aktualizuje bazę danych
   - Przykład: "Dodaj kategorię do wszystkich przedmiotów" → AI zwraca JSON z kategoriami → system aktualizuje DB

3. **Funkcje AI (kolejność implementacji):**
   - **Phase 1:** Chat z aktualizacją danych (podstawowy flow)
   - **Phase 2:** Analiza i optymalizacja packów
   - **Phase 3:** Generowanie list gearu
   - **Later:** Rozpoznawanie parametrów przy imporcie Markdown

4. **UX:**
   - Guzik "AI" na ContainersListPage i ContainerDetailPage
   - Okienko chatu dla interakcji z AI
   - Edycja promptów przed wysłaniem
   - Konfiguracja kontekstu (jakie pola wysłać)
   - Przeglądanie historii i statystyk

---

## 🏗️ Architecture

### Backend Module Structure

```
backend/app/modules/ai/
├── __init__.py
├── README.md
├── router.py                 # API endpoints
├── service.py                # Business logic
├── repository.py             # Database operations
├── schemas.py                # Pydantic schemas
├── db_models.py              # SQLAlchemy models
├── exceptions.py             # Custom exceptions
├── providers/
│   ├── __init__.py
│   ├── base.py              # Abstract base provider
│   ├── openrouter.py        # OpenRouter implementation
│   └── types.py             # Provider types
├── cache/
│   ├── __init__.py
│   ├── cache_service.py     # Cache abstraction
│   ├── redis_cache.py       # Redis implementation
│   └── postgres_cache.py    # PostgreSQL implementation
├── prompts/
│   ├── __init__.py
│   ├── classify.py          # Classification prompts
│   ├── analyze.py           # Pack analysis prompts
│   ├── generate.py          # List generation prompts
│   └── recognize.py         # Parameter recognition prompts
└── utils/
    ├── __init__.py
    ├── token_counter.py     # Token counting utilities
    ├── context_builder.py   # Context preparation
    └── encryption.py        # Token encryption
```

### Frontend Module Structure

```
src/modules/ai/
├── components/
│   ├── AiChatWindow.vue         # Main chat interface
│   ├── AiModelSelector.vue      # Model selection dropdown
│   ├── AiTokenConfig.vue        # Token configuration
│   ├── AiContextConfig.vue      # Context selection
│   ├── AiHistoryViewer.vue      # History browser
│   ├── AiCostDisplay.vue        # Cost/token display
│   └── AiStatusIndicator.vue    # API status indicator
├── composables/
│   ├── useAiChat.ts             # Chat logic
│   ├── useAiModels.ts           # Model management
│   ├── useAiHistory.ts          # History management
│   └── useAiContext.ts          # Context building
├── services/
│   ├── aiApiService.ts          # API client
│   ├── aiChatService.ts         # Chat service
│   ├── aiClassifyService.ts     # Classification service
│   └── aiContextService.ts      # Context preparation
├── store/
│   └── useAiStore.ts            # Pinia store
├── types/
│   ├── index.ts
│   ├── models.ts                # AI models types
│   ├── chat.ts                  # Chat types
│   └── history.ts               # History types
├── i18n/
│   ├── index.ts
│   └── locales/
│       ├── en.json
│       └── pl.json
├── pages/
│   ├── AiChatPage.vue           # Main AI page
│   ├── AiHistoryPage.vue        # History page
│   └── AiSettingsPage.vue       # AI settings
└── routes.ts
```

---

## 📊 Database Schema

### AI User Settings

```sql
CREATE TABLE ai_user_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Token configuration
    use_own_token BOOLEAN DEFAULT FALSE,
    encrypted_api_token TEXT NULL,  -- Encrypted OpenRouter token
    token_validated_at TIMESTAMP NULL,

    -- Model selection
    selected_model VARCHAR(255) DEFAULT 'anthropic/claude-3.5-sonnet',

    -- Context preferences
    context_fields JSONB DEFAULT '["name", "category", "weight"]',

    -- Limits (for system token usage)
    monthly_token_limit INTEGER NULL,
    monthly_tokens_used INTEGER DEFAULT 0,
    monthly_cost_limit DECIMAL(10,2) NULL,
    monthly_cost_used DECIMAL(10,2) DEFAULT 0,

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    UNIQUE(user_id)
);
```

### AI History

```sql
CREATE TABLE ai_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Operation details
    operation_type VARCHAR(50) NOT NULL, -- 'chat', 'classify', 'analyze', 'generate'
    final_prompt TEXT NOT NULL,
    context_data JSONB NULL,
    response_data JSONB NOT NULL,

    -- Model and provider info
    model VARCHAR(255) NOT NULL,
    provider VARCHAR(100) NOT NULL,

    -- Token usage and cost
    tokens_input INTEGER NOT NULL,
    tokens_output INTEGER NOT NULL,
    tokens_total INTEGER NOT NULL,
    cost_input DECIMAL(10,6) NULL,
    cost_output DECIMAL(10,6) NULL,
    cost_total DECIMAL(10,6) NULL,

    -- Metadata
    duration_ms INTEGER NULL,
    used_own_token BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    INDEX idx_ai_history_user_id (user_id),
    INDEX idx_ai_history_created_at (created_at),
    INDEX idx_ai_history_operation_type (operation_type)
);
```

### AI Cache

```sql
CREATE TABLE ai_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Cache key (hash of operation + input + model)
    cache_key VARCHAR(255) NOT NULL UNIQUE,

    -- Operation details
    operation_type VARCHAR(50) NOT NULL,
    input_hash VARCHAR(255) NOT NULL,
    model VARCHAR(255) NOT NULL,

    -- Cached data
    response_data JSONB NOT NULL,

    -- Metadata
    hit_count INTEGER DEFAULT 0,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_accessed_at TIMESTAMP NOT NULL DEFAULT NOW(),

    INDEX idx_ai_cache_cache_key (cache_key),
    INDEX idx_ai_cache_expires_at (expires_at)
);
```

---

## 🔌 API Endpoints

### AI Chat (Primary Flow)

```
POST /api/ai/chat
```

**Główny flow:** Użytkownik → Chat → AI zwraca JSON → System aktualizuje DB

**Request:**
```json
{
  "prompt": "Dodaj kategorię do wszystkich moich przedmiotów",
  "context": {
    "container_ids": ["uuid1", "uuid2"],
    "fields": ["name", "description", "category"]
  },
  "model": "anthropic/claude-3.5-sonnet",
  "expect_structured_output": true  // AI powinno zwrócić JSON do aktualizacji DB
}
```

**Response:**
```json
{
  "message": "AI response text for user",
  "structured_data": {
    "action": "update_items",  // or: "create_items", "update_container", "create_container"
    "items": [
      {
        "id": "item-uuid-1",
        "updates": {
          "category": "shelter",
          "worn": true
        }
      },
      {
        "id": "item-uuid-2",
        "updates": {
          "category": "cooking",
          "consumable": true
        }
      }
    ]
  },
  "model": "anthropic/claude-3.5-sonnet",
  "provider": "anthropic",
  "tokens": {
    "input": 1250,
    "output": 430,
    "total": 1680
  },
  "cost": {
    "input": 0.00375,
    "output": 0.0215,
    "total": 0.02525
  },
  "history_id": "uuid"
}
```

**Frontend następnie:**
1. Wyświetla `message` użytkownikowi w chat
2. Parsuje `structured_data`
3. Wysyła batch update do `/api/gear/items/batch-update` (lub odpowiedniego endpointu)
4. Aktualizuje UI po sukcesie

**Przykłady użycia:**

**Przykład 1: Klasyfikacja przedmiotów**
```
Prompt: "Dodaj kategorię do wszystkich przedmiotów w kontenerze"
AI Response:
{
  "message": "Dodałem kategorie do 15 przedmiotów na podstawie ich nazw i opisów.",
  "structured_data": {
    "action": "update_items",
    "items": [
      {"id": "uuid1", "updates": {"category": "shelter"}},
      {"id": "uuid2", "updates": {"category": "cooking"}},
      ...
    ]
  }
}
```

**Przykład 2: Dodawanie nowych przedmiotów**
```
Prompt: "Wygeneruj listę przedmiotów do ultralight backpackingu"
AI Response:
{
  "message": "Wygenerowałem listę 20 przedmiotów ultralight.",
  "structured_data": {
    "action": "create_items",
    "container_id": "uuid",
    "items": [
      {
        "name": "Zpacks Duplex Tent",
        "category": "shelter",
        "weight": 595,
        "notes": "Ultralight 2-person tent"
      },
      ...
    ]
  }
}
```

**Przykład 3: Aktualizacja kontenera**
```
Prompt: "Zmień nazwę kontenera na 'Summer UL Pack' i dodaj opis"
AI Response:
{
  "message": "Zaktualizowałem nazwę i opis kontenera.",
  "structured_data": {
    "action": "update_container",
    "container_id": "uuid",
    "updates": {
      "name": "Summer UL Pack",
      "description": "Ultralight pack for summer backpacking trips"
    }
  }
}
```

### AI Classify (Batch Classification)

```
POST /api/ai/classify
```

**Request:**
```json
{
  "items": [
    {
      "id": "uuid1",
      "name": "Kurtka puchowa",
      "description": "Lekka kurtka puchowa do -10°C"
    }
  ],
  "classify_fields": ["category", "worn", "consumable"],
  "model": "anthropic/claude-3-haiku"
}
```

**Response:**
```json
{
  "classifications": [
    {
      "item_id": "uuid1",
      "category": "clothing",
      "worn": true,
      "consumable": false,
      "confidence": 0.95
    }
  ],
  "from_cache": false,
  "tokens": {
    "input": 150,
    "output": 50,
    "total": 200
  }
}
```

### AI Analyze (Pack Analysis)

```
POST /api/ai/analyze
```

**Request:**
```json
{
  "container_ids": ["uuid1"],
  "analysis_type": "completeness", // or "weight", "redundancy"
  "additional_context": "Wyjazd w góry na 3 dni, temperatura -5°C do 10°C",
  "model": "anthropic/claude-3.5-sonnet"
}
```

**Response:**
```json
{
  "analysis": {
    "missing_items": [
      {
        "name": "Czapka zimowa",
        "category": "clothing",
        "reason": "Brak nakrycia głowy przy niskich temperaturach"
      }
    ],
    "redundant_items": [],
    "suggestions": [
      "Rozważ lżejszą alternatywę dla śpiwora - obecny jest za ciężki dla tych warunków"
    ]
  },
  "tokens": {...},
  "cost": {...}
}
```

### AI Generate (Generate Pack)

```
POST /api/ai/generate
```

**Request:**
```json
{
  "scenario": "Ultralight backpacking, 2 days, summer",
  "budget": 1500,
  "currency": "USD",
  "preferences": {
    "weight_priority": "high",
    "comfort_priority": "medium"
  },
  "model": "openai/gpt-4o"
}
```

**Response:**
```json
{
  "container": {
    "name": "Ultralight Summer Pack",
    "description": "Generated pack for 2-day summer backpacking",
    "items": [
      {
        "name": "Zpacks Duplex Tent",
        "category": "shelter",
        "weight": 595,
        "quantity": 1,
        "price": 699,
        "url": "https://zpacks.com/...",
        "notes": "Ultralight 2-person tent"
      }
    ]
  },
  "total_weight": 4500,
  "total_cost": 1450,
  "tokens": {...},
  "cost": {...}
}
```

### Models List

```
GET /api/ai/models
```

**Response:**
```json
{
  "models": [
    {
      "id": "anthropic/claude-3.5-sonnet",
      "name": "Claude 3.5 Sonnet",
      "provider": "anthropic",
      "context_window": 200000,
      "pricing": {
        "input": 3.0,  // per 1M tokens
        "output": 15.0
      },
      "recommended_for": ["chat", "analyze", "generate"],
      "available": true
    },
    {
      "id": "anthropic/claude-3-haiku",
      "name": "Claude 3 Haiku",
      "provider": "anthropic",
      "context_window": 200000,
      "pricing": {
        "input": 0.25,
        "output": 1.25
      },
      "recommended_for": ["classify"],
      "available": true
    }
  ]
}
```

### History

```
GET /api/ai/history?limit=50&offset=0&operation_type=chat
```

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "operation_type": "chat",
      "final_prompt": "...",
      "response_preview": "Na podstawie Twojej listy...",
      "model": "anthropic/claude-3.5-sonnet",
      "tokens_total": 1680,
      "cost_total": 0.02525,
      "created_at": "2025-11-26T12:00:00Z"
    }
  ],
  "total": 123,
  "limit": 50,
  "offset": 0
}
```

```
GET /api/ai/history/:id
```

**Response:**
```json
{
  "id": "uuid",
  "operation_type": "chat",
  "final_prompt": "Full prompt text...",
  "context_data": {...},
  "response_data": {...},
  "model": "anthropic/claude-3.5-sonnet",
  "provider": "anthropic",
  "tokens": {...},
  "cost": {...},
  "duration_ms": 2340,
  "created_at": "2025-11-26T12:00:00Z"
}
```

```
DELETE /api/ai/history/:id
DELETE /api/ai/history  (clear all)
```

### Settings

```
GET /api/ai/settings
PUT /api/ai/settings
```

**Response/Request:**
```json
{
  "use_own_token": true,
  "selected_model": "anthropic/claude-3.5-sonnet",
  "context_fields": ["name", "category", "weight", "description"],
  "monthly_tokens_used": 50000,
  "monthly_cost_used": 1.25
}
```

```
POST /api/ai/settings/token
```

**Request:**
```json
{
  "api_token": "sk-or-v1-..."
}
```

**Response:**
```json
{
  "validated": true,
  "message": "Token validated successfully"
}
```

```
DELETE /api/ai/settings/token
```

---

## 🔐 Security

### Token Encryption

Tokeny użytkowników są szyfrowane w bazie danych:

```python
# backend/app/modules/ai/utils/encryption.py

from cryptography.fernet import Fernet
import base64
from app.core.config import settings

def get_cipher():
    """Get Fernet cipher with key from settings."""
    key = settings.AI_TOKEN_ENCRYPTION_KEY
    return Fernet(key)

def encrypt_token(token: str) -> str:
    """Encrypt API token."""
    cipher = get_cipher()
    encrypted = cipher.encrypt(token.encode())
    return base64.b64encode(encrypted).decode()

def decrypt_token(encrypted_token: str) -> str:
    """Decrypt API token."""
    cipher = get_cipher()
    decoded = base64.b64decode(encrypted_token)
    return cipher.decrypt(decoded).decode()
```

### Token Validation

```python
# backend/app/modules/ai/service.py

async def validate_token(self, token: str) -> bool:
    """Validate OpenRouter token with test API call."""
    try:
        provider = OpenRouterProvider(api_key=token)
        # Simple test request with minimal cost
        response = await provider.chat(
            model="anthropic/claude-3-haiku",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=1
        )
        return True
    except Exception as e:
        logger.error(f"Token validation failed: {e}")
        return False
```

---

## 💾 Cache Strategy

### Cache Implementation

```python
# backend/app/modules/ai/cache/cache_service.py

from abc import ABC, abstractmethod
from typing import Any, Optional
from datetime import datetime, timedelta
import hashlib
import json

class CacheService(ABC):
    """Abstract cache service."""

    @abstractmethod
    async def get(self, key: str) -> Optional[dict]:
        """Get cached value."""
        pass

    @abstractmethod
    async def set(self, key: str, value: dict, ttl_days: int):
        """Set cached value with TTL."""
        pass

    @abstractmethod
    async def delete(self, key: str):
        """Delete cached value."""
        pass

    @staticmethod
    def generate_cache_key(
        operation_type: str,
        input_data: dict,
        model: str
    ) -> str:
        """Generate cache key from operation parameters."""
        # Sort keys for consistent hashing
        input_str = json.dumps(input_data, sort_keys=True)
        hash_input = f"{operation_type}:{input_str}:{model}"
        return hashlib.sha256(hash_input.encode()).hexdigest()
```

### PostgreSQL Implementation

```python
# backend/app/modules/ai/cache/postgres_cache.py

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from .cache_service import CacheService
from ..db_models import AICacheDB

class PostgresCacheService(CacheService):
    """PostgreSQL-based cache implementation."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, key: str) -> Optional[dict]:
        """Get from PostgreSQL cache."""
        result = await self.db.execute(
            select(AICacheDB)
            .where(AICacheDB.cache_key == key)
            .where(AICacheDB.expires_at > datetime.utcnow())
        )
        cache = result.scalar_one_or_none()

        if cache:
            # Update hit count and last access
            cache.hit_count += 1
            cache.last_accessed_at = datetime.utcnow()
            await self.db.commit()
            return cache.response_data

        return None

    async def set(self, key: str, value: dict, ttl_days: int):
        """Set in PostgreSQL cache."""
        expires_at = datetime.utcnow() + timedelta(days=ttl_days)

        cache = AICacheDB(
            cache_key=key,
            response_data=value,
            expires_at=expires_at
        )
        self.db.add(cache)
        await self.db.commit()
```

### Cache Usage

```python
# backend/app/modules/ai/service.py

async def classify_items(
    self,
    items: list[dict],
    model: str,
    use_cache: bool = True
) -> list[dict]:
    """Classify items with caching."""

    results = []

    for item in items:
        cache_key = None

        if use_cache:
            cache_key = CacheService.generate_cache_key(
                operation_type="classify",
                input_data={"name": item["name"], "description": item.get("description")},
                model=model
            )

            cached = await self.cache.get(cache_key)
            if cached:
                results.append({**cached, "from_cache": True})
                continue

        # Not in cache - call API
        classification = await self._call_classify_api(item, model)
        results.append({**classification, "from_cache": False})

        # Save to cache
        if use_cache and cache_key:
            await self.cache.set(
                key=cache_key,
                value=classification,
                ttl_days=7  # 7 days for classifications
            )

    return results
```

---

## 🎨 Frontend Implementation

### UI Integration - AI Buttons

**Lokalizacje guzików AI:**

1. **ContainersListPage** - guzik AI w górnej akcjowej sekcji
2. **ContainerDetailPage** - guzik AI obok innych akcji kontenera

**Access Control:**
- Guziki AI widoczne tylko dla adminów (`isAdmin = true`)
- Frontend sprawdza `currentUser.isAdmin` przed pokazaniem
- Backend weryfikuje w middleware

**Implementacja guzików:**

```vue
<!-- src/modules/gear/pages/ContainersListPage.vue -->

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/modules/auth/store/useAuthStore'
import { getActionIcon } from '@/modules/gear/utils/actionIcons'
import AiChatDialog from '@/modules/ai/components/AiChatDialog.vue'

const authStore = useAuthStore()
const isAdmin = computed(() => authStore.currentUser?.isAdmin ?? false)

const AiIcon = getActionIcon('ai')  // Dodamy nową ikonę 'ai' do actionIcons.ts

const showAiDialog = ref(false)

const openAiChat = () => {
  showAiDialog.value = true
}
</script>

<template>
  <div class="container">
    <!-- Existing header actions -->
    <div class="flex items-center justify-between mb-4">
      <h1>Containers</h1>
      <div class="flex gap-2">
        <!-- Existing buttons (Create, Import, etc.) -->

        <!-- AI Button (admin only) -->
        <Button
          v-if="isAdmin"
          variant="outline"
          @click="openAiChat"
        >
          <AiIcon class="size-4" />
          AI Assistant
        </Button>
      </div>
    </div>

    <!-- Rest of the page -->
    <!-- ... -->

    <!-- AI Chat Dialog -->
    <AiChatDialog
      v-if="isAdmin"
      v-model:open="showAiDialog"
      :context="{ container_ids: selectedContainerIds }"
    />
  </div>
</template>
```

```vue
<!-- src/modules/gear/pages/ContainerDetailPage.vue -->

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/modules/auth/store/useAuthStore'
import { getActionIcon } from '@/modules/gear/utils/actionIcons'
import AiChatDialog from '@/modules/ai/components/AiChatDialog.vue'

const authStore = useAuthStore()
const isAdmin = computed(() => authStore.currentUser?.isAdmin ?? false)

const AiIcon = getActionIcon('ai')

const showAiDialog = ref(false)
const containerId = ref<string>()  // From route params

const openAiChat = () => {
  showAiDialog.value = true
}
</script>

<template>
  <div class="container">
    <!-- Container header -->
    <div class="flex items-center justify-between mb-4">
      <h1>{{ container.name }}</h1>
      <div class="flex gap-2">
        <!-- Existing actions (Edit, Delete, Export, etc.) -->

        <!-- AI Button (admin only) -->
        <Button
          v-if="isAdmin"
          variant="outline"
          @click="openAiChat"
        >
          <AiIcon class="size-4" />
          AI
        </Button>
      </div>
    </div>

    <!-- Rest of the page -->
    <!-- ... -->

    <!-- AI Chat Dialog -->
    <AiChatDialog
      v-if="isAdmin"
      v-model:open="showAiDialog"
      :context="{ container_ids: [containerId] }"
    />
  </div>
</template>
```

**Action Icon mapping:**

```typescript
// src/modules/gear/utils/actionIcons.ts

import { Sparkles } from 'lucide-vue-next'

export const actionIconsMap = {
  // ... existing icons
  ai: Sparkles,  // Nowa ikona dla AI
} as const
```

**Backend middleware:**

```python
# backend/app/modules/ai/dependencies.py

from fastapi import Depends, HTTPException, status
from app.modules.auth.dependencies import CurrentUser

async def require_admin(current_user: CurrentUser) -> CurrentUser:
    """Require admin user for AI endpoints."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AI features are only available for admin users"
        )
    return current_user

# Usage in router:
# @router.post("/chat")
# async def chat(
#     request: ChatRequest,
#     admin_user: CurrentUser = Depends(require_admin)
# ):
#     ...
```

---

### AI Chat Component

```vue
<!-- src/modules/ai/components/AiChatWindow.vue -->

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useAiChat } from '../composables/useAiChat'
import { useAiStore } from '../store/useAiStore'
import AiModelSelector from './AiModelSelector.vue'
import AiContextConfig from './AiContextConfig.vue'
import AiCostDisplay from './AiCostDisplay.vue'

const aiStore = useAiStore()
const { sendMessage, isLoading, messages } = useAiChat()

const userMessage = ref('')
const showContextConfig = ref(false)

const handleSend = async () => {
  if (!userMessage.value.trim()) return

  await sendMessage(userMessage.value)
  userMessage.value = ''
}

const selectedModel = computed(() => aiStore.selectedModel)
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- Header with model selector -->
    <div class="flex items-center justify-between border-b p-4">
      <h2 class="text-lg font-semibold">AI Assistant</h2>
      <div class="flex items-center gap-2">
        <AiModelSelector />
        <Button
          variant="outline"
          size="sm"
          @click="showContextConfig = !showContextConfig"
        >
          <Settings class="size-4" />
          Context
        </Button>
      </div>
    </div>

    <!-- Context config (collapsible) -->
    <AiContextConfig v-if="showContextConfig" />

    <!-- Messages -->
    <div class="flex-1 overflow-y-auto p-4 space-y-4">
      <div
        v-for="message in messages"
        :key="message.id"
        :class="[
          'p-3 rounded-lg',
          message.role === 'user'
            ? 'bg-primary text-primary-foreground ml-auto max-w-[80%]'
            : 'bg-muted max-w-[80%]'
        ]"
      >
        <div class="text-sm" v-html="message.content" />
        <AiCostDisplay
          v-if="message.role === 'assistant' && message.tokens"
          :tokens="message.tokens"
          :cost="message.cost"
          class="mt-2"
        />
      </div>

      <div v-if="isLoading" class="flex items-center gap-2">
        <Loader2 class="size-4 animate-spin" />
        <span class="text-sm text-muted-foreground">AI is thinking...</span>
      </div>
    </div>

    <!-- Input -->
    <div class="border-t p-4">
      <div class="flex gap-2">
        <Textarea
          v-model="userMessage"
          placeholder="Ask AI about your gear..."
          :rows="3"
          @keydown.ctrl.enter="handleSend"
        />
        <Button
          :disabled="!userMessage.trim() || isLoading"
          @click="handleSend"
        >
          <Send class="size-4" />
        </Button>
      </div>
      <p class="text-xs text-muted-foreground mt-2">
        Ctrl+Enter to send
      </p>
    </div>
  </div>
</template>
```

### AI Store

```typescript
// src/modules/ai/store/useAiStore.ts

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { IAiModel, IAiSettings, IAiHistoryItem } from '../types'
import { aiApiService } from '../services/aiApiService'

export const useAiStore = defineStore('ai', () => {
  // State
  const settings = ref<IAiSettings | null>(null)
  const availableModels = ref<IAiModel[]>([])
  const history = ref<IAiHistoryItem[]>([])
  const isLoading = ref(false)

  // Computed
  const selectedModel = computed(() =>
    availableModels.value.find(m => m.id === settings.value?.selected_model)
  )

  const hasOwnToken = computed(() => settings.value?.use_own_token ?? false)

  const monthlyUsage = computed(() => ({
    tokens: settings.value?.monthly_tokens_used ?? 0,
    cost: settings.value?.monthly_cost_used ?? 0,
    tokenLimit: settings.value?.monthly_token_limit,
    costLimit: settings.value?.monthly_cost_limit,
  }))

  // Actions
  const loadSettings = async () => {
    isLoading.value = true
    try {
      settings.value = await aiApiService.getSettings()
    } finally {
      isLoading.value = false
    }
  }

  const updateSettings = async (updates: Partial<IAiSettings>) => {
    isLoading.value = true
    try {
      settings.value = await aiApiService.updateSettings(updates)
    } finally {
      isLoading.value = false
    }
  }

  const loadModels = async () => {
    isLoading.value = true
    try {
      const response = await aiApiService.getModels()
      availableModels.value = response.models
    } finally {
      isLoading.value = false
    }
  }

  const setApiToken = async (token: string) => {
    await aiApiService.setApiToken(token)
    await loadSettings()
  }

  const removeApiToken = async () => {
    await aiApiService.removeApiToken()
    await loadSettings()
  }

  const loadHistory = async (params?: { limit?: number; offset?: number; operation_type?: string }) => {
    isLoading.value = true
    try {
      const response = await aiApiService.getHistory(params)
      history.value = response.items
      return response
    } finally {
      isLoading.value = false
    }
  }

  const deleteHistoryItem = async (id: string) => {
    await aiApiService.deleteHistoryItem(id)
    history.value = history.value.filter(item => item.id !== id)
  }

  const clearHistory = async () => {
    await aiApiService.clearHistory()
    history.value = []
  }

  return {
    // State
    settings,
    availableModels,
    history,
    isLoading,

    // Computed
    selectedModel,
    hasOwnToken,
    monthlyUsage,

    // Actions
    loadSettings,
    updateSettings,
    loadModels,
    setApiToken,
    removeApiToken,
    loadHistory,
    deleteHistoryItem,
    clearHistory,
  }
})
```

---

## 📝 Implementation Phases

**Note:** Implementacja zaczyna się od Chat, następnie Classification i Analysis/Generation. Rozpoznawanie parametrów przy imporcie Markdown zostaje na później.

### Phase 1: Infrastructure & Admin Access (Week 1-2)

**Backend:**
- [ ] Create AI module structure (`backend/app/modules/ai/`)
- [ ] Implement OpenRouter provider (basic chat endpoint)
- [ ] Database migrations (ai_user_settings, ai_history, ai_cache)
- [ ] Token encryption utilities (Fernet)
- [ ] Cache service (PostgreSQL implementation only)
- [ ] Admin middleware (`require_admin` dependency)
- [ ] Basic error handling and logging

**Frontend:**
- [ ] Create AI module structure (`src/modules/ai/`)
- [ ] AI store with Pinia (basic state management)
- [ ] Basic API service (aiApiService.ts)
- [ ] Types and interfaces (models, chat, history)
- [ ] Add `ai` icon to actionIcons.ts (Sparkles)

**Testing:**
- [ ] Unit tests for encryption utilities
- [ ] Unit tests for cache service (PostgreSQL)
- [ ] Integration tests for OpenRouter provider
- [ ] Admin middleware tests

### Phase 2: Chat Interface with Structured Output (Week 2-3)

**Backend:**
- [ ] Chat prompts with structured output support
- [ ] POST /ai/chat endpoint
  - [ ] `expect_structured_output` parameter
  - [ ] Structured response parsing (JSON extraction)
  - [ ] Action types: update_items, create_items, update_container, create_container
- [ ] Context builder utility (builds context from container/item data)
- [ ] History recording (full prompt, response, structured_data, tokens, cost)
- [ ] Settings endpoints (GET/PUT /ai/settings)
- [ ] Token management (POST/DELETE /ai/settings/token)
- [ ] Models list endpoint (GET /ai/models)

**Frontend:**
- [ ] AiChatDialog component (modal with chat interface)
- [ ] Model selector component
- [ ] Context configuration (which fields to send)
- [ ] Chat composable (useAiChat.ts)
- [ ] Message display with cost/tokens
- [ ] Structured data parser and DB update logic
  - [ ] Handle update_items action
  - [ ] Handle create_items action
  - [ ] Handle update_container action
  - [ ] Handle create_container action
- [ ] Integration in ContainersListPage (AI button)
- [ ] Integration in ContainerDetailPage (AI button)
- [ ] AI Settings page (token config, model selection)

**Testing:**
- [ ] Chat endpoint tests
- [ ] Structured output parsing tests
- [ ] Context builder tests
- [ ] Frontend chat component tests
- [ ] End-to-end: chat → structured data → DB update

### Phase 3: History & Monitoring (Week 3-4)

**Backend:**
- [ ] History endpoints (GET, DELETE)
- [ ] GET /ai/history (list with filters)
- [ ] GET /ai/history/:id (detail)
- [ ] DELETE /ai/history/:id (single)
- [ ] DELETE /ai/history (clear all)
- [ ] Usage statistics calculation
- [ ] Health check for OpenRouter (optional)

**Frontend:**
- [ ] History viewer page
- [ ] History list with filters (date, operation_type, model)
- [ ] History detail view (full prompt, response, context)
- [ ] Usage statistics display (tokens used, cost)
- [ ] Cost tracking UI
- [ ] History search and filtering

**Testing:**
- [ ] History endpoint tests
- [ ] Statistics calculation tests
- [ ] Frontend history viewer tests

### Phase 4: Analysis & Optimization (Week 4-5)

**Backend:**
- [ ] Analysis prompts (completeness, weight, redundancy)
- [ ] Enhanced chat endpoint for analysis tasks
- [ ] Structured output for analysis results
  - [ ] Missing items suggestions
  - [ ] Redundant items detection
  - [ ] Weight optimization suggestions

**Frontend:**
- [ ] Analysis UI in chat dialog
- [ ] Pre-built prompts for common analysis tasks
  - [ ] "Analyze pack completeness"
  - [ ] "Find redundant items"
  - [ ] "Optimize weight"
- [ ] Results display with actionable items
- [ ] One-click apply suggestions

**Testing:**
- [ ] Analysis prompt tests
- [ ] Structured output validation
- [ ] End-to-end analysis workflow

### Phase 5: Generation (Week 5-6)

**Backend:**
- [ ] Generation prompts
- [ ] Structured output for generated packs
  - [ ] Container metadata (name, description)
  - [ ] Items list with full details
- [ ] Budget and weight constraints

**Frontend:**
- [ ] Generate pack form in chat dialog
- [ ] Pre-built scenario templates
  - [ ] "Ultralight backpacking"
  - [ ] "Winter camping"
  - [ ] "EDC setup"
- [ ] Budget and preference inputs
- [ ] Import generated items to existing/new container

**Testing:**
- [ ] Generation prompt tests
- [ ] Generated data validation
- [ ] Import workflow tests

### Phase 6: Polish & Documentation (Week 6)

- [ ] Error handling improvements
- [ ] Rate limiting (for future non-admin users)
- [ ] Admin documentation
- [ ] Performance optimization
- [ ] Security audit
- [ ] Production deployment
- [ ] Cache cleanup job (expired entries)

### Future Phases (Post-MVP)

**Phase 7: Classification (Later)**
- [ ] Batch classification endpoint
- [ ] Integration with item forms
- [ ] "Recognize parameters" action

**Phase 8: Markdown Import Integration (Later)**
- [ ] AI parameter recognition during Markdown import
- [ ] Automatic category/worn/consumable detection
- [ ] Integration with existing import dialog

---

## ✅ Acceptance Criteria

### Must Have (MVP)

1. **Infrastructure:**
   - ✅ OpenRouter integration working
   - ✅ Token encryption implemented
   - ✅ Database models created (ai_user_settings, ai_history, ai_cache)
   - ✅ PostgreSQL cache service working
   - ✅ Admin-only access implemented (frontend + backend)

2. **Admin User Management:**
   - ✅ Admins can add/remove their own tokens
   - ✅ Token validation on save
   - ✅ Model selection from 10 available models
   - ✅ Context configuration (which fields to send)

3. **Core Feature - Chat with Structured Output:**
   - ✅ Chat interface functional (AiChatDialog)
   - ✅ AI returns structured JSON
   - ✅ System parses and applies updates to DB
   - ✅ Supports actions: update_items, create_items, update_container, create_container
   - ✅ AI buttons visible on ContainersListPage and ContainerDetailPage (admin only)

4. **History:**
   - ✅ All interactions recorded in DB
   - ✅ History browsable (list + detail view)
   - ✅ Can delete history items
   - ✅ Full context preserved (prompt, response, structured_data, tokens, cost)

5. **Cost Tracking:**
   - ✅ Token usage displayed per request
   - ✅ Cost calculated per request
   - ✅ Usage statistics visible

6. **Security:**
   - ✅ Tokens encrypted at rest (Fernet)
   - ✅ API authentication required
   - ✅ Admin middleware protecting AI endpoints
   - ✅ Error messages don't leak sensitive data

### Should Have (Phase 2)

1. **Analysis:**
   - ✅ Pack completeness analysis
   - ✅ Weight optimization suggestions
   - ✅ Redundancy detection
   - ✅ Pre-built analysis prompts

2. **Generation:**
   - ✅ Generate pack from scenario
   - ✅ Budget and preference constraints
   - ✅ Import generated items to container

3. **UX Improvements:**
   - ✅ Clear cost/token display in chat
   - ✅ Model selector with descriptions
   - ✅ Context configuration UI
   - ✅ Pre-built prompt templates

### Nice to Have (Future)

1. **Classification:**
   - ⏸️ Batch classification endpoint
   - ⏸️ Integration with item forms
   - ⏸️ Markdown import parameter recognition

2. **Advanced Features:**
   - ⏸️ Re-run saved prompts
   - ⏸️ Favorite models
   - ⏸️ Usage analytics dashboard
   - ⏸️ Rate limiting for non-admin users

3. **Optimizations:**
   - ⏸️ Redis cache implementation
   - ⏸️ Streaming responses (for long generations)
   - ⏸️ Context compression

---

## 🚨 Risks & Mitigations

### Risk 1: OpenRouter API Downtime

**Impact:** High
**Probability:** Low
**Mitigation:**
- Clear error messages to users
- Health check monitoring
- Status page integration
- No automatic retries (avoid costs)

### Risk 2: High API Costs

**Impact:** High (for system token)
**Probability:** Medium
**Mitigation:**
- Strict rate limiting for system token
- Cache all classifiable operations
- Encourage users to use own tokens
- Monthly cost limits per user

### Risk 3: Token Security

**Impact:** Critical
**Probability:** Low
**Mitigation:**
- Encrypt-at-rest for all tokens
- Secure key management
- Regular security audits
- Token validation on save

### Risk 4: Poor AI Responses

**Impact:** Medium
**Probability:** Medium
**Mitigation:**
- Clear disclaimer on first use
- User can edit prompts
- Multiple model options
- History for debugging

### Risk 5: Context Size Limits

**Impact:** Medium
**Probability:** Medium
**Mitigation:**
- Token counting before send
- Clear error messages
- User-configurable context fields
- Model context window displayed

---

## 📖 Documentation Requirements

### User Documentation

1. **Getting Started Guide:**
   - How to add API token
   - Choosing a model
   - Understanding costs

2. **Feature Guides:**
   - Classifying items
   - Analyzing packs
   - Generating pack lists
   - Using chat interface

3. **FAQ:**
   - Token security
   - Cost management
   - Model recommendations
   - Troubleshooting

### Admin Documentation

1. **Setup Guide:**
   - Environment variables
   - Database migrations
   - OpenRouter account setup
   - Encryption key generation

2. **Monitoring Guide:**
   - Health checks
   - Cost tracking
   - Error monitoring
   - Performance metrics

3. **Maintenance Guide:**
   - Cache management
   - History cleanup
   - Model list updates

---

## 🔧 Configuration

### Environment Variables

```bash
# OpenRouter Configuration
OPENROUTER_API_KEY=sk-or-v1-...  # System token
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Encryption
AI_TOKEN_ENCRYPTION_KEY=...  # Generate with Fernet.generate_key()

# Cache
AI_CACHE_ENABLED=true
AI_CACHE_TTL_CLASSIFY=7  # days
AI_CACHE_TTL_EMBED=30    # days

# Limits (for system token)
AI_SYSTEM_TOKEN_MONTHLY_LIMIT=1000000  # tokens
AI_SYSTEM_TOKEN_COST_LIMIT=50.00       # USD

# Monitoring
AI_HEALTH_CHECK_INTERVAL=300  # seconds
```

### Model Configuration

```python
# backend/app/modules/ai/config.py

AVAILABLE_MODELS = [
    # Top-tier models (best quality, higher cost)
    {
        "id": "anthropic/claude-3.5-sonnet",
        "name": "Claude 3.5 Sonnet",
        "provider": "anthropic",
        "context_window": 200000,
        "pricing": {"input": 3.0, "output": 15.0},
        "recommended_for": ["chat", "analyze", "generate"],
        "description": "Best for complex analysis and generation",
    },
    {
        "id": "openai/gpt-4o",
        "name": "GPT-4o",
        "provider": "openai",
        "context_window": 128000,
        "pricing": {"input": 5.0, "output": 15.0},
        "recommended_for": ["chat", "analyze"],
        "description": "OpenAI's most capable model",
    },
    {
        "id": "google/gemini-pro-1.5",
        "name": "Gemini Pro 1.5",
        "provider": "google",
        "context_window": 1000000,
        "pricing": {"input": 1.25, "output": 5.0},
        "recommended_for": ["chat", "analyze"],
        "description": "Huge context window, good for large datasets",
    },

    # Mid-tier models (good balance)
    {
        "id": "anthropic/claude-3.5-haiku",
        "name": "Claude 3.5 Haiku",
        "provider": "anthropic",
        "context_window": 200000,
        "pricing": {"input": 1.0, "output": 5.0},
        "recommended_for": ["chat", "classify"],
        "description": "Fast and cost-effective, good quality",
    },
    {
        "id": "openai/gpt-4o-mini",
        "name": "GPT-4o Mini",
        "provider": "openai",
        "context_window": 128000,
        "pricing": {"input": 0.15, "output": 0.6},
        "recommended_for": ["classify", "chat"],
        "description": "Affordable with good performance",
    },
    {
        "id": "meta-llama/llama-3.1-70b-instruct",
        "name": "Llama 3.1 70B",
        "provider": "meta",
        "context_window": 128000,
        "pricing": {"input": 0.52, "output": 0.75},
        "recommended_for": ["chat", "analyze"],
        "description": "Open-source, good value",
    },
    {
        "id": "google/gemini-flash-1.5",
        "name": "Gemini Flash 1.5",
        "provider": "google",
        "context_window": 1000000,
        "pricing": {"input": 0.075, "output": 0.30},
        "recommended_for": ["classify", "chat"],
        "description": "Very fast with huge context",
    },

    # Budget models (lowest cost)
    {
        "id": "anthropic/claude-3-haiku",
        "name": "Claude 3 Haiku",
        "provider": "anthropic",
        "context_window": 200000,
        "pricing": {"input": 0.25, "output": 1.25},
        "recommended_for": ["classify"],
        "description": "Most affordable, good for simple tasks",
    },
    {
        "id": "meta-llama/llama-3.1-8b-instruct",
        "name": "Llama 3.1 8B",
        "provider": "meta",
        "context_window": 128000,
        "pricing": {"input": 0.05, "output": 0.08},
        "recommended_for": ["classify"],
        "description": "Ultra-cheap, basic tasks only",
    },
    {
        "id": "mistralai/mistral-7b-instruct",
        "name": "Mistral 7B Instruct",
        "provider": "mistral",
        "context_window": 32000,
        "pricing": {"input": 0.06, "output": 0.06},
        "recommended_for": ["classify"],
        "description": "Budget option for simple classification",
    },
]

# Default model for new users
DEFAULT_MODEL = "anthropic/claude-3.5-haiku"

# Recommended models per task
TASK_RECOMMENDATIONS = {
    "chat": [
        "anthropic/claude-3.5-sonnet",
        "anthropic/claude-3.5-haiku",
        "openai/gpt-4o",
        "google/gemini-pro-1.5",
    ],
    "classify": [
        "anthropic/claude-3.5-haiku",
        "openai/gpt-4o-mini",
        "google/gemini-flash-1.5",
        "anthropic/claude-3-haiku",
    ],
    "analyze": [
        "anthropic/claude-3.5-sonnet",
        "openai/gpt-4o",
        "google/gemini-pro-1.5",
        "meta-llama/llama-3.1-70b-instruct",
    ],
    "generate": [
        "anthropic/claude-3.5-sonnet",
        "openai/gpt-4o",
        "google/gemini-pro-1.5",
    ],
}
```

---

## 🎯 Success Metrics

### Technical Metrics

- **API Response Time:** < 5s for chat, < 2s for classify
- **Cache Hit Rate:** > 50% for classifications
- **Error Rate:** < 1% of requests
- **Uptime:** 99.9% availability

### Business Metrics

- **Adoption Rate:** % of users who try AI features
- **Token Usage:** Average tokens per user per month
- **Cost Efficiency:** Cache savings vs direct API calls
- **User Satisfaction:** Feedback ratings on AI responses

### User Experience Metrics

- **Time to First AI Response:** < 10s from account creation
- **Classification Accuracy:** User correction rate < 20%
- **Feature Discovery:** % users who find AI settings

---

## 📚 References

- [OpenRouter Documentation](https://openrouter.ai/docs)
- [OpenRouter Models List](https://openrouter.ai/models)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [OpenAI API](https://platform.openai.com/docs)
- [Cryptography Library](https://cryptography.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pinia Documentation](https://pinia.vuejs.org/)

---

## 📝 Summary of Key Decisions

1. **Admin-Only Access:** Funkcje AI dostępne tylko dla administratorów w pierwszej wersji
2. **PostgreSQL Cache:** Bez Redis na początku - tylko PostgreSQL
3. **Chat-First Approach:** Zaczynamy od Chat z structured output, potem Analysis i Generation
4. **Structured Output:** AI zwraca JSON, który system automatycznie aplikuje do bazy danych
5. **10 Models:** Lista 10 starannie wybranych modeli (top-tier, mid-tier, budget)
6. **UI Integration:** Guziki AI na ContainersListPage i ContainerDetailPage
7. **No Plans/Limits:** Brak systemów planów i limitów - każdy admin może używać własnego tokena
8. **Classification Later:** Rozpoznawanie parametrów i import Markdown zostają na późniejsze fazy

---

**Last Updated:** 2025-11-26
**Author:** Gear Stack Team
**Status:** Ready for implementation
