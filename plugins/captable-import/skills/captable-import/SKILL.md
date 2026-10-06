---
name: "captable-import"
description: "Use this skill whenever the user wants to populate the CapUCalc Capital Table Editor on app.capucalc.com with equity-class data from a client's cap table. Trigger on phrases like \"load the cap table into CapUCalc\", \"input the captable\", \"fill the CapUCalc cap table\", or whenever a folder has a cap table file (xlsx or pdf) AND the user references CapUCalc or has the company page open in Chrome. The skill locates the source, parses it into Common / Preferred / Notes / Options classes, converts to millions, adds the right column type per class via the \"+\" menu, and computes per-share Face Value so the calc-driven Aggregate Funding flows through. It sets the destination class + conversion price for each convertible so the form marks them complete, and can walk the user through remaining \"missing fields\" interactively. Always use it for this workflow — several mechanics (column-type selector, calc-driven Aggregate, As-Of-Date date max) are easy to miss."
---

# captable-import

This skill takes a client's capital table and populates the matching equity classes in the **CapUCalc Capital Table Editor** in a single web-form pass.

The CapUCalc app lives at `app.capucalc.com`. Each company page lists its cap tables under a "Cap Tables" card; you can either open an existing cap table or click "+ New" to create one and populate it.

## When to use

Use this skill when **all** of the following are true:

- The user wants the CapUCalc Capital Table Editor populated — they may say "load it", "fill it out", "input the cap table", "enter the equity classes", etc.
- A source cap table is available in `.xlsx` or `.pdf` form. Carta exports and DealValuation `DVFinInput-*.xlsx` templates are the most common shapes.
- The user is signed in to CapUCalc and the company page is reachable in their connected browser.

## High-level workflow

1. Locate the source cap table file. If the folder isn't already mounted, call `request_cowork_directory` (or the session's folder-access tool) with the path the user named.
2. Parse it into the canonical class list: any number of Common, Preferred, Convertible Note, and Options classes — name, shares outstanding (actual), and price-per-share / cash raised (actual) per class.
3. Convert actual numbers to millions (divide by 1,000,000). For Preferred classes, also compute Face Value per share = cash raised ÷ shares outstanding (in actual dollars per actual share) if the source doesn't already carry a per-share price. For Profits Interest classes, compute the per-unit threshold on a pre-dilution basis (see "Profits Interest threshold rule").
4. Connect to the browser (`tabs_context_mcp`, `select_browser` for Chrome) and navigate to the CapUCalc company. If the user hasn't shared the URL, open `https://app.capucalc.com/companies` and find the company by name. If the browser shows a sign-in page, ask the user to sign in (never enter credentials) or offer another browser where they may already be signed in.
5. Either open an existing cap table or create a new one (name + "As Of" date). The default cap table has a placeholder Common column that's easier to overwrite than to delete.
6. For each remaining class, click the "+" button at the top right, choose the matching column type from the popover (Common / Preferred / Notes / Options), and fill in the fields the source actually has.
7. Set the destination class + conversion price for each Preferred / Notes / Options column (see Step 5 details below). Without these, the form's "missing fields" badge keeps flagging them.
8. Verify what landed using a JS dump (ideally after closing and reopening the editor, to confirm autosave) and present the table back to the user. Let the form's own "X missing fields" badge track anything the source didn't cover — don't invent values.

## Step 1 — Find the source file

