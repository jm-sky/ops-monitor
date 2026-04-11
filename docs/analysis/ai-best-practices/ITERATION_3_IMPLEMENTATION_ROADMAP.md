# Iteracja 3: Plan implementacji - Implementation Roadmap

> **Data:** 2025-11-28
> **Status:** Kompletna
> **Poprzednie iteracje:**
> - [ITERATION_1_CATEGORIZATION.md](./ITERATION_1_CATEGORIZATION.md)
> - [ITERATION_2_DETAILED_ANALYSIS.md](./ITERATION_2_DETAILED_ANALYSIS.md)
> **Następny krok:** Iteracja 4 - Przegląd i finalizacja

## Cel

Szczegółowy, wykonalny plan implementacji AI best practices z podziałem na małe, przyrostowe zadania (incremental delivery). Każde zadanie może być zaimplementowane i przetestowane niezależnie.

---

## Format zadań

Każde zadanie zawiera:
- **ID** - Unikalny identyfikator (np. PROMPT-001)
- **Tytuł** - Krótki opis zadania
- **Złożoność** - S (Small, <4h), M (Medium, 4-8h), L (Large, 1-2 dni), XL (Extra Large, 2-4 dni)
- **Priorytet** - P0 (Critical), P1 (High), P2 (Medium), P3 (Low)
- **Dependencies** - Które zadania muszą być ukończone wcześniej
- **Definition of Done** - Jasne kryteria ukończenia
- **Pliki do zmiany** - Lista plików do edycji/utworzenia
- **Testy** - Jak przetestować zadanie

---

## Faza 1: Quick Wins (Tydzień 1)

**Cel:** Poprawić jakość promptów, dodać safety, lepsze parsowanie i error handling

**Estymacja:** 5-7 dni
**Priorytet:** P0-P1

### Sprint 1.1: PromptFactory Module (2-3 dni)

#### PROMPT-001: Utworzyć strukturę PromptFactory module
**Złożoność:** S (2-3h)
**Priorytet:** P0
**Dependencies:** Brak

**Zadanie:**
Utworzyć podstawową strukturę katalogu i plików dla PromptFactory.

**Pliki do utworzenia:**
```
backend/app/modules/ai/prompts/
├── __init__.py
├── factory.py
├── constants.py
├── templates/
│   ├── __init__.py
│   ├── system.py
│   ├── actions.py
│   └── examples.py
```

**Definition of Done:**
- [x] Wszystkie pliki utworzone
- [x] Podstawowa struktura klas zdefiniowana
- [x] Import działa: `from app.modules.ai.prompts.factory import PromptFactory`

**Testy:**
```bash
cd backend
python -c "from app.modules.ai.prompts.factory import PromptFactory; print('OK')"
```

---

#### PROMPT-002: Zaimplementować system prompt template
**Złożoność:** M (4-6h)
**Priorytet:** P0
**Dependencies:** PROMPT-001

**Zadanie:**
Stworzyć `templates/system.py` z funkcją `get_chat_system_prompt()` zawierającą:
- Role definition (expert survival gear advisor)
- Domain knowledge (BOB, EDC, GHB, weight categories)
- Safety rules (5 zasad)
- Action execution instructions
- Response format guidelines

**Pliki do zmiany:**
- `backend/app/modules/ai/prompts/templates/system.py` (nowy)

**Definition of Done:**
- [x] `get_chat_system_prompt(app_name: str)` zwraca pełny system prompt
- [x] Zawiera wszystkie safety rules z Iteracji 2
- [x] Zawiera domain knowledge (BOB, EDC, categories)
- [x] Prompt jest < 500 tokenów (sprawdzić przez `len(prompt.split())`)

**Testy:**
```python
from app.modules.ai.prompts.templates.system import get_chat_system_prompt

prompt = get_chat_system_prompt("Gear Stack")
assert "survival gear advisor" in prompt.lower()
assert "BOB" in prompt
assert "NEVER recommend dangerous" in prompt
print(f"Prompt length: {len(prompt.split())} words")
```

---

#### PROMPT-003: Zaimplementować action-specific prompts
**Złożoność:** L (1-2 dni)
**Priorytet:** P1
**Dependencies:** PROMPT-001

**Zadanie:**
Stworzyć `templates/actions.py` z funkcją `get_action_prompt(action, app_name)` i promptami dla:
- `create_item` - z required/optional fields, categories, safety rules
- `update_item` - z updatable fields, validation rules
- `delete_item` - z confirmation rules
- `create_container` - z container types, suggestions

**Pliki do zmiany:**
- `backend/app/modules/ai/prompts/templates/actions.py` (nowy)

