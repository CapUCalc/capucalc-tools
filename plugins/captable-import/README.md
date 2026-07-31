# captable-import

Populates a **CapUCalc Capital Table Editor** on [app.capucalc.com](https://app.capucalc.com) with equity-class data from a client's source cap table.

## What it does

Given:

- A folder containing a cap table file — `.xlsx` (Carta-style "Summary Cap Table" is most common, or the sparse totals-only layout) or `.pdf`
- A CapUCalc company page open in Chrome (with the Claude in Chrome extension connected)

The skill will:

1. Locate and parse the cap table file into a canonical list of classes — Common, Preferred, Convertible Notes, Options.
2. Convert actual share and dollar amounts to millions.
3. Compute per-share Face Value for Preferred series when the source only carries cash raised and shares (or use the source's per-share price when available).
4. Open or create the target cap table in CapUCalc, overwrite the placeholder Common column with the first real class, then add each remaining class with the correct column type (Common / Preferred / Notes / Options).
5. For every Preferred / Notes / Options column, set the "If convertible or exercisable" destination class (typically Common) and the Conversion or Exercise Price Per Share so the form marks those columns complete.
6. Verify entered values via a JS dump and present the result back as a small table.
7. **Optionally** — walk you through any remaining "missing fields" interactively, asking for values one batch at a time and filling them in as you provide them.

Fields the source doesn't cover are left blank; the form's own "X missing fields" badge tracks them. Missing fields is an acceptable outcome — many downstream tools work fine — but the interactive fill mode above helps you drive that number to zero when needed.

## How to use it

Once installed (via the CapUCalc Tools marketplace or as a standalone `.skill`), just ask Cowork:

> "Pull the cap table from `<path-to-folder>` and load it into the CapUCalc page I have open."

> "Take the captable from the xlsx in my Documents folder and fill CapUCalc."

The skill triggers automatically. If it doesn't, mention "CapUCalc" or "app.capucalc.com" by name.

## What you provide

- A folder Cowork can read (you'll be asked to grant access if it isn't already).
- The CapUCalc company URL (the `companies/<uuid>` page) open in Chrome with the Claude in Chrome extension connected.

## What this skill does not do

- It doesn't invent priority-level orderings, issuance dates, dividend rates, or liquidation preferences — those live in legal documents (term sheets, certs of designation), not in summary cap tables.
- It doesn't enter sensitive credentials, payment info, or sharing-permission changes.

## Files

- `skills/captable-import/SKILL.md` — main skill instructions.
- `skills/captable-import/references/parsing.md` — XLSX (Carta and non-Carta) and PDF parsing notes.
- `skills/captable-import/references/form_workflow.md` — full CapUCalc browser workflow, including JS snippets for fast batch entry.
- `skills/captable-import/scripts/parse_captable_xlsx.py` — emits canonical JSON from a Carta Summary Cap Table workbook.
