# Launch kit — LinkedIn post + demo plan

## 60-second Loom demo — script and shot list

**Total time:** 60 seconds. Aim tight — LinkedIn autoplay caps around 90 seconds before drop-off spikes.

### Setup before recording

1. Open Loom (or QuickTime / OBS if you prefer).
2. Have three things ready on your screen:
   - A representative cap table file open in Excel (use a realistic-looking demo file, not real client data — anonymize company names and round the numbers).
   - Chrome open to an empty CapUCalc cap table page.
   - Cowork with a fresh chat.
3. Close every other window. Turn off notifications.
4. Camera on, small circle in the corner — LinkedIn engagement is measurably higher with a talking-head bubble.

### Script (aim for tight cuts, ~5–8 seconds per scene)

**[00:00 – 00:05] Hook — talking head**
"If you build cap tables in CapUCalc, this saves you an hour every time."

**[00:05 – 00:15] Problem — cut to the Excel file, then the empty CapUCalc form**
"You've got the cap table in Excel. You need it in CapUCalc. Copy-paste, one class at a time, converting units. Ten preferred series takes forever."

**[00:15 – 00:25] Solution — cut to Cowork, type the prompt live**
"Now I just say — 'load this cap table into the CapUCalc page I have open' — and hit enter."

**[00:25 – 00:50] Show it working — screen recording, sped up 2–3x**
Silent or with light music. Watch as Cowork:
- Opens the file
- Parses the classes
- Fills each column in the CapUCalc form
- Sets destination class + conversion price

Overlay a subtle counter showing "10 classes in 45 seconds" if you can.

**[00:50 – 00:60] Call to action — talking head**
"Free and open source. Install link in the comments. Try it — takes 2 minutes to set up."

### What to keep out of the demo

- Real client data or numbers.
- Any error messages or retries — record until you get a clean run.
- Screen text smaller than 24pt — nobody reads small text on LinkedIn mobile.
- Your Chrome bookmarks bar. Toggle it off (Ctrl+Shift+B).

### Where to host

- **Loom** — fastest, free tier is fine, generates an embeddable link.
- **YouTube unlisted** — better if you want to embed on the CapUCalc website too.
- **Native LinkedIn video upload** — highest reach; upload the MP4 directly. Recommended.

---

## LinkedIn post — personal (from Cary Potter)

> Every quarter I load client cap tables into CapUCalc — ten preferred classes, unit conversions, convertible destinations, exercise prices. It used to eat most of a morning.
>
> This week I built a Claude skill that does it in about a minute.
>
> Drop in the xlsx from Carta or a term sheet. Say "load this into the cap table I have open." It parses the source, converts to millions, computes per-share face values, adds each column with the right type (common / preferred / notes / options), and even fills in the destination class + conversion price for convertibles. Anything the source doesn't cover (priority level, dates of issuance) it flags and asks you about — no invented values.
>
> Free and open source. Works in Cowork or Claude Code with the Claude in Chrome extension. Install:
>
> ```
> /plugin marketplace add github:capucalc/capucalc-tools
> /plugin install captable-import@capucalc-tools
> ```
>
> Or grab the single-file .skill from the Releases page.
>
> Repo (with docs + demo): github.com/capucalc/capucalc-tools
>
> Built with Anthropic's Claude Skills + Claude in Chrome. If you work in valuation, finance, or accounting and touch cap tables regularly — worth 5 minutes of your time.
>
> Feedback and pull requests welcome.
>
> #CapTable #Valuation #Finance #Accounting #Claude #Automation

**Personal-post tips:**
- Post between 8–10am on a **Tuesday or Wednesday** for the highest B2B reach. Avoid Fridays and weekends.
- Tag CapUCalc's LinkedIn page in the first comment (not the post itself — LinkedIn slightly deprioritizes posts with brand tags).
- If you have a Loom, upload it as native LinkedIn video — links to Loom get 40–60% less reach than a native video.
- Reply to every comment for the first 2 hours. That's when LinkedIn's algorithm decides whether to push the post further.

---

## LinkedIn post — CapUCalc company reshare

Wait ~2 hours after Cary's post, then reshare from the CapUCalc company page with this caption:

> Cary Potter just released `captable-import` — a free, open-source Claude skill that takes an xlsx cap table and populates CapUCalc in about a minute.
>
> If your team is spending mornings transcribing Carta exports, this cuts that to a coffee break.
>
> Install: `/plugin marketplace add github:capucalc/capucalc-tools`
>
> Repo: github.com/capucalc/capucalc-tools

**Company-post tips:**
- Reshare, don't repost. LinkedIn's algorithm rewards resharing your team's content much more than reposting a new version.
- Add one line of value on top of the reshare (like above). Empty reshares underperform.
- Have 2–3 CapUCalc teammates like/comment on the company reshare within the first hour.

---

## Suggested first comment (both posts)

Direct install links get scrubbed from post bodies by LinkedIn's link previewer sometimes, so put the important stuff in the first comment:

> **Direct install (Cowork / Claude Code):**
> `/plugin marketplace add github:capucalc/capucalc-tools`
>
> **Single-file .skill download:** [Releases page URL]
>
> **Docs + workflow reference:** [repo README URL]
>
> **Loom demo:** [Loom URL]

Pin this comment.

---

## Follow-up posts (2–4 weeks after launch)

If the launch post gets traction, plan follow-ups. Ideas:

- **Week 2:** "Here's what surprised me about the first 100 installs" — usage patterns, funniest edge case, one improvement based on feedback.
- **Week 4:** "The 3 CapUCalc quirks this skill catches that you'd otherwise miss" — the As-Of-Date max, the Face Value units convention, the calc-driven Aggregate. Teaches something useful, reinforces the tool.
- **Feature launch:** whenever you ship the next skill in the marketplace, announce it the same way.

Recurring content beats a single launch. Even one thoughtful post a month keeps CapUCalc visible in your target audience's feed.
