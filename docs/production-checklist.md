# Before production

These are teaching applications, not hardened hosted services. Read [agent execution boundaries](../AGENTS.md) and [validation](validation.md).

- Keep provider credentials server-side, scoped and rotated. Prevent headers, exception dumps and URL queries from leaking them.
- Authenticate your application users. Add per-user concurrency, duration, text-size and spending limits. A loopback dev runner is not safe to expose publicly.
- Record user consent and review each provider's terms, retention, residency and supported languages. Maya language support does not imply identical Soniox/LLM coverage.
- Measure the entire path: microphone, STT finalization, LLM, Maya first PCM, client buffer, first sound. Keep warm/cold calls separate. Do not promise a documentation benchmark as a latency SLA.
- Test headphone and speaker operation, echo cancellation, short/long turns, silence, background noise and barge-in on the actual supported devices.
- Test Hindi, Telugu and Indian English using native listeners. Add each promised language and voice to a reviewed sample matrix. PCM integrity does not prove pronunciation quality.
- Bound queues and preserve ordering. Respect metadata and flush normal tails. On interruption discard local queues and old contexts. Never mute only the model while the client keeps playing buffered speech.
- Handle timeouts, disconnects, invalid metadata, provider errors, rate limits and cancellation without hidden provider substitution or replay of partially heard speech.
- Pin and review dependencies. Keep weekly drift checks active, review package advisories, and test upgrades before merging. Never give PR code access to live secrets.
- Monitor safe IDs, errors, first-audio timing, queue delay and dropped/late frames. Don't log customer text/audio by default. No telemetry is embedded in these recipes.
- Load-test an isolated environment within an explicit budget. This cookbook does not establish your production concurrency capacity.
- Provide session teardown, idle limits, resource cleanup, health checks and a rollback plan. Verify production route and final client audio independently after deployment.

Do not claim the whole checklist is satisfied merely because you copied these examples.
