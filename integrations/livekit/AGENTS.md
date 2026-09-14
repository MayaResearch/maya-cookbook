# Coding-agent instructions: LiveKit voice agent with Maya

Read [root AGENTS.md](../../AGENTS.md) first. The [README](README.md) has the integration prompt and optional demo commands.

## Default: integrate into an existing app

- Inspect the user's project and installed LiveKit version before changing it.
- Change only TTS to Maya. Preserve existing STT, LLM, transport, prompts, credentials, turn detection and interruption behavior.
- Read this folder's pyproject.toml and lockfile for the exact tested Maya dependency; inspect the demo's TTS construction as a reference, not as an app replacement.
- Do not copy the cookbook lockfile over the customer's lockfile or silently upgrade/downgrade their framework. If compatibility is outside the tested setup, explain the mismatch and ask before a migration.
- Do not require Soniox or OpenRouter for an existing app. Request only missing configuration names/locations; never key values in chat.
- Run the customer's relevant tests and the applicable keyless integration checks. Paid audio, microphone use and deployment require approval. Report compatibility and untested runtime behavior honestly.

## Optional: run the complete cookbook demo

Only use this path when the user wants a new demo. Execute the README commands from this folder; retain the full checkout for shared references/helpers. The provider choices and behavior below apply to this demo, not to the customer's existing app.

- Outcome: A local microphone conversation: speak, wait for one short reply and interrupt it. Check that playback stops and the next turn does not contain old audio. `download-files` retrieves the VAD asset; it is a setup network download, not a speech API request.
- Configuration: Populate this folder's ignored `.env` from the blank `.env.example` or use a secret manager. Existing process environment wins. The STT model is Soniox `stt-rt-v5`; the LLM defaults explicitly to `openai/gpt-4o-mini` through OpenRouter and can be selected with `OPENROUTER_MODEL`. A Maya key alone is not the full agent stack.
- Boundaries: Maya-maintained plugin at public commit `a2333554`, submitted as independent LiveKit PR 7175 from `maya-research-tts`, not an upstream release. Do not substitute another pending Maya PR or branch. Released LiveKit is pinned to 1.8.0. `--no-sources` is important: the Maya fork's uv workspace redirects dependencies to its development workspace packages. The direct Git dependency still installs with this option. The plugin supports Maya Research voice models; this cookbook release currently tests Calyx with Aarav. Human microphone/browser quality checks are separate from imports and provider tests; changing settings is not evidence of support in every path. For custom incremental TTS, use one stream per segment; do not push text after flush. Keep custom Maya endpoints HTTPS/WSS and bound LLM/overall-turn execution separately; always end or cancel abandoned streams.
- Cleanup: Ctrl+C stops the worker and local microphone session. Console mode does not deploy or provision anything. For rooms only, set `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET` and run `uv run --locked --no-sources agent.py dev`; review costs and transport setup first.

Read [validation](../../docs/validation.md) before promising this is verified. Use keyless tests from the repository root first; request names/locations of missing credentials, never their values in chat. No automatic paid calls, microphone activation, provider substitution, package-cache edits, publication or deployment. Preserve existing outputs. Record versions, commands, failures and unverified device/listening steps.
