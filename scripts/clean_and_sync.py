#!/usr/bin/env python3
"""
clean_and_sync.py — 5etools Homebrew Data Cleaner & Synchronizer

Automates routine cleanup, schema compliance, and synchronizations for the
PoTA campaign pack:
1. Enforces single source identifier ("source": "PoTACampaign").
2. Normalizes mechanics tags (recharge, DCs, hits, spell typos).
3. Fixes/extracts legendaryGroup associations (and extracts misplaced lair/regional entries).
4. Sorts creatures and legendary groups alphabetically.
5. Formats JSON with tabs (\\t) and LF line endings.
6. Synchronizes dateLastModified in data and _generated/index-timestamps.json.
7. Automatically updates creature listings in README.md.

Usage:
  python3 scripts/clean_and_sync.py                  # Clean, fix, and sync existing files
  python3 scripts/clean_and_sync.py --add creature.json # Add creature(s) from JSON file or string
  python3 scripts/clean_and_sync.py --check          # Dry-run validation (exit 0 if clean, 1 if diff)
"""

import argparse
import copy
import json
import re
import sys
import time
from pathlib import Path

# Repository root determined from script location
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = REPO_ROOT / "creature" / "dkNinja; PoTA campaign.json"
TIMESTAMPS_FILE = REPO_ROOT / "_generated" / "index-timestamps.json"
README_FILE = REPO_ROOT / "README.md"
TARGET_SOURCE = "PoTACampaign"
DATA_KEY_IN_TIMESTAMPS = "creature/dkNinja; PoTA campaign.json"

# ==============================================================================
# Extensible Fixer Dictionaries & Patterns
# ==============================================================================

# Spell name typos -> canonical 5e spell names
SPELL_TYPOS = {
	"forbadance": "forbiddance",
}

# Regex replacements applied to all text strings
TEXT_REPLACEMENTS = [
	# Untagged DC: "DC 21", "DC21" -> "{@dc 21}" (ignores already tagged {@dc ...})
	(re.compile(r"(?<!\{@dc )\bDC\s*(\d+)"), r"{@dc \1}"),
	# Untagged hit modifiers: "(+12 to hit)" -> "({@hit 12} to hit)"
	(re.compile(r"\(\+([0-9]+)\s+to\s+hit\)"), r"({@hit \1} to hit)"),
	# Untagged concentration: "dropping concentration on" -> "dropping {@status concentration} on"
	(re.compile(r"\bdropping concentration on\b"), r"dropping {@status concentration} on"),
	# Untagged common skill checks: "Strength (Athletics)" -> "Strength ({@skill Athletics})"
	(re.compile(r"\bStrength \(Athletics\)"), r"Strength ({@skill Athletics})"),
	(re.compile(r"\bDexterity \(Acrobatics\)"), r"Dexterity ({@skill Acrobatics})"),
	(re.compile(r"\bWisdom \(Perception\)"), r"Wisdom ({@skill Perception})"),
	# Untagged common conditions
	(re.compile(r"\bone incapacitated humanoid\b"), r"one {@condition incapacitated} humanoid"),
	(re.compile(r"\bthat isn't incapacitated\b"), r"that isn't {@condition incapacitated}"),
	(re.compile(r"\ba grappled creature\b"), r"a {@condition grappled} creature"),
	# Attack damage hit text normalization
	(re.compile(r"\{@h\}The target takes\s+"), r"{@h}"),
	# Contraction / possessive curly apostrophes
	(re.compile(r"(\w)’(\w)"), r"\1'\2"),
]

# Regex replacements applied to 'name' keys (actions, traits, bonus, reactions)
NAME_REPLACEMENTS = [
	# Recharge syntax in ability names: "(Recharge 5–6)", "(Recharge 5-6)", "(Recharge 6)" -> "{@recharge 5}"
	(re.compile(r"\s*\([Rr]echarge\s*([0-9]+)(?:[–-][0-9]+)?\)"), r" {@recharge \1}"),
]


# ==============================================================================
# Recursive Text Cleaner
# ==============================================================================

def clean_text_value(text: str, parent_key: str = None) -> str:
	"""Applies spell typo fixes, tag normalizations, and name repairs to a string."""
	s = text

	# 1. Spell typos: {@spell typo} -> {@spell fix}
	for typo, fix in SPELL_TYPOS.items():
		s = re.sub(
			rf"\{{@spell\s+{re.escape(typo)}\}}",
			f"{{@spell {fix}}}",
			s,
			flags=re.IGNORECASE,
		)

	# 2. General text replacements (DCs, hits)
	for pattern, repl in TEXT_REPLACEMENTS:
		s = pattern.sub(repl, s)

	# 3. Name-specific replacements
	if parent_key == "name":
		for pattern, repl in NAME_REPLACEMENTS:
			s = pattern.sub(repl, s)

	return s


