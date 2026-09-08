# Maya API reference

The [Maya API documentation](https://www.mayaresearch.ai/llm.txt) is authoritative. This folder is a focused, dated **Maya Calyx-only** companion for the examples, not a new official server implementation or a completeness guarantee for future releases. The catalog intentionally selects 24 Calyx voices from that source; exclusions are publisher choices, not API retirements.

- [HTTP fields and audio](http.md)
- [WebSocket v2 lifecycle](websocket.md)
- [Machine-readable voice/language snapshot](catalog.json)
- [Troubleshooting](../troubleshooting.md)
- [Provenance and pinned versions](../sources.json)

Agent note: use the matching executable recipe and tests. Do not copy incomplete pseudocode from unrelated docs into production.

## Known disagreements, checked 2026-09-08

1. The public reference lists 31 Calyx voices; this cookbook intentionally selects 24. The pinned Pipecat package at `2c3b569` accepts only 19 of the provider's voices. For that integration use the intersection of the cookbook catalog and the package's exported `MODELS`; direct HTTP examples use the 24-voice cookbook selection. Do not patch validation out or replace one voice with another. Upgrade only after a maintained release/commit is tested.
2. The refreshed reference links to the merged Pipecat docs contribution [PR 1257](https://github.com/pipecat-ai/docs/pull/1257). The maintained package is [MayaResearch/pipecat-maya](https://github.com/MayaResearch/pipecat-maya). The cookbook uses the reachable package README and pins its tested commit; a merged docs contribution is not a release of Pipecat core.
3. [LiveKit PR 6899](https://github.com/livekit/agents/pull/6899) is open, not an upstream release. The cookbook pins the public Maya fork.
4. The reference contains conflicting descriptions of concurrency caps. Do not infer one universal cap or a guarantee of unlimited traffic. Use account guidance, bound concurrency and handle 429. These recipes explicitly select Calyx rather than depending on the server's model default.
5. Maya labels little-endian PCM as `audio/L16`. For this provider follow its documented little-endian bytes, not a generic big-endian interpretation of that MIME label. Verify the rate in the actual response.
6. The refreshed request table says `voice` is required and the model default is Calyx, but one older sentence still says only `text` is required. These recipes explicitly send both model and voice and do not depend on that disagreement.

There is no invented `GET /voices` endpoint here. The snapshot is checked against the documented catalog. Perceived pronunciation/voice identity still requires listening; successful synthesis does not prove it.