**Definition of Done:**
- [x] `get_action_prompt(action, app_name)` zwraca action-specific prompt
- [x] Wszystkie 4 akcje mają dedykowane prompty
- [x] Każdy prompt zawiera required fields, validation rules, output format
- [x] Fallback dla unknown actions

**Testy:**
```python
from app.modules.ai.prompts.templates.actions import get_action_prompt

prompt = get_action_prompt("create_item", "Gear Stack")
assert "Required fields" in prompt
assert "category" in prompt
assert "Shelter" in prompt  # Category example

unknown = get_action_prompt("unknown_action", "Gear Stack")
assert "don't recognize" in unknown.lower()
```

---

#### PROMPT-004: Zaimplementować PromptFactory class
**Złożoność:** M (4-6h)
**Priorytet:** P0
**Dependencies:** PROMPT-001, PROMPT-002

**Zadanie:**
Stworzyć `factory.py` z klasą `PromptFactory` i metodami:
- `build_chat_messages(user_message, history, context, include_examples=False)`
- `build_action_prompt(action, user_message, context=None)`
- `_format_context(context)`

**Pliki do zmiany:**
- `backend/app/modules/ai/prompts/factory.py` (nowy)

**Definition of Done:**
- [x] `PromptFactory` class utworzona
- [x] `build_chat_messages()` zwraca list[dict] z messages
- [x] Integruje system prompt z `templates/system.py`
- [x] Dodaje context jeśli przekazany
- [x] Dodaje history i user message

**Testy:**
```python
from app.modules.ai.prompts.factory import PromptFactory

factory = PromptFactory()
messages = factory.build_chat_messages(
    user_message="Add a water filter",
    history=[],
    context={"container": "BOB"},
)

assert len(messages) >= 2  # System + user
assert messages[0]["role"] == "system"
assert messages[-1]["role"] == "user"
assert "water filter" in messages[-1]["content"]
```

---

#### PROMPT-005: Dodać few-shot examples (opcjonalnie)
**Złożoność:** S (2-3h)
**Priorytet:** P2
**Dependencies:** PROMPT-001

**Zadanie:**
Stworzyć `templates/examples.py` z funkcją `get_action_examples()` zawierającą 2-3 przykłady user→assistant dla actions.

**Pliki do zmiany:**
- `backend/app/modules/ai/prompts/templates/examples.py` (nowy)

**Definition of Done:**
- [x] `get_action_examples()` zwraca list[dict] z example messages
- [x] Minimum 2 przykłady (create_item, update_item)
- [x] Każdy przykład zawiera user message + assistant response z JSON

**Testy:**
```python
from app.modules.ai.prompts.templates.examples import get_action_examples

examples = get_action_examples()
assert len(examples) >= 4  # 2 examples * 2 messages each
assert examples[0]["role"] == "user"
assert examples[1]["role"] == "assistant"
```

**Note:** To zadanie jest opcjonalne - można pominąć jeśli prompty działają dobrze bez examples.

---

#### PROMPT-006: Zintegrować PromptFactory z ChatService
**Złożoność:** M (4-6h)
**Priorytet:** P0
**Dependencies:** PROMPT-004

**Zadanie:**
Zmodyfikować `ChatService` aby używał `PromptFactory` zamiast `_build_messages()`.

**Pliki do zmiany:**
- `backend/app/modules/ai/services/chat_service.py`

**Zmiany:**
1. Import: `from app.modules.ai.prompts.factory import PromptFactory`
2. W `__init__`: `self.prompt_factory = PromptFactory()`
3. W `chat()`: zamienić `self._build_messages(...)` na `self.prompt_factory.build_chat_messages(...)`
4. Usunąć metodę `_build_messages()`
5. Wymusić niską temperature: `temperature = min(temperature, 0.4)`

**Definition of Done:**
- [x] ChatService używa PromptFactory
- [x] `_build_messages()` usunięta
- [x] Temperature capped at 0.4 dla safety
- [x] Testy integracyjne przechodzą

**Testy:**
```bash
# Run existing tests
cd backend
pytest app/modules/ai/tests/ -v

# Manual test
curl -X POST http://localhost:8000/api/ai/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"message": "What should I pack for a 3-day hike?"}'
```

---

### Sprint 1.2: Better Structured Output Parsing (1-2 dni)

#### PARSE-001: Utworzyć StructuredOutputParser class
**Złożoność:** M (4-6h)
**Priorytet:** P0
**Dependencies:** Brak

**Zadanie:**
Stworzyć `parsers/structured_output_parser.py` z klasą `StructuredOutputParser` i metodami:
- `parse(message: str) -> StructuredOutput | None`
- `_extract_json_from_code_block(message)`
- `_parse_json_content(message)`
- `_validate_structured_output(data)`

**Pliki do utworzenia:**
- `backend/app/modules/ai/parsers/__init__.py`
- `backend/app/modules/ai/parsers/structured_output_parser.py`