def walk_and_clean(obj, parent_key: str = None):
	"""Recursively traverses any JSON-compatible structure and cleans string values."""
	if isinstance(obj, str):
		return clean_text_value(obj, parent_key)
	elif isinstance(obj, list):
		return [walk_and_clean(item, parent_key) for item in obj]
	elif isinstance(obj, dict):
		return {k: walk_and_clean(v, k) for k, v in obj.items()}
	return obj


# ==============================================================================
# Modular Fixer Functions
# ==============================================================================

def extract_lair_and_regional_from_fluff(data: dict) -> int:
	"""
	If lairActions or regionalEffects are nested inside monster.fluff entries,
	extracts them onto the monster so fix_lair_and_regional_misplacement can
	properly create/link root legendaryGroup entries.
	"""
	fixes = 0
	for monster in data.get("monster", []):
		fluff = monster.get("fluff")
		if not isinstance(fluff, dict):
			continue
		entries = fluff.get("entries")
		if not isinstance(entries, list):
			continue

		lair_actions = None
		regional_effects = None
		intro_lore = []

		def find_sections(items):
			nonlocal lair_actions, regional_effects
			for item in items:
				if isinstance(item, str):
					intro_lore.append(item)
				elif isinstance(item, dict):
					name = item.get("name", "")
					if name == "Lair Actions":
						lair_actions = item.get("entries")
					elif name == "Regional Effects":
						regional_effects = item.get("entries")
					elif "entries" in item and isinstance(item["entries"], list):
						find_sections(item["entries"])

		find_sections(entries)

		if lair_actions or regional_effects:
			if lair_actions and "lairActions" not in monster:
				full_lair = []
				if intro_lore:
					full_lair.append(intro_lore[0])
				if isinstance(lair_actions, list):
					full_lair.extend(lair_actions)
				else:
					full_lair.append(lair_actions)
				monster["lairActions"] = full_lair
				fixes += 1

			if regional_effects and "regionalEffects" not in monster:
				monster["regionalEffects"] = regional_effects
				fixes += 1

			if intro_lore:
				monster["fluff"] = {"entries": [intro_lore[0]]}
			else:
				del monster["fluff"]
				monster["hasFluff"] = False
			fixes += 1

	return fixes


def fix_speed_hover(data: dict) -> int:
	"""Ensures speed has 'canHover': true when fly speed includes hover."""
	fixes = 0
	for monster in data.get("monster", []):
		speed = monster.get("speed")
		if isinstance(speed, dict):
			fly = speed.get("fly")
			if isinstance(fly, dict) and "hover" in fly.get("condition", "").lower():
				if not speed.get("canHover"):
					speed["canHover"] = True
					fixes += 1
	return fixes


def fix_sources(data: dict) -> int:
	"""Ensures all monsters and legendaryGroups use the unified PoTACampaign source."""
	fixes = 0

	for monster in data.get("monster", []):
		if monster.get("source") != TARGET_SOURCE:
			monster["source"] = TARGET_SOURCE
			fixes += 1

		# In 5etools, embedded monster fluff is an object { "entries": [...] } without name/source
		if "fluff" in monster and isinstance(monster["fluff"], dict):
			if "source" in monster["fluff"]:
				del monster["fluff"]["source"]
				fixes += 1
			if "name" in monster["fluff"]:
				del monster["fluff"]["name"]
				fixes += 1

	for lg in data.get("legendaryGroup", []):
		if lg.get("source") != TARGET_SOURCE:
			lg["source"] = TARGET_SOURCE
			fixes += 1

	return fixes


def fix_lair_and_regional_misplacement(data: dict) -> int:
	"""
	5etools schema forbids 'lairActions' and 'regionalEffects' directly on the monster object.
	If present on a monster, extracts them into the root 'legendaryGroup' array.
	"""
	fixes = 0
	lgs = data.setdefault("legendaryGroup", [])
	lg_by_name = {lg["name"]: lg for lg in lgs}

	for monster in data.get("monster", []):
		has_lair = "lairActions" in monster
		has_reg = "regionalEffects" in monster

		if has_lair or has_reg:
			m_name = monster["name"]
			lg = lg_by_name.get(m_name)
			if not lg:
				lg = {
					"name": m_name,
					"source": TARGET_SOURCE,
					"page": monster.get("page", 1),
				}
				lgs.append(lg)
				lg_by_name[m_name] = lg

			if has_lair:
				lg["lairActions"] = monster.pop("lairActions")
			if has_reg:
				lg["regionalEffects"] = monster.pop("regionalEffects")

			monster["legendaryGroup"] = {
				"name": m_name,
				"source": TARGET_SOURCE,
			}
			fixes += 1

	return fixes


