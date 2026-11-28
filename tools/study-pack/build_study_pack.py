#!/usr/bin/env python3
"""Build a sellable study pack for one subject from its live notes page.

    python3 tools/study-pack/build_study_pack.py chemistry --out <folder outside the repo>

Makes, from resources/igcse-<subject>-notes/index.html (notes only; past-paper sections are left out):
  1 Compact Revision Notes  - one PDF, all sections, compact layout, each topic on a new page, contents + bookmarks
  2 Detailed Notes/         - one PDF per section (Exam Guide, each topic, Illustrated Examples), spacious, own cover
  3 Obsidian Vault/         - one Markdown note per section, Start Here index, [[links]], #supplement tags, diagrams as PNG
  READ ME FIRST.txt         - what each file is and how to open it
and zips them as IGCSE-<Subject>-Study-Pack.zip. Every PDF page carries "© Paula" + "personal use only" and a faint
watermark; PDFs open without a password, with copying/editing switched off (random owner password, not stored).
Nothing in the pack mentions or links to the free website. Wording is not changed (format conversion only).
Needs: pip install pymupdf beautifulsoup4 lxml ; Playwright + Chromium (preinstalled in Claude cloud sessions).
"""
import argparse, base64, datetime, html, json, os, re, secrets, shutil, subprocess, sys, tempfile, zipfile
from bs4 import BeautifulSoup, NavigableString, Tag
import pymupdf as fitz

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
FONTS = os.path.join(REPO, 'tools', 'offline-edition', 'fonts')
YEAR = datetime.date.today().year
FOOT = f'© {YEAR} Paula · IGCSE & A Level Tutor · For personal use only — please do not share or resell'

ap = argparse.ArgumentParser()
ap.add_argument('subject', help='e.g. chemistry (page folder igcse-<subject>-notes)')
ap.add_argument('--out', required=True)
a = ap.parse_args()
OUT = os.path.abspath(os.path.expanduser(a.out))
if OUT == REPO or OUT.startswith(REPO + os.sep):
    sys.exit('--out must be outside the repository (the pack is a paid product)')
SLUG = f'igcse-{a.subject}-notes'
page = open(os.path.join(REPO, 'resources', SLUG, 'index.html')).read()
soup = BeautifulSoup(page, 'lxml')
SUBJECT = re.sub(r'^IGCSE\s+|\s+Notes$', '', soup.select_one('.sidebar h1').get_text(strip=True))   # Chemistry
SYL = soup.select_one('.sidebar .syllabus').get_text(' ', strip=True).replace('·', '·')            # Cambridge IGCSE 0620 · 2026–2028 Syllabus
CODE = re.search(r'\b0\d{3}\b', SYL).group(0)
YEARS = (re.search(r'\d{4}\D\d{4}', SYL) or re.search(r'\d{4}', SYL)).group(0)
PACK = f'IGCSE-{SUBJECT.replace(" ", "-")}-Study-Pack'
ROOT = os.path.join(OUT, PACK)
if os.path.exists(ROOT):
    shutil.rmtree(ROOT)
os.makedirs(ROOT)
work = tempfile.mkdtemp(prefix='studypack-')

# ------------------------------------------------------------------ sections (notes only)
sections = []
for sec in soup.select('div.section'):
    sid = sec['id'][4:]
    if sid.startswith('pp-'):
        continue
    for x in sec.select('a.pp-link-box, .licence-line'):
        x.decompose()
    title = sec.select_one('.section-header h2').get_text(' ', strip=True)
    badge = sec.select_one('.section-header .form-badge')
    m = re.match(r'Topic (\d+)', badge.get_text(strip=True)) if badge else None
    sections.append(dict(id=sid, el=sec, title=title, badge=badge.get_text(' ', strip=True) if badge else '',
                         num=int(m.group(1)) if m else None,
                         purpose=(sec.select_one('.section-header .purpose') or Tag(name='p')).get_text(' ', strip=True)))
# file numbers: start-here sections 00, topics by number, extras after the last topic
last = max([s['num'] for s in sections if s['num']] or [0])
extra = 0
for s in sections:
    if s['num'] is None:
        if sections.index(s) == 0 or not any(t['num'] for t in sections[:sections.index(s)]):
            s['n'] = 0
        else:
            extra += 1; s['n'] = last + extra
    else:
        s['n'] = s['num']
    short = re.sub(r':.*$', '', s['title']).strip()           # "Illustrated Examples: See the Chemistry" -> "Illustrated Examples"
    s['short'] = short
    s['file'] = f'{s["n"]:02d} {re.sub(r"[^A-Za-z0-9 ,&()-]+", "", short)}'
