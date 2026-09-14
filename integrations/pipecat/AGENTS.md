# Coding-agent instructions: Pipecat voice agent with Maya

Read [root AGENTS.md](../../AGENTS.md) first. The [README](README.md) has the integration prompt and optional demo commands.

## Default: integrate into an existing app

- Inspect the user's project and installed Pipecat version before changing it.
- Change only TTS to Maya. Preserve existing STT, LLM, transport, prompts, credentials, turn detection and interruption behavior.
- Read this folder's pyproject.toml and lockfile for the exact tested Maya dependency; inspect the demo's TTS construction as a reference, not as an app replacement.
- Do not copy the cookbook lockfile over the customer's lockfile or silently upgrade/downgrade their framework. If compatibility is outside the tested setup, explain the mismatch and ask before a migration.
- Do not require Soniox or OpenRouter for an existing app. Request only missing configuration names/locations; never key values in chat.
- Run the customer's relevant tests and the applicable keyless integration checks. Paid audio, microphone use and deployment require approval. Report compatibility and untested runtime behavior honestly.

## Optional: run the complete cookbook demo

Only use this path when the user wants a new demo. Execute the README commands from this folder; retain the full checkout for shared references/helpers. The provider choices and behavior below apply to this demo, not to the customer's existing app.

- Outcome: Open http://127.0.0.1:7860 in your chosen browser, connect, and say one short sentence. You should hear a Maya reply. Interrupt and start another turn, then disconnect. The packaged Pipecat development UI is an external pinned dependency.
- Configuration: Use this folder's ignored `.env` or your process environment. See blank `.env.example`. Process values win. STT is Soniox `stt-rt-v5`; LLM is explicitly selected with `OPENROUTER_MODEL` through OpenRouter; Maya model/voice/language are configured independently.
- Boundaries: Pin: Pipecat 1.8.1 plus Maya community package commit `2c3b569`. The package accepts 19 Calyx voices, not the 31 in current HTTP docs. Inspect exported `pipecat_maya.MODELS`; newer names such as Diya fail locally. Do not bypass validation or silently substitute voices. There is no claim that Pipecat upstream maintains this package.
- Cleanup: Disconnect in the browser, then Ctrl+C the server. It binds only to loopback in the documented command and has a five-minute per-bot ceiling. Do not expose the development runner publicly or leave billable sessions running.

Keep the explicit one-second pause policy unless asked to tune it, and retest full utterances, short pauses and interruption after changes. Keep the runner local and follow the production checklist before deploying an application.

Read [validation](../../docs/validation.md) before promising this is verified. Use keyless tests from the repository root first; request names/locations of missing credentials, never their values in chat. No automatic paid calls, microphone activation, provider substitution, package-cache edits, publication or deployment. Preserve existing outputs. Record versions, commands, failures and unverified device/listening steps.
