---
name: split-past-papers
description: Move a subject's past-paper sections (Topical Past Papers / Past-Paper Examples) out of its notes page into a separate page on Paula's tutor site, with each notes topic linking to its past papers and each past-paper unit linking back. Use whenever Paula asks to separate, split or move the past papers from the notes for any subject (Biology, Physics, Economics, Business, Accounting, ...), to "do what we did for Chemistry" with past papers, or to give past papers their own page.
---

# Split past papers into their own page

Chemistry was split first (Nov 2026, by hand); this skill does the same for any other notes page in one command.
Result for the owner: `resources/igcse-<subject>-notes/` keeps the notes, `resources/igcse-<subject>-past-papers/`
holds every past-paper section, unchanged. Each notes topic has a "… for this topic" box under its heading and a
"Test yourself on …" box at its end linking to that topic's past papers; each past-paper unit opens with a
"Revise the notes first" box back to the notes; each sidebar has a box to the other page; old `#pp-…` links to the
notes page forward to the new page; search hits open the exact sub-topic.

## How the script decides what goes where
- Past-paper sections = sections whose id starts `pp-` (`sec-pp-unit3`, `sec-pp-ped`, `sec-pp-t2`). Everything else
  (including original "Model Answers" / "Worked Example Answers" sections) stays on the notes page.
- Topic matching uses the section badges: a past-paper badge ending `Topic N` matches notes sections whose badge
  starts `Topic N` or `Topic N.M`. Several past-paper sections can share a topic (Economics 2 and 2.7); several notes
  sections can share one too (Physics 2.1–2.3 all link to unit 2). Topics with past papers but no notes yet (Physics 1
  and 4) get no back link; the script lists them.
- In-page links that would now cross pages are rewritten to the other page.
- Section ids are never renamed. The past-paper group's sidebar label ("Topical Past Papers" / "Past-Paper Examples")
  becomes the new page's name.

## Steps
1. Read `.claude/CLAUDE.md` (the subject's entry) and load `fable-playbook` as usual.
2. **Dry run on a copy** (never skip; the script rewrites the notes page):
   ```bash
   D=<scratchpad>/dry && rm -rf "$D" && mkdir -p "$D" && git archive HEAD | tar -x -C "$D"
   python3 .claude/skills/split-past-papers/scripts/split_past_papers.py igcse-<subject>-notes --root "$D"
   ```
   Check its summary: question count equals the CLAUDE.md figure, every notes topic with past papers is linked, any
   "topics with no notes" are expected. It refuses pages that have no `pp-` sections (already split).
3. **Browser check the copy:** serve it (`cd "$D" && python3 -m http.server 8766`) and run
   `node .claude/skills/split-past-papers/scripts/check_split.js http://localhost:8766/resources/ igcse-<subject>-notes <shots-dir>`.
   It must print `ALL CHECKS PASSED`; then look at the screenshots (desktop and phone, both pages). Large pages
   (Economics) take a couple of minutes, so run it in the background.
4. **Run for real** in the repo (same command without `--root`). It also updates `tools/build-search-index.py`
   (PAGES), `sitemap.xml`, the resources hub card, `DEPLOY.md`, re-runs the hub style layer and rebuilds the search index.
   Review `git diff --stat`: expect the notes page, one new folder and those followers, nothing else.
5. Update the subject's entry in `.claude/CLAUDE.md` (past papers now at `resources/igcse-<subject>-past-papers/`,
   linked both ways). Commit on the session branch; PR to `main` after the browser check (owner's standing preference).

## Things to know
- The script copies the notes page's head, CSS, nav bar, footer and scripts into the new page, so the style layer and
  search box work unchanged. It adds its own small CSS block (`/* >>> split-past-papers */`) for `.pp-link-box` and
  `.side-link`.
- Pages without a sub-topic menu get a small script so `#pp-x-y` heading links open (search relies on it; the
  search builder only uses `pp-` heading anchors on pages that contain `el.tagName === 'H3'`).
- It does not change any wording, prices or "Get it marked" links; those keep working (same folder depth).
- Chemistry was split by an earlier one-off script with the same result, except its sidebar boxes use the
  `.pdf-promo` style instead of `.side-link`.
