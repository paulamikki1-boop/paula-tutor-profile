# Subjects: components and answer conventions

Component numbers are the usual Cambridge pattern (variants 1/2/3 of each paper, e.g. 41, 42, 43). Syllabuses change, so
confirm the current components against the syllabus or the downloaded cover pages before relying on this table.
February/March papers usually exist for variant 2 only (e.g. `0625_m24_qp_42`); the downloader skips missing files.

| Subject (code) | Notes page | Components that suit written answers | Watch out for |
|---|---|---|---|
| Economics (0455) | `resources/igcse-economics-notes/` | Paper 2 structured: 21, 22, 23 | Done 2020–2025. Section A Q1 relies on source material printed before it. |
| Business (0450) | `resources/igcse-business-notes/` (marking subject: "Business Studies") | Paper 1 short answer/data response: 11, 12, 13; Paper 2 case study: 21, 22, 23 | Paper 2 case study is in the **insert** (`_in_`); stimulus quotes come from there. Owner also teaches Edexcel 4BS1 / OxfordAQA 9225 but this skill only covers Cambridge papers. |
| Accounting (0452) | `resources/igcse-accounting-notes/` | Paper 2 structured: 21, 22, 23 (Paper 1 is multiple choice) | Many parts are "Prepare the … account": the answer is a layout. Use the page's `table.ledger` / `table.statement` classes and show workings. Skip parts that need a pre-printed table to be completed. |
| Physics (0625) | `resources/igcse-physics-notes/` | Paper 4 extended theory: 41, 42, 43 (Paper 3 core theory: 31, 32, 33) | Done 2020–2025 (Paper 4, all six topics). Heavy use of figures; skip "on Fig. x.x, draw/mark…". Superscripts flatten in extraction (10<sup>11</sup> → 1011). "DO NOT WRITE IN THIS MARGIN" text can split a sentence, so the validator rejects it; pick another part. Skip content dropped from the 2026–2028 syllabus (logic gates, CRO, relays). |
| Chemistry (0620) | `resources/igcse-chemistry-notes/` | Paper 4: 41, 42, 43 (Paper 3: 31, 32, 33) | Equations need correct formulae, balancing and state symbols; subscripts flatten (H2O). |
| Biology (0610) | `resources/igcse-biology-notes/` | Paper 4: 41, 42, 43 (Paper 3: 31, 32, 33) | Many parts read data from graphs/tables or label diagrams; skip those. Keyword precision matters. |
| English (0500) | `resources/igcse-english-writing-forms/` | Not a good fit: answers depend on long reading passages and are marked holistically | Discuss with Paula before attempting. |

Papers 5/6 (practical and alternative to practical) are rarely worth it: nearly every part depends on apparatus figures
or data tables.

## Answer conventions to paste into `{{SUBJECT_RULES}}`

**Economics / Business (levels-marked longer answers)**
- Define key terms at the start of longer answers; build chains of reasoning (cause, effect, consequence).
- Business: apply every point to the named business in the case (its product, size, figures); use the case data.
- "Discuss" / "Consider… which is best? Justify your answer": both sides with bolded paragraph leads, then
  `<strong>Conclusion.</strong>` making a judgement that depends on specific conditions; for Business, a justified
  recommendation for that business.
- Interpret every calculated figure.

**Accounting**
- Show the formula or working line for every calculation, then the answer with $ and correct labels.
- For accounts and statements use the layout the syllabus expects (Dr/Cr, dates, details, balance c/d and b/d), as HTML
  tables with the page's existing classes; follow the page's worked examples exactly.
- For "advise" / "evaluate" questions: points for and against, then a clear recommendation.

**Physics / Chemistry / Biology**
- Calculations: write the equation in symbols or words, substitute with units, give the answer with a unit and sensible
  significant figures (match the data, usually 2–3 s.f.). Bold the final answer.
- Use the exact scientific vocabulary the mark scheme credits (e.g. "particles collide more frequently", not "move
  faster and hit more"); the examiner reports list the words that lose marks.
- "Describe" vs "Explain": Describe states what happens, Explain gives the reason. "State" needs no reasoning.
- Chemistry: balanced equations with state symbols when asked; ionic equations where the question says ionic.
- Keep answers as short as the marks allow: one creditworthy point per mark is the usual pattern.
