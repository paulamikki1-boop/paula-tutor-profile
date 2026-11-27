---
name: fable-playbook
description: >-
  Working method for every task in this repo: how to plan before starting, break the work into steps, check the result
  before reporting it done, and avoid the mistakes that have cost time here before. Load this at the start of EVERY
  task, however small it looks (a one-line fix, a new notes page, a restyle, a past-paper section, a PDF build, a
  question about the site), before the first edit or command. For a pure question, only the "Reporting" section applies.
---

# Fable playbook

How to run a task on Paula's tutor site from first read to final message. The owner is a tutor, not a developer: she
reads the summary and looks at the live page, not the diff. So the work is only as good as what she sees in a
browser and what you tell her in plain English.

Scale the method to the task. A typo fix needs thirty seconds of planning and one check; a new notes page needs all of
it. Skipping the check is never the saving.

## 1. Plan before touching anything

1. **Restate the request in one sentence, including what "done" looks like to the owner.** "Add Physics topic 1 notes"
   is done when the section opens from the sidebar, is found by search, is linked from the hub and looks right on a
   phone, not when the HTML is written. If you cannot write that sentence, you do not understand the task yet.
2. **Read before deciding.** `.claude/CLAUDE.md` first: it records page structure, anchor naming, owner decisions and
   known traps. Then open the actual files you will change and one finished sibling (the closest existing notes page
   is the specification for a new one). Check whether a skill already covers the job (`paula-web-design`,
   `igcse-topical-past-papers`) and follow it rather than improvising.
3. **List everything the change touches.** On this site one visible change usually has hidden followers: search index,
   sitemap, hub card, homepage subject card, `DEPLOY.md`, the hub style layer, the notes in `CLAUDE.md`. Write the list
   before starting so the followers are steps, not afterthoughts.
4. **Sort the unknowns.** Anything you can find out by reading the repo or running something, find out. Anything with
   an ordinary default, choose it and say so in the summary. Ask the owner only for what is hers alone to decide
   (prices, wording about herself, what to sell, dates, anything about passwords or private files), and ask once,
   early, while carrying on with the parts that do not depend on the answer.
5. **Find the risky step.** Ask which step could damage something already working (a script that rewrites every
   page, a bulk find-and-replace, a rename of anchors that other pages link to). Plan that step to run on one file
   first, with a look at the diff, before running it everywhere.

## 2. Break it into steps

- **Each step ends in something you can check.** "Write the section" is not a step; "section renders, sidebar link
  opens it, hash deep-link works" is.
- **Order: content, then wiring, then generated files, then verification.** Generated files (search index, style
  layer) come last because any later edit makes them stale.
- **Smallest working slice first on big jobs.** For a 200-question past-paper section, take one sub-topic through the
  whole pipeline (extract, write, validate, render, view in browser) before fanning out. Faults in the pipeline then
  cost one sub-topic, not thirty.
- **Change by script when the change repeats, by hand when it is one-off.** Twenty pages need a script and a diff
  review; one page needs an edit. A script that edits HTML must be safe to run twice.
- **Delegate only independent, well-specified pieces.** A sub-agent knows nothing you did not write in its brief:
  give it the files to read, the exact output format, the rules (original wording, exact citations, no third-party
  notes) and what you have already ruled out. Treat what comes back as a draft to verify, not a result. Its figures
  and quotes get the same checks as your own.
- **Keep a running list on long tasks** and tick items only after their check passes. When context is summarised
  mid-task, the list is what stops a step being silently dropped.
- **Commit at stable points** with a message that says what changed and why, on the branch the session assigns.

## 3. Check before saying "done"

Evidence, not expectation. "It should work" means it has not been checked.

**Always**
- Read your own diff top to bottom (`git diff`). Look for stray edits, leftover debug text, files you did not mean to
  touch, and changes far larger than the task warrants.
- Re-read the original request and compare it line by line with what you delivered. Every part asked for is either
  done or named as not done.

**Any page change**
- Serve the site locally (`python3 -m http.server`) and open the page in the pre-installed Chromium via Playwright.
  Check a desktop width and a phone width (about 390px). Take a screenshot and actually look at it.
- Console shows no errors. Click the thing you changed: sidebar item, section hash, filter, search box, form button.
- Internal links are relative (the site lives under `/paula-tutor-profile/`); canonical, og and sitemap URLs are
  absolute. Test links from the page's real folder depth, not from the repo root.
- Nothing scrolls sideways on the phone width; tables sit inside `table-wrap`; SVG diagrams are legible.

