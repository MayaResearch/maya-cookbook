# Instructions for repository checks

Read ../AGENTS.md and ../docs/validation.md. `check_repo.py` is keyless/local. `check_sources.py` makes read-only public requests. `live_smoke.py` makes 8 billable synthesis turns and requires explicit authorization plus an environment key. It never auto-loads a private file or runs in PR CI.

Do not bypass a failure or update an expected hash without comparing sources. Keep failures, skipped checks, sample provenance and human-listening limitations visible. All runtime outputs belong under ignored artifacts, never release files. Do not include credentials in reports.
