# FEATURE-AI-CHAT-ENHANCEMENTS: Rozszerzenie funkcjonalności AI Chat

**Status:** ✅ Completed  
**Priority:** Medium  
**Complexity:** Medium  
**Related:** [FEATURE-AI-IMPLEMENTATION.md](./FEATURE-AI-IMPLEMENTATION.md), [ROADMAP_ONLINE.md](../ROADMAP_ONLINE.md)

## 📋 Overview

Rozszerzenie funkcjonalności AI chat o:
1. Dodanie pola `container_ids` do modelu historii dla efektywnego filtrowania
2. Czat z poziomu Listy Kontenerów z możliwością załączenia przefiltrowanych kontenerów
3. Resume chat z AI History Page z automatycznym przekierowaniem i otwieraniem czatu
4. Panel historii w oknie czatu używając Sheet component z shadcn-vue

## 🎯 Goals

1. **Pole container_ids w historii:**
   - Dodanie dedykowanego pola `container_ids: string[] | null` w modelu historii
   - Migracja bazy danych z wypełnieniem istniejących danych
   - Efektywne filtrowanie historii po container_ids w SQL
   - Wyciąganie container_ids z kluczy context przy zapisie historii

2. **Czat z Listy Kontenerów:**
   - Domyślnie załączanie przefiltrowanych kontenerów do kontekstu czatu
   - Możliwość zmiany selekcji kontenerów w konfiguracji kontekstu czatu
   - Przekazywanie container_ids do AiChatDialog

3. **Resume Chat z AI History Page:**
   - Przycisk "Resume Chat" w AiHistoryPage
   - Automatyczne przekierowanie na odpowiednią stronę (Container Detail lub Containers List)
   - Automatyczne otwieranie czatu i przywracanie historii
   - Obsługa query param `restoreHistoryId`

4. **Panel historii w oknie czatu:**
   - Użycie Sheet component z shadcn-vue (side="left")
   - Przycisk w headerze czatu do otwierania/zamykania panelu
   - Filtrowanie historii po operationType='chat' i container_ids
   - Możliwość przywracania konwersacji z panelu

## 📋 Implementation Plan

### 1. Dodanie pola container_ids do modelu historii AI

**Backend:**
- `backend/app/modules/ai/db_models.py` - dodanie kolumny `container_ids: Mapped[list[str] | None]`
- `backend/migrations/` - migracja dodająca kolumnę i wypełniająca dane z `input_data.context`
- `backend/app/modules/ai/schemas.py` - dodanie pola do `AiHistoryItem` i `AiHistoryDetail`
- `backend/app/modules/ai/services/chat_service.py` - wyciąganie container_ids z kluczy context
- `backend/app/modules/ai/routers/history.py` - opcjonalne filtrowanie po container_ids w query

**Frontend:**
- `src/modules/ai/types/history.ts` - dodanie `container_ids?: string[]`
- `src/modules/ai/composables/useAiHistory.ts` - filtrowanie po container_ids

### 2. Czat z poziomu Listy Kontenerów

**Pliki:**
- `src/modules/gear/pages/ContainersListPage.vue` - przekazywanie `filteredContainers.map(c => c.id)` do `AiChatDialog`
- `src/modules/ai/components/AiChatDialog.vue` - obsługa kontekstu z wieloma kontenerami
- `src/modules/ai/components/AiChatWindow.vue` - obsługa wielu containerIds

### 3. Resume Chat z AI History Page

**Pliki:**
- `src/modules/ai/pages/AiHistoryPage.vue` - logika przekierowania w `handleRestore`
- `src/modules/gear/pages/ContainerDetailPage.vue` - obsługa query param `restoreHistoryId`
- `src/modules/gear/pages/ContainersListPage.vue` - obsługa query param `restoreHistoryId`
- `src/modules/ai/components/AiChatDialog.vue` - automatyczne przywracanie z query param
- `src/modules/ai/components/AiChatWindow.vue` - prop `restoreHistoryId` i przywracanie w `onMounted`

**Logika:**
- Jeśli `historyItem.container_ids` ma dokładnie 1 element → przekieruj do Container Detail
- Jeśli wiele lub brak → przekieruj do Containers List
- Query param `restoreHistoryId` jest usuwany po załadowaniu historii

### 4. Panel historii w oknie czatu używając Sheet

**Pliki:**
- `src/modules/ai/components/AiChatHistorySidebar.vue` - nowy komponent zawartości panelu
- `src/modules/ai/components/AiChatWindow.vue` - integracja Sheet z `side="left"`
- `src/modules/ai/components/AiChatWindowHeader.vue` - SheetTrigger z ikoną historii

**Komponenty Sheet:**
```vue
<Sheet v-model:open="showHistorySidebar">
  <SheetTrigger>...</SheetTrigger>
  <SheetContent side="left">
    <AiChatHistorySidebar :container-ids="containerIds" />
  </SheetContent>
</Sheet>
```

### 5. Tłumaczenia

**Pliki:**
- `src/modules/ai/i18n/locales/pl.ts` i `en.ts`
- Klucze: `ai.chat.history.title`, `ai.chat.history.empty`, `ai.chat.history.restore`, `ai.history.resumeChat`, `ai.chat.history.openHistory`

## ✅ Acceptance Criteria

- [ ] Pole `container_ids` jest zapisywane przy każdej operacji AI z kontekstem kontenerów
- [ ] Migracja wypełnia `container_ids` dla istniejących wpisów historii
- [ ] Czat z Listy Kontenerów domyślnie załącza przefiltrowane kontenery
- [ ] Resume chat przekierowuje na odpowiednią stronę i otwiera czat z historią
- [ ] Panel historii w czacie używa Sheet component i filtruje po operationType i container_ids
- [ ] Wszystkie tłumaczenia są dodane
- [ ] Plan jest zapisany w `docs/features/FEATURE-AI-CHAT-ENHANCEMENTS.md`
- [ ] Wpis jest dodany do `docs/ROADMAP_ONLINE.md`