**Definition of Done:**
- [x] `StructuredOutputParser` class utworzona
- [x] `parse()` parsuje JSON z code blocks
- [x] `parse()` parsuje całą wiadomość jako JSON (fallback)
- [x] Walidacja action (tylko allowed actions)
- [x] Logging przy parsing errors

**Testy:**
```python
from app.modules.ai.parsers.structured_output_parser import StructuredOutputParser

parser = StructuredOutputParser()

# Test 1: JSON in code block
message1 = 'Sure! ```json\n{"action": "create_item", "data": {}}\n```'
result1 = parser.parse(message1)
assert result1 is not None
assert result1.action == "create_item"

# Test 2: Całą wiadomość jako JSON
message2 = '{"action": "update_item", "data": {"id": "123"}}'
result2 = parser.parse(message2)
assert result2.action == "update_item"

# Test 3: Invalid action
message3 = '```json\n{"action": "hack_database", "data": {}}\n```'
result3 = parser.parse(message3)
assert result3 is None  # Invalid action rejected
```

---

#### PARSE-002: Dodać retry logic przy parsing failure
**Złożoność:** M (4-6h)
**Priorytet:** P1
**Dependencies:** PARSE-001

**Zadanie:**
Dodać metodę `_retry_with_clearer_prompt()` w ChatService, która retry'uje request z clarifying message gdy parsing failuje.

**Pliki do zmiany:**
- `backend/app/modules/ai/services/chat_service.py`

**Zmiany:**
1. Dodać metodę `_is_action_request(message: str) -> bool`
2. Dodać metodę `_retry_with_clearer_prompt(user_id, request, previous_response) -> StructuredOutput | None`
3. W `chat()`: jeśli parsing failed i `_is_action_request()` = True, call `_retry_with_clearer_prompt()`

**Definition of Done:**
- [x] Retry logic działa dla action requests
- [x] Retry używa niższej temperature (0.2)
- [x] Maximum 1 retry (nie loop)
- [x] Logging przy retry

**Testy:**
```python
# Symulować AI response bez valid JSON
# Sprawdzić czy ChatService retry'uje

# Manual test:
# 1. Modify OpenRouterProvider to return invalid JSON
# 2. Send action request
# 3. Verify retry happened (check logs)
```

---

#### PARSE-003: Zintegrować StructuredOutputParser z ChatService
**Złożoność:** S (2-3h)
**Priorytet:** P0
**Dependencies:** PARSE-001

**Zadanie:**
Zamienić `_parse_structured_output()` w ChatService na użycie `StructuredOutputParser`.

**Pliki do zmiany:**
- `backend/app/modules/ai/services/chat_service.py`

**Zmiany:**
1. Import: `from app.modules.ai.parsers.structured_output_parser import StructuredOutputParser`
2. W `__init__`: `self.output_parser = StructuredOutputParser()`
3. W `chat()`: zamienić `self._parse_structured_output(...)` na `self.output_parser.parse(...)`
4. Usunąć metodę `_parse_structured_output()`

**Definition of Done:**
- [x] ChatService używa StructuredOutputParser
- [x] `_parse_structured_output()` usunięta
- [x] Testy integracyjne przechodzą

**Testy:**
```bash
pytest app/modules/ai/tests/ -v -k "test_chat"
```

---

### Sprint 1.3: Safety & Fallbacks (1-2 dni)

#### SAFETY-001: Dodać tenacity dla exponential backoff retry
**Złożoność:** S (2-3h)
**Priorytet:** P0
**Dependencies:** Brak

**Zadanie:**
1. Dodać `tenacity==8.2.3` do `requirements.txt`
2. Dodać `@retry` decorator do `OpenRouterProvider.chat()`

**Pliki do zmiany:**
- `backend/requirements.txt`
- `backend/app/modules/ai/providers/openrouter.py`

**Zmiany w `openrouter.py`:**
```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from openai import APIError, RateLimitError, APITimeoutError

class OpenRouterProvider(AIProvider):
    @retry(
        retry=retry_if_exception_type((RateLimitError, APITimeoutError, APIError)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def chat(self, ...):
        # existing implementation
```

**Definition of Done:**
- [x] `tenacity` dodane do requirements
- [x] `@retry` decorator na `OpenRouterProvider.chat()`
- [x] Retry tylko dla: RateLimitError, APITimeoutError, APIError
- [x] Max 3 retries z exponential backoff (2s, 4s, 8s)

**Testy:**
```bash
# Install tenacity
pip install -r backend/requirements.txt

# Test retry manually:
# 1. Temporarily modify OpenRouterProvider to raise RateLimitError
# 2. Call chat()
# 3. Verify 3 retries happen (check logs with timestamps)
```

