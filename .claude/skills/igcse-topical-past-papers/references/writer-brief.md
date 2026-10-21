# Writer brief: topical past-paper model answers

Copy this file into the run's work folder, fill in every `{{…}}`, and point each writer agent at it. The writer's
prompt then only needs: "Read and follow <path>/BRIEF.md. Your agent key is `<key>`. Your sub-topics: …".

---

You are writing exam-quality **model answers** to real Cambridge IGCSE {{SUBJECT}} ({{CODE}}) {{PAPER_LABEL}} questions
for a tutor's public revision website. Your result is a JSON file; the lead agent validates it and renders the HTML.
Do not edit the repo.

WORK = {{WORK_DIR}}

## Inputs (all local; do not fetch anything else)
- `WORK/papers/questions.json`: every marked question part. Fields: `id` (the citation, e.g. `{{EXAMPLE_REF}}`),
  `session`, `file` (e.g. `{{EXAMPLE_FILE}}`), `marks`, `question`, `stem` (the shared lead-in for a sub-part, if any),
  `stimulus` (text before the question's first part, or the insert / Section A source), `refers_to_figure`.
- `WORK/papers/<file>.txt`: the full question paper. Swap `_qp_` for `_ms_` for its **mark scheme**, `_in_` for its
  **insert** (case studies, source booklets) when one exists.
- `WORK/papers/{{CODE}}_<s><yy>_er_<comp>.txt`: the examiner report for that component, where one exists (the whole
  report is `_er.txt`). Use what it says strong and weak answers did.
- Mark-scheme and paper text lose some symbols in extraction (× signs, superscripts, subscripts): read numbers with care
  and check against the question's own figures.
- Style reference, read first: `{{STYLE_PAGE}}` (the same page the sections will be added to). Read its exam-technique
  / "how to answer" section if it has one, its Common Mistake / tip boxes, and any existing model answers: those are the
  tutor's own tips and every answer must follow them.{{STYLE_EXTRA}}

## Your job
For each sub-topic you are given:
1. Find the question parts in `questions.json` that mainly test that sub-topic. Read the wording and use the mark scheme
   when unsure. A part belongs to one sub-topic only; pick its main focus and ignore parts that mainly test a sub-topic
   that is not on your list.
2. Choose **4 to 6**, covering the range of command words and marks that exist for that sub-topic (e.g. a 1–2 mark
   State/Define/Calculate, a 3–4 mark Explain/Describe, a 5–6 mark longer answer, and the paper's top-mark question type).
   Spread them across years and sessions; prefer recent papers when two are similar.
3. **Skip** a part when:
   - answering needs a figure, graph, circuit, table or apparatus diagram that cannot be put into one or two sentences
     of quoted text (`refers_to_figure` is a hint, not a rule: "Fig. 2.1 shows a ball falling" may be fine, "use Fig. 2.1
     to determine…" is not);
   - it asks the student to draw on, complete or plot something printed in the paper;
   - its wording already appears on the style page (grep it);
   - its paper has no mark scheme in the folder.
4. Write the model answer and the commentary.

## Writing rules
- `question`: copy it from questions.json. You may delete obvious extraction junk (answer-line labels, figure labels,
  stray "1 2" numbering, units printed after answer lines) but must not reword anything: the validator checks that every
  sentence appears word for word in the paper. If superscripts were flattened (e.g. `7.8 × 1011` for 7.8 × 10¹¹), write
  them as HTML (`7.8 &times; 10<sup>11</sup>`); the validator unescapes HTML before checking, so do the same with `<sup>`
  only where it is unambiguous, and say so in your summary.
- `stimulus`: one to three sentences quoted **verbatim** from the stem, stimulus or insert that a student needs in order
  to answer (exact words; "&hellip;" for a cut). Include a sub-part's `stem` whenever the question refers to it
  ("this gas", "the train"); use `null` only when the question makes sense entirely on its own.
- `id`, `session`, `marks`: copy exactly from questions.json, then confirm the question number against the printed paper
  and mark scheme (the id must cite the right question and part).
- The answer must be **original**: do not copy mark-scheme lines or examiner-report sample answers; use them only to
  know what earns marks. Write at full-mark standard, as a strong 15–16-year-old would in the exam, not a textbook.
  Length matches the marks.
- Subject conventions:
  {{SUBJECT_RULES}}
- Diagrams: when the question says "using a diagram", or a sketch earns marks, add `diagram`: an inline SVG
  `<figure class="diagram"><svg viewBox="0 0 320 240" role="img" aria-label="…">…</svg><figcaption>Figure: …</figcaption></figure>`,
  `stroke="currentColor"`, text `font-family="DM Sans, sans-serif"` size 11–12, axes and every line/point labelled, no
  overlapping labels. Any `<marker id>` must start with your agent key (e.g. `arr-{{KEY_EXAMPLE}}-1`). Otherwise `null`.
- `why`: 1–3 sentences on why the answer gets full marks, tied to the mark scheme ("One mark for…", level descriptors
  for levels-marked questions), plus a common pitfall from the examiner report when there is one.
- Per sub-topic: `intro` (one sentence on what these questions test and what examiners reward) and `pitfall` (one or two
  sentences on the commonest mistake, from the examiner reports where possible; `null` if nothing reliable).
- HTML in all strings: UK spelling; entities for typographic characters (`&rsquo;` `&ldquo;` `&rdquo;` `&ndash;`
  `&mdash;` `&times;` `&divide;` `&minus;` `&deg;` `&hellip;`); tags limited to `<p>`, `<strong>`, `<em>`, `<sub>`,
  `<sup>`, `<br>`, `<ul>`, `<ol>`, `<li>`, and `<table class="...">` only if the style page already uses that table class.

## Output
Write `WORK/answers/<agent-key>.json` (create the folder if needed):
```json
{"key": "u3a", "subtopics": [
  {"code": "3.1", "title": "…", "intro": "…", "pitfall": "…",
   "items": [
     {"id": "…", "session": "…", "marks": 2, "question": "…", "stimulus": "…",
      "answer": ["<p>…</p>", "<p>…</p>"], "why": "…", "diagram": null}
   ]}
]}
```
Before finishing, run `python3 {{SKILL_DIR}}/scripts/build_sections.py {{CONFIG_PATH}} --check` and fix every line
it prints that mentions your key or your sub-topic codes (it checks ids, verbatim wording, marks, missing fields, question
count per sub-topic and marker-id clashes; the writing rules above are yours to keep). Then reply with 3–5 lines: sub-topics done, questions per sub-topic, and any
sub-topic with fewer than 4 usable questions and why.
