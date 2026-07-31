# How to publish CapUCalc Tools on GitHub

This is a one-time setup guide, written for someone who has never used GitHub before. Skip the sections you've already done.

Total time: about 30 minutes.

## Step 1 — Create your GitHub account (5 min)

1. Go to **https://github.com** and click **Sign up**.
2. Use an email you can access — GitHub sends a verification code.
3. Pick a username. Since you'll be creating a **CapUCalc** organization next, use *your own* name (e.g. `carypotter`) rather than `capucalc` for your personal account. The org gets the brand name.
4. Choose the **Free** plan when prompted. Sufficient for what we're doing.
5. Verify the email GitHub sends you.

You now have `github.com/<your-username>` as your personal profile.

## Step 2 — Create the CapUCalc organization (3 min)

Organizations on GitHub let you own repos under a company name and add teammates later.

1. From any GitHub page, click your avatar (top right) → **Your organizations** → **New organization**.
2. Pick the **Free** plan.
3. **Organization name:** `capucalc` (lowercase; will become `github.com/capucalc`).
4. **Contact email:** the CapUCalc address.
5. **This organization belongs to:** "A business or institution."
6. Skip the "add members" screen — you can add teammates later.

Your org now exists at **`github.com/capucalc`**.

## Step 3 — Create the marketplace repo (2 min)

1. Go to **`github.com/capucalc`**. Click the green **New** button (or **Create new repository**).
2. **Repository name:** `capucalc-tools` (matches the marketplace folder name).
3. **Description:** `Official CapUCalc plugin marketplace — skills for finance and accounting pros who use CapUCalc.`
4. **Public** — required for teammates to install without extra auth setup.
5. **Do NOT** check "Add a README", "Add .gitignore", or "Choose a license." You already have those files locally; adding them here creates conflicts.
6. Click **Create repository**.

You land on an empty repo page with instructions. Ignore them — the next step uses the easier web upload path.

## Step 4 — Upload the files (10 min, no command line needed)

1. On the empty repo page, look for the link that says **"uploading an existing file"** in the top instructions block. Click it.
2. A drag-and-drop area appears.
3. **Open File Explorer** (Windows) and navigate to:
   ```
   C:\Users\CaryPotter\OneDrive - Deal Valuation\Documents\CapUCalc Tools
   ```
4. **Select every file and folder** in that directory (`Ctrl+A`), then drag them all onto the GitHub upload area at once. Do **not** drag the `CapUCalc Tools` folder itself — drag its *contents*. Repo root should end up with `README.md`, `LICENSE`, `PUBLISH.md`, `captable-import.skill`, and the `.claude-plugin/` and `plugins/` folders.
5. Wait for uploads to finish (may take a minute; there are ~10 small files).
6. At the bottom, in the **Commit changes** panel:
   - Leave the default message ("Add files via upload"), or write "Initial commit."
   - Click **Commit changes**.

Your repo now has all the files. You should see the README rendered on the landing page.

## Step 5 — Verify the install command works (5 min)

Any teammate can now install with:

```
/plugin marketplace add github:capucalc/capucalc-tools
/plugin install captable-import@capucalc-tools
```

Test it yourself in a fresh Cowork session to make sure. If Cowork can't find the marketplace, wait 1–2 minutes for GitHub's CDN to catch up.

## Step 6 — (Optional) Create a Release for the `.skill` file (5 min)

For users who don't want the whole marketplace, offer a direct `.skill` download.

1. On the repo page, click **Releases** (right sidebar) → **Create a new release**.
2. **Tag:** `v0.2.0` (matches the version in `marketplace.json`).
3. **Title:** `captable-import v0.2.0 — CapUCalc Tools launch`.
4. **Description:** short changelog — "First public release of captable-import: populate a CapUCalc cap table from an xlsx or pdf in one pass."
5. Under **Attach binaries**, drag in `captable-import.skill`.
6. Click **Publish release**.

The `.skill` file now has a permanent download URL you can link from LinkedIn or the CapUCalc website.

## Step 7 — Set the repo topics for discoverability (1 min)

1. On the repo landing page, click the ⚙ next to **About** (top-right of the file list).
2. Add topics: `capucalc`, `cap-table`, `valuation`, `finance`, `accounting`, `claude`, `cowork`, `claude-in-chrome`, `skill`.
3. Click **Save changes**.

These make the repo show up in GitHub search for finance and Claude-related queries.

## Updating the repo later

When you make changes to the skill:

1. Bump the version numbers in `marketplace.json` and `plugins/captable-import/.claude-plugin/plugin.json`.
2. Repackage the `.skill` (`python -m scripts.package_skill ...`).
3. Upload the updated files via the web UI (**Add file** → **Upload files** at the repo root), or use `git` from a terminal if you're comfortable with it.
4. If you cut a new Release, tag it with the new version (e.g. `v0.3.0`).

That's it. Teammates who've already added the marketplace will pull the latest automatically on their next Cowork session.

## Troubleshooting

- **"Repository not found" when a teammate tries to install** — make sure the repo is Public (Settings → General → Danger Zone → "Change repository visibility").
- **Some files didn't upload** — GitHub's web uploader limits how many files can go in one batch. If you see gaps, do a second upload for the missing files.
- **`.skill` file rejected** — GitHub restricts uploads over 100 MB in the web UI. The `.skill` file is only ~15 KB so this shouldn't happen; if it does, use `git` from a terminal instead.
