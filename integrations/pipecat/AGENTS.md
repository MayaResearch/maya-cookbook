# Coding-agent instructions: Pipecat voice agent with Maya

Read [root AGENTS.md](../../AGENTS.md) first. The [README](README.md) is the single source for exact install, configure, run, verification and stop commands. Execute from this folder; retain the full checkout for shared references/helpers.

- Outcome: Open http://127.0.0.1:7860 in your chosen browser, connect, and say one short sentence. You should hear a Maya reply. Interrupt and start another turn, then disconnect. The packaged Pipecat development UI is an external pinned dependency.
- Configuration: Use this folder's ignored `.env` or your process environment. See blank `.env.example`. Process values win. STT is Soniox `stt-rt-v5`; LLM is explicitly selected with `OPENROUTER_MODEL` through OpenRouter; Maya model/voice/language are configured independently.
- Boundaries: Pin: Pipecat 1.8.1 plus Maya community package commit `2c3b569`. The package accepts 19 Calyx voices, not the 31 in current HTTP docs. Inspect exported `pipecat_maya.MODELS`; newer names such as Diya fail locally. Do not bypass validation or silently substitute voices. There is no claim that Pipecat upstream maintains this package.
- Cleanup: Disconnect in the browser, then Ctrl+C the server. It binds only to loopback in the documented command and has a five-minute per-bot ceiling. Do not expose the development runner publicly or leave billable sessions running.

Keep the explicit one-second pause policy unless asked to tune it, and retest full utterances, short pauses and interruption after changes. Keep the runner local and follow the production checklist before deploying an application.

Read [validation](../../docs/validation.md) before promising this is verified. Use keyless tests from the repository root first; request names/locations of missing credentials, never their values in chat. No automatic paid calls, microphone activation, provider substitution, package-cache edits, publication or deployment. Preserve existing outputs. Record versions, commands, failures and unverified device/listening steps.
