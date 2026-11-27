# Paula's tutor website — project notes for Claude

Paula is an IGCSE/GCSE/A Level tutor in Kuala Lumpur (Cambridge & Edexcel). This repo is her static website.
Owner prefers: changes merged straight to `main` via a PR after browser testing; plain-English summaries; teen-appropriate
(not childish) design for study materials; never copy third-party notes (Save My Exams, r/IGCSE guides, past papers) —
use them only as a topic checklist and write original content.
  Exception (owner-approved): topical past-paper sections may quote Cambridge question wording exactly, cited with the full
  reference (e.g. `0455/22/M/J/25 Q2(d)`) and a UCLES credit line; the model answers must still be original.

**Every task: load the skill `fable-playbook` (`.claude/skills/fable-playbook/SKILL.md`) before the first edit or command** —
it sets how to plan, split the work into steps, check the result in a browser and report back.

## Site
- Live: https://paulamikki1-boop.github.io/paula-tutor-profile/ (GitHub Pages, project subpath → **all internal links must be
  relative**; canonical/og/sitemap URLs absolute). No build step; plain HTML/CSS/JS.
- Brand: navy `#0a1628`, blue `#1e3a5f`, accent `#4a90d9`, sky `#e8f0fe`. Whole site uses the "hub" style since Nov 2026 (DM Sans + DM Mono,
  rounded cards; see skill `.claude/skills/paula-web-design/`). The homepage has its own full stylesheet; every other page
  gets the look from a shared override layer at the end of its `<style>` block. **After adding a page or changing the
  layer, run** `python3 .claude/skills/paula-web-design/scripts/apply_hub_layer.py`.
- Contact: WhatsApp +60 10-368 6902 (`wa.me/60103686902`), Facebook https://www.facebook.com/paulamikkitutor
- Google Business Profile: "Paula IGCSE & A-level Tuition" (Tutoring service).

## Pages
- `index.html` — homepage (hero photo embedded as base64 WebP, About Me boxes, subject cards linking to notes,
  mobile Menu button, Facebook + WhatsApp CTAs, OG preview image `assets/og-image.jpg`).
