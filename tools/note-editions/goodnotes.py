import re, json, subprocess, pathlib, pymupdf, html as H
D = pathlib.Path("gn").resolve(); D.mkdir(exist_ok=True); from ir import SUBJ, B
import shutil
for f in ("dm400.ttf","dm400i.ttf","dm500.ttf","dm700.ttf","corm700.ttf"): shutil.copy(B/f"{SUBJ}pdf"/f, D/f)
NAME = {"chem": "Chemistry", "bio": "Biology", "econ": "Economics", "acct": "Accounting"}[SUBJ]; CODE = {"chem": "0620", "bio": "0610", "econ": "0455", "acct": "0452"}[SUBJ]
YEARS = "2027-2029" if SUBJ in ("econ", "acct") else "2026-2028"
SRC = B/f"{SUBJ}pdf"/f"{NAME.lower()}-notes.html"
from ir import TOPICS, FOOTER, B
EXTRA = """
@page{size:A4;margin:13mm 88mm 16mm 13mm}
@page:first{margin:0}
.cover{width:210mm}
.conventions{grid-template-columns:1fr 1fr}
.structure-card{grid-template-columns:1fr}
.checklist ul{columns:1}
.diagram svg{max-width:100%}
table{font-size:8.6pt} th{font-size:7.2pt}
.toc-row{font-size:10pt}
.topic{break-before:page!important;page-break-before:always!important}
.notes-lines{break-inside:avoid;margin-top:6mm}
.notes-lines h4{color:var(--accent);margin:0 0 1mm}
.notes-lines div{height:8.5mm;border-bottom:1px solid #c9d5e3}
"""
LINES = '<div class="notes-lines"><h4>My notes</h4>' + "<div></div>" * 10 + "</div>"
def make(pages):
    s = SRC.read_text()
    s = s.replace("</style>", EXTRA + "</style>", 1)
    s = re.sub(r'<span class="toc-page">\d*</span>', lambda m, it=iter(TOPICS): f'<span class="toc-page">{pages.get(next(it)[1], "")}</span>', s)
    s = s.replace("</section>\n<section class=\"topic\"", "</section><section class=\"topic\"")
    head, body = s.split('<section class="topic"', 1); body = '<section class="topic"' + body
    body = re.sub(r'(</section>)(?=\s*<section class="(?:topic|back)")', LINES + r"\1", body)
    s = head + body
    (D/"notes.html").write_text(s)
    subprocess.run(["node", str(B/f"{SUBJ}pdf"/"render.js"), str(D/"notes.html"), str(D/"raw.pdf")], check=True, cwd=str(B/f"{SUBJ}pdf"))
    return pymupdf.open(D/"raw.pdf")
from ir import parse
# each topic's first page starts with its badge ("Topic 3 · ...", "Model Answers · Topic 1", "Start Here · Paper 2")
BADGE = {slug: parse(n, slug)[0]["badge"].lower() for n, slug, t, g in TOPICS}
def locate(doc):
    p = {}
    for i in range(2, doc.page_count):
        txt = doc[i].get_text()
        for n, slug, title, g in TOPICS:
            if slug not in p and " ".join(txt.lower().split()).startswith(BADGE[slug]): p[slug] = i + 1
    return p
doc = make({}); pages = locate(doc)
for _ in range(4):
    doc = make(pages); new = locate(doc)
    if new == pages: break
    pages = new
assert len(pages) == len(TOPICS), pages
F = str(D/"dm400.ttf")
for i in range(1, doc.page_count):
    pg = doc[i]; pg.wrap_contents(); w, h = pg.rect.width, pg.rect.height
    x0 = w - 88 * 72 / 25.4 + 14
    if i >= 2:
        pg.insert_text((x0, 40), "NOTES", fontsize=7, fontname="dm", fontfile=F, color=(0.29, 0.56, 0.85))
        y = 62
        while y < h - 60:
            pg.draw_line((x0, y), (w - 30, y), color=(0.80, 0.85, 0.91), width=0.5); y += 24
        pg.draw_line((x0 - 8, 30), (x0 - 8, h - 50), color=(0.87, 0.90, 0.94), width=0.6)
    kw = dict(fontsize=7, fontname="dm", fontfile=F, color=(0.54, 0.59, 0.66))
    pg.insert_text((37, h - 24), FOOTER, **kw)
    num = str(i + 1); pg.insert_text((w - 30 - pymupdf.get_text_length(num, fontsize=7), h - 24), num, **kw)
toc = [[1, "Cover", 1], [1, "Contents", 2]] + [[1, (f"Model Answers: {t}" if g.startswith("Past Paper") else f"Worked Examples: {t}" if g.startswith("Worked Example") else f"{n}. {t}"), pages[s]] for n, s, t, g in TOPICS] + [[1, "Want your answers checked?", doc.page_count]]
doc.set_toc(toc)
links = sum(1 for l in doc[1].get_links() if l["kind"] == pymupdf.LINK_GOTO or l.get("page") is not None)
doc.set_metadata({"title": f"IGCSE {NAME} Revision Notes - GoodNotes edition (Cambridge {CODE}, {YEARS})", "author": "Paula"})
out = pathlib.Path(f"out/IGCSE-{NAME}-Compact-Notes-GoodNotes-Edition.pdf"); doc.save(out, garbage=3, deflate=True)
print(doc.page_count, "pages; contents links:", links, pages)
