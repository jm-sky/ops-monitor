# Prompt Engineering Best Practices

Design prompts to be clear, specific, and unambiguous. Always describe the task, expected answer format, and provide context (climate, terrain, user profile, etc.) to "ground" the model. For example, start with a system or first message like: "You are an expert survival gear recommender. Given the user's trip details and inventory, return a JSON list of needed items." Then in the user prompt include explicit requirements (terrain type, climate conditions) and any relevant user constraints. Use few-shot examples if needed to illustrate format and style, and specify tone or verbosity if relevant. Iteratively refine prompts: test outputs, examine errors, and adjust wording until results are reliable.

Explicit Instructions: Tell the model exactly what data to produce and how (e.g. "List each recommended item with keys: name, category, reason"). Clearly define any domain-specific terms (e.g. "ALICE pack" or "synthetic insulation"). Avoid vague queries like "What should I pack?" without structure.

System Messages: Use a system prompt layer to set rules (e.g. "Do not suggest illegal or unsafe items" or "Answer only based on given info") to guard against off-topic or hallucinated responses.

Temperature/Creativity: For factual or recommendation tasks, keep model temperature low (~0) to favor consistency and reduce randomness. Only raise temperature when creativity is desired (e.g. storytelling about survival tips).

Conciseness: Keep prompts as brief as possible while providing needed context. Long prompts can introduce noise. CloudSquid notes that "shorter prompts often outperform longer ones" due to focus.

Prompt Templates: Factor out static parts of prompts into reusable templates (for each feature/endpoint). Have a PromptFactory module that, given parameters (user_profile, context, etc.), returns a fully-formed prompt. This ensures consistency and maintainability.

