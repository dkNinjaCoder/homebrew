# CLAUDE.md

> **IMPORTANT**: Before performing any tasks or making any changes in this repository, **read [`AGENTS.md`](AGENTS.md) thoroughly**.

All rules, architecture details, schemas, and standards for this repository are defined in [`AGENTS.md`](AGENTS.md).

## Critical Highlights

- **NO NPM / NODE COMMANDS**: Never run `npm install`, `npm test`, `npm run ...`, or `node ...`. Node dependencies are not installed locally and must not be installed in this environment. Validation is handled by remote CI.
- **Maintenance Script**: Run `python3 scripts/clean_and_sync.py` to automatically normalize sources, fix mechanics tags/spelling, sort creatures, sync timestamps, and update `README.md`.
- **Validation**: Run `python3 scripts/clean_and_sync.py --check` or standard Python JSON loading.
- **Workflow**: See [`AGENTS.md`](AGENTS.md) for full instructions and checklist.
