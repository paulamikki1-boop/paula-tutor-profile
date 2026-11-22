# Offline personal copies (for selling the notes, e.g. on Shopee)

Makes one HTML file per buyer from the live notes pages: it opens in any browser on a phone, tablet or laptop with no
internet, looks like the website (sidebar, topic menu, diagrams, embedded fonts) and includes the subject's past
papers. No password. Every copy shows the buyer's name and Paula's copyright: a banner at the top, a line under every
section heading, a faint diagonal watermark, the page title and the footer.

```bash
python3 tools/offline-edition/make_offline.py chemistry --buyer "Aisha Rahman" --order 2611220001 --out ~/orders
```

- `subject` = the page folder name without `igcse-` / `-notes` (chemistry, biology, physics, economics, business,
  accounting). If `resources/igcse-<subject>-past-papers/` exists it is merged into the same file.
- `--out` must be outside this repo: buyer names must never be committed (the repo is public). The script refuses
  otherwise.
- Output name: `IGCSE-Chemistry-Notes-Aisha-Rahman-2611220001.html` (about 0.7–1 MB).
- The site search box is left out (it needs the website); everything else works offline.
- The name is a deterrent, not a lock: anyone who edits HTML could remove it. Use the locked PDFs where stronger
  protection matters.

Fonts in `fonts/` are DM Sans and DM Mono (SIL Open Font License 1.1, `fonts/OFL.txt`), embedded in each copy.