- `resources/index.html` — resources hub: "Search all notes" box, subject/level filters, cards.
- Notes pages (sidebar + sections layout, `showSection()` + URL hash per section):
  - `resources/igcse-english-writing-forms/` (Cambridge 0500)
  - `resources/igcse-biology-notes/` (0610, 2026–2028 syllabus **version 3**, Aug 2026, uploaded by the owner; 21 topics in
    syllabus order: **Topic 20 = Human influences (id `human-influences`, past papers `pp-unit21`, h3s `pp-21-x` labelled
    20.x), Topic 21 = Biotechnology (id `biotechnology`, `pp-unit20`, `pp-20-x` labelled 21.x)** — ids kept from the old
    order so links still work). "Exam Guide" `#exam-guide` first in the sidebar (papers/timing from the syllabus: P1/P2 45 min
    40 MCQ 30%, P3/P4 1h15 80 marks 50%, P5 1h15 / P6 1h 40 marks 20%; AO1 50 / AO2 30 / AO3 20; the **14** syllabus command
    words; key calculations; practical contexts; table/graph/drawing rules). "Illustrated Examples" `#illustrated` (10 original
    worked examples with SVGs, `st-illustrated-1`…`10`). Full QC + syllabus alignment done Nov 2026 (every Core/Supplement
    bullet covered and labelled, practical methods added, off-syllabus items tagged `key-term bg-term` "Background" /
    `.background-note`, e.g. deficiency symptoms, 2,4-D, loop of Henle, fitness).
    "Topical Past Papers" sidebar group: `#pp-unit1`…`#pp-unit21` (**290 questions** across 39 sub-topics, e.g. `h3#pp-14-3`):
    real 0610 Paper 4 (41/42/43) questions 2020–2026 (67 from May/June 2026 added Nov 2026), verbatim + cited, original
    answers, every answer checked against the mark schemes (papers from pastpapers.papacambridge.com; no examiner reports exist
    there for M/J 2020, M/J 2024, O/N 2023–2025 or M/J 2026, so those notes rely on the mark scheme only). 62 original
    "Revision diagram (not required by the question)" SVGs in the answers. Past-paper h3s keep the older grouped sub-topic
    names (e.g. 7.3 "Chemical Digestion and Absorption" spans syllabus 7.4–7.5). No "Get it marked" links. Timing tip says
    "under 1 minute per mark". Sidebar sub-topics as on Chemistry (arrow toggle, hover flyout, scroll-spy; same JS): notes h3
    ids `st-<section>-<n>` (e.g. `#st-transport-animals-2`), past-paper units list their `pp-` h3s. Figures with viewBox ≥ 440
    wide get `.diagram.wide`. Don't re-run the topical-past-papers renderer on this page: it would rebuild the sections and
    drop the diagrams and fixes (new questions were inserted with a one-off script instead).
  - `resources/igcse-chemistry-notes/` (0620, 2026–2028, 12 topics) plus "Exam Guide" section `#exam-guide` (papers/timing/
    command words/key relationships, from the official 2026–2028 syllabus **version 2**, Aug 2026: P1/P2 45 min 40 MCQ 30%,
    P3/P4 1h15 80 marks 50%, P5 1h15 / P6 1h 40 marks 20%) and "Illustrated Examples" `#illustrated` (10 original worked
    examples with SVG diagrams). Full QC + syllabus alignment done Nov 2026 (every calculation re-worked, every Core/Supplement
    bullet covered and labelled, off-syllabus items tagged `key-term bg-term` "Background" or `.background-note`).
    Sidebar sub-topics as on Accounting (arrow toggle, hover flyout, scroll-spy): notes h3 ids `st-<section>-<n>` (e.g.
    `#st-stoichiometry-5`). Each topic has a `a.pp-link-box` under its header and one at the end (`.end`) linking to its
    past-paper unit; the sidebar has a "Topical Past Papers" box (styled `.pdf-promo`) linking to the separate page.
    Old `#pp-…` hashes on the notes page are forwarded by JS to the past-papers page (owner asked for separate pages, Nov 2026).
  - `resources/igcse-chemistry-past-papers/` — **separate page** for Chemistry's Topical Past Papers: `#pp-unit1`…`#pp-unit12`
    (168 questions across 29 grouped sub-topics, e.g. `h3#pp-2-5` = 2.5–2.7 structures; sub-topic menu reuses the `pp-x-y`
    ids). Real 0620 Paper 4 (41/42/43) questions 2020–2025, verbatim + cited, original answers, 44 original SVG diagrams.
    Each unit starts with a "Revise the notes first" `a.pp-link-box` back to `../igcse-chemistry-notes/#<topic>`; sidebar has a
    "← Back to the notes" box. Same CSS/JS as the notes page. No "Get it marked" links (marking page only offers
    full-paper marking for Chemistry). Economics and Physics were split the same way; Biology, Business and Accounting still keep past papers inside their notes page. Figures sit in `figure.diagram`; `.example-block`
    text is italic, so the page sets `.diagram { font-style: normal }`.
  - `resources/igcse-economics-notes/` (0455 NEW syllabus 2027–2029, official syllabus PDF from cambridgeinternational.org
    `/Images/718148-2027-2029-syllabus.pdf`; 2027 specimen Paper 2 + mark scheme `/Images/718809-…`, `/Images/718805-…`).
    Exam Technique (P1 40 MCQ 1h 30%; P2 2h 80 marks 70%: Section A Q1 (a)–(f) 20 marks, Section B three from four, 2/4/6/8;
    only Section B (d) Discuss [8] is levels-marked (L3 6–8), Section A (f) Discuss [6] point-marked max 4 per side; AO weights;
    the 9 syllabus command words), 6 topics whose h3s are exactly the syllabus sub-topics (1.1–6.4, PED = 2.6, PES = 2.7),
    37 model answers, "Illustrated Examples" `#illustrated` (12 original worked examples, two per topic, SVGs drawn to scale).
    Full QC + syllabus alignment done Nov 2026 (every calculation re-worked, every syllabus bullet covered, independently
    reviewed); off-syllabus items tagged `key-term bg-term` "Background" / `.background-note` (micro vs macro, role of
    government, mobility of all factors, fixed exchange rates, pyramids/dependency ratio, etc.). 113 SVG diagrams in all;
    figures with viewBox ≥ 430 wide get `.diagram.wide`. Sidebar sub-topics as on Chemistry/Physics (arrow toggle, hover
    flyout, scroll-spy; same JS): notes h3 ids `st-<section>-<n>` (e.g. `#st-allocation-of-resources-6`), past-paper units
    list their `pp-` h3s.
    Each topic has `a.pp-link-box`es (under its header and `.end`) to its past-paper unit; sidebar `.side-link` box to the
    past-papers page; old `#pp-…` hashes forward there (split Nov 2026 with skill `split-past-papers`).
  - `resources/igcse-economics-past-papers/` — **separate page** for Economics' Topical Past Papers: `#pp-unit1`…`#pp-unit6`
    (187 questions across 38 sub-topics, `h3#pp-2-3` etc.) and `#pp-ped` (11 questions). Each unit opens with a "Revise the
    notes first" box back to the notes; same CSS/JS as the notes page. All real 0455 Paper 2 questions 2020–2025, verbatim + cited (`span.pp-ref`), with
    original exemplar answers; 68 SVG diagrams (60 added Nov 2026 as "Revision diagram (not required by the question)",
    reviewed). Headings keep the old (pre-2027) sub-topic numbers the papers were set on; a `.syl-tag` beside each heading
    gives the 2027–2029 number where it differs. Papers/mark schemes/examiner reports came from pastpapers.papacambridge.com.
    Paper 1 (MCQ) not covered. "Get it marked" links → marking page.
  - `resources/igcse-accounting-notes/` (0452 NEW syllabus 2027–2029: exam technique, 7 topics, 30 worked examples + "Illustrated Examples" section `#illustrated` (8 original examples, 11 inline SVG diagrams) + "Past-Paper Examples" sidebar group `#pp-t1`…`#pp-t7` (one section per syllabus topic; 55 real 0452 Paper 2 questions 2023–2026 (15 from F/M and M/J 2026 added Nov 2026; M/J 2026 Papers 21 and 23 are identical, cited as /21/), verbatim + cited, 83 original SVG diagrams, original model answers; figures checked against the mark schemes, new ones independently reviewed. Headings are numbered "Past paper 1…55" in page order; to add questions, insert blocks before each section's `p.pp-credit` and renumber. Note: `extract_questions.py` mislabels some Paper 2 question numbers (e.g. M/J/25 Jasmine is Q3 not Q4), so always take numbers from the printed paper; some column headings that wrap across lines in the PDF are not quoted verbatim, and a few advice answers use extra figures worked out from the paper, labelled as such). Full QC pass done Nov 2026 (every calculation re-worked, explanations corrected), then aligned with the official 2027–2029 syllabus PDF (owner uploaded it): syllabus terminology in the original notes (statement of profit or loss, allowance for irrecoverable debts, owner’s equity, uncredited deposits, statement of changes in equity), the ten syllabus ratios with syllabus formulas (ROCE = profit before interest ÷ capital employed), Paper 1 40 MCQs/1h30/30% and Paper 2 five 20-mark questions/1h45/70%, the 16 syllabus command words, and every topic bullet covered (incl. revaluation method, 7.3 data storage). Past-paper answers keep the older papers’ wording, with a note;
    `table.ledger` / `table.statement` layouts, `ledger colsN` adds the Dr/Cr divider; sidebar sub-topics: every sidebar item (7 notes topics, 4 worked-answer sections, Illustrated, the 7 past-paper sections) has an arrow toggle + `.subnav` list of its h3s (ids `st-<section>-<n>`, e.g. `#st-procedures-2`, `#st-pp-t5-15` deep-link; past-paper/answer h3 ids go by position, so they shift if blocks are inserted), inline list for the open topic, hover flyout on desktop, scroll-spy highlight. `tools/build-search-index.py` links search hits to `st-` anchors)
  - `resources/igcse-business-notes/` (0450: exam technique, 6 topics (1.1–6.3), Key Formulas page, 3 model-answer sections with
    original cases — Siti's Batik Studio, Arjun's FixIt, KL Scoot, BrewHaus — 4 SVG diagrams; notes also flag Edexcel 4BS1 / OxfordAQA 9225)
    plus "Topical Past Papers" sidebar group: `#pp-unit1`…`#pp-unit6` (148 questions across 25 sub-topics 1.1–6.3, `h3#pp-3-3` etc.).
    Real 0450 Paper 1 (11/12/13) and Paper 2 case-study (21/22/23, stimulus quoted from the insert) questions 2020–2025,
    verbatim + cited, original answers, most sub-topics include a 6-mark (e) or 12-mark (b); "Get it marked" links → marking page.
  - `resources/igcse-physics-notes/` (0625, 2026–2028, official syllabus **version 2**, Dec 2025; all six topics, one section per
    sub-topic: 1.1–1.8 Motion/forces/energy (ids `physical-quantities`, `motion`, `mass-weight`, `density`, `forces`, `turning-effect`,
    `momentum`, `energy-work-power`, `energy-resources`, `pressure`), 2.1–2.3 Thermal, 3.1–3.4 Waves, 4.1–4.5 Electricity & magnetism
    (`magnetism`, `electric-charge`, `current-voltage-resistance`, `electrical-energy`, `circuits`, `circuit-components`,
    `practical-electricity` = syllabus 4.4 "Electrical safety", `em-induction`, `motor-effect`, `transformer`), 5.1–5.2 Nuclear,
    6.1–6.2 Space; plus "Exam Guide" `#exam-guide` (papers/timing/15 syllabus command words/symbols+units/practical skills, all
    from the syllabus: P1/P2 45 min 40 MCQ 30%, P3/P4 1h15 80 marks 50%, P5 1h15 / P6 1h 40 marks 20%), "Key Equations"
    (every equation in topics 1–6, Supplement-tagged) and "Illustrated Examples" `#illustrated` (10 original worked examples with
    SVGs); landing section is 1.1. Full QC + syllabus alignment done Nov 2026 (every calculation re-worked, every Core/Supplement
    bullet covered and labelled; off-syllabus items tagged `key-term bg-term` "Background" / `.background-note`). 52 notes SVGs;
    `.formula-box`, `.nuclide` (A/Z stacked) classes; figures with viewBox ≥ 440 wide get `.diagram.wide` (scroll inside the figure
    on phones so labels stay legible). Sidebar sub-topics as on Chemistry (arrow toggle, hover flyout, scroll-spy): notes h3 ids
    `st-<section>-<n>` (e.g. `#st-motor-effect-6`), past-paper units list their `pp-` h3s. Malaysian mains quoted as 230 V.
    No Physics PDFs yet, so no shop promo box.)
    Each notes topic links to its past-paper unit (`a.pp-link-box`), sidebar `.side-link` box; old `#pp-…` hashes forward.
  - `resources/igcse-physics-past-papers/` — **separate page** (split Nov 2026): `#pp-unit1`…`#pp-unit6` (180 questions across 31 sub-topics; `h3#pp-1-5-1` etc.).
    Real 0625 Paper 4 (41/42/43) questions 2020–2025, verbatim + cited, original answers, 50 SVG diagrams (41 added Nov 2026,
    reviewed); parts on content dropped from the 2026–2028 syllabus (logic gates etc.) skipped. A few papers say take g = 10 N/kg
    and their answers follow that. No "Get it marked" links (marking page only offers full-paper marking for Physics).
  - Older stubs: chemistry past-paper technique, A-level biology definitions, physics formula sheet, economics essay guide.
- `marking/` — paid past-paper marking page: full past papers (Chem/Phys/Bio/Maths) RM10–30 per paper, cheaper in batches;
  questions RM10–20 / essays RM20–40 (Business/Econ/English); 48-hour turnaround; form opens WhatsApp prefilled.
  Accounting not yet listed (owner to decide). Economics model answers have "Get it marked" links that prefill the form.
- `shop/` — PDF notes shop: embeds 4 Payhip product pages (`payhip-embed-page`, data-keys `oVPXO`, `F1jYU`, `mJxkK`, `qWKMF`; one shared embed-page.js script). Linked from the nav on the
  homepage, hub, marking and Bio/Chem notes pages, a "Get these notes as a PDF" box in the Bio/Chem sidebars, and
  "PDF available" tags on the Bio/Chem hub cards. Add new subjects here when their PDFs go on Payhip.
- Show/hide answers: `resources/pp-answers.js` (loaded before `../search.js` on every page with `span.pp-ref`: Accounting,
  Biology and Business notes, Chemistry/Economics/Physics past-papers pages). It hides each past-paper answer behind a
  "Show answer" button (question = first bold-only paragraph in the `example-block`; Accounting's multi-part blocks get one
  button per bold "(a)…" part) plus its "Why this scores" box, and adds one "Show all answers" switch per section;
  printing shows everything. A `div.pp-stimulus` between two parts stays visible (it ends the previous part's answer). `make_offline.py` pastes it into offline copies. Any new past-paper page must load it.
- Search: `resources/search.js` + `resources/search-index.json` (hits link to `st-`/`pp-` h3 anchors). **Rebuild after editing notes:** `python3 tools/build-search-index.py`.
  New notes page → add to `PAGES` in that script and include `<script src="../search.js"></script>`.
- `sitemap.xml`, `DEPLOY.md` (structure + search instructions).
- Skill `.claude/skills/paula-web-design/`: designs or restyles pages for all three of Paula's sites (hub, SEO portfolio, this
  site) in a saved style; the "hub" style is the first one (`styles/hub-style.md` + `.css`).
- Skill `.claude/skills/igcse-topical-past-papers/`: builds topical past-paper Q&A sections for any IGCSE notes page
  (download papers, extract questions, parallel writer agents, verbatim validator, renderer). Used for Economics, Physics, Business, Chemistry and Biology. pastpapers.co sits behind a Cloudflare bot check; use PapaCambridge.
  Its renderer targets the notes page; Chemistry, Economics and Physics past papers now live in `resources/igcse-<subject>-past-papers/`.
- Skill `.claude/skills/split-past-papers/`: one command moves a subject's `pp-` sections into `resources/igcse-<subject>-past-papers/`
  with link boxes both ways, old-link forwarding and all followers (search, sitemap, hub card, DEPLOY.md); includes a
  Playwright checker. Applied to Economics and Physics (Nov 2026); dry-run tested on Biology, Business and Accounting, not yet
  applied to them (owner to choose).

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

## Offline personal copies (selling on Shopee)
- `tools/offline-edition/make_offline.py <subject> --buyer "Name" --order N --out <folder outside repo>` makes one
  self-contained HTML file per buyer (works offline, embedded DM fonts, notes + past papers merged, no password).
  Owner chose **no password, just names**: Paula's © and the buyer's name/order on a top banner, every section header,
  a faint diagonal watermark, title and footer. Never write buyer copies into the repo (script refuses).
  Top bar in copies = Home (About page made from the homepage, `about_page.py`), Notes, WhatsApp; owner asked that copies
  never mention or link to the free site (no Resources/Marking/Shop, no "free notes", no marking card) — script enforces it.
- **Order Maker** (`tools/offline-edition/build_order_maker.py --out <dir>`): one ~3 MB `Order-Maker.html` the owner keeps on her
  laptop; makes buyer copies in the browser with no tokens (identical to make_offline.py output). Rebuild and send it to her
  whenever notes change (shows its build date).
- Shopee: digital items use the "Virtual Goods" shipping channel, which since 1 Sep 2026 needs Seller KYC as a
  Registered Business (SSM) — owner to confirm her shop status. Delivery = send the file/link per order.

## Editable editions (Obsidian / handwriting PDF / Word)
- Converter scripts in `tools/note-editions/` (see its README). Done: Chemistry (vault, GoodNotes PDF, Word), Biology (vault, GoodNotes PDF).
- Note sources + PDF build files are in the owner's private **Paula-Notes-Build-Kit.zip** (never commit them; repo is public).
  Ask the owner to upload it, set `NOTES_SRC` to its `sources/` folder, then run the scripts.

## Open items / ideas
- Owner to confirm dates: tutoring since 2020 vs 2021; A Level certificate shows June 2022 series.
- Official syllabus PDFs can be downloaded from the subject
  page on cambridgeinternational.org (link "2026-2028 syllabus" → `/Images/<id>-2026-2028-syllabus.pdf`).
- Business notes: paper layout described is the 0450 format (P1 4×20: 2/2/4/6/6; P2 case 4×20: 8/12) — check against the
  current syllabus year. Owner's sample questions were OxfordAQA 9225 style; model answers use original cases, not past-paper text.
- Possible next: Physics PDFs, Maths notes, Business PDFs, Economics detailed PDFs, custom domain
  (Cloudflare Pages or Netlify), Accounting on the marking page, store name (top picks: "Notes by Paula", "A* Starts Here").
