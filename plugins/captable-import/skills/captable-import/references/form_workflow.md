# CapUCalc Capital Table Editor — browser workflow

Detailed step-through for the form-fill phase, after the cap table has been parsed and converted to millions.

## Connect and navigate

```
mcp__claude-in-chrome__list_connected_browsers    # confirm a browser is paired
mcp__claude-in-chrome__select_browser(deviceId)   # if more than one
mcp__claude-in-chrome__tabs_context_mcp(createIfEmpty: true)
mcp__claude-in-chrome__navigate(url=<company URL>, tabId=<id>)
```

If `list_connected_browsers` returns an empty list, ask the user to install the Claude in Chrome extension, sign in, and Connect from the side panel. Do NOT fall back to scraping or curl — the page is auth-gated.

Company URL format: `https://app.capucalc.com/companies/<uuid>`. The user supplies the URL — don't hard-code it.

## Open or create the cap table

The company page's right column has a **Cap Tables** card listing existing cap tables, each with an **Open** button. Also a **"+ New"** button at the top of the card to create a new one.

To **open** an existing table: click Open. The editor opens in a full-page overlay.

To **create** a new one: click "+ New" → fill Name (required) and As Of Date (required) → Shares/Units and Currency (both default to Millions — keep them) → click "Create Cap Table". You land back on the company page; click Open on the newly-created row to enter the editor.

The editor's header shows:
- **"As Of" Date** — the effective date for this cap table.
- **Units** dropdown (Actual / Thousands / Millions / Billions) — confirm this is "Millions".
- **Currency** dropdown (Thousands / Millions / Billions) — confirm "Millions".

A default Common column appears with placeholder name "Common Stock" and shares "100". Overwrite this for the first common class rather than deleting.

## The "As Of" date affects issuance-date validation

**Important quirk.** All `<input type="date">` fields under "Date of Original Issuance" have a `max` attribute equal to the cap table's As Of date. If you try to set an issuance date later than the As Of date, the value fails silently — no error, the field just stays empty.

If the user wants an issuance date later than the current As Of date, change the As Of date first (`form_input` on the As Of Date field), then the issuance date will accept the later value.

## Identify the form structure

Call `read_page` once with `filter: "interactive"` and note the textbox refs in document order. The default cap table has:

- One name textbox (the placeholder Common name)
- One shares textbox (the placeholder "100")
- Plus Liquidation-Preferences and Dividend-Rate textboxes for that column
- An "Add column" button (the "+" at the top right)

After each new column is added, the document order grows. The most reliable way to grab the right ref for a newly added column is to call `read_page` immediately after the click and walk the new textboxes in order — refs shift as columns are inserted.

## Fill the first Common column

Overwrite the placeholder rather than deleting it:

```
form_input(ref=<name ref>, value="<first common class name>")
form_input(ref=<shares ref>, value="<shares in millions, 6 decimals>")
```

## Add each remaining class

For each remaining class:

1. Click the "+" button (`find` for "Add column plus button at top right").
2. From the popover, click the column-type button matching the class:
   - **Common** for common stock
   - **Preferred** for preferred series
   - **Notes** for convertible notes (the form does not say "Convertible Note")
   - **Options** for option-pool / RSU classes — only use when the user explicitly asks
3. Wait ~1 second for the column to render.
4. Use JS to identify the new column's inputs (rightmost x-position) and set name, shares, face value in one shot (see snippet below).
5. Dismiss the "New X added" toast before clicking "+" again. Toasts can occlude the "+" button; if the next click doesn't seem to open the menu, dismiss the toast (`find` for "Close toast button") and retry, or wait ~2s.

## Type-specific input rules

**Common**

- Name: from the source.
- Shares Outstanding (millions): from the source ÷ 1,000,000.
- Everything else: leave blank unless the source explicitly carries it.

**Preferred**