**Notes content**
- Re-work every calculation independently instead of re-reading it. Accounting totals must balance; physics and
  chemistry answers need units and sensible significant figures.
- Check terminology, formulas and paper format against the syllabus year named on the page, not from memory.
- Past-paper quotes are character-for-character from the paper, with the full reference and the UCLES credit. Take
  question numbers from the printed paper (the extraction script mislabels some). Check answers against the mark
  scheme. Run the skill's verbatim validator.
- Count what you claim: if the summary says 180 questions across 31 sub-topics, the page contains exactly that.

**After notes or structure changes**
- `python3 tools/build-search-index.py`, then search for a phrase from the new content and follow the hit.
- `python3 .claude/skills/paula-web-design/scripts/apply_hub_layer.py` after adding a page or changing the layer;
  confirm the diff touches only what you expect.
- Sitemap, hub card, homepage card, `DEPLOY.md` and `CLAUDE.md` updated where the change calls for it.

**Before pushing**
- Nothing private in the commit: no passwords, no note sources, no build-kit files, no PDFs meant for sale. The repo
  is public.
- `git status` is clean, and the push went to the assigned branch and succeeded.

If a check cannot be run, say so in the summary and say why. Never report a check you did not perform.

## 4. Mistakes to watch for

**Process**
- Starting to edit before reading the sibling page, then rebuilding it to match afterwards.
- Declaring success from the code rather than from the rendered page. Most faults on this site are visible only in a
  browser: a section that does not open, a card that overflows on a phone, a link that 404s under the subpath.
- Fixing the symptom you were shown and not looking for the same fault elsewhere. If one page has it, grep the rest.
- Forgetting the followers: stale search index, missing sitemap entry, style layer not re-applied.
- Scope creep. Do not restyle, rename or "tidy" things nobody asked about. Mention them in the summary instead.
- A run of failed attempts at the same fix. After two, stop and re-examine the assumption, do not try a third variant.
- Trusting memory over the file. Notes in `CLAUDE.md` and your own recollection of a page can be out of date; the
  file on disk is the truth. When they disagree, believe the file and correct the note.
- Treating a sub-agent's report, a script's "OK" or an exit code of 0 as proof. Open the output.

**Content**
- Copying or closely paraphrasing third-party notes (Save My Exams, r/IGCSE guides). They are a topic checklist only;
  every explanation is written fresh. The single exception is Cambridge question wording in past-paper sections,
  quoted exactly and cited.
- Inventing a citation, a mark allocation, a syllabus code or a statistic. If you do not have the source, find it or
  leave it out and say so.
- Writing for the wrong syllabus year or exam board, or mixing old and new terminology on one page.
- A tone that is childish or lecture-like. The readers are teenagers revising: clear, direct, respectful.
- Arithmetic that was typed, not worked. Re-derive it.

**Site**
- Absolute internal links, or links that work from the root but not from `resources/<page>/`.
- Renaming or renumbering section ids. Other pages, the search index and "Get it marked" links point at them.
- Editing the shared style layer by hand in one page instead of through the script, so pages drift apart.
- Re-running the topical-past-papers renderer (`build_sections.py` without `--check`) on a page whose past-paper sections
  were later edited by hand (diagrams, mark-scheme fixes): it rebuilds the sections and silently drops that work. To add
  questions, validate with `--check` and insert the new blocks with a small script.
- Adding features the page has deliberately left out (CLAUDE.md records several, such as no "Get it marked" links on
  the science pages).

**Actions that need the owner first**
- Deleting content, force-pushing, changing prices or contact details, anything involving the selling PDFs or their
  passwords, and posting anywhere outside the repo. Look at what you are about to remove before removing it.
- Opening a pull request or merging: do it when the owner asks. Her standing preference is a PR to `main` after
  browser testing, so offer it when the work is ready.

## 5. Reporting

Write the final message for someone who was not watching and does not read code.

- Lead with what she can now see or do, in plain English, with the page and section named.
- Then what you checked and how (for example "opened on desktop and phone widths, search finds it"), and anything you
  could not check.
- Then anything she needs to decide or do, each as a short, specific question with your recommendation.
- State problems plainly. A failed check, a skipped part or a doubt about a fact goes in the summary, never buried
  and never left out.
- No file-by-file changelog unless she asks. No jargon she would have to look up.

## 6. Keeping the notes current

When a task changes the site's structure, adds a page, or settles an owner decision, update `.claude/CLAUDE.md` in
the same commit so the next session starts from the truth. Record lasting facts (structure, conventions, decisions,
traps), not a diary of what was done. If a trap cost you time and would cost the next session time, add one line
about it to section 4 of this file.
