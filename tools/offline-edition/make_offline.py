#!/usr/bin/env python3
"""Make a personal offline copy of a subject's notes (one HTML file) with Paula's name and the buyer's name on it.

    python3 tools/offline-edition/make_offline.py chemistry --buyer "Aisha Rahman" --order 2611220001 --out ~/orders

* Source: the live pages in this repo, resources/igcse-<subject>-notes/ (+ resources/igcse-<subject>-past-papers/ if
  that page exists, so the past papers are included in the same file).
* Output: one self-contained .html file that opens in any browser with no internet: fonts are embedded, the sidebar,
  topic menu and links between notes and past papers all work inside the file. The site search box is left out
  (it needs the website).
* Every copy carries the buyer's name and Paula's copyright: a banner at the top, a line under every section heading,
  a faint diagonal watermark behind the text (also when printed), the page title and the footer.
* Buyer names must never be committed: write output OUTSIDE the repo (--out). The script refuses an --out inside it.
"""
import argparse, base64, html, os, re, sys, urllib.parse, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import about_page

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
LIVE = 'https://paulamikki1-boop.github.io/paula-tutor-profile/'

ap = argparse.ArgumentParser()
ap.add_argument('subject', help='e.g. chemistry, biology, economics (page folder igcse-<subject>-notes)')
ap.add_argument('--buyer', default=None, help="buyer's name as it should appear on the copy")
ap.add_argument('--order', default='', help='Shopee order number (optional, shown next to the name)')
ap.add_argument('--out', required=True, help='output folder (outside the repo)')
ap.add_argument('--master', action='store_true', help='make a master copy with placeholders (for the Order Maker)')
a = ap.parse_args()

out_dir = os.path.abspath(os.path.expanduser(a.out))
if out_dir == REPO or out_dir.startswith(REPO + os.sep):
    sys.exit('--out must be outside the repository (buyer names must never be committed)')
NOTES = f'igcse-{a.subject}-notes'
PP = f'igcse-{a.subject}-past-papers'
notes_path = os.path.join(REPO, 'resources', NOTES, 'index.html')
if not os.path.exists(notes_path) and os.path.exists(os.path.join(REPO, 'resources', f'igcse-{a.subject}', 'index.html')):
    NOTES = f'igcse-{a.subject}'                     # e.g. english-writing-forms
    notes_path = os.path.join(REPO, 'resources', NOTES, 'index.html')
if not os.path.exists(notes_path):
    sys.exit(f'no notes page at resources/{NOTES}/')
page = open(notes_path).read()
pp_path = os.path.join(REPO, 'resources', PP, 'index.html')
pp_page = open(pp_path).read() if os.path.exists(pp_path) else None

if a.master:                       # placeholders the Order Maker replaces (letters only, so escaping never changes them)
    a.buyer, a.order = 'QQBUYERQQ', 'QQORDERQQ'
if not a.buyer:
    sys.exit('--buyer is required (or --master)')
buyer = re.sub(r'\s+', ' ', a.buyer).strip()
order = re.sub(r'\s+', ' ', a.order).strip()
B = html.escape(buyer)
WHO = B + (f' &middot; Order {html.escape(order)}' if order else '')
YEAR = datetime.date.today().year

def split(p):
    m0 = p.index('<main class="main">') + len('<main class="main">'); m1 = p.index('</main>')
    return p[:m0], p[m0:m1], p[m1:]

head, main, tail = split(page)

# ---------------------------------------------------------------- merge the past-papers page into the same file
if pp_page:
    ph, pm, _ = split(pp_page)
    pnav = ph[ph.index('<nav class="sidebar">'):ph.index('</nav>', ph.index('<nav class="sidebar">'))]
    # the past-paper group = everything from its first section label onwards (after the header and side boxes)
    g = re.search(r'\n  <div class="nav-section-label">', pnav)
    pp_group = pnav[g.start():]
    pp_group = pp_group.replace('<div class="nav-item active"', '<div class="nav-item"')
    pm = pm.replace('<div class="section active" id="sec-', '<div class="section" id="sec-')
    main = main + pm
    n0 = head.index('<nav class="sidebar">'); n1 = head.index('</nav>', n0)
    head = head[:n1].rstrip() + '\n' + pp_group.rstrip() + '\n' + head[n1:]
    # past-paper sub-topic CSS (scroll margins) and link-box CSS come from the past-papers head if missing
    if '.pp-link-box' not in head:
        css = re.search(r'/\* >>> split-past-papers.*?/\* <<< split-past-papers \*/\n', ph, re.S)
        if css:
            head = head.replace('</style>', css.group(0) + '</style>', 1)