If the user names a folder, mount it via `request_cowork_directory` (or the session's folder-access tool). If the user only refers to "the cap table" or "the folder", ask which one. Don't assume.

## Step 2 — Parse the source

Prefer XLSX over PDF when both exist. For Carta-style "Summary Cap Table" layouts (sections labeled "Common Stock classes", "Preferred Stock classes", "Convertibles"), use the bundled helper:

```bash
python "scripts/parse_captable_xlsx.py" "<path-to-xlsx>"
```

It emits JSON with the canonical class list.

For non-Carta workbooks — e.g. sparse spreadsheets with only totals and price-per-share rows, or files where "letters" like A / B / E2 / G1 identify Preferred series — you'll need to parse manually. See `references/parsing.md` for guidance.

### DealValuation `DVFinInput-*.xlsx` ("Capital structure" sheet)

Parse these manually. Column A = label, column B = unit hint, columns C onward = one class per column (most senior first). Match on the column-A labels, since row numbers can drift between template versions. Typical rows:

- **Convertible debt (~rows 13–29)**: name row 14, face value ($ millions) row 16, interest rows 17–19, maturity row 20, conversion price row 27.
- **Preferred stock (~rows 31–49)**: name row 32, date of issuance row 34, shares outstanding row 35, liquidation preference per unit row 36, conversion price per unit row 37, dividend rows 41–43.
- **Common stock (~rows 51–60)**: name row 52, shares outstanding row 55, dividend rows 56–58.
- **Options / Profits Interest (~rows 61–82)**: name row 62, **"Profit Interest Aggregate Threshold" ($ millions) row 63**, option groups rows 65–80, total shares outstanding row 81, weighted-average exercise price row 82.

Units matter: **share counts are usually in 000s** (column B says "000s"; the note in B1 says units are set on the workbook's Setup tab). With 000s, Shares (M) = value ÷ 1,000. Dollar amounts are usually already in $ millions.

If a Preferred column has a liquidation preference per unit (row 36) and no separate price, use it as Face Value; use row 37 as the Conversion Price. If both are blank, leave Face Value and Conversion Price blank and flag them.

## Profits Interest threshold rule

CapUCalc has no aggregate-threshold field. Enter a profits interest as an **Options** column, with the per-unit threshold in **Conversion or Exercise Price Per Share**. Always convert an aggregate threshold on a **pre-dilution** basis:

> **Per-unit threshold = Aggregate threshold ($) ÷ total units outstanding before the profits interest** (all Common + Preferred units; exclude the profits-interest units themselves and other options).

Example (Interpret, 9/2026): threshold $92.5M; Common 112,281 + Series A 678,947 + Series B 331,579 = 1,122,807 pre-dilution units, so the threshold is **$82.38 per unit**. Do **not** divide by the profits-interest unit count ($92.5M ÷ 198,142 = $466.84 is wrong).

Enter it as a plain number (e.g. `82.38`); the form reformats it as `$82.38`. Set the Options column's destination class to the Common class. Show the user the calculation (numerator, denominator, result).

## Step 3 — Convert to millions

The CapUCalc form defaults to "Millions" for both Units and Currency. Keep that convention. Apply these rules:

- **Shares Outstanding (millions)** = actual shares ÷ 1,000,000. Keep at least 6 decimal places so small classes don't round to zero.
- **Aggregate Funding (millions)** = actual cash raised ÷ 1,000,000. This is what the form's "Aggregate Funding at Date of Issuance" row should *display*.
- **Face Value or Original Price per unit at Issuance** stays in **actual dollars per actual share**, not millions per share. The form computes Aggregate (in millions) = Face Value × Shares (in millions) — that math only works when Face Value is in $/share.

For Preferred classes:
- If the source already carries a per-share price (PPS, "Share Class Original Issue Price", liquidation preference per unit), use it directly as Face Value.
- If it only carries cash raised and shares outstanding, compute Face Value = cash raised ÷ shares outstanding using the *actual* numbers.
- If it carries neither (some later-stage series may not), leave Face Value blank — the form's "missing fields" badge will flag it and the user can supply later.

## Step 4 — Open the CapUCalc company page

The company URL format is `https://app.capucalc.com/companies/<uuid>`. If the user gives only a company name, open `https://app.capucalc.com/companies` and click the company. The page lists existing Cap Tables with an Open button per table — click Open on the one the user wants populated. Or click "+ New" to create a new cap table (name + "As Of" date required). After "Create Cap Table" the editor usually opens directly.

If the source has no valuation date, use today's date as the As Of date and tell the user.

**Watch the "As Of" date.** All Date of Original Issuance inputs in the form have a `max` attribute equal to the cap table's As Of date. If you try to set an issuance date later than the As Of date, the value fails silently. If the user asks for a later date, change the As Of date first, then the issuance date will accept it.

## Step 5 — Fill the form

See `references/form_workflow.md` for the full step-by-step. The key rules:

- The first Common class **overwrites** the default Common column. Don't add a fresh one and leave the placeholder behind.
- Each subsequent class is added by clicking the "+" at the top-right of the table and choosing the matching type from the popover: **Common**, **Preferred**, **Notes** (convertible notes), or **Options** (also used for Profits Interest).
- Common columns expose only Name, Shares Outstanding, Additional Liquidation Preferences, and Dividend / Interest Rate as direct inputs. Preferred adds Priority Level, Date of Original Issuance, Face Value, a destination-class selector, and a vesting type. Notes columns have no Shares or Face Value rows — Aggregate Funding is a directly editable input there.
- **Convertible / exercisable classes need a destination + a conversion price.** For each Preferred, Notes, or Options column, use the "If convertible or exercisable, select destination class" dropdown — choose the appropriate common class (almost always the first Common entered). Once a destination is selected, a "Conversion or Exercise Price Per Share" sub-row appears: enter the Face Value for Preferred, the pre-dilution per-unit threshold for Profits Interest, and leave the exercise price blank for ordinary Options unless a strike price is available in the source.
- Enter only what the source contains. Leave Priority Level, Date of Original Issuance, Maturity Date, etc. blank if the source doesn't carry them. The form's own header badge ("X missing fields") will track gaps for the user.
- After each "+ → type" selection, the form shows a green toast like "New Preferred added". Toasts don't always auto-dismiss and can occlude the "+" button and the header. Dismiss them first (`find` for "Close toast button").

### Known UI quirks

- **The "+" (Add column) button toggles its popover.** A second click closes it silently, and with 3+ columns the button can be pushed off-screen behind the horizontal scrollbar. Most reliable: click it via JS — `document.querySelector('button[title="Add column"]').click()` — wait ~600 ms, then click the button whose text is exactly `Preferred` / `Common` / `Notes` / `Options` and whose y-position is near the top of the page (the per-column "Notes" links at the bottom share the text "Notes").
- **Screenshots can time out** on the editor. Prefer `get_page_text`, `find`, and JS reads.
- **Autosave**: there is no Save button. Values persist once the input/change/blur events fire; verify by closing and reopening the editor.

## Step 6 — Verify

After all columns are entered, dump the form's input values via `javascript_tool` to confirm name, shares, face value, destination, and conversion price for each class. See `references/form_workflow.md` for the exact JS snippet.

Present the result to the user as a small table: one row per class with Type, Name, Shares (M), Face Value/sh, Aggregate (M, calc), and any explicit destination/conversion price entries.

After verifying, **always remind the user** of two things:

1. The form's header badge ("X missing fields") still shows what's left. Typical residual fields the source doesn't cover — the user may need to complete them by hand from term sheets, certificates of designation, board minutes, or option-grant agreements:
   - **Priority Level of Seniority** (Preferred & Notes) — the seniority rank, 1–10.
   - **Date of Original Issuance** (Preferred & Notes & Options) — when the class was issued.
   - **Maturity Date** (Notes) — when the convertible matures.
   - **Dividend / Interest Rate** (Preferred & Notes) and its "Paid or accrued" / "Accrual Period" sub-fields.
   - **Threshold Vesting Type**, **Vesting Benchmark Class**, **Vesting Target Price** (Preferred & Notes & Options) — when vesting/threshold conditions apply.
   - **Additional Liquidation Preferences** (Preferred) — beyond the 1x non-participating default.
   - **Face Value + Conversion Price** for any series where the source didn't carry a per-share price.
   - **Exercise Price Per Share** (Options) — if a strike is in the option grants and wasn't in the source file.
2. **"Missing fields" is an acceptable outcome.** The cap table is functional for many downstream uses (share counts, ownership percentages, waterfall structure) even with the badge non-zero. But if the user needs it to read "0 missing fields" for a specific downstream tool, they can either supply the values by hand OR invoke the follow-up mode below.

## Step 7 — Interactive fill for missing fields (optional)

After the initial pass, offer the user a follow-up mode:

> "I've populated everything from the source. There are still N missing fields the file didn't cover. Want me to walk through them and fill them in?"

If they say yes:

1. **Enumerate the missing fields.** Use JS to find every input/select in the form that's currently empty and whose row-label the skill knows about (Priority Level, Date of Original Issuance, Maturity Date, etc.). Group them by column (class) so the user can answer in a natural order.
2. **Ask in batches, not one at a time.** Group related fields into a single `AskUserQuestion` call. For example:
   - Priority Level of Seniority for all Preferred classes at once (list each class with its currently-empty rank, offer 1–10 for each or "skip" if unknown).
   - Date of Original Issuance for all classes at once.
   - Dividend Rate for all classes at once.
3. **Fill and verify.** After each batch, use the same JS row-label + Y-position pattern (see `references/form_workflow.md`) to write the values into the form. Re-read the missing-fields badge and report the new count to the user.
4. **Handle the As Of date constraint.** If the user gives an issuance date later than the current As Of date, warn them and offer to update the As Of date (the max attribute on date inputs is driven by it).
5. **Stop when the user says stop or when the badge reaches 0.**

The user is always allowed to say "skip this one — I don't have that info yet." Fields marked skipped stay in the missing-fields count and the user can revisit later. Do not invent values.

Field-specific input hints:

- **Priority Level of Seniority**: 1–10 dropdown. 1 = most senior. Latest series usually senior; ask the user if unclear.
- **Date of Original Issuance / Maturity Date**: `<input type="date">`. Enter as YYYY-MM-DD. Bounded by the As Of date's `max` — see the form_workflow note.
- **Dividend / Interest Rate**: percentage, entered as a decimal (e.g. 0.08 for 8%). Its "Paid or accrued" (Paid/Accrued) and "Accrual Period" (Daily/Monthly/Quarterly/Semi-Annually/Annually) sub-dropdowns need to be set when the rate is non-zero.
- **Additional Liquidation Preferences**: dollar amount in millions on top of the standard 1x liquidation preference.
- **Threshold Vesting Type**: Price or Internal Rate of Return. Only applies when the class has performance-based vesting.

## What this skill does not do

- It does not invent priority-level orderings, issuance dates, dividend rates, or liquidation preferences. Those live in legal documents (term sheets, certs of designation), not in summary cap tables.
- It does not enter sensitive credentials, payment info, or sharing-permission changes — standard Cowork policy.

## Sharing this skill

This skill is portable. To hand it to a teammate, package it and share the `.skill` file, or point them at the CapUCalc Tools marketplace once it's hosted.