by_id = {s['id']: s for s in sections}
ID_OWNER = {}
for s in sections:
    for el in s['el'].select('[id]'):
        ID_OWNER[el['id']] = s['id']
    ID_OWNER[s['id']] = s['id']

def clean_links(sec_el):
    for a_ in sec_el.select('a[href]'):
        h = a_['href']
        a_.attrs.pop('onclick', None)
        if h.startswith('#'):
            t = h[1:]
            a_['href'] = '#sec-' + t if t in by_id else ('#' + t if t in ID_OWNER else '#')
        elif not h.startswith('https://wa.me'):
            a_.unwrap()                                       # no links to the website
for s in sections:
    clean_links(s['el'])
    s['html'] = str(s['el']).replace('class="section active"', 'class="section"')

# ------------------------------------------------------------------ print HTML -> PDF
style = page[page.index('<style>') + 7:page.index('</style>')]
def font64(n):
    return base64.b64encode(open(os.path.join(FONTS, n), 'rb').read()).decode()
FONTCSS = (f"@font-face{{font-family:'DM Sans';font-weight:100 1000;src:url(data:font/woff2;base64,{font64('DMSans-latin-var.woff2')}) format('woff2')}}"
           f"@font-face{{font-family:'DM Mono';font-weight:400;src:url(data:font/woff2;base64,{font64('DMMono-400.woff2')}) format('woff2')}}"
           f"@font-face{{font-family:'DM Mono';font-weight:500;src:url(data:font/woff2;base64,{font64('DMMono-500.woff2')}) format('woff2')}}")
PRINT = '''
html, body { background: #fff !important; }
/* shadows and blurs would be turned into pictures in the PDF (big files): borders are enough on paper */
*, *::before, *::after { box-shadow: none !important; text-shadow: none !important; filter: none !important; backdrop-filter: none !important; }
body { margin: 0; }
.pack { max-width: none !important; padding: 0 !important; margin: 0 !important; }
.pack .section { display: block !important; break-before: page; }
.pack .section:first-child { break-before: auto; }
.pack figure, .pack .tip-box, .pack .mistake-box, .pack .conventions, .pack .mnemonic, .pack tr { break-inside: avoid; }
.pack h3, .pack h4 { break-after: avoid; }
.pack .table-wrap { overflow: visible !important; }
.pack a { color: inherit; text-decoration: none; }
.cover { break-after: page; min-height: 250mm; display: flex; flex-direction: column; justify-content: center; padding: 0 6mm; }
.cover .k { font-family: 'DM Mono', monospace; font-size: 13px; letter-spacing: .1em; text-transform: uppercase; color: #2563eb; }
.cover h1 { font-size: 46px; line-height: 1.05; letter-spacing: -.03em; color: #0a1628; margin: 14px 0 16px; }
.cover .sub { font-size: 17px; color: #46546a; max-width: 560px; line-height: 1.55; }
.cover .by { margin-top: 40px; padding-top: 18px; border-top: 1px solid #e1e7f0; font-size: 15px; color: #0a1628; }
.cover .by span { display: block; color: #5d6b80; font-size: 13px; margin-top: 4px; }
.cover .bar { width: 64px; height: 6px; border-radius: 3px; background: linear-gradient(90deg, #2563eb, #4a90d9); margin-bottom: 26px; }
.toc { break-after: page; }
.toc h2 { font-size: 26px; color: #0a1628; margin-bottom: 14px; }
.toc ol { list-style: none; padding: 0; }
.toc li { display: flex; gap: 10px; padding: 8px 0; border-bottom: 1px solid #e1e7f0; font-size: 15px; color: #0a1628; }
.toc li .no { font-family: 'DM Mono', monospace; color: #2563eb; width: 28px; }
.toc li .t { flex: 1; }
.toc li .pg { font-family: 'DM Mono', monospace; color: #5d6b80; }
.toc .key { margin-top: 18px; font-size: 13px; color: #5d6b80; line-height: 1.6; }
'''
COMPACT = '.pack { font-size: 14px; } .pack .section-header { margin-bottom: 14px; } .pack p, .pack li { line-height: 1.5; }'
DETAILED = '.pack .section { break-before: auto; } .pack p, .pack li { line-height: 1.75; } .pack h3 { margin-top: 34px; }'

