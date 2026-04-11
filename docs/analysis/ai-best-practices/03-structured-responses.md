# Enforcing Structured (JSON) Responses

To parse AI output automatically, enforce a structured JSON format.  Modern LLM APIs support structured output modes or function calls. You should:

Supply a JSON Schema or Format: In the system/user prompt, include a clear JSON schema or example. For instance, "Respond ONLY with a JSON object matching: { items: [ {name: string, weight_kg: number, category: string, rationale: string} ] }." Many models now honor a provided schema (OpenRouter calls this structured outputs, a subset of tool-calling).

Use JSON Mode or Function Call: If using OpenAI (via OpenRouter), set response_format={"type":"json_object"} or invoke as a function call. This forces the model to output valid JSON. The Instructor library example shows defining a Pydantic response model and instructing the model to match it.

Prompt Conventions: Tell the model explicitly: "Output must be valid JSON with no extraneous text." You can start/stop delimiters (e.g. json ...) but many new APIs do this automatically.

Validation Post-Processing: On the backend, validate/parsing the returned JSON (e.g. with Pydantic). If parsing fails or required fields are missing, treat it as an error or retry with a clearer prompt. For fallback, you might strip any extra text and attempt to JSON-parse.

Benefits: Well-structured output "helps integrate the model's responses into workflows without cleanup" – it "reduces ambiguity and hallucinations" by constraining the answer.   Tasks like listing gear are ideal for JSON (fixed fields like item names, quantities, categories).