---

#### SAFETY-002: Dodać graceful fallback responses
**Złożoność:** M (4-5h)
**Priorytet:** P0
**Dependencies:** Brak

**Zadanie:**
Dodać try/except w ChatService.chat() i metodę `_create_fallback_response()`.

**Pliki do zmiany:**
- `backend/app/modules/ai/services/chat_service.py`

**Zmiany:**
1. Wrap główny kod w `chat()` w try/except
2. Catch `OpenRouterError` i generic `Exception`
3. Dodać metodę `_create_fallback_response(error_message, user_message)`
4. Return fallback zamiast raise error

**Definition of Done:**
- [x] Try/except w `chat()` method
- [x] Separate handling dla `OpenRouterError` vs generic `Exception`
- [x] `_create_fallback_response()` zwraca valid AiChatResponse
- [x] Fallback message jest user-friendly
- [x] Logging przy każdym fallback (error level)

**Testy:**
```python
# Symulować AI failure
# Sprawdzić czy zwraca fallback zamiast raise

# Manual test:
# 1. Temporarily modify OpenRouterProvider to always raise error
# 2. Send chat request
# 3. Verify fallback response returned
# 4. Verify error logged
```

---

#### SAFETY-003: Dodać logging dla wszystkich errors
**Złożoność:** S (2-3h)
**Priorytet:** P1
**Dependencies:** SAFETY-002

**Zadanie:**
Dodać strukturalne logowanie (z user_id, request_id, error type) dla wszystkich error cases.

**Pliki do zmiany:**
- `backend/app/modules/ai/services/chat_service.py`
- `backend/app/modules/ai/providers/openrouter.py`

**Zmiany:**
1. Import: `import logging; logger = logging.getLogger(__name__)`
2. Log przy parsing errors (w PARSE-001)
3. Log przy retry (w PARSE-002)
4. Log przy API errors (w SAFETY-001)
5. Log przy fallbacks (w SAFETY-002)

**Format logów:**
```python
logger.error(
    "AI chat failed",
    extra={
        "user_id": user_id,
        "error_type": type(e).__name__,
        "error_message": str(e),
        "request_message": request.message[:100],  # First 100 chars
    }
)
```

**Definition of Done:**
- [x] Logging w wszystkich error paths
- [x] Structured logs z extra fields
- [x] Różne log levels (error, warning, info)

**Testy:**
```bash
# Run app and check logs
# Trigger various errors and verify logs contain expected fields
```

---

## Faza 2: Function Calling Implementation (Tydzień 2)

**Cel:** Zaimplementować native function calling / tool use dla agent actions

**Estymacja:** 3-5 dni
**Priorytet:** P1

### Sprint 2.1: Tool Definitions (1 dzień)

#### TOOLS-001: Stworzyć tool definitions
**Złożoność:** L (1 dzień)
**Priorytet:** P1
**Dependencies:** Brak (ale logicznie po Fazie 1)

**Zadanie:**
Stworzyć `prompts/tools.py` z funkcją `get_tools()` definiującą:
- `create_item` tool
- `update_item` tool
- `delete_item` tool
- `create_container` tool
- `get_container_details` tool (opcjonalnie)

**Pliki do utworzenia:**
- `backend/app/modules/ai/prompts/tools.py`

**Definition of Done:**
- [x] `get_tools()` zwraca list of tool definitions w OpenAI format
- [x] Każdy tool ma: name, description, parameters (JSON schema)
- [x] Parameters zawierają: type, properties, required fields
- [x] Enums dla kategorii, priority, status, weightUnit, color

**Testy:**
```python
from app.modules.ai.prompts.tools import get_tools

tools = get_tools()
assert len(tools) >= 4  # Minimum 4 tools
assert all(t["type"] == "function" for t in tools)

# Check create_item tool
create_item = next(t for t in tools if t["function"]["name"] == "create_item")
assert "parameters" in create_item["function"]
assert "properties" in create_item["function"]["parameters"]
assert "name" in create_item["function"]["parameters"]["properties"]
assert "category" in create_item["function"]["parameters"]["properties"]
assert "required" in create_item["function"]["parameters"]
```

---

### Sprint 2.2: Provider Updates (1 dzień)

#### TOOLS-002: Dodać tools support do OpenRouterProvider
**Złożoność:** M (4-6h)
**Priorytet:** P1
**Dependencies:** TOOLS-001

**Zadanie:**
Zaktualizować `OpenRouterProvider.chat()` aby wspierał tools parameter i zwracał tool_calls.

**Pliki do zmiany:**
- `backend/app/modules/ai/providers/openrouter.py`
- `backend/app/modules/ai/providers/base.py`

