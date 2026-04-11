# Proposed AI Integration Architecture

Below is a high-level sketch of the FastAPI modules and flow:

- API Layer (FastAPI endpoints): Defines routes (e.g. POST /recommend) that accept JSON input (trip details, user profile). Uses Pydantic for input validation. Each route injects dependencies like AIService, GearRepository, CacheLayer, and an Auth guard.

- PromptFactory Module: Takes domain objects (trip context, inventory list, user profile) and constructs the final LLM prompt (system+user messages). Encapsulates prompt templates and formatting logic.

- AIService Module: Encapsulates all interaction with OpenRouter/LLMs. Methods like generate_recommendations(prompt) call the OpenRouter API, handle retries/backoff, and return raw JSON or text. Internally, it sets parameters (model name, temperature, JSON mode) and applies rate-limits. The service uses an asynchronous HTTP client.

- ResponseParser/Validator: After AIService returns data, this component parses the response into a structured form (e.g. a Pydantic model matching the expected schema). It checks JSON validity and required fields. If validation fails, it triggers fallback logic (e.g. try reformatting or a simpler prompt).

- CacheLayer: A simple cache (e.g. LRU cache or Redis) keyed on prompt hash or a request signature. Before calling AIService, check cache. After a successful parse, store the result. This reduces latency/cost for repeat queries.

- Embedding/RAG Module: Handles retrieval from the embedding store. Given the trip context or question, it queries a vector DB to fetch relevant text passages. Those are fed into PromptFactory to enrich the prompt. This module also manages vector store indexing/updating.

- GearRepository: Abstraction over the gear inventory database. Provides methods like get_equipment_by_category(), list_all_gear(), etc. Used to validate or augment LLM suggestions (e.g. filtering nonexistent items).

- RecommendationEngine (Business Logic): Applies domain rules and combines AI output with data. For instance, it might merge LLM-suggested items with user's existing inventory, enforce weight limits, or score items. This keeps critical logic in code, not LLM.

- Logger & Metrics: Cross-cutting services that log each request/response (with sanitized data) and expose metrics (latency, error rates). Integrate with monitoring tools (Prometheus, Grafana, etc.).

- Security/Config: Modules for API key or JWT verification on endpoints, and config management (e.g. loading OpenRouter API keys, model names, and prompt templates from secure config).


In summary, the system flow is: Request → PromptFactory → (Cache?) → RAG retrieval → Enhanced Prompt → AIService → ResponseParser → RecommendationEngine → Response. Key modules like PromptFactory, AIService, CacheLayer, and Validator each handle one concern, yielding a clean, testable architecture.