# links between the two pages become links inside this file
both = main
both = re.sub(r'href="\.\./(%s|%s)/#([^"]+)"' % (re.escape(NOTES), re.escape(PP)), r'href="#\2"', both)
both = re.sub(r'href="\.\./(%s|%s)/"' % (re.escape(NOTES), re.escape(PP)), 'href="#"', both)
main = both

# ---------------------------------------------------------------- head: offline fonts, title, no web-only bits
def font_face():
    def b64(name):
        return base64.b64encode(open(os.path.join(HERE, 'fonts', name), 'rb').read()).decode()
    return ('/* DM Sans and DM Mono, SIL Open Font License 1.1 (embedded so the file works offline) */\n'
            f"@font-face {{ font-family: 'DM Sans'; font-style: normal; font-weight: 100 1000; font-display: swap; src: url(data:font/woff2;base64,{b64('DMSans-latin-var.woff2')}) format('woff2'); }}\n"
            f"@font-face {{ font-family: 'DM Mono'; font-style: normal; font-weight: 400; font-display: swap; src: url(data:font/woff2;base64,{b64('DMMono-400.woff2')}) format('woff2'); }}\n"
            f"@font-face {{ font-family: 'DM Mono'; font-style: normal; font-weight: 500; font-display: swap; src: url(data:font/woff2;base64,{b64('DMMono-500.woff2')}) format('woff2'); }}\n")

head = re.sub(r'\s*<link rel="(preconnect|canonical)"[^>]*>', '', head)
head = re.sub(r'\s*<link href="https://fonts\.googleapis\.com[^>]*>', '', head)
head = re.sub(r'\s*<meta property="og:[^>]*>', '', head)
h1 = re.search(r'<h1>(.*?)</h1>', head).group(1)                       # e.g. IGCSE Chemistry Notes
head = re.sub(r'<title>.*?</title>', f'<title>{h1} &mdash; personal copy for {B} | &copy; Paula</title>', head, count=1)
head = head.replace('<meta name="viewport"', '<meta name="robots" content="noindex">\n    <meta name="viewport"', 1)

wm_text = f'© Paula · IGCSE Tutor · {buyer}' + (f' · {order}' if order else '')
wm_svg = (f"<svg xmlns='http://www.w3.org/2000/svg' width='600' height='340'><text x='300' y='175' text-anchor='middle' "
          f"transform='rotate(-22 300 170)' font-family='DM Sans, Arial, sans-serif' font-size='14' "
          f"fill='%230a1628' fill-opacity='0.08'>{html.escape(wm_text)}</text></svg>")
wm_url = 'data:image/svg+xml;utf8,' + urllib.parse.quote(wm_svg, safe="=:/,'%() .#")
LIC_CSS = f'''{font_face()}
/* personal-copy marks */
.licence-banner {{ max-width: 1168px; width: calc(100% - 32px); box-sizing: border-box; margin: 12px auto 0; padding: 10px 18px; border-radius: 12px; background: #e8f0fe; border: 1px solid #c7d8f5; color: #1e3a5f; font-size: 13.5px; line-height: 1.5; }}
.licence-banner strong {{ color: #0a1628; }}
.licence-line {{ font-family: var(--mono, 'DM Mono', monospace); font-size: 11px; letter-spacing: .04em; color: #6b7a90; margin-top: 10px; }}
.main {{ background-image: url("{wm_url}"); background-repeat: repeat; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
@media print {{ .licence-banner {{ display: block !important; }} }}
'''
head = head.replace('</style>', LIC_CSS + '</style>', 1)

# site navigation: keep it, but point it at the live site (a local file has no ../../)
# top bar: Home opens the About page inside the file, Notes goes back to the notes; no website links
nav = re.search(r'<nav class="nav">.*?</nav>', head, re.S).group(0)
new_nav = re.sub(r'<a href="\.\./\.\./" class="nav-brand">', '<a href="#home" class="nav-brand">', nav)
new_nav = re.sub(r'\s*<a href="\.\./\.\./(resources|marking|shop)/">[^<]*</a>', '', new_nav)
new_nav = re.sub(r'<a href="\.\./\.\./">Home</a>', '<a href="#home">Home</a>\n            <a href="#notes">Notes</a>', new_nav)
head = head.replace(nav, new_nav)
tail = re.sub(r'\s*<a href="[^"]*marking/"[^>]*class="marking-btn"[^>]*>.*?</a>', '', tail, flags=re.S)
tail = re.sub(r'\s*<a [^>]*class="marking-btn"[^>]*>.*?</a>', '', tail, flags=re.S)