**Zmiany w `base.py`:**
```python
@dataclass
class ChatResponse:
    message: str
    tool_calls: list[dict[str, Any]] | None = None  # ✅ Add
    # ... existing fields
```

**Zmiany w `openrouter.py`:**
```python
async def chat(
    self,
    messages: list[dict[str, str]],
    model: str,
    max_tokens: int | None = None,
    temperature: float = 1.0,
    tools: list[dict[str, Any]] | None = None,  # ✅ Add
    tool_choice: str | dict | None = None,  # ✅ Add
    **kwargs: Any,
) -> ChatResponse:
    response = await self.client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        tools=tools,  # ✅ Pass
        tool_choice=tool_choice,  # ✅ Pass
        **kwargs
    )

    # ✅ Extract tool_calls
    tool_calls = None
    if hasattr(choice.message, 'tool_calls') and choice.message.tool_calls:
        tool_calls = [
            {
                "id": tc.id,
                "type": tc.type,
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                }
            }
            for tc in choice.message.tool_calls
        ]

    return ChatResponse(
        message=message_content,
        tool_calls=tool_calls,  # ✅ Return
        # ... existing fields
    )
```

**Definition of Done:**
- [x] `ChatResponse` ma `tool_calls` field
- [x] `OpenRouterProvider.chat()` przyjmuje `tools` i `tool_choice`
- [x] `OpenRouterProvider.chat()` zwraca `tool_calls` jeśli są

**Testy:**
```python
import asyncio
from app.modules.ai.providers.openrouter import OpenRouterProvider
from app.modules.ai.prompts.tools import get_tools

async def test_tools():
    provider = OpenRouterProvider()
    tools = get_tools()

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Add a water filter to my bag"}
    ]

    response = await provider.chat(
        messages=messages,
        model="openai/gpt-4o-mini",
        tools=tools,
        tool_choice="auto",
    )

    print(f"Tool calls: {response.tool_calls}")
    if response.tool_calls:
        assert response.tool_calls[0]["function"]["name"] == "create_item"

asyncio.run(test_tools())
```

---

### Sprint 2.3: ChatService Integration (1-2 dni)

#### TOOLS-003: Zintegrować tools z ChatService
**Złożoność:** L (1-2 dni)
**Priorytet:** P1
**Dependencies:** TOOLS-002

**Zadanie:**
Zaktualizować `ChatService.chat()` aby:
1. Przekazywał tools do provider
2. Obsługiwał tool_calls w response
3. Wykonywał tool calls (na razie tylko parse, nie execute)
4. Fallback na regex parsing dla non-tool models

**Pliki do zmiany:**
- `backend/app/modules/ai/services/chat_service.py`

**Zmiany:**
```python
from app.modules.ai.prompts.tools import get_tools

class ChatService:
    async def chat(self, user_id: str, request: AiChatRequest) -> AiChatResponse:
        # ... existing code ...

        # ✅ Get tools
        tools = get_tools()

        # ✅ Call AI with tools
        response = await provider.chat(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            tools=tools,
            tool_choice="auto",
        )

        # ✅ Handle tool calls (preferred)
        structured = None
        if response.tool_calls:
            tool_call_result = await self._handle_tool_calls(response.tool_calls)
            if tool_call_result:
                structured = StructuredOutput(
                    action=tool_call_result["action"],
                    data=tool_call_result["data"],
                )
        else:
            # Fallback: parse from message (existing logic)
            structured = self.output_parser.parse(response.message)

        # ... rest of code ...

    async def _handle_tool_calls(
        self, tool_calls: list[dict[str, Any]]
    ) -> dict[str, Any] | None:
        """Handle tool calls from AI.

        For now, just convert to structured output format.
        In future, can actually execute actions via GearService.
        """
        import json

        if not tool_calls:
            return None

        # Take first tool call (for now)
        tool_call = tool_calls[0]
        function_name = tool_call["function"]["name"]
        arguments = json.loads(tool_call["function"]["arguments"])

        return {
            "action": function_name,
            "data": arguments,
        }
```

**Definition of Done:**
- [x] ChatService przekazuje tools do provider
- [x] ChatService obsługuje tool_calls w response
- [x] `_handle_tool_calls()` konwertuje tool_calls do StructuredOutput
- [x] Fallback na regex parsing jeśli brak tool_calls
- [x] Testy integracyjne przechodzą

**Testy:**
```bash
# Test with tool-compatible model
curl -X POST http://localhost:8000/api/ai/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "message": "Add a Sawyer Mini water filter to my BOB",
    "model": "openai/gpt-4o-mini"
  }'

# Verify response contains structured_output with action="create_item"
```

---

#### TOOLS-004: Dodać fallback dla non-tool models
**Złożoność:** S (2-3h)
**Priorytet:** P2
**Dependencies:** TOOLS-003

