# Iteracja 2: Szczegółowa analiza wybranych obszarów

> **Data:** 2025-11-28
> **Status:** Kompletna
> **Poprzednia iteracja:** [ITERATION_1_CATEGORIZATION.md](./ITERATION_1_CATEGORIZATION.md)
> **Następny krok:** Iteracja 3 - Plan implementacji

## Kontekst użytkownika

Na podstawie odpowiedzi z Iteracji 1:

**Use case:**
- Chat assistant z agent actions (structured JSON output)
- AI może wykonywać akcje: dodawać/usuwać/zmieniać items i containers
- AI może pobierać dane przez funkcje/komendy (np. `get_container_detailed_content`)

**Timeline:** Krok po kroku, incrementalne wdrożenie

**Approach:** Pragmatyczny - solidnie, ale bez over-engineeringu

**Brak:** Baza items do recommendation (na razie), zaawansowany monitoring

---

## Obszary do szczegółowej analizy (High Priority)

Na podstawie Iteracji 1, skupiamy się na:

1. **Prompt Engineering (#02)** - PromptFactory, templates, safety rules
2. **Structured Responses (#03)** - JSON mode, validation, function calling
3. **Safety & Fallbacks (#04)** - safety guards, retry logic, error handling
4. **Function Calling / Tool Use** - integracja AI z gear operations

---

## 1. Prompt Engineering - Szczegółowa analiza

### 1.1 Gap Analysis (co brakuje)

#### Obecna implementacja (w `chat_service.py:153-174`)

```python
system_prompt = f"""You are a helpful AI assistant for a gear management application {settings.app.name}.
You help users manage their survival gear, bug-out bags, and equipment.

When the user asks you to perform actions (like adding items, updating quantities, etc.),
respond in a conversational way AND include structured output in JSON format at the end of your message.

Format your structured output as:
```json
{
  "action": "action_name",
  "data": {...}
}
```

Available actions:
- create_item: Create a new gear item
- update_item: Update existing item
- delete_item: Delete an item
- create_container: Create a new container
- None: Just conversation, no action needed

Keep your responses concise and helpful."""
```

#### Problemy z obecnym promptem:

1. ❌ **Zbyt ogólny** - brak explicit instructions dla każdej akcji (jakie pola są wymagane?)
2. ❌ **Brak safety rules** - nie ma "don't hallucinate", "if unsure, ask user"
3. ❌ **Brak domain knowledge** - nie definiuje terminów survivalowych (EDC, BOB, etc.)
4. ❌ **Brak examples** - zero few-shot examples dla actions
5. ❌ **Temperature nie jest wymuszana** - default 1.0 jest za wysoka dla factual tasks
6. ❌ **Hardcoded** - każda zmiana wymaga edycji kodu
7. ❌ **Brak wersjonowania** - nie ma tracking zmian w promptach
8. ❌ **Brak role clarity** - "helpful AI assistant" jest zbyt vague

### 1.2 Propozycja rozwiązania

#### A. Wyodrębnić PromptFactory module

**Struktura:**
```
backend/app/modules/ai/prompts/
├── __init__.py
├── factory.py           # PromptFactory class
├── templates/
│   ├── __init__.py
│   ├── system.py        # System prompts
│   ├── actions.py       # Action-specific prompts
│   └── examples.py      # Few-shot examples
└── constants.py         # Prompt constants (domain terms, rules)
```

**Przykład implementacji `prompts/factory.py`:**

```python
"""Prompt factory for building AI prompts."""

from typing import Any

from app.core.config import settings

from .templates import actions, examples, system


class PromptFactory:
    """Factory for building AI prompts with templates."""

    def __init__(self):
        """Initialize prompt factory."""
        self.app_name = settings.app.name

    def build_chat_messages(
        self,
        user_message: str,
        history: list[dict[str, str]],
        context: dict[str, Any] | None = None,
        include_examples: bool = False,
    ) -> list[dict[str, str]]:
        """Build messages array for chat.

        Args:
            user_message: User's message
            history: Previous messages in conversation
            context: Optional context data
            include_examples: Whether to include few-shot examples

        Returns:
            List of messages for AI
        """
        messages = []

        # System message with instructions
        messages.append({
            "role": "system",
            "content": system.get_chat_system_prompt(self.app_name)
        })

        # Add few-shot examples if requested
        if include_examples:
            messages.extend(examples.get_action_examples())

        # Add context if provided
        if context:
            messages.append({
                "role": "system",
                "content": self._format_context(context)
            })

        # Add conversation history
        messages.extend(history)

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        return messages

    def build_action_prompt(
        self,
        action: str,
        user_message: str,
        context: dict[str, Any] | None = None,
    ) -> list[dict[str, str]]:
        """Build messages for specific action.

        Args:
            action: Action type (create_item, update_item, etc.)
            user_message: User's request
            context: Optional context data

        Returns:
            List of messages for AI
        """
        messages = []

        # Get action-specific system prompt
        action_prompt = actions.get_action_prompt(action, self.app_name)
        messages.append({"role": "system", "content": action_prompt})

        # Add context if provided
        if context:
            messages.append({
                "role": "system",
                "content": self._format_context(context)
            })

        # Add user message
        messages.append({"role": "user", "content": user_message})

        return messages

    def _format_context(self, context: dict[str, Any]) -> str:
        """Format context data for prompt.

        Args:
            context: Context dictionary

        Returns:
            Formatted context string
        """
        import json

        return f"Current context:\n{json.dumps(context, indent=2)}"
```

**Przykład `prompts/templates/system.py`:**

```python
"""System prompt templates."""


def get_chat_system_prompt(app_name: str) -> str:
    """Get system prompt for chat.

    Args:
        app_name: Application name

    Returns:
        System prompt text
    """
    return f"""You are an expert survival gear advisor and assistant for {app_name}.

Your role:
- Help users manage their survival gear, bug-out bags (BOB), and everyday carry (EDC) equipment
- Provide accurate, safety-focused advice based on survival best practices
- Execute actions when explicitly requested by the user

Domain knowledge:
- BOB (Bug-Out Bag): Emergency evacuation bag with 72h supplies
- EDC (Everyday Carry): Items carried daily for preparedness
- GHB (Get Home Bag): Supplies to reach home in emergency
- Weight categories: Ultralight (<10kg), Light (10-15kg), Medium (15-20kg), Heavy (>20kg)
- Priority levels: Critical (life-sustaining), High (important comfort/safety), Medium (useful), Low (nice-to-have)

Safety rules:
1. NEVER recommend dangerous, illegal, or unethical items
2. ALWAYS prioritize user safety (e.g., water > gadgets)
3. If you're unsure about user's request, ASK for clarification
4. If you don't have enough context, REQUEST missing information
5. NEVER invent item specifications - use provided data or ask user

Action execution:
When user requests an action (add item, create container, etc.):
1. Respond conversationally to acknowledge the request
2. Include structured output in JSON format
3. Only execute actions you're CERTAIN about - ask if unclear

Response format:
- Be concise but helpful (2-3 sentences for simple questions)
- Use survival/outdoor terminology appropriately
- When executing actions, confirm what you're doing

Temperature setting: Use low temperature (0.2-0.4) for factual/action tasks.

Keep responses practical and actionable."""
```

**Przykład `prompts/templates/actions.py`:**

```python
"""Action-specific prompt templates."""


def get_action_prompt(action: str, app_name: str) -> str:
    """Get action-specific system prompt.

    Args:
        action: Action type
        app_name: Application name

    Returns:
        Action-specific prompt
    """
    prompts = {
        "create_item": _get_create_item_prompt(app_name),
        "update_item": _get_update_item_prompt(app_name),
        "delete_item": _get_delete_item_prompt(app_name),
        "create_container": _get_create_container_prompt(app_name),
    }

    return prompts.get(action, _get_default_prompt(app_name))


def _get_create_item_prompt(app_name: str) -> str:
    """Prompt for creating items."""
    return f"""You are an expert gear assistant for {app_name}.

Task: Create a new gear item based on user request.

Required fields:
- name (string, 1-100 chars): Item name
- category (string): Item category (see categories list below)
- quantity (integer, >= 1): Number of items
- priority (string): critical | high | medium | low
- status (string): owned | missing | toBuy

Optional fields:
- weight (number): Item weight
- weightUnit (string): g | kg
- notes (string): Additional notes
- expirationDate (date): Expiration date if applicable
- price (number): Item price
- currency (string): Price currency (USD, EUR, PLN, etc.)
- url (string): Product URL
- brand (string): Brand name
- color (string): Item color
- quality (string): low | medium | high
- wearable (boolean): Whether item is wearable
- consumable (boolean): Whether item is consumable

Categories:
- Shelter: Tents, tarps, bivvies, sleeping bags, hammocks
- Water: Bottles, filters, purification, bladders
- Fire: Lighters, matches, ferro rods, tinder
- Food: MREs, freeze-dried, energy bars, cooking gear
- FirstAid: Medical supplies, medications, trauma kits
- Tools: Knives, multitools, saws, axes
- Clothing: Jackets, pants, base layers, rain gear
- Navigation: Maps, compasses, GPS, headlamps
- Communication: Radios, signal devices, whistles
- Documents: IDs, cash, important papers
- Hygiene: Toiletries, sanitation, cleaning
- Electronics: Batteries, chargers, power banks
- Defense: Non-lethal defense items
- Misc: Other items

Safety rules:
1. NEVER create dangerous/illegal items
2. If category is unclear, ask user
3. Assign appropriate priority based on item type:
   - Critical: Water, shelter, first aid, fire
   - High: Food, tools, clothing
   - Medium: Electronics, hygiene
   - Low: Comfort items
4. If user doesn't specify required fields, ASK

Output format:
Respond conversationally, then include:
```json
{{
  "action": "create_item",
  "data": {{
    "name": "...",
    "category": "...",
    "quantity": 1,
    "priority": "...",
    "status": "...",
    // ... other fields
  }}
}}
```"""


def _get_update_item_prompt(app_name: str) -> str:
    """Prompt for updating items."""
    return f"""You are an expert gear assistant for {app_name}.

Task: Update an existing gear item.

Updatable fields: (same as create_item, plus):
- containerId (UUID): Move to different container (if nested)

Important:
- Only update fields user explicitly mentions
- Preserve other fields unchanged
- If updating quantity and it becomes 0, suggest deletion instead
- Validate new values (e.g., weight > 0, valid category)

Safety:
- Confirm significant changes (e.g., deleting expensive items)
- If unsure which item to update, ask for clarification

Output format:
```json
{{
  "action": "update_item",
  "data": {{
    "id": "item-uuid",
    "updates": {{
      "quantity": 2,
      // only changed fields
    }}
  }}
}}
```"""


def _get_delete_item_prompt(app_name: str) -> str:
    """Prompt for deleting items."""
    return f"""You are an expert gear assistant for {app_name}.

Task: Delete a gear item.

Safety:
- Confirm deletion if item is expensive (price > $50)
- Confirm deletion if item is critical priority
- If user says "remove" without context, ask which item

Output format:
```json
{{
  "action": "delete_item",
  "data": {{
    "id": "item-uuid",
    "reason": "user requested removal"
  }}
}}
```"""


def _get_create_container_prompt(app_name: str) -> str:
    """Prompt for creating containers."""
    return f"""You are an expert gear assistant for {app_name}.

Task: Create a new container (bag/pack).

Required fields:
- name (string): Container name
- description (string): Container purpose/description

Optional fields:
- color (string): default | blue | green | red | yellow | purple | orange | pink | teal | indigo
- shared (boolean): Whether container is shared with others

Common container types:
- Bug-Out Bag (BOB): 72-hour emergency evacuation bag
- Get Home Bag (GHB): Supplies to reach home
- EDC (Everyday Carry): Daily carried items
- INCH Bag: "I'm Never Coming Home" - long-term survival
- Car Kit: Vehicle emergency supplies
- First Aid Kit: Medical supplies
- Admin Pouch: Documents, cash, important papers

Suggestions:
- Recommend appropriate color for type (e.g., red for first aid)
- Suggest initial items if user wants

Output format:
```json
{{
  "action": "create_container",
  "data": {{
    "name": "...",
    "description": "...",
    "color": "default"
  }}
}}
```"""


def _get_default_prompt(app_name: str) -> str:
    """Default prompt for unknown actions."""
    return f"""You are a helpful assistant for {app_name}.

Respond conversationally. If user asks for an action you don't recognize, explain what you CAN do:
- Create gear items
- Update existing items
- Delete items
- Create containers
- Answer questions about survival gear"""
```

**Przykład `prompts/templates/examples.py`:**

```python
"""Few-shot examples for actions."""


def get_action_examples() -> list[dict[str, str]]:
    """Get few-shot examples for actions.

    Returns:
        List of example messages
    """
    return [
        {
            "role": "user",
            "content": "Add a Sawyer Mini water filter to my BOB"
        },
        {
            "role": "assistant",
            "content": """I'll add a Sawyer Mini water filter to your Bug-Out Bag. This is an excellent choice for water purification - lightweight and reliable.

```json
{
  "action": "create_item",
  "data": {
    "name": "Sawyer Mini Water Filter",
    "category": "Water",
    "quantity": 1,
    "priority": "critical",
    "status": "owned",
    "brand": "Sawyer",
    "weight": 56,
    "weightUnit": "g",
    "notes": "Filters up to 100,000 gallons"
  }
}
```"""
        },
        {
            "role": "user",
            "content": "Change the quantity of my energy bars to 6"
        },
        {
            "role": "assistant",
            "content": """I'll update the quantity of your energy bars to 6.

```json
{
  "action": "update_item",
  "data": {
    "id": "item-uuid-here",
    "updates": {
      "quantity": 6
    }
  }
}
```"""
        },
    ]
```

### 1.3 Implementacja w ChatService

**Zmiany w `chat_service.py`:**

```python
from app.modules.ai.prompts.factory import PromptFactory

class ChatService:
    def __init__(
        self,
        settings_service: SettingsService,
        history_repo: HistoryRepository,
        cache_service: PostgresCacheService | None = None,
    ):
        self.settings_service = settings_service
        self.history_repo = history_repo
        self.cache_service = cache_service
        self.prompt_factory = PromptFactory()  # ✅ Add PromptFactory

    async def chat(self, user_id: str, request: AiChatRequest) -> AiChatResponse:
        # ... existing code ...

        # ✅ Use PromptFactory instead of _build_messages
        messages = self.prompt_factory.build_chat_messages(
            user_message=request.message,
            history=request.history,
            context=request.context,
            include_examples=False,  # Can be enabled for better results
        )

        # ✅ Force low temperature for factual tasks
        temperature = min(temperature, 0.4)  # Cap at 0.4 for safety

        # ... rest of the code ...

    # ❌ Remove _build_messages method (replaced by PromptFactory)
```

### 1.4 Trade-offs i koszty

**Pros:**
- ✅ Łatwe zarządzanie promptami (templates w osobnych plikach)
- ✅ Versioning przez Git
- ✅ Testowalne (unit tests dla PromptFactory)
- ✅ Safety rules jasno zdefiniowane
- ✅ Domain knowledge embedded
- ✅ Łatwa iteracja (zmiana promptu nie wymaga edycji service)

**Cons:**
- ⚠️ Więcej plików (ale lepiej zorganizowane)
- ⚠️ Dłuższe prompty = więcej tokenów = wyższy koszt (ale lepsza jakość)

**Koszt:**
- **Effort:** Small-Medium (2-3 dni)
- **Tokens:** +20-30% więcej tokenów przez dłuższe prompty (ale offset przez lepszą jakość i mniej retry)
- **Maintainability:** Znacznie lepsze

### 1.5 Rekomendacje

**Must have:**
1. Wyodrębnić PromptFactory
2. Dodać safety rules do system prompt
3. Dodać domain knowledge (BOB, EDC, categories)
4. Wymusić niską temperature (0.3-0.4) dla actions

**Nice to have:**
2. Few-shot examples (można dodać później jeśli potrzeba)
3. Action-specific prompts (można zacząć od jednego uniwersalnego)

---

## 2. Structured Responses - Szczegółowa analiza

### 2.1 Gap Analysis

#### Obecna implementacja

**Parsowanie JSON (w `chat_service.py:192-212`):**

```python
def _parse_structured_output(self, message: str) -> StructuredOutput | None:
    # Look for JSON code blocks
    json_pattern = r"```json\s*(\{.*?\})\s*```"
    match = re.search(json_pattern, message, re.DOTALL)

    if not match:
        return None

    try:
        data = json.loads(match.group(1))
        return StructuredOutput(action=data.get("action"), data=data.get("data", {}))
    except (json.JSONDecodeError, ValueError):
        return None
```

**Problemy:**

1. ❌ **Nie używa JSON mode** - nie ma `response_format={"type":"json_object"}`
2. ❌ **Prymitywne parsowanie** - regex może nie złapać edge cases
3. ❌ **Brak walidacji action** - `action` może być dowolny string (nie enum)
4. ❌ **Brak walidacji data** - `data` może zawierać co kolwiek
5. ❌ **Brak retry logic** - jeśli parsing fail, zwraca None
6. ❌ **Brak error logging** - nie wiemy dlaczego parsing failed
7. ❌ **Non-greedy regex** - `.*?` może source błędów z nested JSON

### 2.2 Propozycja rozwiązania

#### Opcja A: JSON Mode (OpenAI compatible models)

**Zalety:**
- ✅ Native JSON output (bez markdown code blocks)
- ✅ Gwarantowany valid JSON
- ✅ Szybsze (mniej tokenów)

**Wady:**
- ⚠️ Nie wszystkie modele w OpenRouter wspierają `response_format`
- ⚠️ Wymaga explicit JSON schema w promptcie

**Implementacja:**

```python
# W OpenRouterProvider
async def chat(
    self,
    messages: list[dict[str, str]],
    model: str,
    max_tokens: int | None = None,
    temperature: float = 1.0,
    response_format: dict[str, str] | None = None,  # ✅ Add parameter
    **kwargs: Any,
) -> ChatResponse:
    try:
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,  # ✅ Pass to API
            **kwargs
        )
        # ... rest
```

```python
# W ChatService
async def chat(self, user_id: str, request: AiChatRequest) -> AiChatResponse:
    # ...

    # ✅ Enable JSON mode for compatible models
    json_mode_models = ["openai/gpt-4o", "openai/gpt-4o-mini", "openai/gpt-3.5-turbo"]
    response_format = None
    if model in json_mode_models:
        response_format = {"type": "json_object"}

    response = await provider.chat(
        messages=messages,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        response_format=response_format,  # ✅ Pass JSON mode
    )
```

#### Opcja B: Function Calling / Tool Use (Recommended)

**Zalety:**
- ✅ **Najlepsza opcja dla agent actions!**
- ✅ Native support w OpenAI/Anthropic/OpenRouter
- ✅ Built-in schema validation
- ✅ Lepsze rezultaty (model "wie" że to function call)
- ✅ Separacja conversation <> actions

**Wady:**
- ⚠️ Wymaga większych zmian w kodzie
- ⚠️ Nie wszystkie modele wspierają (ale większość tak)

**Implementacja - Function Calling:**

```python
# Nowy plik: prompts/tools.py
"""Tool definitions for function calling."""

from typing import Any


def get_tools() -> list[dict[str, Any]]:
    """Get tool definitions for AI function calling.

    Returns:
        List of tool definitions in OpenAI format
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "create_item",
                "description": "Create a new gear item in a container",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Item name (1-100 characters)",
                        },
                        "category": {
                            "type": "string",
                            "enum": [
                                "Shelter", "Water", "Fire", "Food", "FirstAid",
                                "Tools", "Clothing", "Navigation", "Communication",
                                "Documents", "Hygiene", "Electronics", "Defense", "Misc"
                            ],
                            "description": "Item category",
                        },
                        "quantity": {
                            "type": "integer",
                            "minimum": 1,
                            "description": "Number of items",
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["critical", "high", "medium", "low"],
                            "description": "Item priority level",
                        },
                        "status": {
                            "type": "string",
                            "enum": ["owned", "missing", "toBuy"],
                            "description": "Item status",
                        },
                        "weight": {
                            "type": "number",
                            "description": "Item weight (optional)",
                        },
                        "weightUnit": {
                            "type": "string",
                            "enum": ["g", "kg"],
                            "description": "Weight unit",
                        },
                        "notes": {
                            "type": "string",
                            "description": "Additional notes",
                        },
                        # ... other optional fields
                    },
                    "required": ["name", "category", "quantity", "priority", "status"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "update_item",
                "description": "Update an existing gear item",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "description": "Item UUID to update",
                        },
                        "updates": {
                            "type": "object",
                            "description": "Fields to update (same schema as create_item)",
                        },
                    },
                    "required": ["id", "updates"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "delete_item",
                "description": "Delete a gear item",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "description": "Item UUID to delete",
                        },
                    },
                    "required": ["id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "create_container",
                "description": "Create a new gear container (bag/pack)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Container name",
                        },
                        "description": {
                            "type": "string",
                            "description": "Container description/purpose",
                        },
                        "color": {
                            "type": "string",
                            "enum": [
                                "default", "blue", "green", "red", "yellow",
                                "purple", "orange", "pink", "teal", "indigo"
                            ],
                            "description": "Container color",
                        },
                    },
                    "required": ["name", "description"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_container_details",
                "description": "Get detailed information about a container and its items",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "container_id": {
                            "type": "string",
                            "description": "Container UUID (optional, if not provided returns all containers)",
                        },
                    },
                    "required": [],
                },
            },
        },
    ]
```

**Zmiana w OpenRouterProvider:**

```python
async def chat(
    self,
    messages: list[dict[str, str]],
    model: str,
    max_tokens: int | None = None,
    temperature: float = 1.0,
    tools: list[dict[str, Any]] | None = None,  # ✅ Add tools parameter
    tool_choice: str | dict | None = None,  # ✅ Add tool_choice
    **kwargs: Any,
) -> ChatResponse:
    try:
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,  # ✅ Pass tools
            tool_choice=tool_choice,  # ✅ Pass tool_choice
            **kwargs
        )

        choice = response.choices[0]
        message_content = choice.message.content or ""

        # ✅ Handle tool calls
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
            tool_calls=tool_calls,  # ✅ Return tool calls
            prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
            completion_tokens=response.usage.completion_tokens if response.usage else 0,
            total_tokens=response.usage.total_tokens if response.usage else 0,
            model=response.model,
            finish_reason=choice.finish_reason,
            raw_response=response.model_dump(),
        )
```

**Zmiana w ChatResponse (providers/base.py):**

```python
@dataclass
class ChatResponse:
    """Response from AI chat completion."""

    message: str
    tool_calls: list[dict[str, Any]] | None = None  # ✅ Add tool_calls
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    model: str = ""
    finish_reason: str | None = None
    raw_response: dict[str, Any] | None = None
```

**Zmiana w ChatService:**

```python
from app.modules.ai.prompts.tools import get_tools

class ChatService:
    async def chat(self, user_id: str, request: AiChatRequest) -> AiChatResponse:
        # ... existing code ...

        # ✅ Get tools for function calling
        tools = get_tools()

        # Call AI with tools
        response = await provider.chat(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            tools=tools,  # ✅ Pass tools
            tool_choice="auto",  # AI decides when to use tools
        )

        # ✅ Handle tool calls (if any)
        tool_call_result = None
        if response.tool_calls:
            tool_call_result = await self._execute_tool_calls(
                user_id, response.tool_calls
            )

        # ✅ Parse structured output from tool calls (preferred)
        # OR from message content (fallback for non-tool models)
        structured = None
        if tool_call_result:
            structured = StructuredOutput(
                action=tool_call_result["action"],
                data=tool_call_result["data"],
            )
        else:
            # Fallback: parse from message (existing regex logic)
            structured = self._parse_structured_output(response.message)

        # ... rest of the code ...

    async def _execute_tool_calls(
        self, user_id: str, tool_calls: list[dict[str, Any]]
    ) -> dict[str, Any] | None:
        """Execute tool calls from AI.

        Args:
            user_id: User ID
            tool_calls: List of tool calls from AI

        Returns:
            Tool call result or None
        """
        import json

        # For now, just return the first tool call
        # (later can handle multiple tool calls)
        if not tool_calls:
            return None

        tool_call = tool_calls[0]
        function_name = tool_call["function"]["name"]
        arguments = json.loads(tool_call["function"]["arguments"])

        # Map function name to action
        return {
            "action": function_name,
            "data": arguments,
        }
```

#### Opcja C: Hybrid Approach (JSON Mode + Better Validation)

Jeśli function calling jest zbyt dużą zmianą na start, można:

1. Używać JSON mode (jeśli model wspiera)
2. Dodać Pydantic validation dla StructuredOutput
3. Dodać retry logic przy validation errors

**Implementacja:**

```python
# Nowy plik: parsers/structured_output_parser.py
"""Parser and validator for structured AI outputs."""

import json
import logging
import re
from typing import Any

from pydantic import BaseModel, ValidationError

from app.modules.ai.schemas import StructuredOutput


logger = logging.getLogger(__name__)


class StructuredOutputParser:
    """Parser for structured AI outputs with validation and retry."""

    def parse(self, message: str) -> StructuredOutput | None:
        """Parse structured output from AI message.

        Args:
            message: AI message content

        Returns:
            Parsed and validated structured output or None
        """
        # Try parsing JSON from code blocks
        parsed_data = self._extract_json_from_code_block(message)

        # If no code block, try parsing entire message as JSON
        if not parsed_data:
            parsed_data = self._parse_json_content(message)

        if not parsed_data:
            logger.warning("Failed to parse JSON from AI response")
            return None

        # Validate and create StructuredOutput
        try:
            return self._validate_structured_output(parsed_data)
        except ValidationError as e:
            logger.error(f"Validation error for structured output: {e}")
            return None

    def _extract_json_from_code_block(self, message: str) -> dict[str, Any] | None:
        """Extract JSON from markdown code block.

        Args:
            message: Message with potential code block

        Returns:
            Parsed JSON or None
        """
        # Try multiple patterns
        patterns = [
            r"```json\s*(\{.*?\})\s*```",  # ```json { ... } ```
            r"```\s*(\{.*?\})\s*```",      # ``` { ... } ```
        ]

        for pattern in patterns:
            match = re.search(pattern, message, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    continue

        return None

    def _parse_json_content(self, message: str) -> dict[str, Any] | None:
        """Try parsing entire message as JSON.

        Args:
            message: Message content

        Returns:
            Parsed JSON or None
        """
        try:
            return json.loads(message)
        except json.JSONDecodeError:
            return None

    def _validate_structured_output(self, data: dict[str, Any]) -> StructuredOutput:
        """Validate structured output data.

        Args:
            data: Parsed JSON data

        Returns:
            Validated StructuredOutput

        Raises:
            ValidationError: If validation fails
        """
        # Validate action is one of allowed actions
        allowed_actions = [
            "create_item",
            "update_item",
            "delete_item",
            "create_container",
            None,
        ]

        action = data.get("action")
        if action not in allowed_actions:
            raise ValidationError(f"Invalid action: {action}")

        # Create StructuredOutput (Pydantic will validate)
        return StructuredOutput(
            action=action,
            data=data.get("data", {}),
        )
```

**Usage w ChatService:**

```python
from app.modules.ai.parsers.structured_output_parser import StructuredOutputParser

class ChatService:
    def __init__(self, ...):
        # ...
        self.output_parser = StructuredOutputParser()

    async def chat(self, user_id: str, request: AiChatRequest) -> AiChatResponse:
        # ...

        # Parse with better validation
        structured = self.output_parser.parse(response.message)

        # If parsing failed and it was an action request, retry
        if not structured and self._is_action_request(request.message):
            logger.info("Retrying with clearer prompt due to parsing failure")
            structured = await self._retry_with_clearer_prompt(
                user_id, request, response.message
            )

        # ...

    def _is_action_request(self, message: str) -> bool:
        """Check if message is likely an action request."""
        action_keywords = ["add", "create", "update", "change", "delete", "remove"]
        return any(keyword in message.lower() for keyword in action_keywords)

    async def _retry_with_clearer_prompt(
        self, user_id: str, request: AiChatRequest, previous_response: str
    ) -> StructuredOutput | None:
        """Retry with clearer prompt when parsing fails.

        Args:
            user_id: User ID
            request: Original request
            previous_response: Previous AI response

        Returns:
            Parsed output or None
        """
        # Add clarifying message
        retry_messages = request.history + [
            {"role": "user", "content": request.message},
            {"role": "assistant", "content": previous_response},
            {
                "role": "user",
                "content": "Please provide the action in valid JSON format inside ```json code block."
            },
        ]

        # Get user settings (for model, etc.)
        user_settings = await self.settings_service.get_settings(user_id)
        model = request.model or user_settings.selected_model

        # Simple retry (no caching)
        provider = OpenRouterProvider()
        response = await provider.chat(
            messages=retry_messages,
            model=model,
            max_tokens=500,
            temperature=0.2,  # Lower temp for retry
        )

        return self.output_parser.parse(response.message)
```

### 2.3 Rekomendacje

**Recommended approach:**

**Faza 1 (Quick win - 1-2 dni):**
1. Implement better parser (StructuredOutputParser) z validation
2. Add logging dla parsing errors
3. Add basic retry logic

**Faza 2 (Systematic - 3-5 dni):**
1. Implement Function Calling / Tool Use (recommended!)
2. Define tools w `prompts/tools.py`
3. Update OpenRouterProvider i ChatService
4. Fallback na regex parsing dla non-tool models

**Why Function Calling is better:**
- Native support dla agent actions
- Built-in schema validation
- Lepsze rezultaty (model rozumie że to tool)
- Separacja conversation <> actions
- Industry standard (OpenAI, Anthropic, OpenRouter)

---

## 3. Safety & Fallbacks - Szczegółowa analiza

### 3.1 Gap Analysis

**Obecny stan:**
- ✅ Basic try/except w `OpenRouterProvider.chat`
- ❌ Brak safety guards w promptach
- ❌ Brak exponential backoff retry
- ❌ Brak fallback responses
- ❌ Brak output validation (czy item istnieje w DB?)
- ❌ Brak rate limiting
- ❌ Brak model failover

### 3.2 Propozycja rozwiązania

#### A. Safety Guards w Promptach

**Już pokryte w sekcji #1 (Prompt Engineering):**
- Safety rules w system prompt
- "Don't hallucinate" instructions
- "If unsure, ask user" rules

#### B. Exponential Backoff Retry

**Użyj `tenacity` library:**

```bash
# backend/requirements.txt
tenacity==8.2.3
```

**Implementacja w OpenRouterProvider:**

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
    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str,
        max_tokens: int | None = None,
        temperature: float = 1.0,
        **kwargs: Any,
    ) -> ChatResponse:
        """Send chat completion with automatic retry on failures.

        Retries up to 3 times with exponential backoff:
        - 1st retry: wait 2s
        - 2nd retry: wait 4s
        - 3rd retry: wait 8s

        Args:
            messages: Chat messages
            model: Model ID
            max_tokens: Max tokens
            temperature: Sampling temperature
            **kwargs: Additional args

        Returns:
            Chat response

        Raises:
            OpenRouterError: After all retries exhausted
        """
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )

            # ... rest of implementation ...

        except (RateLimitError, APITimeoutError, APIError) as e:
            # tenacity will retry these automatically
            raise
        except Exception as e:
            # Other errors are not retried
            raise OpenRouterError(f"OpenRouter API request failed: {e}") from e
```

#### C. Graceful Fallback Responses

**W ChatService:**

```python
async def chat(self, user_id: str, request: AiChatRequest) -> AiChatResponse:
    try:
        # ... existing code ...

        # Call AI
        response = await provider.chat(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        # ... parse structured output ...

        return AiChatResponse(...)

    except OpenRouterError as e:
        logger.error(f"AI chat failed for user {user_id}: {e}")

        # Return graceful fallback response
        return self._create_fallback_response(
            error_message=str(e),
            user_message=request.message,
        )

    except Exception as e:
        logger.exception(f"Unexpected error in AI chat for user {user_id}: {e}")

        return self._create_fallback_response(
            error_message="An unexpected error occurred",
            user_message=request.message,
        )


def _create_fallback_response(
    self, error_message: str, user_message: str
) -> AiChatResponse:
    """Create fallback response when AI fails.

    Args:
        error_message: Error message
        user_message: Original user message

    Returns:
        Fallback response
    """
    return AiChatResponse(
        message=(
            "I'm sorry, I'm having trouble processing your request right now. "
            "Please try again in a moment, or rephrase your question."
        ),
        structured_output=None,
        tokens={"prompt": 0, "completion": 0, "total": 0},
        cost=0.0,
        model="fallback",
        prompt=user_message,
    )
```

#### D. Output Validation (Optional - P2)

**Jeśli chcemy walidować czy items exist w DB:**

```python
# Nowy plik: services/output_validator.py
"""Validator for AI output against business rules."""

import logging
from uuid import UUID

from app.modules.gear.repository import GearRepository
from app.modules.ai.schemas import StructuredOutput


logger = logging.getLogger(__name__)


class OutputValidator:
    """Validates AI output against business rules and database."""

    def __init__(self, gear_repo: GearRepository):
        """Initialize validator.

        Args:
            gear_repo: Gear repository
        """
        self.gear_repo = gear_repo

    async def validate(
        self, user_id: str, output: StructuredOutput
    ) -> tuple[bool, str | None]:
        """Validate structured output.

        Args:
            user_id: User ID
            output: Structured output from AI

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not output or not output.action:
            return True, None  # No action, nothing to validate

        action = output.action
        data = output.data

        # Validate based on action type
        if action == "create_item":
            return await self._validate_create_item(user_id, data)
        elif action == "update_item":
            return await self._validate_update_item(user_id, data)
        elif action == "delete_item":
            return await self._validate_delete_item(user_id, data)
        elif action == "create_container":
            return await self._validate_create_container(user_id, data)

        return True, None

    async def _validate_create_item(
        self, user_id: str, data: dict
    ) -> tuple[bool, str | None]:
        """Validate create_item action."""
        # Check required fields
        required = ["name", "category", "quantity", "priority", "status"]
        missing = [f for f in required if f not in data]
        if missing:
            return False, f"Missing required fields: {', '.join(missing)}"

        # Validate weight (if provided)
        if "weight" in data and data["weight"] <= 0:
            return False, "Weight must be positive"

        # Validate quantity
        if data["quantity"] <= 0:
            return False, "Quantity must be positive"

        return True, None

    async def _validate_update_item(
        self, user_id: str, data: dict
    ) -> tuple[bool, str | None]:
        """Validate update_item action."""
        # Check item exists
        item_id = data.get("id")
        if not item_id:
            return False, "Missing item ID"

        try:
            item_uuid = UUID(item_id)
        except ValueError:
            return False, "Invalid item ID format"

        # Check item exists in DB (and belongs to user)
        item = await self.gear_repo.get_item(item_uuid)
        if not item:
            return False, f"Item {item_id} not found"

        # TODO: Check if item belongs to user's container
        # (requires user_id in items or join with containers)

        return True, None

    async def _validate_delete_item(
        self, user_id: str, data: dict
    ) -> tuple[bool, str | None]:
        """Validate delete_item action."""
        # Similar to update_item
        return await self._validate_update_item(user_id, data)

    async def _validate_create_container(
        self, user_id: str, data: dict
    ) -> tuple[bool, str | None]:
        """Validate create_container action."""
        # Check required fields
        required = ["name", "description"]
        missing = [f for f in required if f not in data]
        if missing:
            return False, f"Missing required fields: {', '.join(missing)}"

        return True, None
```

**Usage w ChatService:**

```python
from app.modules.ai.services.output_validator import OutputValidator

class ChatService:
    def __init__(
        self,
        settings_service: SettingsService,
        history_repo: HistoryRepository,
        cache_service: PostgresCacheService | None = None,
        output_validator: OutputValidator | None = None,  # Optional
    ):
        self.settings_service = settings_service
        self.history_repo = history_repo
        self.cache_service = cache_service
        self.output_validator = output_validator

    async def chat(self, user_id: str, request: AiChatRequest) -> AiChatResponse:
        # ... existing code ...

        # Parse structured output
        structured = self.output_parser.parse(response.message)

        # Validate output (if validator is available)
        if structured and self.output_validator:
            is_valid, error_msg = await self.output_validator.validate(
                user_id, structured
            )

            if not is_valid:
                logger.warning(f"AI output validation failed: {error_msg}")
                # Option 1: Return error to user
                # Option 2: Retry with feedback
                # Option 3: Clear the action (treat as conversation only)
                structured = None  # Clear invalid action
                cleaned_message += f"\n\n(Note: Action was rejected - {error_msg})"

        # ... rest of code ...
```

### 3.3 Rekomendacje

**Must have (Faza 1):**
1. Exponential backoff retry (tenacity) - 1 dzień
2. Graceful fallback responses - 1 dzień
3. Safety guards w promptach (już w #1) - 0 dni (part of prompt work)

**Nice to have (Faza 2):**
4. Output validation (OutputValidator) - 2-3 dni
5. Rate limiting (per-user) - 1-2 dni
6. Model failover - 2-3 dni (może być później)

---

## 4. Function Calling / Tool Use Integration

### 4.1 Dlaczego Function Calling?

W kontekście Twojego use case (agent wykonuje akcje), **Function Calling jest najlepszym rozwiązaniem** bo:

1. ✅ **Native support** - OpenAI/Anthropic/OpenRouter mają built-in function calling
2. ✅ **Schema validation** - model rozumie schema i generuje valid JSON
3. ✅ **Lepsze rezultaty** - model "wie" że wywołuje funkcję, nie tylko pisze tekst
4. ✅ **Separacja** - conversation vs actions są oddzielone
5. ✅ **Extensible** - łatwo dodać nowe funkcje (np. `get_container_details`)
6. ✅ **Industry standard** - wszyscy używają (ChatGPT, Claude, etc.)

### 4.2 Implementation Roadmap

**Krok 1: Define Tools** (1 dzień)
- Stworzyć `prompts/tools.py` z tool definitions
- Zdefiniować 4-5 podstawowych tools (create_item, update_item, delete_item, create_container, get_container_details)

**Krok 2: Update Provider** (1 dzień)
- Dodać `tools` i `tool_choice` parameters do OpenRouterProvider.chat
- Handle tool_calls w response

**Krok 3: Update ChatService** (1-2 dni)
- Pass tools do provider
- Handle tool_calls w response
- Execute tool calls (na razie mock - tylko zwrócenie function name + args)
- Fallback na regex parsing dla non-tool models

**Krok 4: Integrate with GearService** (2-3 dni - opcjonalne na start)
- Actually execute actions (create items, etc.)
- Wymaga permission checks (czy user może modyfikować container?)
- Wymaga transaction handling

### 4.3 Example Flow

**User:** "Add a Sawyer Mini water filter to my BOB"

**AI (with function calling):**
1. Model decides to use `create_item` tool
2. Returns tool_call:
```json
{
  "id": "call_abc123",
  "type": "function",
  "function": {
    "name": "create_item",
    "arguments": "{\"name\":\"Sawyer Mini Water Filter\",\"category\":\"Water\",\"quantity\":1,\"priority\":\"critical\",\"status\":\"owned\",\"brand\":\"Sawyer\",\"weight\":56,\"weightUnit\":\"g\"}"
  }
}
```

**ChatService:**
1. Parses tool_call
2. (Opcjonalnie) Executes action via GearService
3. Returns response:
```json
{
  "message": "I've added a Sawyer Mini Water Filter to your Bug-Out Bag.",
  "structured_output": {
    "action": "create_item",
    "data": {...}
  },
  "tokens": {...},
  "cost": 0.002
}
```

**Frontend:**
1. Displays message
2. Executes action locally (or via backend if we integrated)

---

## Podsumowanie i następne kroki

### Co analizowaliśmy:

1. ✅ **Prompt Engineering** - PromptFactory, templates, safety rules, domain knowledge
2. ✅ **Structured Responses** - JSON mode, function calling, validation, retry
3. ✅ **Safety & Fallbacks** - retry with backoff, graceful fallbacks, output validation

### Rekomendowane podejście (Pragmatic Balance):

**Quick Wins (Tydzień 1):**
1. Wyodrębnić PromptFactory z templates (2 dni)
2. Dodać safety rules i domain knowledge do promptów (1 dzień)
3. Implement better StructuredOutputParser z validation (1 dzień)
4. Dodać exponential backoff retry (tenacity) (1 dzień)
5. Dodać graceful fallback responses (1 dzień)

**Systematic Implementation (Tydzień 2):**
6. Implement Function Calling / Tool Use (3-4 dni)
   - Define tools
   - Update provider
   - Update ChatService
   - Fallback dla non-tool models

**Optional Enhancements (Tydzień 3 lub później):**
7. Output validation (OutputValidator) (2 dni)
8. Actually execute tool calls via GearService (2-3 dni)
9. Rate limiting (1-2 dni)
10. Structured logging (1 dzień)

### Total effort estimate:
- **Minimum viable (Quick wins):** 1 tydzień
- **Solid foundation (Quick wins + Function calling):** 2 tygodnie
- **Full implementation:** 3-4 tygodnie

### Gotowy na Iterację 3?

W Iteracji 3 stworzę szczegółowy plan implementacji z:
- Konkretne tasks (break down)
- Kolejność (dependencies)
- Definicje "done"
- Złożoność (S/M/L)

Masz jakieś pytania lub uwagi do tej analizy?