def fix_legendary_group_references(data: dict) -> int:
	"""
	Validates monster.legendaryGroup references.
	If the legendaryGroup definition does not exist in the root 'legendaryGroup' array,
	removes the dangling reference to keep the 5etools schema valid.
	"""
	fixes = 0
	valid_lg_names = {lg["name"]: lg for lg in data.get("legendaryGroup", [])}

	for monster in data.get("monster", []):
		lg_ref = monster.get("legendaryGroup")
		if not lg_ref:
			continue

		lg_name = lg_ref.get("name") if isinstance(lg_ref, dict) else lg_ref
		if lg_name in valid_lg_names:
			if isinstance(lg_ref, dict) and lg_ref.get("source") != TARGET_SOURCE:
				monster["legendaryGroup"]["source"] = TARGET_SOURCE
				fixes += 1
		else:
			# Remove dangling reference
			del monster["legendaryGroup"]
			fixes += 1

	return fixes


def sort_entries(data: dict) -> int:
	"""Sorts monsters and legendary groups alphabetically by name."""
	fixes = 0

	if "monster" in data:
		original_names = [m["name"] for m in data["monster"]]
		data["monster"].sort(key=lambda m: m["name"])
		if [m["name"] for m in data["monster"]] != original_names:
			fixes += 1

	if "legendaryGroup" in data:
		original_names = [lg["name"] for lg in data["legendaryGroup"]]
		data["legendaryGroup"].sort(key=lambda lg: lg["name"])
		if [lg["name"] for lg in data["legendaryGroup"]] != original_names:
			fixes += 1

	return fixes


# ==============================================================================
# README Synchronization
# ==============================================================================

def generate_readme_creature_bullet(monster: dict, lgs_by_name: dict) -> str:
	"""Generates a formatted markdown bullet line for a monster in README.md."""
	name = monster["name"]
	cr = monster.get("cr", "?")
	m_type = monster.get("type", "")

	if isinstance(m_type, dict):
		base_t = m_type.get("type", "").capitalize()
		tags = [t.capitalize() for t in m_type.get("tags", [])]
		type_str = f"{base_t} ({', '.join(tags)})" if tags else base_t
	else:
		type_str = str(m_type).capitalize()

	lg = lgs_by_name.get(name)
	features = []
	if any("mythic" in t.get("name", "").lower() for t in monster.get("trait", [])) or "mythic" in monster:
		features.append("Mythic Phase")
	if lg and lg.get("lairActions"):
		features.append("Lair Actions")
	if lg and lg.get("regionalEffects"):
		features.append("Regional Effects")

	feat_str = ""
	if features:
		if len(features) == 1:
			feat_str = f", with {features[0]}"
		elif len(features) == 2:
			feat_str = f", with {features[0]} and {features[1]}"
		else:
			feat_str = f", with {features[0]}, {features[1]}, and {features[2]}"

	return f"  - **{name}** — CR {cr} {type_str}{feat_str}"


def sync_readme(data: dict) -> bool:
	"""Updates the creature list in README.md to reflect current monsters."""
	if not README_FILE.exists():
		return False

	lgs_by_name = {lg["name"]: lg for lg in data.get("legendaryGroup", [])}
	bullet_lines = [
		generate_readme_creature_bullet(m, lgs_by_name)
		for m in data.get("monster", [])
	]
	new_bullets_text = "\n".join(bullet_lines) + "\n"

	content = README_FILE.read_text(encoding="utf-8")

	pattern = re.compile(
		r"(- \*\*`creature/dkNinja; PoTA campaign\.json`\*\*:.*?\n)(?:  - \*\*.*?\n)+(\nAll creatures are grouped under)",
		re.DOTALL,
	)

	match = pattern.search(content)
	if not match:
		print("Warning: Could not locate creature bullet section in README.md.")
		return False

	updated_content = pattern.sub(rf"\g<1>{new_bullets_text}\g<2>", content)

	if updated_content != content:
		README_FILE.write_text(updated_content, encoding="utf-8")
		return True
	return False


# ==============================================================================
# Creature Importer
# ==============================================================================

def add_incoming_creatures(data: dict, incoming) -> list:
	"""
	Parses and merges one or more incoming creature dictionaries.
	Updates existing creature if same name exists, otherwise appends.
	"""
	if isinstance(incoming, dict):
		if "monster" in incoming:
			incoming_list = incoming["monster"]
			if "legendaryGroup" in incoming:
				existing_lgs = {lg["name"]: lg for lg in data.setdefault("legendaryGroup", [])}
				for lg in incoming["legendaryGroup"]:
					existing_lgs[lg["name"]] = lg
				data["legendaryGroup"] = list(existing_lgs.values())
		else:
			incoming_list = [incoming]
	elif isinstance(incoming, list):
		incoming_list = incoming
	else:
		raise ValueError(f"Unsupported incoming data format: {type(incoming)}")

	monsters = data.setdefault("monster", [])
	monsters_by_name = {m["name"]: i for i, m in enumerate(monsters)}
	added_names = []

	for item in incoming_list:
		if not isinstance(item, dict) or "name" not in item:
			continue
		name = item["name"]
		if name in monsters_by_name:
			monsters[monsters_by_name[name]] = item
		else:
			monsters.append(item)
			monsters_by_name[name] = len(monsters) - 1
		added_names.append(name)

	return added_names