**Zadanie:**
Dodać logikę w ChatService aby:
1. Sprawdzać czy model wspiera tools (whitelist)
2. Jeśli nie wspiera, używać starych promptów (bez tools)
3. Fallback na regex parsing

**Pliki do zmiany:**
- `backend/app/modules/ai/services/chat_service.py`

**Zmiany:**
```python
# Model whitelist (models supporting function calling)
TOOL_COMPATIBLE_MODELS = [
    "openai/gpt-4o",
    "openai/gpt-4o-mini",
    "openai/gpt-3.5-turbo",
    "anthropic/claude-3-5-sonnet",
    "anthropic/claude-3-haiku",
    # Add more as needed
]

class ChatService:
    async def chat(self, user_id: str, request: AiChatRequest) -> AiChatResponse:
        # ... existing code ...

        # ✅ Check if model supports tools
        model_supports_tools = any(
            model.startswith(prefix) for prefix in TOOL_COMPATIBLE_MODELS
        )

        # Get tools only if supported
        tools = get_tools() if model_supports_tools else None

        # Call AI
        response = await provider.chat(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            tools=tools if model_supports_tools else None,
            tool_choice="auto" if model_supports_tools else None,
        )

        # ... rest of code (already handles fallback)
```

**Definition of Done:**
- [x] Model whitelist zdefiniowana
- [x] Tools przekazywane tylko dla compatible models
- [x] Non-compatible models używają regex parsing
- [x] Logging który path został użyty (tools vs regex)

**Testes:**
```bash
# Test with non-tool model
curl -X POST http://localhost:8000/api/ai/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "message": "Add a water filter",
    "model": "google/gemini-flash-1.5"
  }'

# Verify fallback to regex parsing
```

---

## Faza 3: Optional Enhancements (Tydzień 3+ lub później)

**Cel:** Nice-to-have features dla lepszego monitoringu, quality, i robustności

**Estymacja:** 5-8 dni (opcjonalnie)
**Priorytet:** P2-P3

### Sprint 3.1: Output Validation (2-3 dni)

#### VALID-001: Utworzyć OutputValidator class
**Złożoność:** L (1-2 dni)
**Priorytet:** P2
**Dependencies:** Brak (ale logicznie po Function Calling)

**Zadanie:**
Stworzyć `services/output_validator.py` z klasą `OutputValidator` i metodami:
- `validate(user_id, output) -> (bool, error_message | None)`
- `_validate_create_item(user_id, data)`
- `_validate_update_item(user_id, data)`
- `_validate_delete_item(user_id, data)`
- `_validate_create_container(user_id, data)`

**Pliki do utworzenia:**
- `backend/app/modules/ai/services/output_validator.py`

**Definition of Done:**
- [x] OutputValidator class utworzona
- [x] Validation dla wszystkich 4 action types
- [x] Checks: required fields, valid UUIDs, item existence (via GearRepository)
- [x] Returns (is_valid, error_message)

**Testy:**
```python
from app.modules.ai.services.output_validator import OutputValidator
from app.modules.ai.schemas import StructuredOutput

# Mock GearRepository
validator = OutputValidator(gear_repo=mock_gear_repo)

# Valid output
output = StructuredOutput(
    action="create_item",
    data={
        "name": "Water filter",
        "category": "Water",
        "quantity": 1,
        "priority": "critical",
        "status": "owned",
    }
)
is_valid, error = await validator.validate(user_id="123", output=output)
assert is_valid is True

# Invalid output (missing required field)
output_invalid = StructuredOutput(
    action="create_item",
    data={"name": "Water filter"}  # Missing category, quantity, etc.
)
is_valid, error = await validator.validate(user_id="123", output=output_invalid)
assert is_valid is False
assert "Missing required fields" in error
```

---

#### VALID-002: Zintegrować OutputValidator z ChatService
**Złożoność:** M (4-6h)
**Priorytet:** P2
**Dependencies:** VALID-001

**Zadanie:**
Dodać OutputValidator do ChatService i wywołać `validate()` przed zwróceniem structured output.

**Pliki do zmiany:**
- `backend/app/modules/ai/services/chat_service.py`
- `backend/app/modules/ai/dependencies.py` (inject GearRepository)

**Zmiany:**
```python
class ChatService:
    def __init__(
        self,
        settings_service: SettingsService,
        history_repo: HistoryRepository,
        cache_service: PostgresCacheService | None = None,
        output_validator: OutputValidator | None = None,  # ✅ Add
    ):
        # ...
        self.output_validator = output_validator

    async def chat(self, user_id: str, request: AiChatRequest) -> AiChatResponse:
        # ... existing code ...

        # Parse structured output
        structured = ...  # from tool_calls or regex

        # ✅ Validate if validator available
        if structured and self.output_validator:
            is_valid, error_msg = await self.output_validator.validate(
                user_id, structured
            )

            if not is_valid:
                logger.warning(f"Output validation failed: {error_msg}")
                # Option 1: Clear action, keep message
                structured = None
                cleaned_message += f"\n\n_Note: Action validation failed - {error_msg}_"
                # Option 2: Retry with feedback
                # Option 3: Return error to frontend

        # ... rest of code
```

