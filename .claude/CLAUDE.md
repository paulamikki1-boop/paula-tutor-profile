# Paula's tutor website — project notes for Claude

Paula is an IGCSE/GCSE/A Level tutor in Kuala Lumpur (Cambridge & Edexcel). This repo is her static website.
Owner prefers: changes merged straight to `main` via a PR after browser testing; plain-English summaries; teen-appropriate
(not childish) design for study materials; never copy third-party notes (Save My Exams, r/IGCSE guides, past papers) —
use them only as a topic checklist and write original content.

## Site
- Live: https://paulamikki1-boop.github.io/paula-tutor-profile/ (GitHub Pages, project subpath → **all internal links must be
  relative**; canonical/og/sitemap URLs absolute). No build step; plain HTML/CSS/JS.
- Brand: navy `#0a1628`, blue `#1e3a5f`/`#2a5080`, accent `#4a90d9`, sky `#e8f0fe`; fonts Cormorant Garamond (headings) + DM Sans.
- Contact: WhatsApp +60 10-368 6902 (`wa.me/60103686902`), Facebook https://www.facebook.com/paulamikkitutor
- Google Business Profile: "Paula IGCSE & A-level Tuition" (Tutoring service).

## Pages
- `index.html` — homepage (hero photo embedded as base64 WebP, About Me boxes, subject cards linking to notes,
  mobile Menu button, Facebook + WhatsApp CTAs, OG preview image `assets/og-image.jpg`).
- `resources/index.html` — resources hub: "Search all notes" box, subject/level filters, cards.
- Notes pages (sidebar + sections layout, `showSection()` + URL hash per section):
  - `resources/igcse-english-writing-forms/` (Cambridge 0500)
  - `resources/igcse-biology-notes/` (0610, 2026–2028, 21 topics, inline SVG diagrams in PDFs only)
  - `resources/igcse-chemistry-notes/` (0620, 2026–2028, 12 topics)
  - `resources/igcse-economics-notes/` (0455 NEW syllabus 2027–2029: exam technique, 6 topics, 37 model answers, 12 SVG diagrams)
  - `resources/igcse-accounting-notes/` (0452 NEW syllabus 2027–2029: exam technique, 7 topics, 30 worked examples;
    `table.ledger` / `table.statement` layouts, `ledger colsN` adds the Dr/Cr divider)
  - Older stubs: chemistry past-paper technique, A-level biology definitions, physics formula sheet, economics essay guide.
- `marking/` — paid past-paper marking page: full past papers (Chem/Phys/Bio/Maths) RM10–30 per paper, cheaper in batches;
  questions RM10–20 / essays RM20–40 (Business/Econ/English); 48-hour turnaround; form opens WhatsApp prefilled.
  Accounting not yet listed (owner to decide). Economics model answers have "Get it marked" links that prefill the form.
- Search: `resources/search.js` + `resources/search-index.json`. **Rebuild after editing notes:** `python3 tools/build-search-index.py`.
  New notes page → add to `PAGES` in that script and include `<script src="../search.js"></script>`.
- `sitemap.xml`, `DEPLOY.md` (structure + search instructions).

## Conventions for new notes pages
Same component classes as existing notes pages: `section-header/form-badge/purpose`, `structure-card/step`, `conventions/convention-item`,
`table-wrap`, `example-block/ex-label`, `tip-box`, `mistake-box`, `checklist`, `key-term` (Supplement tag for Bio/Chem only),
`figure.diagram` with inline SVG. Add: homepage subject card link (`a.subject-card` + "Free notes →"), hub card, sitemap entry,
DEPLOY.md line, search index entry.

## PDFs (built outside the repo)
Sold as two products per subject, delivered as zips to the owner (not in this repo):
- **Compact Revision Notes** (one PDF per subject, condensed, each topic on a new page) and
- **Detailed Notes** (one PDF per topic, spacious layout, own cover).
- Done: Biology, Chemistry, Accounting (compact + detailed); Economics (compact only).
- Each has an unlocked master copy and a locked "FOR SELLING" copy: AES-256 password to open, print allowed, copy/edit blocked,
  faint "© Paula · IGCSE Tutor" diagonal watermark + "For personal use only" line. Passwords are kept privately by the owner —
  never commit them.
- Built with Playwright/Chromium HTML→PDF (`page.pdf`, A4) + PyMuPDF for page numbers, watermark and encryption. The build
  scripts lived in a temporary session folder and are NOT in the repo; recreate from the notes pages' HTML if needed.

## Open items / ideas
- Owner to confirm dates: tutoring since 2020 vs 2021; A Level certificate shows June 2022 series.
- Exam Technique sections for Economics/Accounting describe 2027 papers generally — check against syllabus PDFs.
- Possible next: Physics/Maths/Business notes, Economics detailed PDFs, Payhip "Buy PDF" buttons, custom domain
  (Cloudflare Pages or Netlify), Accounting on the marking page, store name (top picks: "Notes by Paula", "A* Starts Here").