# ==============================================================================
# Main Pipeline
# ==============================================================================

def run_pipeline(add_payload=None, force_timestamp: bool = False, check_mode: bool = False):
	if not DATA_FILE.exists():
		print(f"Error: Data file not found at {DATA_FILE}")
		sys.exit(1)

	original_text = DATA_FILE.read_text(encoding="utf-8")
	data = json.loads(original_text)
	snapshot_before = copy.deepcopy(data)

	# 1. Add incoming creatures if provided
	added_names = []
	if add_payload is not None:
		added_names = add_incoming_creatures(data, add_payload)
		print(f"Imported/Updated creature(s): {', '.join(added_names)}")

	# 2. Extract nested lairActions / regionalEffects from fluff if present
	extract_lair_and_regional_from_fluff(data)

	# 3. Extract misplaced lairActions / regionalEffects from monsters into root legendaryGroup
	fix_lair_and_regional_misplacement(data)

	# 4. Ensure hover speeds have canHover: true
	fix_speed_hover(data)

	# 5. Fix sources
	fix_sources(data)

	# 6. Clean up dangling legendaryGroup references
	fix_legendary_group_references(data)

	# 5. Walk and clean text tags & spell typos
	data = walk_and_clean(data)

	# 6. Sort monsters and legendary groups alphabetically
	sort_entries(data)

	# Check whether data changed compared to initial state
	data_changed = (data != snapshot_before) or (add_payload is not None)

	# Format output JSON
	timestamp = int(time.time())
	if data_changed or force_timestamp:
		data.setdefault("_meta", {})["dateLastModified"] = timestamp

	new_text = json.dumps(data, indent="\t", ensure_ascii=False) + "\n"

	if check_mode:
		clean = (new_text == original_text)
		if clean:
			print("Check passed: Data file is clean, sorted, and properly tagged.")
			sys.exit(0)
		else:
			print("Check failed: Differences found. Run scripts/clean_and_sync.py to apply fixes.")
			sys.exit(1)

	# Write changes if modified
	if new_text != original_text or data_changed or force_timestamp:
		DATA_FILE.write_text(new_text, encoding="utf-8")
		print(f"Updated {DATA_FILE.relative_to(REPO_ROOT)}")

		# Sync timestamps file
		if TIMESTAMPS_FILE.exists():
			ts_data = json.loads(TIMESTAMPS_FILE.read_text(encoding="utf-8"))
			ts_data.setdefault(DATA_KEY_IN_TIMESTAMPS, {})["m"] = timestamp
			TIMESTAMPS_FILE.write_text(json.dumps(ts_data, indent="\t", ensure_ascii=False) + "\n", encoding="utf-8")
			print(f"Updated {TIMESTAMPS_FILE.relative_to(REPO_ROOT)} with timestamp {timestamp}")

	# Sync README
	readme_updated = sync_readme(data)
	if readme_updated:
		print(f"Updated {README_FILE.relative_to(REPO_ROOT)} creature list.")

	print(f"Complete. Total creatures in pack: {len(data.get('monster', []))}")


def main():
	parser = argparse.ArgumentParser(
		description="Clean, format, and synchronize 5etools homebrew creature pack."
	)
	parser.add_argument(
		"--add",
		metavar="JSON_OR_PATH",
		help="Add or update creature(s) from a JSON file, raw JSON string, or '-' for stdin.",
	)
	parser.add_argument(
		"--force-timestamp",
		action="store_true",
		help="Force update dateLastModified even if no data changed.",
	)
	parser.add_argument(
		"--check",
		action="store_true",
		help="Dry run check mode: exit 0 if file is clean, 1 if fixes are needed.",
	)

	args = parser.parse_args()

	payload = None
	if args.add:
		if args.add == "-":
			payload = json.load(sys.stdin)
		elif Path(args.add).exists():
			payload = json.loads(Path(args.add).read_text(encoding="utf-8"))
		else:
			try:
				payload = json.loads(args.add)
			except Exception as e:
				print(f"Error parsing JSON from --add argument: {e}")
				sys.exit(1)

	run_pipeline(
		add_payload=payload,
		force_timestamp=args.force_timestamp,
		check_mode=args.check,
	)


if __name__ == "__main__":
	main()
