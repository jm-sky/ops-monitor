# Safety, Hallucination Checks & Fallbacks

AI hallucinations or unsafe suggestions must be guarded against. Build multi-layer checks:

Guard in Prompts: As a first step, instruct the model not to invent items. E.g. "If unsure, return an empty list or say you don't know". Use system rules like "Answer only based on input data." Maintain a very low temperature for safety.

Ground with Facts (RAG): Don't rely on the model's memory. Instead retrieve related info (e.g. from gear manuals or a knowledge base) and include it in the prompt. Retrieval-augmented generation (RAG) ensures responses are based on provided facts. For example, embed relevant gear specs or survival guidelines so the model "answers from these specific facts".

Output Validation: After receiving AI output, automatically verify it. For example, check that recommended item names exist in your gear database. Use business rules (e.g. weight limits, duplications). Parasoft suggests "automated verification" – e.g. a lightweight "judge" model or simple code that assigns confidence or flags inconsistencies. If checks fail, you can retry, switch prompts, or warn the user.

Error Handling: Wrap all LLM calls with try/except. On API errors or timeouts, log the issue and retry (using exponential backoff) or switch to a backup model/provider via OpenRouter. For example, annotate calls with @retry to recover from transient failures. Have an alternate path: if one model fails, route the request to another model with similar capability (OpenRouter supports "routing across providers").

Fallback Responses: If AI fails or output is invalid, return a safe default (e.g. an empty recommendation list with a warning) rather than crashing. In critical cases, flag for human review. The Parasoft guide even suggests human-in-the-loop checks if errors are costly. For most gear recommendations, an incomplete answer is likely preferable to a hallucination, so handle it gracefully (e.g. "Unable to generate recommendations at this time").

