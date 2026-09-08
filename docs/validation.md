# Validation status

Maya Calyx-only public beta, checked on 8 September 2026. Every example and blank configuration template selects `Maya Calyx` and defaults to `Aarav`; the current catalog offers 24 selected speakers. The recipes were built and exercised with synthetic speech. This is not a production certification or an upstream integration release.

## Results

| Layer | Current result | What it does not prove |
| --- | --- | --- |
| Clean release-only installation | 20 checks passed from a fresh extraction, with separate environments and no provider keys | Other operating systems or a GitHub-hosted CI run |
| Python keyless tests | 183 passed after the 24-speaker selection, including rejection of excluded speakers; pytest 9.1.1 | Provider, browser or microphone behavior |
| TypeScript tests | 33 passed after the selection change; strict type check passed. Earlier core checks also ran on Node 22.18.0 and 24.19.0 | Browser integration, perceptual quality |
| Maya HTTP live checks | Every selected speaker has successful recorded synthesis; the Calyx-only recipe also passed fresh hi/te/en calls with Aarav before this selection-only change | Every pronunciation, naturalness or accent |
| Selected speaker matrix | 264 unchanged valid non-silent WAVs, 24 speakers in 11 languages, one short shared sentence per language. No identical file hashes or signal-threshold warnings | Comprehensive pronunciation, accent, speaker identity or streaming chunk verification |
| Selected automatic transcription | All 72 selected hi/te/en clips transcribed | Transcript coverage is not a pronunciation score. The other eight languages were not transcribed |
| Maya WebSocket live checks | Calyx hi/te/en, cancellation and a new turn after cancellation passed; rerun after the Calyx-only changes | Physical playback or full-duplex microphone behavior |
| TypeScript/curl live CLI | Both generated fresh valid Calyx Aarav WAV files | All device/platform combinations |
| LiveKit TTS plugin | Fresh Calyx Aarav synthesis through the pinned plugin produced a valid WAV | Full microphone conversation or upstream release status |
| Pipecat TTS worker | Fresh Calyx Aarav synthesis through the pinned worker produced a valid WAV | Browser conversation, automatic barge-in or telephony |
| LiveKit complete agent | Fresh synthetic English audio went through the actual AgentSession, Soniox, GPT-4o-mini through OpenRouter and Calyx Aarav to a recorded sink | Physical console microphone, room transport or speaker playback |
| Pipecat complete agent | Fresh synthetic English audio went through the actual runner and a WebRTC peer, Soniox, GPT-4o-mini through OpenRouter and Calyx Aarav; final PCM reached the peer. The pause-policy test produced one LLM request for the full utterance | Physical microphone, arbitrary pauses, noisy input or universal interruption quality |
| From-scratch full provider chain | Fresh Hindi, Telugu and English turns passed with the documented GPT-4o-mini default and Calyx Aarav | Every language/voice combination or live microphone behavior |
| Public opt-in live smoke command | Rerun with Calyx Aarav: 8 of 8 checks passed and 7 completed synthetic WAV files were saved | A load test or a latency SLA |
| Pipecat development UI | Loaded visibly in a local browser with the WebRTC connection controls | The microphone was not activated and no browser call was made |
| Human listening / physical device testing | Not completed for this build | No claim of universal pronunciation or production readiness |

The Calyx-only retest passed all 10 workflow checks, covering 17 bounded synthesis turns and producing 16 valid non-silent WAV files (the cancelled turn is not saved as completed speech). The live tests used synthetic prompts. Their recordings and raw run evidence are kept outside the release candidate. No credentials or customer recordings are included here. First PCM receipt is not the listener's time to first sound.

The speaker catalog is a selected Calyx-only subset. Selection checks were rerun without paid generation; the sample recordings are unchanged.

Tests ran on macOS, Apple Silicon, Python 3.12.14. Core integrations are pinned to LiveKit 1.8.0 and Pipecat 1.8.1, with the Maya plugin Git revisions in [sources.json](sources.json). Linux CI is provided, including separate recipe install/import jobs; its result must be checked separately on GitHub. The latest source refresh found that Maya's guide now presents Calyx/Aarav, removes the other model and speed documentation, and links to merged Pipecat docs PR 1257. The diff was reviewed before updating the source checksum. The executable cookbook already selected Calyx/Aarav explicitly and omitted speed; its HTTP and v2 protocol behavior did not change. Both maintained integration branch heads are unchanged. Local links, formatting, types and release-file checks passed.

The release-file scan checked credential patterns, blank credential templates and exact matches for the three credentials used in testing. It excludes real environment files, local environments, generated audio and private evidence. A scan is not a promise that every possible secret detector or dependency review has been completed.

## Reproduce keyless tests

From the repository root:

```sh
uv sync --locked
uv run --locked pytest -q
uv run --locked ruff check .
uv run --locked ruff format --check .
python3 scripts/check_repo.py
cd quickstarts/typescript
pnpm install --frozen-lockfile
pnpm test
pnpm check
```

Install each selected example separately using its README. LiveKit deliberately uses `--no-sources` to avoid the source fork's older workspace dependency overrides. Do not combine environments or change installed package files to get tests passing.

## Reproduce bounded live speech checks

After reviewing the script and authorizing 8 billable Maya synthesis turns, set `MAYA_API_KEY` in the process environment. From the root:

```sh
uv run --locked python scripts/live_smoke.py --allow-paid --output artifacts/live-smoke
```

This writes seven completed synthetic WAVs and a sanitized report. The cancelled turn is not saved as completed speech. It stops on a failing request, never switches provider, and refuses to overwrite the output directory. It does not run automatically in CI.

For a single integration-specific synthesis, after its locked install:

```sh
# In integrations/livekit, Maya key only:
uv run --locked --no-sources verify_tts.py --output livekit.wav
# In integrations/pipecat, Maya key only:
uv run --locked verify_tts.py --output pipecat.wav
```

## Beta evidence and production follow-up

- [x] All keyless README install/check commands pass from a fresh release-only checkout on the tested macOS runtime.
- [x] Full voice-agent provider paths pass with synthetic input and received audio within the scope above.
- [ ] Microphone/browser/interrupt tests and human listening for promised languages are recorded separately.
- [ ] Independent agent handoff: an agent receives only the repo and the provided prompt, then its actual output is checked. This has not been performed by an independent agent in this build.
- [x] Current source drift, local link checks and release-file scans pass.
- [ ] Linux GitHub CI has actually executed successfully.
- [x] Maya Research authorized publishing this scoped cookbook as a public beta.
- [ ] A production maintainer roster, code ownership and security-response process are established.

Public beta is permission to share the documented examples, not a claim that the open human/device and production-security checks passed. Keep these limitations visible and do not mark an unchecked item complete without evidence.
