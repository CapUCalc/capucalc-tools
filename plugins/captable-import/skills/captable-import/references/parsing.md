# Parsing the source cap table

The skill needs, per equity class: **type** (Common / Preferred / Notes / Options), **name**, **shares outstanding (actual)**, and one of {**cash raised (actual)**, **price per share (actual $/share)**}. A **totals row** for verification is also useful.

## XLSX cap tables (Carta-style "Summary Cap Table")

The most common shape. Indicators:

- Workbook contains a sheet named "Summary Cap Table" (sometimes alongside Intermediate / Detailed).
- Column headers around row 5: `Shares Authorized`, `Shares Issued and Outstanding`, `Fully Diluted Shares`, `Fully Diluted Ownership`, `Cash Raised (USD)`.
- Sections labeled in column A: "Common Stock classes", "Preferred Stock classes", "Convertibles", plus stock-incentive-plan sections near the bottom.
- Each class row: name in column A, shares in B/C/D, ownership in E, cash raised in F.

### Bundled parser

For Carta-style XLSX files:

```bash
python "scripts/parse_captable_xlsx.py" "<absolute-path-to-xlsx>"
```

Emits JSON like:

```json
{
  "as_of": "11/30/2025",
  "classes": [
    {"type": "Common",     "name": "Common (CS) Stock",  "shares": 19000000, "cash_raised": 1900.0},
    {"type": "Preferred",  "name": "Series A Preferred", "shares": 5052131,  "cash_raised": 3770000.0}
  ]
}
```

Use `Issued and Outstanding` (Carta column C) for `shares` — that's what the form's "Shares Outstanding (millions)" expects.

## Non-Carta / sparse spreadsheet layouts

Some cap tables are just a compact summary — a header row of class names, a totals row, a price-per-share row, and everything else empty. Example seen in the field:

```
Row 4:  Share type | Common | A | B | C | D | E2 | F | G1 | G3 | H | Options | Warrants
Row 43: Total      | 13,031,978.75 | 16,391,399 | 11,343,504 | ...
Row 44: PPS        |               | 0.56371    | 1.3223428  | ...
```

For this layout:
- Column headers are single-letter or short-letter class identifiers (A, B, E2, G1, etc.). These are **all Preferred series** unless the header says "Common", "Options", or "Warrants".
- Totals in Row N are per-class share counts (actual). Convert to millions ÷ 1,000,000.
- Row N+1 has price per share (PPS) — this **is** the Face Value / Original Issue Price for those series.
- Later series (e.g. F, G1, G3, H) may have blank PPS. Leave Face Value blank and note it to the user.
- Row headers like "DA E2" typically encode series-specific dividend/accrual rates — surface to the user; skill doesn't currently enter these.

## PDF cap tables

Use the `anthropic-skills:pdf` skill to extract text first, then parse.

Common PDF shapes:

- **Carta PDF export** — same Summary Cap Table sheet rendered to PDF. Same row/column structure as the XLSX. Extracted text usually preserves column order.
- **Term-sheet appendix** — one-page summary at issuance. Watch fully-diluted vs. issued-and-outstanding — prefer issued-and-outstanding.
- **Founder-built spreadsheet printed to PDF** — inconsistent. Confirm columns with the user before populating.

After extracting, build the same JSON shape the XLSX parser emits and proceed identically.

## Sanity checks before populating

Before opening the browser:

1. Sum all `shares` for Common + Preferred. Should match the source's "Total issued and outstanding" or fully-diluted total.
2. Sum all `cash_raised` (if present) across all classes. Should match the source's "Totals" row.
3. If either is off by more than rounding error, flag it to the user before continuing.

## Unusual share counts

Some cap tables have very large share counts (hundreds of millions or billions of shares) — this happens when a company has split heavily, denominated in fractional shares, or is in a non-USD context. Enter the numbers as-is (in millions) — don't second-guess.

## Example — Carta layout

Source (actual):

| type | name | shares | cash_raised |
|---|---|---:|---:|
| Common | Common (CS) Stock | 19,000,000 | $1,900.00 |
| Preferred | Series A Preferred (PA) Stock | 5,052,131 | $3,770,000.00 |
| Preferred | Series B Preferred (B) Stock | 1,193,385 | $11,910,000.00 |
| Notes | CN Notes (CN) | — | $1,850,000.00 |

After conversion:

| type | name | Shares (M) | Face Value/sh | Aggregate (M) |
|---|---|---:|---:|---:|
| Common | Common (CS) Stock | 19.000000 | — | — |
| Preferred | Series A Preferred (PA) Stock | 5.052131 | $0.74622 | $3.77 (calc) |
| Preferred | Series B Preferred (B) Stock | 1.193385 | $9.98 | $11.91 (calc) |
| Notes | CN Notes (CN) | — | — | $1.85 |
