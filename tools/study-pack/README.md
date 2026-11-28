# Study pack builder (PDFs + Obsidian + READ ME, for selling)

```bash
pip install pymupdf beautifulsoup4 lxml
python3 tools/study-pack/build_study_pack.py chemistry --out <folder outside the repo>
```

Builds `IGCSE-<Subject>-Study-Pack/` and `.zip` from the **live notes page** (`resources/igcse-<subject>-notes/`), so the
pack always matches the checked website notes:

- `1 <Subject> <code> - Compact Revision Notes.pdf`: all sections, compact layout (scale 0.8), each topic on a new
  page, contents page with real page numbers and links, PDF bookmarks.
- `2 Detailed Notes/`: one PDF per section (Exam Guide, topics, Illustrated Examples), spacious, own cover.
- `3 <Subject> <code> Obsidian Vault/`: one Markdown note per section, a Start Here index, prev/next and `[[links]]`,
  `#supplement` tags, callouts for tips/mistakes/examples, diagrams rendered to PNG in `assets/`.
- `READ ME FIRST.txt`: what each file is and how to open it.

Every PDF page has a faint "© Paula · IGCSE Tutor" watermark, a footer "© <year> Paula … personal use only" and page
numbers. PDFs open **without a password** (owner's choice); printing is allowed, copying/editing is switched off with a
random owner password that is not stored. The past-paper sections are **left out** (Cambridge question wording should not
be resold). The script checks that nothing mentions the free website. Format conversion only: the wording is unchanged.

Uses the notes page's own CSS (screen look, shadows removed so files stay small), the DM fonts from
`tools/offline-edition/fonts/`, Playwright/Chromium for HTML→PDF and PNG, PyMuPDF for stamps, bookmarks and permissions.
Never commit the output (paid product).