def doc_html(body, extra_css):
    return (f'<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><style>{FONTCSS}\n{style}\n{PRINT}\n{extra_css}</style>'
            f'</head><body><main class="main pack">{body}</main></body></html>')

def cover(kicker, title, sub):
    return (f'<div class="cover"><div class="bar"></div><div class="k">{html.escape(kicker)}</div><h1>{html.escape(title)}</h1>'
            f'<p class="sub">{html.escape(sub)}</p><div class="by">Written by Paula<span>IGCSE, GCSE &amp; A Level Tutor · Kuala Lumpur · '
            f'WhatsApp +60 10-368 6902</span></div></div>')

def toc(pages=None):
    rows = ''.join(f'<li><span class="no">{s["n"]:02d}</span><a class="t" href="#sec-{s["id"]}">{html.escape(s["title"])}</a>'
                   f'<span class="pg">{pages[i] if pages else "00"}</span></li>' for i, s in enumerate(sections))
    return (f'<div class="toc"><h2>Contents</h2><ol>{rows}</ol><p class="key"><strong>Supplement</strong> = Extended tier only '
            f'(Papers 2 and 4). <strong>Background</strong> = useful context beyond the {YEARS} syllabus, not examined. '
            f'Tip boxes are examiner tips; red boxes are common mistakes; tick the checklist at the end of each topic.</p></div>')

NODE = r'''
const { chromium } = require('playwright');
const jobs = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8'));
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.emulateMedia({ media: 'screen' });
  for (const j of jobs) {
    await p.goto('file://' + j.html, { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    if (j.pdf) await p.pdf({ path: j.pdf, format: 'A4', printBackground: true, scale: j.scale,
                             margin: { top: j.m, bottom: j.mb, left: j.m, right: j.m } });
    if (j.figs) {
      await p.setViewportSize({ width: 760, height: 1000 });
      const els = await p.$$('figure.diagram');
      for (let i = 0; i < els.length; i++) await els[i].screenshot({ path: j.figs + '/fig-' + String(i + 1).padStart(3, '0') + '.png' });
    }
  }
  await b.close();
})();
'''
node_js = os.path.join(work, 'render.js')
open(node_js, 'w').write(NODE)

def render(jobs):
    jf = os.path.join(work, 'jobs.json')
    json.dump(jobs, open(jf, 'w'))
    r = subprocess.run(['node', node_js, jf], capture_output=True, text=True, cwd=work,
                       env=dict(os.environ, NODE_PATH=subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()))
    if r.returncode:
        sys.exit(r.stderr[-2000:])

def finish_pdf(path, title, skip_first=True):
    d = fitz.open(path)
    n = len(d)
    for i, pg in enumerate(d):
        if skip_first and i == 0:
            continue
        w, h = pg.rect.width, pg.rect.height
        pg.insert_text((w / 2 - 150, h / 2 + 40), '© Paula · IGCSE Tutor', fontsize=34, color=(0.04, 0.09, 0.16),
                       fill_opacity=0.045, stroke_opacity=0.045, morph=(fitz.Point(w / 2, h / 2), fitz.Matrix(-30)))
        pg.insert_text((36, h - 18), FOOT, fontsize=7.5, color=(0.36, 0.42, 0.5))
        lab = f'{i + 1} / {n}'
        pg.insert_text((w - 36 - fitz.get_text_length(lab, fontsize=8), h - 18), lab, fontsize=8, color=(0.36, 0.42, 0.5))
    d.set_metadata({'title': title, 'author': 'Paula — IGCSE & A Level Tutor', 'subject': f'Cambridge IGCSE {SUBJECT} {CODE}',
                    'creator': 'Paula', 'producer': 'Paula'})
    perms = fitz.PDF_PERM_PRINT | fitz.PDF_PERM_PRINT_HQ | fitz.PDF_PERM_ACCESSIBILITY
    tmp = path + '.tmp'
    d.save(tmp, encryption=fitz.PDF_ENCRYPT_AES_256, owner_pw=secrets.token_urlsafe(24), user_pw='', permissions=perms,
           garbage=3, deflate=True)
    d.close()
    os.replace(tmp, path)

