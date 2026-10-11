"""Parse the Chemistry topic fragments (same sources as the PDFs) into a simple block list."""
import pathlib, re, json, html
from bs4 import BeautifulSoup, NavigableString, Tag
import os
B = pathlib.Path(os.environ.get("NOTES_SRC", pathlib.Path(__file__).resolve().parent.parent)).resolve()
import os
SUBJ = os.environ.get("SUBJ", "chem")
CHEM, DIAG, BUILD = B/SUBJ, B/f"{SUBJ}pdf"/"diagrams", B/f"{SUBJ}pdf"/"build.py"
_src = BUILD.read_text()
TOPICS = [(int(n), s, html.unescape(t), html.unescape(g)) for n, s, t, g in
          re.findall(r'\((\d+),"([a-z-]+)","([^"]+)","([^"]+)"\)', _src)]
MANIFEST = {}
for f in DIAG.glob("manifest-*.jsonl"):
    for line in f.read_text().splitlines():
        if line.strip(): e = json.loads(line); MANIFEST[e["slug"]] = e
COVER_SUB_CHEM = "Clear, exam-focused notes for all 12 topics: key definitions, balanced equations, worked calculations, chemical tests, labelled diagrams, examiner tips and a checklist for every topic."
HOWTO_CHEM = ["Work through one topic at a time, starting with the diagram.",
 "Learn the key definitions word for word, and practise each worked calculation until you can do it without looking.",
 "Test yourself: close the notes, then redraw the diagram and explain the topic from memory.",
 "Tick the checklist at the end of each topic when you can do every point."]
_t = lambda x: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", x))).strip()
COVER_SUB = _t(re.search(r'<p class="cover-sub">(.*?)</p>', _src, re.S).group(1))
HOWTO = [_t(x) for x in re.findall(r"<li>(.*?)</li>", re.search(r'class="howto">(.*?)</ol>', _src, re.S).group(1), re.S)]
BACK = ["Want your answers checked?", "Send me your past paper and I’ll mark it with examiner-style feedback within 48 hours.",
 "paulamikki1-boop.github.io/paula-tutor-profile/marking", "Lessons online or in person in KL · WhatsApp +60 10-368 6902"]
FOOTER = "© Paula - IGCSE Tutor - personal use only, not for resale"

def inl(node, fmt=frozenset()):
    """-> list of (text, fmt) runs; fmt subset of {b,i,sub,sup,ext}; '\n' for <br>."""
    out = []
    for ch in node.children:
        if isinstance(ch, NavigableString):
            t = re.sub(r"\s+", " ", str(ch))
            if t: out.append((t, fmt))
        elif ch.name == "br": out.append(("\n", fmt))
        elif "key-term" in ch.get("class", []): out.append(("Supplement", fmt | {"ext"}))
        else:
            f = {"strong": "b", "b": "b", "em": "i", "i": "i", "sub": "sub", "sup": "sup"}.get(ch.name)
            out += inl(ch, fmt | {f} if f else fmt)
    # trim
    while out and not out[0][0].strip(): out.pop(0)
    while out and not out[-1][0].strip(): out.pop()
    if out: out[0] = (out[0][0].lstrip(), out[0][1]); out[-1] = (out[-1][0].rstrip(), out[-1][1])
    return [r for r in out if r[0]]

def plain(runs): return "".join(t for t, f in runs if "ext" not in f).strip()

def split_ext(runs):
    """remove Supplement tag runs; return (runs, is_ext)"""
    ext = any("ext" in f for t, f in runs)
    r = [x for x in runs if "ext" not in x[1]]
    if r: r[0] = (r[0][0].lstrip(), r[0][1])
    return r, ext

FIGS = pathlib.Path(f"figs-{SUBJ}")  # inline SVGs (Economics) are written here for png.js
RAW_SVGS = []  # raw <svg> text of the current fragment, in order (lxml lowercases viewBox etc.)
def figure(el, name):
    FIGS.mkdir(exist_ok=True)
    svg = RAW_SVGS[int(name.rsplit("-", 1)[1]) - 1]
    if "xmlns=" not in svg: svg = svg.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1)
    (FIGS/f"{name}.svg").write_text(svg)
    cap = el.figcaption
    return ("figure", name, plain(inl(cap)) if cap else "")

BLOCKY = ("p", "ul", "ol", "figure")
def box_parts(el, n, slug, nfig):
    """example/tip boxes with <p>/<ul>/<figure> children -> list of parts (Economics model answers)"""
    parts, loose = [], []
    def flush():
        r = inl_list(loose)
        if r: parts.append(("p", r))
        loose.clear()
    for ch in el.children:
        if isinstance(ch, Tag) and ch.name in BLOCKY:
            flush()
            if ch.name == "p": parts.append(("p", inl(ch)))
            elif ch.name == "figure": nfig[0] += 1; parts.append(figure(ch, f"{n:02d}-{slug}-{nfig[0]}"))
            else: parts.append((ch.name, [inl(li) for li in ch.find_all("li", recursive=False)]))
        else: loose.append(ch)
    flush()
    return parts

