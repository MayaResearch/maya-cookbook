# Agent guidance for documentation

Read ../AGENTS.md first. Every guide links to runnable code and verification. Use sources.json and api-reference/catalog.json as dated evidence, not a forever-current contract.

Keep command examples aligned with their executable files. Never add unsupported voice, latency, regional, quality or upstream-release claims. Preserve disagreements between the public API reference and the maintained integrations in api-reference/README.md. A model's claimed language support is not an evaluation result.

After edits run `python3 scripts/check_repo.py` from the repository root plus the relevant tests. Follow maintenance.md before updating pins or source hashes. A passing link check does not validate an API payload or audio.