# "Get it marked" buttons point to the marking page on the website: leave them out of copies
main = re.sub(r'\s*<a\b[^>]*href="\.\./\.\./marking/[^"]*"[^>]*>.*?</a>', '', main, flags=re.S)

def absolutise(s):
    s = re.sub(r'href="\.\./\.\./([^"]*)"', lambda m: f'href="{LIVE}{m.group(1)}"', s)
    s = re.sub(r'href="\.\./([a-z0-9-]+/[^"]*)"', lambda m: f'href="{LIVE}resources/{m.group(1)}"', s)
    return s
head = absolutise(head)
main = absolutise(main)
tail = absolutise(tail)

# breadcrumbs -> licence banner
banner = (f'<div class="licence-banner">Personal copy for <strong>{WHO}</strong>. '
          f'&copy; {YEAR} Paula &mdash; IGCSE &amp; A Level Tutor. For your own revision only; please do not share or resell.</div>')
head = re.sub(r'<div class="breadcrumbs">.*?</div>', banner, head, count=1, flags=re.S)
# sidebar: drop the shop / other-page boxes, note that search needs the website
head = re.sub(r'\s*<a class="(pdf-promo|side-link)"[^>]*>.*?</a>', '', head, flags=re.S)
head = head.replace('</h1>', f'</h1>\n    <div class="licence-line" style="color:#8fbdf0">Licensed to {B}</div>', 1)

# every section heading carries the buyer's name
main = re.sub(r'(<div class="section-header">.*?)(\n    </div>)',
              lambda m: m.group(1) + f'\n      <div class="licence-line">Personal copy for {WHO} &middot; &copy; Paula</div>' + m.group(2),
              main, flags=re.S)

# ---------------------------------------------------------------- tail: no search, no forwarding, licensed footer
tail = re.sub(r'\s*<script src="\.\./search\.js"></script>', '', tail)
tail = re.sub(r'\s*<script src="[^"]*search\.js"></script>', '', tail)
tail = re.sub(r'<footer class="footer">.*?</footer>',
              f'<footer class="footer"><p>&copy; {YEAR} Paula &mdash; IGCSE &amp; A Level Tutor in Kuala Lumpur. '
              f'Personal copy for {WHO}. For personal use only; not for sharing or resale.</p></footer>', tail, count=1, flags=re.S)
tail = re.sub(r'\s*<script type="application/ld\+json">.*?</script>', '', tail, flags=re.S)
syl = re.search(r'class="syllabus">(.*?)<', head)
syl = syl.group(1).strip() if syl else ''
nq = main.count('class="pp-ref"')
notes_line = (f'These {h1} are written by Paula' + (f' for the {syl}' if syl else '') +
              (f', with {nq} real past-paper questions and full-mark model answers.' if nq else '.') +
              ' Use <a class="text-link" href="#notes">Notes</a> at the top to go back to them.')
idx = open(os.path.join(REPO, 'index.html')).read()
a_css, a_html, a_js = about_page.build(idx, notes_line)
head = head.replace('</style>', a_css + '\n</style>', 1)
head = head.replace(banner, banner + '\n' + a_html, 1)
tail = tail.replace('</body>', a_js + '</body>', 1)
doc = head + main + tail
# the notes page forwards old #pp- links to the past-papers page; inside one file they open in place
doc = re.sub(r"\s*// The topical past papers moved to their own page[^\n]*\n\s*if \(/\^pp-/\.test\(h\)\)[^\n]*\n", '\n', doc)
doc = re.sub(r'<script>/\* past papers moved to their own page.*?</script>\n?', '', doc, flags=re.S)
assert 'location.replace' not in doc, 'forwarding script still present'
assert '../search.js' not in doc
# nothing in the copy may point to or mention the free website
visible = re.sub(r'data:[^"\')]+', '', doc)
left = re.findall(r'paulamikki1-boop\.github\.io|href="[^"]*(?:resources|marking|shop)/|free (?:notes|revision|study)', visible, re.I)
if left:
    sys.exit(f'copy still mentions the website: {sorted(set(left))[:6]}')

safe = re.sub(r'[^A-Za-z0-9]+', '-', buyer).strip('-') or 'buyer'
fname = f'{h1.replace(" ", "-")}-{safe}' + (f'-{re.sub(r"[^A-Za-z0-9]+", "", order)}' if order else '') + '.html'
os.makedirs(out_dir, exist_ok=True)
if a.master:
    fname = f'master-{a.subject}.html'
path = os.path.join(out_dir, fname)
open(path, 'w').write(doc)
print(f'{path}  ({len(doc) // 1024} KB, {len(re.findall(r'<div class="section( active)?" id="sec-', doc))} sections, '
      f'{doc.count("class=\"pp-ref\"")} past-paper questions)')