def section_pages(path, first=0):
    """first page (1-based) of each section, found by its h2 text (search starts after the cover/contents)."""
    d = fitz.open(path)
    out, start = [], first
    for s in sections:
        key = re.sub(r'\s+', ' ', s['title'])[:40]
        for i in range(start, len(d)):
            if key in re.sub(r'\s+', ' ', d[i].get_text()):
                out.append(i + 1); start = i; break
        else:
            out.append(None)
    d.close()
    return out

# compact: two passes so the contents page shows real page numbers
cname = f'1 {SUBJECT} {CODE} - Compact Revision Notes.pdf'
cpath = os.path.join(ROOT, cname)
cbody = lambda pages: (cover(f'Cambridge IGCSE {SUBJECT} {CODE} · {YEARS} syllabus', f'IGCSE {SUBJECT} Compact Revision Notes',
                             f'Every topic in one file: key ideas, definitions, equations, worked examples, diagrams, examiner tips and a checklist for each topic.')
                       + toc(pages) + ''.join(s['html'] for s in sections))
chtml = os.path.join(work, 'compact.html')
open(chtml, 'w').write(doc_html(cbody(None), COMPACT))
render([dict(html=chtml, pdf=cpath, scale=0.8, m='12mm', mb='16mm')])
pages = section_pages(cpath, first=2)
open(chtml, 'w').write(doc_html(cbody([p or '' for p in pages]), COMPACT))
render([dict(html=chtml, pdf=cpath, scale=0.8, m='12mm', mb='16mm', figs=None)])
pages = section_pages(cpath, first=2)
d = fitz.open(cpath)
d.set_toc([[1, f'{s["n"]:02d} {s["title"]}', p] for s, p in zip(sections, pages) if p])
d.saveIncr(); d.close()
finish_pdf(cpath, f'IGCSE {SUBJECT} {CODE} — Compact Revision Notes')

# detailed: one PDF per section, own cover
ddir = os.path.join(ROOT, '2 Detailed Notes')
os.makedirs(ddir)
jobs = []
for s in sections:
    h = os.path.join(work, f'd-{s["id"]}.html')
    kick = f'Detailed Notes · Cambridge IGCSE {SUBJECT} {CODE}' + (f' · Topic {s["num"]}' if s['num'] else '')
    open(h, 'w').write(doc_html(cover(kick, s['title'], s['purpose']) + s['html'], DETAILED))
    s['pdf'] = os.path.join(ddir, f'{s["file"]}.pdf')
    jobs.append(dict(html=h, pdf=s['pdf'], scale=0.92, m='18mm', mb='20mm'))
render(jobs)
for s in sections:
    finish_pdf(s['pdf'], f'IGCSE {SUBJECT} {CODE} — {s["title"]} (Detailed Notes)')

# ------------------------------------------------------------------ Obsidian vault
VAULT = os.path.join(ROOT, f'3 {SUBJECT} {CODE} Obsidian Vault')
os.makedirs(os.path.join(VAULT, 'assets'))
# diagrams -> PNG (rendered from the compact HTML, in page order)
figdir = os.path.join(work, 'figs'); os.makedirs(figdir)
fhtml = os.path.join(work, 'figs.html')
open(fhtml, 'w').write(doc_html(''.join(s['html'] for s in sections), COMPACT))
render([dict(html=fhtml, pdf=None, figs=figdir)])
fig_files = sorted(os.listdir(figdir))
fig_iter = iter(fig_files)

SUB = str.maketrans('0123456789+-−=()', '₀₁₂₃₄₅₆₇₈₉₊₋₋₌₍₎')
SUP = str.maketrans('0123456789+-−=()n', '⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁻⁼⁽⁾ⁿ')
def script(t, kind):
    keys = '0123456789+-−=()' + ('n' if kind == 'sup' else '')
    return t.translate(SUB if kind == 'sub' else SUP) if t and all(c in keys for c in t) else f'<{kind}>{t}</{kind}>'

def link_target(href):
    t = href[1:]
    if t.startswith('sec-'):
        t = t[4:]
    owner = ID_OWNER.get(t)
    return by_id[owner]['file'] if owner else None

