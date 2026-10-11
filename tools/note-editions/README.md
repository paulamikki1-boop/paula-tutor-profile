# Note editions converter

Turns the notes source files (the same ones used for the paid PDFs) into:

| Script | Output |
|---|---|
| `obsidian.py` | Obsidian vault: one `.md` per topic, Start Here index, `[[links]]`, `#supplement` tags, diagrams in `assets/` |
| `goodnotes.py` | Handwriting PDF (A4): notes on the left 60%, ruled margin on the right 40%, "My notes" lines per topic, clickable contents + bookmarks |
| `word.py` | Word editions: Compact `.docx` + one Detailed `.docx` per topic (real headings, editable tables) — Chemistry only so far |
| `png.js` | Renders the diagram SVGs to PNG (DM Sans) for the vault / Word |

**The note content is NOT in this repo** (the repo is public and the notes are a paid product).
The sources live in Paula's private **Paula-Notes-Build-Kit.zip** (`sources/` = topic fragments, PDF build
files, diagrams, fonts). Upload that zip to a new Claude session to make new editions.

## Run (from any empty working folder)

```bash
pip install beautifulsoup4 lxml pymupdf pillow python-docx
npm install playwright            # Chromium is preinstalled in Claude cloud sessions
export NOTES_SRC=/path/to/Paula-Notes-Build-Kit/sources
T=/path/to/tools/note-editions
cp $NOTES_SRC/chempdf/dm*.ttf .                       # fonts for png.js
mkdir -p assets-bio && node $T/png.js $NOTES_SRC/biopdf/diagrams assets-bio
SUBJ=bio python3 $T/obsidian.py                       # -> out/Biology 0610 Vault
SUBJ=bio python3 $T/goodnotes.py                      # -> out/IGCSE-Biology-Compact-Notes-GoodNotes-Edition.pdf
```
`SUBJ` is `bio`, `chem` or `econ` (folder names in `sources/`). The GoodNotes edition uses the built Compact HTML
(`sources/<subj>pdf/<subject>-notes.html`).

## Adding a new subject
1. Put its topic fragments in `sources/<code>/` and its `<code>pdf/` folder (build.py with the `TOPICS` list,
   diagrams + `manifest-*.jsonl`, built `*-notes.html`, fonts, render.js) next to them.
2. Add the subject name/code to the `CFG` dict in `obsidian.py` and `NAME`/`CODE` in `goodnotes.py`, and a
   `RELATED_<CODE>` topic-link map in `obsidian.py`.
3. `ir.py` handles the component classes used by Bio/Chem/Econ (tables, conventions, steps, tip/mistake/example
   boxes, checklists, Supplement tags, multi-paragraph model-answer boxes, inline `figure.diagram` SVGs).
   Accounting ledgers use extra classes — `ir.py` stops with "unhandled …" so you can add them.

**Economics:** its diagrams are mostly inline SVGs in the topic fragments. `ir.py` writes them to `figs-econ/`,
so render both folders into the assets:
```bash
SUBJ=econ python3 $T/ir.py && mkdir -p assets-econ
node $T/png.js $NOTES_SRC/econpdf/diagrams assets-econ && node $T/png.js figs-econ assets-econ
SUBJ=econ python3 $T/obsidian.py && SUBJ=econ python3 $T/goodnotes.py
```

Rules: format conversion only (never change wording); unlocked files keep the footer
"© Paula - IGCSE Tutor - personal use only, not for resale". Never commit note content or passwords here.
