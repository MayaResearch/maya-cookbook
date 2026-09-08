# Keep the cookbook current

Read [AGENTS.md](../AGENTS.md). Reproducible and latest are different: lockfiles record what passed; drift checks tell maintainers what changed.

1. Run `python3 scripts/check_sources.py` from the root. It checks the canonical Maya text hash, integration branch heads, and public source reachability. It is read-only and needs no provider keys.
2. If the contract changed, inspect the actual diff. Reconcile HTTP/WebSocket behavior, catalog.json, guides and tests together. Never merely change the expected hash to turn a failing check green.
3. Inspect maintained integration releases/commits. Pin immutable Git SHAs, not `main`. Preserve upstream authorship and licensing. Do not import internal inference/training files.
4. Update one example's dependencies, regenerate its lockfile, reinstall cleanly, and run unit, contract and live checks relevant to that change.
5. Update docs/validation.md with exact version/date/command and separate failed, skipped and passed checks. Human listening and device tests remain separately tracked.
6. Review code and secret-scan the complete candidate before publication. No generated recordings or private environments are release files.

The CI workflow runs keyless checks on changes and a scheduled read-only source-drift check after publication. Paid checks remain manually authorized and local. Nothing here provisions a GPU or deploys an app.

Before publishing, assign real maintainers and review rules. This candidate deliberately does not invent GitHub team ownership or a security email alias. Use the currently documented Maya contacts until a dedicated intake is established.