def inline(node):
    out = []
    for ch in node.children:
        if isinstance(ch, NavigableString):
            out.append(re.sub(r'\s+', ' ', str(ch)))
            continue
        if not isinstance(ch, Tag):
            continue
        cls = ch.get('class') or []
        if ch.name == 'br':
            out.append('<br>')
        elif 'key-term' in cls:
            out.append(' *(Background)* ' if 'bg-term' in cls else ' *(Supplement)* #supplement ')
        elif ch.name in ('strong', 'b'):
            t = inline(ch).strip(); out.append(f'**{t}**' if t else '')
        elif ch.name in ('em', 'i'):
            t = inline(ch).strip(); out.append(f'*{t}*' if t else '')
        elif ch.name in ('sub', 'sup'):
            out.append(script(ch.get_text(), ch.name))
        elif ch.name == 'a':
            t = inline(ch).strip(); tgt = link_target(ch.get('href', '')) if ch.get('href', '').startswith('#') else None
            out.append(f'[[{tgt}|{t}]]' if tgt else (f'[{t}]({ch["href"]})' if ch.get('href', '').startswith('https://wa.me') else t))
        elif ch.name in ('svg', 'script', 'style'):
            continue
        else:
            out.append(inline(ch))
    s = ''.join(out)
    return re.sub(r'[ \t]+', ' ', s)

def cell(td):
    parts = []
    for ch in td.children:
        if isinstance(ch, Tag) and ch.name in ('ul', 'ol'):
            parts += ['• ' + inline(li).strip() for li in ch.find_all('li', recursive=False)]
        elif isinstance(ch, Tag) and ch.name == 'p':
            parts.append(inline(ch).strip())
        else:
            parts.append(inline(BeautifulSoup(f'<x>{ch}</x>', 'lxml').x).strip() if isinstance(ch, Tag) else re.sub(r'\s+', ' ', str(ch)).strip())
    return '<br>'.join(p for p in parts if p).replace('|', '\\|')

def figure(fig):
    f = next(fig_iter)
    new = f'{fig_files.index(f) + 1:03d}.png'
    shutil.copy(os.path.join(figdir, f), os.path.join(VAULT, 'assets', new))
    cap = fig.find('figcaption')
    return [f'![[{new}]]'] + ([f'*{inline(cap).strip()}*'] if cap else []) + ['']

INLINE_TAGS = {'strong', 'b', 'em', 'i', 'sub', 'sup', 'a', 'span', 'br', 'code', 'small', 'u'}

def heading(tag, level):
    t = inline(tag).strip()
    sup = '#supplement' in t
    t = re.sub(r'\s*\*\((Supplement|Background)\)\*\s*(#supplement)?\s*', ' ', t).strip()
    bg = '(Background)' in inline(tag)
    return [level + ' ' + t + (' *(Supplement)*' if sup else '') + (' *(Background)*' if bg else '')] + (['#supplement'] if sup else []) + ['']