**Definition of Done:**
- [x] OutputValidator injected w ChatService
- [x] Validation wywołane dla każdego structured output
- [x] Handling validation failures (clear action + message)
- [x] Logging przy validation failures

**Testy:**
```bash
# Test with invalid action (e.g., missing required field)
# Verify action is cleared and user gets friendly message
```

---

### Sprint 3.2: Structured Logging & Monitoring (1-2 dni)

#### LOG-001: Dodać structured JSON logging
**Złożoność:** M (4-6h)
**Priorytet:** P2
**Dependencies:** Brak

**Zadanie:**
Skonfigurować structured logging (JSON format) z `python-json-logger`.

**Pliki do zmiany:**
- `backend/requirements.txt`
- `backend/app/core/logging_config.py` (nowy)
- `backend/app/main.py`

**Zmiany:**
1. Dodać `python-json-logger==2.0.7` do requirements
2. Stworzyć `logging_config.py` z JSON formatter
3. Configure w `main.py` startup

**Definition of Done:**
- [x] `python-json-logger` installed
- [x] Logging config w osobnym pliku
- [x] JSON format dla production logs
- [x] Context fields: request_id, user_id, timestamp

**Testy:**
```bash
# Run app and check log format
python backend/app/main.py

# Verify logs are JSON (not plaintext)
```

---

#### LOG-002: Dodać request_id tracking
**Złożoność:** M (4-6h)
**Priorytet:** P2
**Dependencies:** LOG-001

**Zadanie:**
Dodać middleware generujący `request_id` dla każdego requesta i propagujący do logów.

**Pliki do zmiany:**
- `backend/app/core/middleware.py` (nowy lub istniejący)
- `backend/app/main.py`

**Zmiany:**
```python
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="")

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())
        request_id_var.set(request_id)

        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

# In main.py
app.add_middleware(RequestIDMiddleware)
```

**Definition of Done:**
- [x] Middleware generuje unique request_id
- [x] request_id w request.state
- [x] request_id w response headers
- [x] request_id w logs (via ContextVar)

**Testes:**
```bash
# Check response headers
curl -v http://localhost:8000/api/ai/chat
# Verify X-Request-ID header present
```

---

#### LOG-003: Dodać cache hit/miss metrics logging
**Złożoność:** S (2-3h)
**Priorytet:** P2
**Dependencies:** Brak

**Zadanie:**
Dodać logging cache hit/miss w ChatService.

**Pliki do zmiany:**
- `backend/app/modules/ai/services/chat_service.py`

**Zmiany:**
```python
async def chat(self, user_id: str, request: AiChatRequest) -> AiChatResponse:
    # ... existing code ...

    # Check cache
    if settings.ai.cache_enabled and self.cache_service:
        cached = await self.cache_service.get(cache_key)
        if cached:
            logger.info(
                "Cache hit",
                extra={
                    "user_id": user_id,
                    "cache_key": cache_key,
                    "model": model,
                }
            )
            return ...  # cached response
        else:
            logger.info(
                "Cache miss",
                extra={
                    "user_id": user_id,
                    "cache_key": cache_key,
                    "model": model,
                }
            )

    # ... rest of code
```

**Definition of Done:**
- [x] Log cache hits z user_id, model
- [x] Log cache misses z user_id, model
- [x] Info level (nie warning/error)

**Testes:**
```bash
# Send same request twice
# Verify first is cache miss, second is cache hit
```

---

### Sprint 3.3: Rate Limiting (1 dzień)

#### RATE-001: Dodać rate limiting per-user
**Złożoność:** M (4-6h)
**Priorytet:** P3
**Dependencies:** Brak

**Zadanie:**
Dodać rate limiting używając `slowapi`.

**Pliki do zmiany:**
- `backend/requirements.txt`
- `backend/app/core/rate_limit.py` (nowy)
- `backend/app/modules/ai/routers/chat.py`

**Zmiany:**
1. Dodać `slowapi==0.1.9` do requirements
2. Stworzyć rate limit config
3. Dodać decorator do chat endpoint

**Example:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("", response_model=AiChatResponse)
@limiter.limit("10/minute")  # 10 requests per minute
async def chat(...):
    ...
