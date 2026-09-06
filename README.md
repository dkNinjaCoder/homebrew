# dkNinja's Homebrew

Homebrew JSONs compatible with [5etools](https://5e.tools/).

## Contents

- **`creature/dkNinja; Belial.json`**: Belial (Prince of the Covetous, Lord of Lusts) — CR 22 Fiend (Devil).
- **`creature/dkNinja; Tanazir Silverquil.json`**: Tanazir Silverquil — CR 26 Dragon, including Mythic Phase, Lair Actions, and Regional Effects.

---

## How to Import into 5etools

### Option 1: Automatic via Repository URL (Recommended)
1. In 5etools, navigate to **Utilities** &rarr; **Homebrew Manager** (or click the **Manage Homebrew** button on any page).
2. Click the **gear / settings icon** next to the **"Get Homebrew"** button.
3. Set the **Base Repository URL** to:
   ```text
   https://raw.githubusercontent.com/dkNinjaCoder/homebrew/master/
   ```
4. Click **"Get Homebrew"**.
5. Select the homebrews you want to add and click to import.

### Option 2: Load from URL
1. In the 5etools **Homebrew Manager**, click **"Load from URL"**.
2. Enter the raw URL for the creature you wish to import:
   - **Belial**:
     ```text
     https://raw.githubusercontent.com/dkNinjaCoder/homebrew/master/creature/dkNinja;%20Belial.json
     ```
   - **Tanazir Silverquil**:
     ```text
     https://raw.githubusercontent.com/dkNinjaCoder/homebrew/master/creature/dkNinja;%20Tanazir%20Silverquil.json
     ```

### Option 3: Manual File Upload
1. Download either JSON file from the [`creature/`](creature/) directory.
2. In the 5etools **Homebrew Manager**, click **"Upload File"** and select the downloaded file.

---

## Development & Maintenance

This repository adheres to the official [TheGiddyLimit/homebrew](https://github.com/TheGiddyLimit/homebrew) repository conventions:
- Categorized subdirectories (e.g. `creature/`)
- Filename format: `Author; Brew Name.json`
- Tab indents, LF line endings, UTF-8 encoding
- Pre-generated index files in `_generated/` for 5etools repository discovery

### Scripts

```bash
# Install dependencies
npm install

# Validate data against official 5etools schemas and rules
npm test

# Clean data and update _generated/ index files
npm run build
```