def blocks(el, depth=0):
    L = []
    buf = []                                   # loose inline content (text, <strong>, <sub>, <br> ...) forms one paragraph
    def flush():
        if not buf:
            return
        holder = BeautifulSoup('<x></x>', 'lxml').x
        for n in buf:
            holder.append(n.__copy__() if isinstance(n, Tag) else NavigableString(str(n)))
        lines = [x.strip() for x in inline(holder).split('<br>')]
        lines = [x for x in lines if x]
        if lines:
            L.extend(lines + [''])
        buf.clear()
    for ch in list(el.children):
        if isinstance(ch, NavigableString) or (isinstance(ch, Tag) and ch.name in INLINE_TAGS and not (ch.get('class') or [''])[0] in ('tip-label', 'mistake-label', 'ex-label', 'bg-label')):
            buf.append(ch)
            continue
        flush()
        if not isinstance(ch, Tag):
            continue
        cls = (ch.get('class') or [''])[0]
        if cls in ('section-header',) or ch.name in ('script', 'style'):
            continue
        if ch.name == 'h3':
            L += heading(ch, '##')
        elif ch.name == 'h4':
            L += heading(ch, '###')
        elif ch.name == 'p':
            t = inline(ch).strip()
            if t: L += [t, '']
        elif ch.name in ('ul', 'ol'):
            for i, li in enumerate(ch.find_all('li', recursive=False)):
                sub = li.find(['ul', 'ol'], recursive=False)
                if sub: sub.extract()
                L.append(('- ' if ch.name == 'ul' else f'{i + 1}. ') + inline(li).strip())
                if sub:
                    L += ['    - ' + inline(x).strip() for x in sub.find_all('li', recursive=False)]
            L.append('')
        elif cls == 'table-wrap' or ch.name == 'table':
            t = ch if ch.name == 'table' else ch.find('table')
            rows = t.find_all('tr')
            head = [cell(x) for x in rows[0].find_all(['th', 'td'])]
            L += ['| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)]
            for r in rows[1:]:
                c = [cell(x) for x in r.find_all(['th', 'td'])]
                L.append('| ' + ' | '.join(c + [''] * (len(head) - len(c))) + ' |')
            L.append('')
        elif ch.name == 'figure':
            L += figure(ch)
        elif cls in ('tip-box', 'mistake-box', 'example-block', 'background-note'):
            lab = ch.select_one('.tip-label, .mistake-label, .ex-label, .bg-label')
            label = inline(lab).strip() if lab else ''
            if lab: lab.extract()
            kind = {'tip-box': 'tip', 'mistake-box': 'warning', 'example-block': 'example', 'background-note': 'note'}[cls]
            inner = blocks(ch, depth + 1)
            if not any(x.strip() for x in inner):
                inner = [inline(ch).strip()]
            L += [f'> [!{kind}] {label}'] + [('> ' + x) if x else '>' for x in inner]
            while L and L[-1] == '>': L.pop()
            L.append('')
        elif cls == 'checklist':
            h = ch.find(['h4', 'h3'])
            L += [f'### {inline(h).strip() if h else "Checklist"}', ''] + [f'- [ ] {inline(li).strip()}' for li in ch.select('li')] + ['']
        elif cls == 'conventions':
            for it in ch.select('.convention-item'):
                lab = it.select_one('.conv-label'); val = it.select_one('.conv-value')
                L.append(f'- **{inline(lab).strip() if lab else ""}:** {inline(val).strip() if val else ""}')
            L.append('')
        elif cls == 'structure-card':
            for st in ch.select('.step'):
                num = st.select_one('.step-num'); sc = st.select_one('.step-content')
                t = sc.find('strong'); body = sc.find('span')
                L.append(f'{num.get_text(strip=True) if num else "-"}. **{inline(t).strip() if t else ""}** — {inline(body).strip() if body else ""}')
            L.append('')
        elif cls == 'mnemonic':
            L += ['> ' + ' '.join(inline(sp).strip() for sp in ch.find_all('span', recursive=False)), '']
        else:
            inner = blocks(ch, depth + 1)
            L += inner if any(x.strip() for x in inner) else ([inline(ch).strip(), ''] if inline(ch).strip() else [])
    flush()
    return L

start = f'{SUBJECT} {CODE} - Start Here'
for i, s in enumerate(sections):
    nav = []
    if i: nav.append(f'← [[{sections[i - 1]["file"]}]]')
    nav.append(f'[[{start}|Start Here]]')
    if i + 1 < len(sections): nav.append(f'[[{sections[i + 1]["file"]}]] →')
    L = [f'# {s["title"]}', '', f'*{s["badge"]}*', '', s['purpose'], '', ' · '.join(nav), ''] + blocks(s['el']) + ['---', ' · '.join(nav), '', f'*{FOOT}*', '']
    md = re.sub(r'\n{3,}', '\n\n', '\n'.join(L))
    open(os.path.join(VAULT, s['file'] + '.md'), 'w').write(md)
idx = [f'# {SUBJECT} {CODE} - Start Here', '', f'**Cambridge IGCSE {SUBJECT} {CODE} · {YEARS} syllabus · Revision notes by Paula**', '',
       '## Contents', ''] + [f'- [[{s["file"]}]]' for s in sections] + [
       '', '## Key', '', '- *(Supplement)* and the tag #supplement = Extended tier only (Papers 2 and 4). Click the tag to list every Supplement section.',
       f'- *(Background)* = useful context beyond the {YEARS} syllabus; not examined.',
       '- Tip boxes = examiner tips · warning boxes = common mistakes · example boxes = worked examples · [ ] = checklist you can tick.', '',
       '## How to use these notes', '', '1. Work through one topic at a time; read the diagrams first.',
       '2. Learn definitions word for word and redo each worked example without looking.',
       '3. Add your own notes, highlights and links: this vault is yours to edit.',
       '4. Tick the checklist at the end of each topic when you can do every point.', '',
       '---', f'*{FOOT}*', '']
open(os.path.join(VAULT, start + '.md'), 'w').write('\n'.join(idx))

# ------------------------------------------------------------------ README + zip
total_pages = sum(len(fitz.open(s['pdf'])) for s in sections)
readme = f'''IGCSE {SUBJECT.upper()} STUDY PACK  ·  Cambridge IGCSE {SUBJECT} {CODE}  ·  {YEARS} syllabus
Written by Paula, IGCSE, GCSE & A Level Tutor (Kuala Lumpur)
==========================================================================================

Thank you for buying this pack! Here is what is inside and how to open each part.

WHAT'S INSIDE
-------------
• {cname}
   All {len(sections)} sections in one PDF ({len(fitz.open(cpath))} pages): the exam guide, every syllabus topic and the
   illustrated worked examples. Each topic starts on a new page; the contents page and the bookmarks are clickable.
   Best for: quick revision, printing, last-minute review.

• 2 Detailed Notes (folder)
   One PDF per section ({len(sections)} files, {total_pages} pages in total), with a spacious layout and its own cover.
   Best for: learning a topic properly, reading on a tablet, writing on with a stylus.

• 3 {SUBJECT} {CODE} Obsidian Vault (folder)
   The same notes as {len(sections)} linked Markdown notes plus a "Start Here" page, with the diagrams as images.
   Best for: students who like to edit, highlight, add their own notes and link ideas together.

The three formats contain the same notes, so use whichever suits you.

HOW TO OPEN THE FILES
---------------------
• First, unzip (extract) the pack. On a phone: open the .zip in the Files app and tap Extract/Unzip.
• PDFs: open with any PDF reader (phone, tablet, laptop). To write on them, import into GoodNotes, Notability,
  Samsung Notes, OneNote or Xodo. The PDFs print normally.
• Obsidian: download Obsidian (free) from obsidian.md, choose "Open folder as vault", and pick the
  "{SUBJECT} {CODE} Obsidian Vault" folder. Start with "{start}".
  (Any Markdown app also works; the files are plain text.)

READING THE NOTES
-----------------
• "Supplement" marks Extended-tier content (Papers 2 and 4). Core students can skip it.
• "Background" marks useful context beyond the {YEARS} syllabus; it is not examined.
• Blue boxes are examiner tips, red boxes are common mistakes, and every topic ends with a checklist.
• The notes follow the Cambridge IGCSE {SUBJECT} {CODE} syllabus for examination in {YEARS.replace("–", " to ").replace("-", " to ")}.

PLEASE NOTE
-----------
This pack is for your own personal study only. Please do not share, upload, forward or resell the files.
Each PDF page carries a copyright line. © {YEAR} Paula. All rights reserved.

NEED HELP?
----------
I offer one-to-one IGCSE, GCSE and A Level lessons, online or in person in Kuala Lumpur.
WhatsApp: +60 10-368 6902   ·   Facebook: facebook.com/paulamikkitutor

Good luck with your exams!
— Paula
'''
open(os.path.join(ROOT, 'READ ME FIRST.txt'), 'w').write(readme)

zpath = os.path.join(OUT, PACK + '.zip')
if os.path.exists(zpath):
    os.remove(zpath)
with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
    for dp, dn, fn in os.walk(ROOT):
        for f in sorted(fn):
            full = os.path.join(dp, f)
            z.write(full, os.path.relpath(full, OUT))
shutil.rmtree(work, ignore_errors=True)

# no website mentions anywhere in the pack
bad = []
for dp, dn, fn in os.walk(ROOT):
    for f in fn:
        p = os.path.join(dp, f)
        txt = open(p, errors='ignore').read() if f.endswith(('.md', '.txt')) else ''.join(pg.get_text() for pg in fitz.open(p)) if f.endswith('.pdf') else ''
        if re.search(r'github\.io|paulamikki1-boop|free (notes|revision)|resources/|marking|payhip', txt, re.I):
            bad.append(f)
print(f'{zpath}  ({os.path.getsize(zpath) // 1024} KB)')
print(f'compact: {len(fitz.open(cpath))} pages; detailed: {len(sections)} PDFs, {total_pages} pages; vault: {len(sections) + 1} notes, {len(fig_files)} diagrams')
if bad:
    print('WARNING: website mentions in', bad)
