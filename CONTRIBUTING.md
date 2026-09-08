# Contributing

Read [AGENTS.md](AGENTS.md). Keep each recipe small and runnable from the documented setup. Use the maintained integration packages; do not vendor private inference code.

For a change, explain the user-visible outcome, pin dependencies, update the scoped README and agent prompt, add positive and failure tests, and run the keyless suite. Include a redacted validation record and cite the current primary API source. Do not declare every voice/language tested from one successful sample.

Never run live paid checks using credentials from a pull request. Maintainers may separately run a bounded synthetic suite on reviewed code. Preserve existing files and distinguish old evidence from new runs.

Before publication, maintainers must review license, sources, owners and security intake. No contributor should push, deploy or publish on another person's behalf without authorization.