def inl_list(nodes):
    w = BeautifulSoup("<span></span>", "lxml").span
    for x in nodes: w.append(x.__copy__() if isinstance(x, Tag) else NavigableString(str(x)))
    return inl(w)

def parse(n, slug):
    src = (CHEM/f"{n:02d}-{slug}.html").read_text()
    RAW_SVGS[:] = re.findall(r"<svg\b.*?</svg>", src, re.S)
    s = BeautifulSoup(src, "lxml")
    sec = s.select_one(".section")
    hdr = sec.select_one(".section-header")
    meta = dict(badge=plain(inl(hdr.select_one(".form-badge"))), title=plain(inl(hdr.h2)), purpose=inl(hdr.select_one(".purpose")))
    blocks = []; nfig = [0]
    for el in sec.find_all(recursive=False):
        c = el.get("class", [""])[0] if el.get("class") else ""
        if c == "section-header": continue
        if el.name in ("h3", "h4"):
            r, ext = split_ext(inl(el)); blocks.append(("h", 3 if el.name == "h3" else 4, r, ext))
        elif el.name == "p": blocks.append(("p", inl(el)))
        elif el.name in ("ul", "ol"): blocks.append((el.name, [inl(li) for li in el.find_all("li", recursive=False)]))
        elif c == "table-wrap":
            t = el.table
            head = [inl(th) for th in t.select("thead th")] or [inl(x) for x in t.tr.find_all(["th"])]
            rows = [[inl(td) for td in tr.find_all("td")] for tr in t.select("tbody tr")] or \
                   [[inl(td) for td in tr.find_all("td")] for tr in t.find_all("tr") if tr.find("td")]
            blocks.append(("table", head, rows))
        elif c == "conventions":
            blocks.append(("conv", [(plain(inl(i.select_one(".conv-label"))), inl(i.select_one(".conv-value"))) for i in el.select(".convention-item")]))
        elif c == "structure-card":
            st = []
            for d in el.select(".step"):
                sc = d.select_one(".step-content"); title = sc.find("strong"); body = sc.find("span")
                st.append((plain(inl(d.select_one(".step-num"))), inl(title) if title else [], inl(body) if body else []))
            blocks.append(("steps", st))
        elif c == "mnemonic":
            runs = []
            for sp in el.find_all("span", recursive=False):
                if runs: runs.append((" ", frozenset()))
                runs += inl(sp)
            blocks.append(("mnemonic", runs))
        elif el.name == "figure": nfig[0] += 1; blocks.append(figure(el, f"{n:02d}-{slug}-{nfig[0]}"))
        elif c in ("tip-box", "mistake-box", "example-block"):
            lab = el.select_one(".tip-label,.mistake-label,.ex-label"); label = plain(inl(lab)); lab.extract()
            kind = {"tip-box": "tip", "mistake-box": "mistake", "example-block": "example"}[c]
            if el.find(BLOCKY, recursive=False): blocks.append(("box", kind, label, [], box_parts(el, n, slug, nfig)))
            else: blocks.append(("box", kind, label, inl(el)))
        elif c == "checklist":
            blocks.append(("checklist", plain(inl(el.h4)), [inl(li) for li in el.select("li")]))
        else: raise SystemExit(f"unhandled {el.name}.{c} in {slug}")
    # diagram: same placement rule as the PDF build
    e = MANIFEST.get(slug)
    if not e and not (DIAG/f"{n:02d}-{slug}.svg").exists(): return meta, blocks  # topic without a separate diagram
    fig = ("figure", f"{n:02d}-{slug}", e["caption"] if e else "")
    pos = 0
    if e and e.get("after_h3"):
        tgt = re.sub(r"\s+", " ", e["after_h3"]).strip().lower()
        for i, b in enumerate(blocks):
            if b[0] == "h" and b[1] == 3:
                full = (("supplement " if b[3] else "") + plain(b[2])).lower()
                if tgt in full or tgt in plain(b[2]).lower():
                    j = i + 1
                    while j < len(blocks) and not (blocks[j][0] == "h" and blocks[j][1] == 3) and blocks[j][0] != "checklist": j += 1
                    pos = j; break
        else: raise SystemExit(f"diagram anchor not found {slug}")
    blocks.insert(pos, fig)
    return meta, blocks

def all_topics():
    return [(n, slug, title, grp, *parse(n, slug)) for n, slug, title, grp in TOPICS]
if __name__ == "__main__":
    for n, slug, title, grp, meta, blocks in all_topics():
        print(n, title, len(blocks), [i for i, b in enumerate(blocks) if b[0] == "figure"], meta["badge"])
