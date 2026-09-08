# TypeScript: server-side text to speech

## Before you start

Node 22.18+ and pnpm; Maya API key. This is not browser code.

Read [current validation](../../docs/validation.md) and the [API reference](../../docs/api-reference/README.md). Use synthetic text first. Running speech/agent commands makes billable provider calls.

## Configure

Set `MAYA_API_KEY` in the process environment. Optional `MAYA_MODEL`, `MAYA_VOICE` and `MAYA_LANGUAGE`. `.env.example` is a template, not automatically loaded. No key belongs in `VITE_*`, `NEXT_PUBLIC_*` or browser JavaScript.

## Run

From `quickstarts/typescript/` in the complete cookbook checkout:

```sh
pnpm install --frozen-lockfile
pnpm test
pnpm check
pnpm start --check
pnpm start --text 'Hello! Your order will arrive tomorrow.' --language en --output english.wav
```

## Expected result and verification

A playable `english.wav`. The output reports sample rate and PCM byte count. Test files exercise status failures, redirects, timeouts, format validation and exact WAV bytes.

Run the repository keyless suite from the root as described in [AGENTS.md](../../AGENTS.md). An install or an HTTP 200 alone is not a passed audio check. Verify the saved file, the audible final word and any interruption behavior independently.

## Stop and clean up

The process exits after one request. Ctrl+C stops it. Existing output files are never overwritten.

## Limits and troubleshooting

The quickstart buffers a complete bounded clip, not real-time playback. No automatic retry or fallback. The catalog comes from the shared dated JSON, not a second handwritten voice list.

See [troubleshooting](../../docs/troubleshooting.md) and [production requirements](../../docs/production-checklist.md). Tested version/date and any unverified steps are in the validation report; don't infer a universal quality or latency guarantee.

## Ask your coding agent

> Read the root AGENTS.md and quickstarts/typescript/AGENTS.md. Run this example using this README's pinned setup. Report missing credential names without printing secrets. Run the relevant keyless checks first. Ask before billable calls or using my microphone. Preserve existing files and the selected providers/model/voice. Verify the documented output and report passed, failed and unverified checks separately. Do not publish, deploy or provision resources.
