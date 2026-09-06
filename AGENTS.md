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

## Standard Checklist When Adding / Updating Creatures

Whenever modifying or adding a creature:
1. **Edit [`creature/dkNinja; PoTA campaign.json`](file:///home/manan/Programs/homebrew/creature/dkNinja;%20PoTA%20campaign.json)**:
   - Insert/update the creature object in the `"monster"` array (maintain alphabetical order).
   - If the creature has lair actions / regional effects, add the entry in the `"legendaryGroup"` array (maintain alphabetical order) and reference it via `"legendaryGroup"` in the monster block.
   - Update `_meta.dateLastModified` with the current Unix timestamp (`date +%s`).
2. **Edit [`_generated/index-timestamps.json`](file:///home/manan/Programs/homebrew/_generated/index-timestamps.json)**:
   - Update the `"m"` timestamp for `"creature/dkNinja; PoTA campaign.json"` to match `_meta.dateLastModified`.
3. **Edit [`README.md`](file:///home/manan/Programs/homebrew/README.md)**:
   - Add/update the creature under `## Contents` (maintain alphabetical order).
4. **Quick Syntax Validation**:
   - Run: `python3 -c "import json; json.load(open('creature/dkNinja; PoTA campaign.json')); json.load(open('_generated/index-timestamps.json')); print('OK')"`
