# Troubleshooting

Read [agent guidance](../AGENTS.md). Use synthetic text when reproducing a failure.

| What happened? | What to check first |
| --- | --- |
| 401 / startup refused | Is the right `MAYA_API_KEY` loaded in this process? Check names/presence, never print its value. Fix or rotate the key; don't loop retries. |
| 400 / invalid voice | Case-sensitive model/voice pairing. Pipecat's pinned catalog is narrower than current HTTP docs. |
| Noise / chipmunk / slow voice | Raw PCM is not WAV. Check actual rate, mono, 16-bit little-endian. Do not feed mu-law to a PCM sink. |
| Empty output / no speech | Status first, content type second, nonempty aligned bytes third. JSON is not audio even if saved with a .wav extension. |
| Wrong language pronunciation | Use the matching script/language. Omit language for mixed text. Do not normalize numbers a second time. |
| Missing ending | Wait for normal completion, preserve final PCM bytes and drain normal playback. Don't close on the first packet. |
| Speech continues after interruption | Stop local playback and empty its queue immediately. Cancel synthesis by context ID and ignore late old-context packets. |
| Long pause | Separate TLS/startup, STT finalization, LLM response, first PCM receipt and actual playback. A downloaded WAV is not a streaming latency benchmark. |
| Bot answers before the sentence finishes | Check turn-end policy separately from TTS chunks. The Pipecat recipe waits one second after VAD silence; longer pauses can still end a turn. Retest pauses and delayed final transcripts before shortening it. |
| Hindi/Telugu speech transcribed in another script | For a known single language, set the matching hint (`hi` or `te`). For multilingual calls leave the strict hint unset and evaluate language detection separately. |
| Pipecat newer voice rejected | Do not patch its installed package or fall back to a different voice. Choose a supported voice explicitly, or test a maintained package update. |
| No microphone device | Grant local microphone permission and select the device. A headless CI runner cannot test your speakers. Use a synthetic input WAV for API-path checks. |
| Import / install fails | Use the folder's pinned lockfile, Python 3.12 and the documented setup command. Don't install all examples into one shared environment. |
| Output exists | Choose another filename; examples preserve existing files. |
| 429 / 5xx | Back off within your own budget, and only retry safely before any audio delivery. Do not replay partially heard speech. |

The from-scratch example records one bounded utterance and then replies. It is intentionally half-duplex; talking over it does not perform automatic barge-in. Use Ctrl+C to stop or choose a framework example for conversational interruption.

For support, include the example, OS/runtime, dependency versions, exact redacted command, timestamp, HTTP request ID or WebSocket session/context ID. Include synthetic expected text and format metadata. Never include credentials, customer calls or unrelated logs.
