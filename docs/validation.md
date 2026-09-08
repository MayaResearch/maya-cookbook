# Validation status

Maya Research Cookbook public beta, refreshed on 9 September 2026 for the independent LiveKit contribution below. The current tested model is `Maya Calyx`. Every example and blank configuration template selects it explicitly and defaults to `Aarav`; the current catalog offers 24 selected speakers. The recipes were built and exercised with synthetic speech. Results apply to these versions, not automatically to future models. This is not a production certification or an upstream integration release.

## Results

| Layer | Current result | What it does not prove |
| --- | --- | --- |
| Clean release-only installation | 20 checks passed from a fresh extraction, with separate environments and no provider keys | Every operating system or runtime version |
| Linux GitHub CI | Keyless suite and all five separate recipe install/import jobs passed in [the first main-branch run](https://github.com/MayaResearch/maya-cookbook/actions/runs/34258959362) | Paid provider calls or physical microphone/speaker behavior |
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

Tests ran on macOS, Apple Silicon, Python 3.12.14. Core integrations are pinned to LiveKit 1.8.0 and Pipecat 1.8.1, with the Maya plugin Git revisions in [sources.json](sources.json). Linux CI is provided, including separate recipe install/import jobs; its result must be checked separately on GitHub. The source refresh found that Maya's guide now presents Calyx/Aarav, removes the other model and speed documentation, and links to merged Pipecat docs PR 1257. The diff was reviewed before updating the source checksum. The executable cookbook already selected Calyx/Aarav explicitly and omitted speed; its HTTP and v2 protocol behavior did not change.

### Independent LiveKit contribution, 9 September 2026

The cookbook now pins Maya plugin commit `a2333554`, including fixes from review of new [LiveKit PR 7175](https://github.com/livekit/agents/pull/7175). This is a self-contained implementation on `maya-research-tts`, built directly from upstream main `e9a3422f`, with no older Maya PR commits in its branch history. Removing another pending contribution does not remove this cookbook's pinned source. Maya Research remains the provider name; Calyx is the currently documented model, not the permanent integration name.

- 121 hermetic Maya plugin tests passed on each of Python 3.10.21, 3.12.14 and 3.13.15. The Python 3.12 combined plugin, audio-emitter and connection-pool run passed 147 tests. Focused strict typing passed on all three versions; repository lint and formatting passed. The tests use an in-memory WebSocket and run in the upstream unit category without keys or network.
- Initial contribution `b37bbeac` passed LiveKit's [upstream Linux unit job](https://github.com/livekit/agents/actions/runs/34264250168/job/102189523716), 2,713 tests with 5 skipped. Current revision checks are shown on the PR. The contributor agreement is now signed; maintainer review and merge remain pending.
- Eight real Maya checks passed again after the review fixes: one-shot and streamed Hindi, Telugu and English, completed-turn connection reuse, active-turn cancellation, and a new turn after cancellation. Seven completed valid non-silent WAVs are kept privately. One additional real two-sentence turn survived a 2.201-second client-input pause with a 1-second response timeout, continued in the same context, and produced 183,840 PCM bytes. That targeted pause check uses an explicit BasicSentenceTokenizer; the eight-check suite uses the default tokenizer.
- The revised Maya plugin passed a fresh synthetic full-agent turn using this cookbook's locked LiveKit 1.8.0/provider environment: Soniox, OpenRouter and Maya produced 184,320 PCM bytes at the recorded sink, with a final transcription and no agent errors. No installed dependency files were patched.
- Protocol tests cover wrong audio formats, split PCM samples and short tails, malformed audio, missing endings, late-context messages, cancellation, concurrent turn isolation, model/voice changes during an active turn, and preventing replay after partial audio. A slow first text input is not treated as a server failure. Current LiveKit requires a new stream for each segment; text pushed after flush is not a second segment.
- Review regressions additionally cover shutdown overlapping a connection acquisition, direct/factory/prewarm cancellation, pauses between sentences, timeout re-arm after new text or a closer, endless unanswered input, blocked text writes and rejection of plaintext URLs. The protocol has no per-sentence completion acknowledgement; once audio has progressed with input still open, the plugin cannot distinguish provider idle from LLM idle. Applications must bound the overall turn and close abandoned input.
- A fresh source-only cookbook extraction passed all 20 install/check steps with the new immutable plugin pin: every recipe installed separately, 183 Python tests and 33 TypeScript tests passed, both agent modules imported, and documentation/credential checks passed. Only the LiveKit plugin pin changed in its lockfile; framework and other provider dependencies stayed fixed. The selected-speaker recordings and Pipecat source were not changed or regenerated in this follow-up.

These checks do not certify physical microphone/speaker behavior, LiveKit room transport, human listening quality, or an upstream package release. Maintainer review and merge are separate from local tests.

The follow-up review also identified that an explicit language could not be cleared. The pinned fix accepts `update_options(language=None)` while omitted arguments preserve existing settings. Tests cover an uninterrupted active turn, invalid-update atomicity and connection reuse. A real Hindi turn produced 130,560 PCM bytes, then clearing the language produced a mixed Hindi/English turn with 192,000 PCM bytes; its new startup request omitted the language field.

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

Install each selected example separately using its README. LiveKit deliberately uses `--no-sources` to avoid the source fork's development workspace dependency overrides. Do not combine environments or change installed package files to get tests passing.

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
- [x] Linux GitHub CI has executed successfully, including all five recipe installation/import jobs.
- [x] Maya Research authorized publishing this scoped cookbook as a public beta.
- [ ] A production maintainer roster, code ownership and security-response process are established.

Public beta is permission to share the documented examples, not a claim that the open human/device and production-security checks passed. Keep these limitations visible and do not mark an unchecked item complete without evidence.
