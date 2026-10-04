#!/usr/bin/env python3
"""Build resources/search-index.json from the notes pages.

Run from the repository root after changing any notes page:
    python3 tools/build-search-index.py
"""
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = [
    ("Biology", "igcse-biology-notes"),
    ("Chemistry", "igcse-chemistry-notes"),
    ("Economics", "igcse-economics-notes"),
    ("Accounting", "igcse-accounting-notes"),
    ("Business", "igcse-business-notes"),
    ("English", "igcse-english-writing-forms"),
]


def text(fragment):
    fragment = re.sub(r"<(script|style|svg)\b.*?</\1>", " ", fragment, flags=re.S)
    fragment = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html.unescape(fragment)).strip()


entries = []
for subject, slug in PAGES:
    page = (ROOT / "resources" / slug / "index.html").read_text()
    main = page[page.index('<main class="main">'):page.index("</main>")]
    # each notes section is a <div class="section ..." id="sec-...">
    starts = [m for m in re.finditer(r'<div class="section[^"]*" id="sec-([a-z0-9-]+)">', main)]
    for i, m in enumerate(starts):
        body = main[m.end():starts[i + 1].start() if i + 1 < len(starts) else len(main)]
        title = text(re.search(r"<h2>(.*?)</h2>", body, re.S).group(1))
        # split the section into chunks at each <h3>; the part before the first h3 is the intro
        parts = re.split(r"(<h3>.*?</h3>)", body, flags=re.S)
        heading, chunk = "", parts[0]
        for part in parts[1:] + [None]:
            if part is None or part.startswith("<h3>"):
                t = text(chunk)
                if t:
                    entries.append({"s": subject, "u": f"{slug}/", "id": m.group(1),
                                    "t": title, "h": heading, "x": t})
                if part is not None:
                    heading, chunk = text(part), ""
            else:
                chunk += part

out = ROOT / "resources" / "search-index.json"
out.write_text(json.dumps(entries, ensure_ascii=False, separators=(",", ":")))
print(f"{len(entries)} entries, {out.stat().st_size // 1024} KB -> {out.relative_to(ROOT)}")
