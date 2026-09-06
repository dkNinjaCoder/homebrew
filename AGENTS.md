# AGENTS.md — Developer & AI Instructions

This document provides essential context and instructions for AI coding assistants working in this repository. Read this before making changes to avoid unnecessary searches or invalid commands.

---

## ⚠️ Critical Rule: No Node / NPM Commands

- **DO NOT run `npm` commands under any circumstances** (e.g., `npm install`, `npm test`, `npm run build`, `npm ci`).
- **DO NOT run `node` scripts or attempt to install Node dependencies.**
- Node packages (`5etools-utils`, etc.) are not locally installed and must not be installed in this environment. CI handles validation remotely on push.
- If you need to validate JSON syntax or file contents, use standard Python (`python3 -c "import json; json.load(open('creature/dkNinja; PoTA campaign.json'))"`).

---

## Repository Context & Architecture

This repository is a **5etools-compatible homebrew repository** adhering to the [TheGiddyLimit/homebrew](https://github.com/TheGiddyLimit/homebrew) structure.

- **Author**: `dkNinja`
- **Primary Data File**: [`creature/dkNinja; PoTA campaign.json`](file:///home/manan/Programs/homebrew/creature/dkNinja;%20PoTA%20campaign.json)
- **Unified Source Identifier**:
  - `source`: `"PoTACampaign"`
  - `abbreviation`: `"PoTA"`
  - `full`: `"PoTA campaign"`
  - **All creatures and legendary groups in this file MUST use `"source": "PoTACampaign"`**. Do not use ad-hoc source names like `dkNinja`, `CustomCampaign`, or per-monster source strings.

---

## File Formatting & Styling Standards

- **Indentation**: **Tabs (`\t`)**, not spaces (`indent_style = tab` in `.editorconfig`).
- **Line Endings**: **LF (`\n`)**.
- **Encoding**: UTF-8.
- **Alphabetical Ordering**: Creatures in `"monster"` and entries in `"legendaryGroup"` should be kept in alphabetical order by `name`.
- **5etools Tagging**: Always format mechanics with standard 5etools tags:
  - Spells: `{@spell counterspell}`, `{@spell fireball}`
  - DCs & Dice: `{@dc 21}`, `{@dice 1d10}`, `{@damage 4d10}`
  - Conditions: `{@condition paralyzed}`, `{@condition frightened}`
  - Skills: `{@skill Arcana}`, `{@skill Perception}`
  - Attacks & Hits: `{@atk ms}`, `{@hit 13}`, `{@h}`, `{@recharge 5}`

---

## 5etools Data Schemas

### 1. Root Object in `creature/dkNinja; PoTA campaign.json`
```json
{
	"_meta": {
		"sources": [ ... ],
		"edition": "classic",
		"dateAdded": 1725609600,
		"dateLastModified": <unix_epoch_seconds>
	},
	"monster": [ ... ],
	"legendaryGroup": [ ... ]
}
```

### 2. Linking Creatures to Legendary Groups
A monster references its legendary group inside the monster object:
```json
"legendaryGroup": {
	"name": "Renwick the Ascendant",
	"source": "PoTACampaign"
}
```

### 3. Legendary Group Schema
In 5etools, `legendaryGroup` definitions do **NOT** accept a top-level `"entries"` array (`additionalProperties: false`). Instead, lair actions and regional effects must be placed in their dedicated arrays:
```json
{
	"name": "Renwick the Ascendant",
	"source": "PoTACampaign",
	"page": 1,
	"lairActions": [
		"Optional descriptive text about the lair sanctum...",
		"On initiative count 20 (losing initiative ties), <Name> takes a lair action...",
		{
			"type": "list",
			"items": [
				"Lair action 1...",
				"Lair action 2..."
			]
		}
	],
	"regionalEffects": [
		"The region containing <Name>'s lair is warped...",
		{
			"type": "list",
			"items": [
				"Regional effect 1...",
				"Regional effect 2..."
			]
		},
		"If <Name> is destroyed, the regional effects fade over the course of {@dice 1d10} days."
	]
}
```

---

## Automated Maintenance Script: `scripts/clean_and_sync.py`

A dedicated Python script is provided at [`scripts/clean_and_sync.py`](file:///home/manan/Programs/homebrew/scripts/clean_and_sync.py) to automatically perform all routine cleanups, schema validations, and file synchronizations.

### What the Script Handles Automatically:
1. **Source Unification**: Sets `"source": "PoTACampaign"` on all creatures and legendary groups.
2. **Mechanics & Tag Normalization**:
   - Replaces untagged DCs (e.g., `DC 21`, `DC21`) with `{@dc 21}`.
   - Replaces untagged hit bonuses (e.g., `(+12 to hit)`) with `({@hit 12} to hit)`.
   - Normalizes recharge syntax in action/trait names (e.g., `(Recharge 5–6)` -> `{@recharge 5}`).
   - Fixes common spell typos (e.g., `forbadance` -> `forbiddance`).
3. **Legendary Group Handling**:
   - Automatically extracts any `lairActions` or `regionalEffects` accidentally placed directly on a monster object into the root `legendaryGroup` array.
   - Cleans up dangling `legendaryGroup` references on monsters that don't have matching definitions.
4. **Alphabetical Sorting**: Sorts both `"monster"` and `"legendaryGroup"` arrays alphabetically by `name`.
5. **Timestamp Synchronization**: Updates `_meta.dateLastModified` and `_generated/index-timestamps.json` with the current Unix timestamp whenever data changes.
6. **Documentation Synchronization**: Re-generates and updates the creature list in [`README.md`](file:///home/manan/Programs/homebrew/README.md) under `## Contents`.

### How to Run:
```bash
# Clean, fix, and sync existing data in-place:
python3 scripts/clean_and_sync.py

# Or add/update creature(s) directly from a JSON file, string, or stdin:
python3 scripts/clean_and_sync.py --add creature.json

# Dry-run validation (exits 0 if clean, 1 if fixes are needed):
python3 scripts/clean_and_sync.py --check
```

### Adding New Fixes to the Script:
When you discover a new typo pattern, schema issue, or tag normalization rule, **add it to [`scripts/clean_and_sync.py`](file:///home/manan/Programs/homebrew/scripts/clean_and_sync.py)**:
- **Spell Typos**: Add entries to `SPELL_TYPOS = { "typo": "correct" }`.
- **Text Regexes**: Add tuples to `TEXT_REPLACEMENTS = [ (compiled_regex, replacement), ... ]`.
- **Name Regexes**: Add tuples to `NAME_REPLACEMENTS = [ (compiled_regex, replacement), ... ]`.
- **Structural / Schema Fixes**: Add a new `fix_*` function and call it inside `run_pipeline()`.

---

## Standard Checklist When Adding / Updating Creatures

Whenever modifying or adding a creature:
1. **Add/Edit Creature**:
   - Either paste/edit the creature in [`creature/dkNinja; PoTA campaign.json`](file:///home/manan/Programs/homebrew/creature/dkNinja;%20PoTA%20campaign.json), OR run:
     ```bash
     python3 scripts/clean_and_sync.py --add path/to/creature.json
     ```
2. **Run the Cleaner & Synchronizer**:
   - Run:
     ```bash
     python3 scripts/clean_and_sync.py
     ```
   - This automatically fixes tags, normalizes sources, sorts entries alphabetically, syncs timestamps across files, and updates [`README.md`](file:///home/manan/Programs/homebrew/README.md).
3. **Verify Everything is Clean**:
   - Run:
     ```bash
     python3 scripts/clean_and_sync.py --check
     ```

