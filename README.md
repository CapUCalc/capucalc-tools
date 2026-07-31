# CapUCalc Tools

Official plugin marketplace for **CapUCalc** — the valuation platform at [app.capucalc.com](https://app.capucalc.com). Bundles time-saving skills for finance and accounting professionals who use CapUCalc day-to-day.

## Plugins

| Plugin | What it does |
|---|---|
| `captable-import` | Reads a client's source cap table (xlsx or pdf) and populates the matching equity classes in the CapUCalc Capital Table Editor. Handles the millions conversion, per-share Face Value computation, and destination-class / conversion-price fill-in for convertibles. Can also walk you through any missing fields interactively. |

More plugins coming.

## Compatibility

**Runtime:** Cowork (recommended) or Claude Code. Both support Skills plus the Claude in Chrome extension, which this skill drives to fill the CapUCalc form. Not compatible with claude.ai chat or direct API calls, which don't have the browser tools.

**Model:** Any current Claude model works. Opus and Sonnet are both strong picks for finance work; Haiku will run the happy path but is less reliable for edge cases (toast collisions, silent date-field rejections, the "Face Value is $/share not $M/share" convention). We recommend **Opus for client-facing cap tables**, **Sonnet for routine internal work**.

**Browser:** Chrome with the [Claude in Chrome](https://claude.com/chrome) extension installed and signed in to the same Anthropic account as your Cowork session.

## Install (Cowork)

You'll need [Cowork](https://claude.com/cowork) installed and signed in, plus the [Claude in Chrome](https://claude.com/chrome) extension installed and signed in to the same account.

### One-time: add the marketplace

Once we've published the marketplace repo, install it with:

```
/plugin marketplace add github:capucalc/capucalc-tools
```

Until then, you can install directly from a local copy of this folder:

```
/plugin marketplace add <path-to-CapUCalc Tools folder>
```

### Install a plugin

```
/plugin install captable-import@capucalc-tools
```

### First run

Open Cowork, make sure your Chrome browser is connected (the extension side panel should say "Connected"), then try a prompt like:

> "Pull the cap table from the xlsx in [folder path] and load it into the CapUCalc page I have open."

The skill triggers automatically. If it doesn't, mention "CapUCalc" or "app.capucalc.com" by name.

## Alternative: single-file `.skill` install

If you don't want to add a whole marketplace, download the packaged `.skill` file and import it directly into Cowork. Simpler for a one-time install; no auto-updates.

## Chrome profiles and CapUCalc accounts (read this if you use more than one)

Chrome profiles are isolated. Each profile has its own cookies, signed-in sessions, and extensions. If you sign in to CapUCalc as different accounts in different profiles, Cowork can only act through one profile at a time.

- **The Claude in Chrome extension is installed and connected per profile.** Whichever profile is currently paired with your Cowork session is the one Cowork drives. Cookies visible to that profile are the only ones Cowork can use.
- **Closing the paired profile disconnects the link.** If you then open a different profile, Cowork may attach to it (if it also has the extension) — and that profile's CapUCalc account becomes the target. The URL Cowork navigates to is the same, but the logged-in user is different.
- **There is no visible "which account am I on" cue in the URL or page layout.** The mistake is silent. The skill will happily populate the wrong company if profiles got swapped.

Recommendations:

1. Pick one profile to be your "CapUCalc profile" and use it consistently. Install the Claude in Chrome extension there and keep it signed in.
2. Before starting a task, glance at the Claude in Chrome side panel to confirm which profile + Cowork session are paired.
3. If you must switch profiles mid-day, close all Chrome windows, open the correct profile, let the extension reconnect, then resume.
4. For high-stakes runs, ask Cowork to "screenshot the top-right user menu and tell me which CapUCalc account is signed in" before it touches the form — a cheap sanity check.

## Layout

```
CapUCalc Tools/
├── .claude-plugin/
│   └── marketplace.json
├── plugins/
│   └── captable-import/
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── skills/
│       │   └── captable-import/
│       │       ├── SKILL.md
│       │       ├── references/
│       │       │   ├── parsing.md
│       │       │   └── form_workflow.md
│       │       └── scripts/
│       │           └── parse_captable_xlsx.py
│       └── README.md
└── README.md    ← you are here
```

## Maintaining this marketplace

- **Adding a new skill to an existing plugin:** drop the new skill folder under `plugins/<plugin-name>/skills/<new-skill-name>/`. Picks up automatically.
- **Adding a brand-new plugin:** create a new folder under `plugins/`, add a `.claude-plugin/plugin.json`, and append an entry to the `plugins` array in `.claude-plugin/marketplace.json`.
- **Bumping versions:** keep `version` in sync between `marketplace.json` (the plugin entry) and the plugin's own `plugin.json`. Bump the marketplace's top-level `version` whenever the catalog itself changes.
- **Sensitive material:** never commit client folders, term sheets, or actual cap tables. Skills read from the user's own filesystem at run time.

## Contact

Publisher: **CapUCalc** — [app.capucalc.com](https://app.capucalc.com)
