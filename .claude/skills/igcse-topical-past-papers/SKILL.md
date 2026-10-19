---
name: igcse-topical-past-papers
description: Build "Topical Past Papers" sections on Paula's tutor website: real Cambridge IGCSE past-paper questions sorted by syllabus sub-topic, each quoted exactly with its paper reference (e.g. 0625/42/M/J/24 Q2(b)(ii)), session and marks, plus an original full-mark model answer, a "Why this scores" note and examiner-report pitfalls, rendered into that subject's notes page. Use this whenever Paula asks for topical questions, past-paper questions by topic, exemplar or model answers to past papers, "do the same as Economics for Physics/Chemistry/Biology/Business/Accounting", or wants to add or refresh past-paper Q&A for any IGCSE subject, even if she doesn't say "topical".
---

# IGCSE topical past papers

This turns Cambridge past papers into topic-sorted question-and-model-answer sections on one of the notes pages in
this repo. It was first built for Economics 0455 (`resources/igcse-economics-notes/`, sections `#pp-unit1`–`#pp-unit6`
and `#pp-ped`); open that page to see the finished result before starting another subject.

The work splits into a mechanical part (download, extract, validate, render), which the bundled scripts handle,
and a writing part (choosing questions and writing answers), which parallel writer agents handle from a shared brief.
Keep that split: the scripts are what guarantee every quoted question really is word for word from a real paper.

## Ground rules (from the owner)
- Quoting Cambridge question wording exactly is allowed **only** with the full reference on each question and the UCLES
  credit line the renderer adds. Everything else, answers, commentary, intros, must be original. Don't copy mark-scheme
  bullets or the sample answers printed in examiner reports.
- Never present an answer for a paper you could not get the mark scheme for, and never invent or "fix" a reference.
  If papers can't be downloaded, stop and say so instead of writing questions from memory.
- Follow the page's own exam-technique tips; the answers should sound like a strong 15–16-year-old in the exam.
- Changes reach the live site through a PR to `main` after browser testing (see `.claude/CLAUDE.md`).

## Step 1: agree the scope (ask if unclear)
Settle these with Paula before downloading anything. Propose defaults from `references/subjects.md` and the notes page:
- **Subject and syllabus code** and which **components** (e.g. Physics Paper 4 = 41,42,43). Multiple-choice papers
  don't suit written model answers; leave them out unless she asks.
- **Years** (default the last six series, 2020–2025) and which notes page the sections go on.
- **Sub-topic list**: use the notes page's sidebar/syllabus numbering so headings match her notes. Write it out as
  `code  title` lines (e.g. `2.3  Demand`).
- **How many per sub-topic** (default 4–6) and whether to pilot one sub-topic first. For a new subject, piloting one
  sub-topic and showing her the page is usually worth it before fanning out.

## Step 2: download and extract
Work in a scratch folder (`WORK`). PapaCambridge must be reachable; if a download is refused by the network policy,
read the environment's network documentation and tell Paula which host to allow (`pastpapers.papacambridge.com`).

```bash
python3 SKILL_DIR/scripts/download_papers.py WORK/papers --code 0625 --years 2020-2025 --components 41,42,43
python3 SKILL_DIR/scripts/extract_questions.py WORK/papers --code 0625
```
The extractor prints the papers with the fewest parts. Open one or two question papers and compare by eye: question
numbers, sub-parts like (b)(ii), and marks should line up. Papers that print Question 1 without a number, chart axis
ticks that look like question numbers, and "in (ii)" inside a sentence are already handled; if a paper still parses
badly, fix the extractor rather than hand-editing questions.json.

## Step 3: write the config and the brief
1. Copy `references/config-example.json` to `WORK/config.json` and fill it in (page, folders, code, subject,
   paper label, years, topic list with sidebar titles, marking subject or `null` if `marking/` doesn't offer it).
2. Copy `references/writer-brief.md` to `WORK/BRIEF.md` and fill every `{{…}}`. Put the subject's answer
   conventions into `{{SUBJECT_RULES}}`, taking them from `references/subjects.md` and the page's exam-technique section.

## Step 4: fan out the writers
Split the sub-topics into groups of about 3–5 (aim for ≤9 writers) and launch them in parallel, in the background, as
general-purpose agents with a short prompt:
`Read and follow WORK/BRIEF.md exactly. Your agent key is u2a. Your sub-topics: 2.3 Demand; 2.4 Supply; …`
Give each group a key (`u1`, `u2a`, `u2b`…). Add one line of scope per sub-topic when the boundary with a neighbour is
fuzzy (e.g. "price-mechanism questions belong to 2.2, not 2.9"); this is what keeps two writers from picking the same
question. While they run, tell Paula what's happening; don't poll their transcripts.

## Step 5: validate, render, check
```bash
python3 SKILL_DIR/scripts/build_sections.py WORK/config.json --check   # problems only
python3 SKILL_DIR/scripts/build_sections.py WORK/config.json           # writes the page
python3 tools/build-search-index.py
```
The validator drops anything it can't stand behind: unknown ids, wording or source text that isn't verbatim in the paper,
answers with no "why". It keeps the first of any question chosen twice. Read its output; if many items from one writer were
dropped, send that writer the lines to fix (SendMessage) rather than patching the JSON yourself. Re-running the renderer
replaces the sections it built before, so iterate freely.

Then check the page in Chromium (`executablePath: '/opt/pw-browsers/chromium'`) at 1280px and 390px: every
`#sec-pp-unitN` opens from the sidebar, no console errors, no horizontal scroll. Screenshot **every diagram** and look
at them, as writers can't see their SVGs. Spot-check a few answers yourself, especially every calculation.

## Step 6: ship
Update `.claude/CLAUDE.md` (the page's entry: section ids, question count, source), commit, push, open a PR to `main`
and give Paula the link plus a short plain-English summary: questions per topic, sub-topics with no long questions,
sessions with no examiner report, and anything skipped. If the session can't merge, tell her how (open the PR → **Merge
pull request** → **Confirm merge**; the site updates 1–2 minutes later, hard-refresh to see it).

## Files
- `scripts/download_papers.py`: QP/MS/insert/examiner-report download + pdftotext.
- `scripts/extract_questions.py`: every marked part, with nested sub-parts, stems, inserts and figure flags.
- `scripts/build_sections.py`: validator + renderer (sections, sidebar group, CSS, mark links, credit line).
- `references/writer-brief.md`: the template brief for writer agents.
- `references/subjects.md`: components and answer conventions per IGCSE subject; read the row for the subject at hand.
- `references/config-example.json`: config template.
