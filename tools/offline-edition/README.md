# Offline personal copies (for selling the notes, e.g. on Shopee)

Makes one HTML file per buyer from the live notes pages: it opens in any browser on a phone, tablet or laptop with no
internet, looks like the website (sidebar, topic menu, diagrams, embedded fonts) and includes the subject's past
papers. No password. Every copy shows the buyer's name and Paula's copyright: a banner at the top, a line under every
section heading, a faint diagonal watermark, the page title and the footer.

```bash
python3 tools/offline-edition/make_offline.py chemistry --buyer "Aisha Rahman" --order 2611220001 --out ~/orders
```

- `subject` = the page folder name without `igcse-` / `-notes` (chemistry, biology, physics, economics, business,
  accounting, english-writing-forms). All seven tested (Nov 2026). If `resources/igcse-<subject>-past-papers/` exists it is merged into the same file.
- `--out` must be outside this repo: buyer names must never be committed (the repo is public). The script refuses
  otherwise.
- Output name: `IGCSE-Chemistry-Notes-Aisha-Rahman-2611220001.html` (about 0.7–1 MB).
- The site search box is left out (it needs the website); everything else works offline.
- Top bar: **Home** (opens an About page inside the file, built from the live homepage by `about_page.py`), **Notes**
  and WhatsApp. No Resources, Marking or Shop links, and nothing in the copy mentions or links to the free website
  (the script stops if it finds a mention). The About page drops the marking card, the "past papers marked" badge,
  the "Free notes" subject links, the portfolio link and the "Get it marked" buttons (Business, Economics); photos are shrunk (copy is about 1.7 MB).
- The name is a deterrent, not a lock: anyone who edits HTML could remove it. Use the locked PDFs where stronger
  protection matters.

Fonts in `fonts/` are DM Sans and DM Mono (SIL Open Font License 1.1, `fonts/OFL.txt`), embedded in each copy.

## Order Maker (no tokens per order)

```bash
python3 tools/offline-edition/build_order_maker.py --out ~/Desktop
```

Builds `Order-Maker.html` (about 3 MB, all seven subjects): Paula opens it in her browser, picks the subject, types the
buyer's name and order number and clicks **Make copy**; the browser saves the personalised file. Works offline, nothing
is sent anywhere, and the result is byte-for-byte what `make_offline.py` would make (tested for all subjects with a
name containing quotes, &, <, %, ! and accents). It holds a master copy of each subject (`make_offline.py --master`,
placeholders `QQBUYERQQ` / `QQORDERQQ`), gzip-packed, with shared photos stored once. **Rebuild it after the notes change**
(the page shows the date it was built). Order number is required in the Order Maker.
