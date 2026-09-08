# Available speakers

Checked against [Maya's API reference](https://www.mayaresearch.ai/llm.txt) on 8 September 2026. This cookbook offers **24 selected Maya Calyx speakers**, intentionally fewer than the 31 in that reference. Names and model names are case-sensitive. The [machine-readable catalog](api-reference/catalog.json) contains the exact selected values. Starter examples use `Aarav`.

| Model | Speaker names |
| --- | --- |
| `Maya Calyx` | Aarav, Kabir, Rohan, Amit, Kavita, Sagar, Arushi, Neeraj, SagarM, Diya, Neha, Samar, Nila, Sana, Rahul, Rehan, Seema, Riya, Shreeraj, Tarini, Tripti, Vikas, Vikram, Zara |

Maya Calyx documents these eleven language codes: Hindi (`hi`), Telugu (`te`), Indian English (`en`), Tamil (`ta`), Bengali (`bn`), Gujarati (`gu`), Kannada (`kn`), Malayalam (`ml`), Marathi (`mr`), Odia (`or`), Punjabi (`pa`). Documented support is not a guarantee of equal accent or pronunciation quality across all voices.

- `Sagar` and `SagarM` are different speakers. `Neha P` is retired; use the current `Neha` only when that is the speaker you intend.
- The source calls `Nila` a Tamil speaker and `Vikram` a Telugu speaker. This does not certify regional accent quality.
- Riley, Christine, Jackson, Christopher, Vance, Shailika and Gargi are intentionally excluded from this cookbook and its listening selection. This is a publisher choice, not a claim that the provider retired those voices. Indian English remains available on the selected speakers.
- The pinned Pipecat community package validates a narrower catalog: 19 Calyx voices. A voice working through direct HTTP does not mean that the older package accepts its name. Do not bypass validation or silently select another voice.

## Sample coverage

A follow-up matrix generated one short reference sentence for each speaker-language pair. The current selection contains **264 valid, non-silent WAV files: 24 speakers by 11 languages**, with no duplicate file hashes or signal-threshold warnings. These are unchanged recordings filtered from the original test run, not regenerated or improved audio. Complete recordings, exact requests and hashes are kept in the separate local sample pack, not this source repository. Original excluded recordings and findings remain preserved outside the cookbook.

Automatic Soniox transcription covered all **72 selected Hindi, Telugu and English clips**. This measures transcript coverage, not a pronunciation or naturalness score. The other eight languages have file and signal checks. Audition the voices using your own application's text before choosing one.

See [validation](validation.md) for the distinction between generated audio, measured checks and remaining human/device review.
