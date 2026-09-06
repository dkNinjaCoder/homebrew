# dkNinja's Homebrew — PoTA campaign

Homebrew JSONs compatible with [5etools](https://5e.tools/).

## Contents

- **`creature/dkNinja; PoTA campaign.json`**: Single homebrew pack (**PoTA campaign**) containing:
  - **Belial (Prince of the Covetous, Lord of Lusts)** — CR 22 Fiend (Devil)
  - **Tanazir Silverquil** — CR 26 Dragon, with Mythic Phase, Lair Actions, and Regional Effects

Both creatures are grouped under the single source **PoTA campaign (PoTA)**.

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
5. Select **"PoTA campaign"** and click to add. Both creatures will be imported under the single `PoTA` source.

### Option 2: Load from URL
1. In the 5etools **Homebrew Manager**, click **"Load from URL"**.
2. Enter the raw URL:
   ```text
   https://raw.githubusercontent.com/dkNinjaCoder/homebrew/master/creature/dkNinja;%20PoTA%20campaign.json
   ```

### Option 3: Manual File Upload
1. Download the [`creature/dkNinja; PoTA campaign.json`](creature/dkNinja;%20PoTA%20campaign.json) file.
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
