# Performance & Scaling

Optimize LLM usage and backend performance for low latency and high throughput:

Caching: Cache AI responses for identical or similar prompts to avoid repeated API calls. For example, use an LRU cache keyed by (user_id, prompt_text) as in Kumar's example. Log cache hit/miss rates to tune cache size (see [30]). Also consider semantic caching: for very similar queries, reuse the nearest cached response.

Asynchronous Concurrency: Call OpenRouter asynchronously so multiple users or parallel tasks can be served. FastAPI's async support lets you await the LLM call, and you can run many in parallel (bounded by rate limits). If on a multi-core server, use asyncio or thread pools to maximize throughput.

Rate Limiting: Throttle incoming requests per user or IP to avoid API quota spikes and to protect backend resources. In [30], they limit chat to "10 requests per minute per IP". Use FastAPI middleware or libraries (like slowapi) to enforce rate limits.

Serverless/Auto-Scaling: Deploy on platforms that auto-scale (Azure Functions, AWS Lambda, Kubernetes auto-scaling) so the system can handle bursts of traffic. This also helps manage cost during low-traffic periods.

Model/Provider Failover: Use OpenRouter's multi-model capability. For example, if GPT-4o hits rate limit or latency spikes, route the call to Claude 3.5 or Gemini Flash transparently. Implement logic to switch providers on the fly (e.g. try-primary, else try-secondary).

Versioning: Keep track of LLM versions and prompt versions. Tag each request with the model name and version used. When upgrading models (e.g. moving from GPT-4 to GPT-4o), use A/B testing on a small user subset to compare outputs. Version your prompt templates too, so you can roll back if a new prompt yields poorer results.

Monitoring: Instrument latency and error metrics. Monitor LLM response times and tail latencies. Cache monitoring (hit rates) is critical, as Kumar's example logs hits vs misses. Use these metrics to scale and optimize (e.g. increase cache if misses are high, or scale up concurrency if latencies grow).

