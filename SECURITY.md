# Security

Do not put API keys, customer audio or private model files in issues, pull requests, recordings or agent prompts. The examples contain blank credential placeholders only.

For a suspected vulnerability, contact [charan@mayaresearch.ai](mailto:charan@mayaresearch.ai) privately using the support contact published in Maya's API reference. Start with a minimal description; do not send live secrets or customer data. This candidate does not claim an established response-time SLA or enabled GitHub private-reporting portal.

If a credential is exposed, revoke/rotate it at its provider and verify the old credential no longer works. Deleting it from the latest commit is not sufficient. Do not reuse exposed historical keys from messages or logs.

Browser examples are local development only. Never expose their billable endpoints without authentication, cost limits and a security review. See the [production checklist](docs/production-checklist.md).
