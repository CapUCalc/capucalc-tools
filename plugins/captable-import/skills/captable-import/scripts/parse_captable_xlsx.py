#!/usr/bin/env python3
"""
Parse a Carta-style "Summary Cap Table" XLSX into the canonical class list
the captable-import skill expects.

Usage:
    python parse_captable_xlsx.py <path-to-xlsx>

Output (stdout JSON):
{
  "as_of": "<date string from header>",
  "classes": [
    {"type": "Common"|"Preferred"|"Notes"|"Options",
     "name": "<class name>",
     "shares": <int|null>,           # actual count, Issued and Outstanding
     "cash_raised": <float|null>     # actual USD
    },
    ...
  ],
  "totals": {
     "fully_diluted_shares": <int|null>,
     "cash_raised": <float|null>
  }
}

Robust to small variants in section labels and header text. For non-Carta
layouts, parse manually — see references/parsing.md.
"""

import json
import re
import sys
from pathlib import Path

try:
    import openpyxl
except ImportError:
    sys.stderr.write(
        "openpyxl is required. Install with: pip install openpyxl --break-system-packages\n"
    )
    sys.exit(2)


# Section heading -> canonical column type in CapUCalc
SECTION_TYPES = [
    (re.compile(r"common\s+stock\s+classes", re.I), "Common"),
    (re.compile(r"preferred\s+stock\s+classes", re.I), "Preferred"),
    (re.compile(r"convertibles?", re.I), "Notes"),
    (re.compile(r"stock\s+incentive\s+plan", re.I), "Options"),
]

# Rows to skip inside a section (subtotals, plan bookkeeping)
SKIP_NAME_PATTERNS = [
    re.compile(r"^\s*total\b", re.I),
    re.compile(r"shares\s+available", re.I),
    re.compile(r"rsas?\s+not\s+purchased", re.I),
    re.compile(r"options\s+and\s+rsus?\s+issued", re.I),
]


def find_summary_sheet(wb):
    """Return the worksheet most likely to be the summary cap table."""
    candidates = []
    for name in wb.sheetnames:
        score = 0
        lower = name.lower()
        if "summary" in lower:
            score += 10
        if "cap" in lower and "table" in lower:
            score += 5
        if "intermediate" in lower or "detailed" in lower:
            score -= 3
        candidates.append((score, name))
    candidates.sort(reverse=True)
    return wb[candidates[0][1]]


def find_header_row(ws):
    """Locate the row containing the column-header labels. Returns (row_idx, col_map)."""
    targets = {
        "shares_outstanding": [
            re.compile(r"issued\s+and\s+outstanding", re.I | re.S),
            re.compile(r"outstanding\s+shares", re.I),
        ],
        "fully_diluted": [re.compile(r"fully\s+diluted\s+shares", re.I)],
        "cash_raised": [
            re.compile(r"cash\s+raised", re.I),
            re.compile(r"funds?\s+raised", re.I),
            re.compile(r"capital\s+raised", re.I),
        ],
    }

    for row_idx in range(1, min(ws.max_row, 20) + 1):
        col_map = {"name": 1}
        found = {"shares_outstanding": False, "cash_raised": False}
        for col_idx in range(1, ws.max_column + 1):
            cell_val = ws.cell(row=row_idx, column=col_idx).value
            if not isinstance(cell_val, str):
                continue
            txt = cell_val.replace("\n", " ").strip()
            for key, pats in targets.items():
                for p in pats:
                    if p.search(txt):
                        col_map[key] = col_idx
                        if key in found:
                            found[key] = True
                        break
        if found["shares_outstanding"] and found["cash_raised"]:
            return row_idx, col_map
    raise RuntimeError("Could not locate header row with Shares Outstanding + Cash Raised columns.")


def detect_as_of(ws):
    """Pull an as-of date from the first ~5 rows of the sheet (string form)."""
    for row_idx in range(1, 6):
        for col_idx in range(1, ws.max_column + 1):
            v = ws.cell(row=row_idx, column=col_idx).value
            if isinstance(v, str):
                m = re.search(r"as\s+of\s+([0-9/.\-]+)", v, re.I)
                if m:
                    return m.group(1)
    return None


def parse_classes(ws, header_row, col_map):
    classes = []
    current_type = None
    totals = {"fully_diluted_shares": None, "cash_raised": None}

    name_col = col_map["name"]
    shares_col = col_map.get("shares_outstanding")
    fd_col = col_map.get("fully_diluted")
    cash_col = col_map.get("cash_raised")

    for row_idx in range(header_row + 1, ws.max_row + 1):
        name_val = ws.cell(row=row_idx, column=name_col).value
        if not isinstance(name_val, str):
            continue
        name_stripped = name_val.strip()
        if not name_stripped:
            continue

        # Section heading?
        new_type = None
        for pat, t in SECTION_TYPES:
            if pat.search(name_stripped):
                new_type = t
                break
        if new_type is not None:
            current_type = new_type
            continue

        # Grand totals row?
        if re.match(r"^\s*totals?\b", name_stripped, re.I):
            fd_val = ws.cell(row=row_idx, column=fd_col).value if fd_col else None
            cash_val = ws.cell(row=row_idx, column=cash_col).value if cash_col else None
            if isinstance(fd_val, (int, float)) and fd_val:
                totals["fully_diluted_shares"] = int(fd_val)
            if isinstance(cash_val, (int, float)) and cash_val:
                totals["cash_raised"] = float(cash_val)
            continue

        # Subtotals / plan housekeeping
        if any(p.search(name_stripped) for p in SKIP_NAME_PATTERNS):
            continue

        if current_type is None:
            continue

        shares_val = ws.cell(row=row_idx, column=shares_col).value if shares_col else None
        cash_val = ws.cell(row=row_idx, column=cash_col).value if cash_col else None

        shares_int = int(shares_val) if isinstance(shares_val, (int, float)) and shares_val else None
        cash_float = float(cash_val) if isinstance(cash_val, (int, float)) and cash_val else None

        if shares_int is None and cash_float is None:
            continue

        classes.append({
            "type": current_type,
            "name": name_stripped,
            "shares": shares_int,
            "cash_raised": cash_float,
        })

    return classes, totals


def main():
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: parse_captable_xlsx.py <path-to-xlsx>\n")
        sys.exit(2)
    path = Path(sys.argv[1])
    if not path.exists():
        sys.stderr.write(f"File not found: {path}\n")
        sys.exit(2)

    wb = openpyxl.load_workbook(path, data_only=True)
    ws = find_summary_sheet(wb)
    header_row, col_map = find_header_row(ws)
    as_of = detect_as_of(ws)
    classes, totals = parse_classes(ws, header_row, col_map)

    out = {
        "source_file": str(path),
        "sheet": ws.title,
        "as_of": as_of,
        "classes": classes,
        "totals": totals,
    }
    json.dump(out, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
