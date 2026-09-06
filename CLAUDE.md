# CLAUDE.md

> **IMPORTANT**: Before performing any tasks or making any changes in this repository, **read [`AGENTS.md`](AGENTS.md) thoroughly**.

All rules, architecture details, schemas, and standards for this repository are defined in [`AGENTS.md`](AGENTS.md).

## Critical Highlights

- **NO NPM / NODE COMMANDS**: Never run `npm install`, `npm test`, `npm run ...`, or `node ...`. Node dependencies are not installed locally and must not be installed in this environment. Validation is handled by remote CI.
- **Python for Validation**: If validating JSON files, use standard Python (`python3 -c "import json; ..."`).
- **Single Source Identifier**: All homebrew content in [`creature/dkNinja; PoTA campaign.json`](creature/dkNinja;%20PoTA%20campaign.json) must use `"source": "PoTACampaign"`.
- **Indentation & Formatting**: Tabs (`\t`), LF (`\n`), UTF-8 encoding.
- **Full Checklist**: See [`AGENTS.md`](AGENTS.md) for the 4-step checklist when adding or updating creatures.
