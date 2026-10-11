import re, shutil, pathlib
from ir import all_topics, HOWTO, COVER_SUB, BACK, FOOTER
import os
from ir import SUBJ, DIAG
CFG = {"chem": ("Chemistry", "0620"), "bio": ("Biology", "0610"), "econ": ("Economics", "0455")}[SUBJ]
YEARS = "2027–2029" if SUBJ == "econ" else "2026–2028"
OUT = pathlib.Path(f"out/{CFG[0]} {CFG[1]} Vault")
SUB = str.maketrans("0123456789+-−=()aeoxhklmnpst", "₀₁₂₃₄₅₆₇₈₉₊₋₋₌₍₎ₐₑₒₓₕₖₗₘₙₚₛₜ")
SUP = str.maketrans("0123456789+-−=()n", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁻⁼⁽⁾ⁿ")
UNMAPPED = set()
RELATED_CHEM = {1:[2,12],2:[1,3,8],3:[2,4,7],4:[2,6,9],5:[6,11],6:[3,4,5],7:[3,8,12],8:[2,7,9],9:[4,8,10],10:[9,11],11:[5,10],12:[1,7]}
RELATED_BIO = {1:[2,18],2:[1,3],3:[2,8,13],4:[5,7],5:[4,7,12],6:[8,12,19],7:[4,5,9],8:[3,6,9],9:[8,10,11],10:[9,15],11:[9,12],12:[5,6,11],13:[3,9],14:[15,16],15:[10,14],16:[14,17],17:[16,18,20],18:[17,1],19:[6,21],20:[17,21],21:[19,20]}
RELATED_ECON = {0:[1,7],1:[0,2,7],2:[1,3,8],3:[2,8],4:[5,9],5:[4,6,10],6:[5,10],7:[0,1],8:[2,3],9:[4],10:[5,6]}
RELATED = {"bio": RELATED_BIO, "chem": RELATED_CHEM, "econ": RELATED_ECON}[SUBJ]
def script(t, table, k):
    if all(c in table_keys[k] for c in t): return t.translate(table)
    UNMAPPED.add(t); return f"<{k}>{t}</{k}>"
table_keys = {"sub": set("0123456789+-−=()aeoxhklmnpst"), "sup": set("0123456789+-−=()n")}
def md(runs, cell=False):
    out = []
    for t, f in runs:
        if t == "\n": out.append("<br>" if cell else "\n"); continue
        if "ext" in f: out.append("(Ext) #supplement"); continue
        if cell: t = t.replace("|", "\\|")
        if "sub" in f: t = script(t, SUB, "sub")
        elif "sup" in f: t = script(t, SUP, "sup")
        if "b" in f and t.strip():
            lead, core, trail = re.match(r"(\s*)(.*?)(\s*)$", t, re.S).groups(); t = f"{lead}**{core}**{trail}"
        out.append(t)
    s = "".join(out).replace("****", "")
    return s
def name(n, title, grp=""): return f"{n:02d} " + ("Model Answers - " if grp.startswith("Past Paper") else "") + title.replace(":", " -")  # no colons in file names (Windows/iOS)
def box_parts(parts):
    """multi-paragraph boxes (Economics model answers) -> callout lines"""
    L = []
    for i, p in enumerate(parts):
        if i: L += [">"]
        if p[0] == "p": L += ["> " + line for line in md(p[1]).split("\n")]
        elif p[0] in ("ul", "ol"): L += ["> " + ("- " if p[0] == "ul" else f"{j+1}. ") + md(r) for j, r in enumerate(p[1])]
        elif p[0] == "figure": L += [f"> ![[{p[1]}.png]]", f"> *{p[2]}*"]
    return L
def emit(n, title, meta, blocks, names):
    L = [f"# {title}", "", f"*{meta['badge']}*  ", md(meta["purpose"]), "",
         "**Related:** " + " · ".join(f"[[{names[r]}]]" for r in RELATED[n]) + f" · [[{CFG[0]} {CFG[1]} - Start Here|Start Here]]", ""]
    for b in blocks:
        k = b[0]
        if k == "h":
            L += [("## " if b[1] == 3 else "### ") + md(b[2]) + (" (Ext)" if b[3] else "")]
            if b[3]: L += ["#supplement"]
            L += [""]
        elif k == "p": L += [md(b[1]), ""]
        elif k in ("ul", "ol"):
            L += [("- " if k == "ul" else f"{i+1}. ") + md(r).replace("\n", "\n  ") for i, r in enumerate(b[1])] + [""]
        elif k == "table":
            L += ["| " + " | ".join(md(h, True) for h in b[1]) + " |", "|" + "---|" * len(b[1])]
            L += ["| " + " | ".join(md(c, True) for c in r) + " |" for r in b[2]] + [""]
        elif k == "conv": L += [f"- **{lab}:** {md(v)}" for lab, v in b[1]] + [""]
        elif k == "steps": L += [f"{num}. **{md(t)}** — {md(body)}" for num, t, body in b[1]] + [""]
        elif k == "mnemonic": L += ["> " + md(b[1]), ""]
        elif k == "box":
            kind = {"tip": "tip", "mistake": "warning", "example": "example"}[b[1]]
            L += [f"> [!{kind}] {b[2]}"]
            if len(b) > 4: L += box_parts(b[4])
            else: L += ["> " + line for line in md(b[3]).split("\n")]
            L += [""]
        elif k == "checklist": L += [f"### {b[1]}", ""] + [f"- [ ] {md(r)}" for r in b[2]] + [""]
        elif k == "figure": L += [f"![[{b[1]}.png]]", f"*{b[2]}*", ""]
    L += ["---", f"*{FOOTER}*", ""]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(L))
if __name__ == "__main__":
    if OUT.exists(): shutil.rmtree(OUT)
    (OUT/"assets").mkdir(parents=True)
    for f in pathlib.Path(f"assets-{SUBJ}").iterdir(): shutil.copy(f, OUT/"assets"/f.name)
    T = all_topics(); names = {n: name(n, t, g) for n, s, t, g, m, b in T}
    idx = [f"# {CFG[0]} {CFG[1]} - Start Here", "", f"**Cambridge IGCSE {CFG[1]} · {YEARS} syllabus · Revision Notes by Paula**", "", COVER_SUB, "",
           "**Key:** " + ("" if SUBJ == "econ" else "(Ext) / #supplement = Extended tier only (Papers 2 & 4) · ") + "tip boxes = examiner tips · warning boxes = common mistakes · [ ] = tick-off checklist", "", "## Contents", ""]
    grp = None
    for n, s, t, g, meta, blocks in T:
        if g != grp: idx += ["", f"### {g}"]; grp = g
        idx.append(f"{n}. [[{names[n]}]]")
        (OUT/f"{names[n]}.md").write_text(emit(n, t, meta, blocks, names))
    idx += ["", "## How to use these notes", ""] + [f"{i+1}. {h}" for i, h in enumerate(HOWTO)]
    idx += ["", f"## {BACK[0]}", "", BACK[1], "", f"**{BACK[2]}**", "", BACK[3], "", "---", f"*{FOOTER}*", ""]
    (OUT/f"{CFG[0]} {CFG[1]} - Start Here.md").write_text("\n".join(idx))
    print("unmapped sub/sup kept as HTML:", sorted(UNMAPPED))
