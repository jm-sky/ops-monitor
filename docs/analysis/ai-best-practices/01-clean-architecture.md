# Clean Architecture & Service Boundaries

Adopt a layered, domain-driven design so that AI calls are isolated from core business logic.  For example, use separate layers/modules – e.g. a Domain layer with survival-gear entities and rules, an Application/Service layer orchestrating workflows, an Infrastructure layer handling external calls (databases, LLM APIs), and a Presentation/API layer (FastAPI endpoints).  In practice, implement an AIService (in Infrastructure) that encapsulates all LLM interactions (via OpenRouter) and is injected into your application logic (Presentation layer) via FastAPI’s dependency injection.  This ensures the business logic (recommending gear) doesn't depend on OpenRouter or FastAPI specifics.  Define clear interfaces or repository patterns for inventory and user data, so AI calls become just another external dependency. For example, Kumar et al. use an AIService class with methods (and caching) injected into FastAPI routes. This clean layering (domain→application→infrastructure→API) yields maintainability and testability.

Separate Concerns: Keep "what gear to recommend" logic in domain/use-case classes; have a PromptFactory build LLM prompts; and an AIService that calls OpenRouter.  Inject these via FastAPI dependencies so routes remain thin.

Dependency Injection: Define interfaces (e.g. IGearRepository) for data access. The LLM integration should call these interfaces (or use retrieved data) rather than hardcode queries.

Stateless Services: Make the AIService and related components stateless or idempotent, using external storage (cache, DB) for state. This allows horizontal scaling (e.g. deploying on multiple instances or serverless functions).

Microservice Option: If scale demands or organizational separation, consider running AI logic as a separate microservice. But even within one FastAPI app, logically isolate it (as above) so you could extract it later.