```

**Definition of Done:**
- [x] `slowapi` installed
- [x] Rate limit na chat endpoint (10 req/min per IP)
- [x] 429 response przy przekroczeniu limitu
- [x] Rate limit headers w response

**Testes:**
```bash
# Send 11 requests quickly
# Verify 11th returns 429 Too Many Requests
```

---

## Faza 4: Future Enhancements (P3, opcjonalnie)

Te zadania mogą poczekać na późniejsze iteracje:

### Możliwe future tasks (nie priorytet):

1. **Actually Execute Tool Calls** - Wywołać GearService.create_item() itd. z ChatService
2. **RAG/Embeddings** - Vector DB dla retrieval-augmented generation
3. **Model Failover** - Automatyczne przełączanie między modelami przy failures
4. **A/B Testing Framework** - Testowanie różnych promptów/modeli
5. **User Feedback Mechanism** - Thumbs up/down dla AI responses
6. **Semantic Caching** - Cache based on embedding similarity, nie exact match
7. **Advanced Monitoring** - Prometheus/Grafana integration

---

## Summary & Tracking

### Effort Estimates

| Faza | Sprint | Tasks | Estymacja | Priorytet |
|------|--------|-------|-----------|-----------|
| Faza 1 | 1.1 PromptFactory | PROMPT-001 do PROMPT-006 | 2-3 dni | P0 |
| Faza 1 | 1.2 Structured Parsing | PARSE-001 do PARSE-003 | 1-2 dni | P0 |
| Faza 1 | 1.3 Safety & Fallbacks | SAFETY-001 do SAFETY-003 | 1-2 dni | P0 |
| **Faza 1 Total** | | | **5-7 dni** | **P0** |
| Faza 2 | 2.1 Tool Definitions | TOOLS-001 | 1 dzień | P1 |
| Faza 2 | 2.2 Provider Updates | TOOLS-002 | 1 dzień | P1 |
| Faza 2 | 2.3 ChatService Integration | TOOLS-003, TOOLS-004 | 1-2 dni | P1 |
| **Faza 2 Total** | | | **3-4 dni** | **P1** |
| Faza 3 | 3.1 Output Validation | VALID-001, VALID-002 | 2-3 dni | P2 |
| Faza 3 | 3.2 Logging & Monitoring | LOG-001 do LOG-003 | 1-2 dni | P2 |
| Faza 3 | 3.3 Rate Limiting | RATE-001 | 1 dzień | P3 |
| **Faza 3 Total** | | | **4-6 dni** | **P2-P3** |
| **GRAND TOTAL** | | | **12-17 dni** | |

### Recommended Timeline

**Minimum Viable (2 tygodnie):**
- Faza 1: Quick Wins (1 tydzień)
- Faza 2: Function Calling (1 tydzień)

**Solid Foundation (3 tygodnie):**
- Faza 1 + Faza 2 + Faza 3.1 (Validation)

**Full Implementation (3-4 tygodnie):**
- Wszystkie fazy

### Dependencies Graph

```
PROMPT-001 (Create structure)
  ├─> PROMPT-002 (System prompt) ──┐
  ├─> PROMPT-003 (Action prompts) ─┤
  ├─> PROMPT-005 (Examples)        ├─> PROMPT-004 (PromptFactory) ──> PROMPT-006 (Integrate)
  └─────────────────────────────────┘

PARSE-001 (Parser class) ──┬─> PARSE-003 (Integrate)
                            └─> PARSE-002 (Retry logic)

SAFETY-001 (Tenacity) ──┬─> SAFETY-003 (Logging)
SAFETY-002 (Fallback) ──┘

TOOLS-001 (Tool defs) ──> TOOLS-002 (Provider) ──> TOOLS-003 (ChatService) ──> TOOLS-004 (Fallback)

VALID-001 (Validator class) ──> VALID-002 (Integrate)

LOG-001 (JSON logging) ──> LOG-002 (Request ID) ──> LOG-003 (Cache metrics)
```

### Critical Path

Dla najszybszego delivery (Minimum Viable):
1. PROMPT-001 → PROMPT-002 → PROMPT-004 → PROMPT-006 (PromptFactory baseline)
2. PARSE-001 → PARSE-003 (Better parsing)
3. SAFETY-001 → SAFETY-002 (Retry + Fallback)
4. TOOLS-001 → TOOLS-002 → TOOLS-003 (Function calling)

**Total Critical Path:** ~10-12 dni

---

## Gotowy do Iteracji 4?

W **Iteracji 4** (Przegląd i finalizacja) zrobimy:
1. Przegląd całego planu
2. Weryfikację dependencies
3. Doprecyzowanie niejasnych punktów
4. Zatwierdzenie ostatecznego planu
5. Stworzenie tracking board (opcjonalnie)

Masz jakieś pytania lub uwagi do tego roadmapu?