- Name: from the source.
- Shares Outstanding (millions): from the source ÷ 1,000,000.
- Face Value or Original Price per unit at Issuance: if the source has PPS ("Share Class Original Issue Price" or similar), use it directly. Otherwise compute cash raised (actual $) ÷ shares (actual). Enter as actual dollars per actual share, **not** millions per share. The form's `(calc)` Aggregate Funding row will then display = Face Value × Shares (M), which equals cash raised in millions.
- **Destination class**: in the "If convertible or exercisable, select destination class" dropdown, choose the appropriate Common class (usually the first Common entered). Required by the form.
- **Conversion or Exercise Price Per Share**: this sub-row appears after the destination is selected (may need to click the row's `>` expander or "Expand All" in the Type-column header). Enter the same Face Value here.
- Priority Level of Seniority, Date of Original Issuance, Additional Liquidation Preferences, Dividend Rate, vesting type: leave blank unless the user supplies them.

**Notes** (convertible note)

- Name: from the source.
- Aggregate Funding at Date of Issuance: cash raised ÷ 1,000,000. This row is directly editable for Notes columns (no Face Value × Shares calc).
- **Destination class** and **Conversion Price Per Share**: same pattern as Preferred. Pick the Common class as destination; enter the convertible's stated conversion price if known. Otherwise leave the conversion price blank and flag to the user.
- Date of Original Issuance, Maturity Date, Dividend / Interest Rate: leave blank unless the user supplies them.
- Notes columns have **no** Shares Outstanding row and **no** Face Value row.

**Options**

Only use when the user explicitly asks.

- **Destination class**: pick the Common class the options exercise into.
- **Exercise Price Per Share**: leave blank unless a strike price is available in the source (option grant agreements, plan summary).

## Fast batch entry via JavaScript

Walking through 5–10 columns with `form_input` + `find` for each cell is slow. Use these patterns instead.

### Set name, shares, face value on the rightmost (newly added) column

```javascript
(() => {
  const all = Array.from(document.querySelectorAll('input[type="text"], input:not([type])'));
  const g = {};
  all.forEach(i => { const x = Math.round(i.getBoundingClientRect().x/5)*5; (g[x]=g[x]||[]).push(i); });
  const xs = Object.keys(g).map(Number).sort((a,b) => a-b);
  const r = g[xs[xs.length-1]];
  r.sort((a,b) => a.getBoundingClientRect().y - b.getBoundingClientRect().y);
  const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
  const setV = (el, v) => {
    setter.call(el, v);
    el.dispatchEvent(new Event('input', {bubbles: true}));
    el.dispatchEvent(new Event('change', {bubbles: true}));
    el.dispatchEvent(new Event('blur', {bubbles: true}));
  };
  setV(r[0], '<class name>');
  setV(r[1], '<shares in millions>');
  setV(r[2], '<face value in $/share>');  // omit for classes without PPS
})();
```

### Set destination class to the first Common on every applicable column

```javascript
(() => {
  const selects = Array.from(document.querySelectorAll('select'));
  const setter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value').set;
  selects.forEach(s => {
    const commonOpt = Array.from(s.options).find(o => o.textContent.trim() === '<first common class name>');
    if (commonOpt) {
      setter.call(s, commonOpt.value);
      s.dispatchEvent(new Event('change', { bubbles: true }));
      s.dispatchEvent(new Event('input', { bubbles: true }));
    }
  });
})();
```

Replace `'<first common class name>'` with the actual textContent of the Common option, not the UUID.

### Set Conversion Price for every Preferred column by row label

```javascript
(() => {
  const label = Array.from(document.querySelectorAll('*'))
    .find(el => el.textContent && el.textContent.trim() === 'Conversion or Exercise Price Per Share' && el.children.length === 0);
  const y = label.getBoundingClientRect().y;
  const inputs = Array.from(document.querySelectorAll('input[type="text"], input[type="number"], input:not([type])'))
    .filter(i => Math.abs(i.getBoundingClientRect().y - y) <= 12)
    .sort((a, b) => a.getBoundingClientRect().x - b.getBoundingClientRect().x);
  const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
  const values = ['<val for col1>', '<val for col2>', '<val for col3>'];  // left-to-right per Preferred column
  inputs.forEach((inp, i) => {
    if (i < values.length && values[i]) {
      setter.call(inp, values[i]);
      inp.dispatchEvent(new Event('input', { bubbles: true }));
      inp.dispatchEvent(new Event('change', { bubbles: true }));
      inp.dispatchEvent(new Event('blur', { bubbles: true }));
    }
  });
})();
```

This label → Y-position → left-to-right inputs pattern works for any row that has one input per column: Face Value, Conversion Price, Additional Liquidation Preferences, Dividend Rate, etc.

### Set Date of Original Issuance (respecting the As Of max)

```javascript
(() => {
  // Change As Of date first (via form_input on the As Of Date field)
  // if the issuance dates you need are later than the current As Of.
  const label = Array.from(document.querySelectorAll('*'))
    .find(el => el.textContent && el.textContent.trim() === 'Date of Original Issuance' && el.children.length === 0);
  const y = label.getBoundingClientRect().y;
  const dateInputs = Array.from(document.querySelectorAll('input[type="date"]'))
    .filter(i => Math.abs(i.getBoundingClientRect().y - y) <= 12)
    .sort((a, b) => a.getBoundingClientRect().x - b.getBoundingClientRect().x);
  const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
  // Set all issuance dates to 2025-02-15
  dateInputs.forEach(el => {
    setter.call(el, '2025-02-15');
    el.dispatchEvent(new Event('input', {bubbles: true}));
    el.dispatchEvent(new Event('change', {bubbles: true}));
    el.dispatchEvent(new Event('blur', {bubbles: true}));
  });
})();
```

If the value doesn't stick, inspect `el.getAttribute('max')` — it's probably before your target date and you need to update the As Of date first.

## Verify before handing off

Run a JS read of all text inputs:

```javascript
(() => {
  const all = Array.from(document.querySelectorAll('input[type="text"], input:not([type])'));
  const g = {};
  all.forEach(i => { const x = Math.round(i.getBoundingClientRect().x/5)*5; (g[x]=g[x]||[]).push(i); });
  const xs = Object.keys(g).map(Number).sort((a,b) => a-b);
  return xs.map(x => {
    const col = g[x];
    col.sort((a,b) => a.getBoundingClientRect().y - b.getBoundingClientRect().y);
    return col.map(i => i.value).filter(v => v !== '');
  });
})();
```

Also grab the missing-fields badge:

```javascript
Array.from(document.querySelectorAll('span, div'))
  .find(el => {
    const t = (el.textContent || '').trim();
    return /^\d+\s*missing/i.test(t) && t.length < 50;
  })?.textContent.trim();
```

Then summarize back to the user as a small Markdown table. Note that `(calc)` aggregate values are derived from Face Value × Shares and are read-only.

## Common failure modes

- **The "+" click does nothing.** A toast is overlapping the button. Take a screenshot to confirm, dismiss any toasts (`find` for "Close toast button"), and click "+" again.
- **`form_input` says "previous: <X>" with the same value as before.** Ref points to the *old* column's textbox. Refs from before the column was added still resolve to the old column.
- **Aggregate Funding shows a wrong number for Preferred.** Face Value was entered in the wrong unit. It should be **actual dollars per actual share**, not millions per share. Recompute: cash raised (actual $) ÷ shares (actual count).
- **Date inputs won't accept a value.** Check the `max` attribute — it defaults to the cap table's As Of date. Update the As Of date first if you need a later issuance date.
- **Series shows up as wrong type.** Delete the column with the trash icon and re-add via "+" → correct type. Type can't be changed after creation.
