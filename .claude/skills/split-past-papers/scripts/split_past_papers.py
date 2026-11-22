#!/usr/bin/env python3
"""Move a subject's past-paper sections out of its notes page into a separate page, linked both ways.

    python3 .claude/skills/split-past-papers/scripts/split_past_papers.py igcse-biology-notes [--root DIR] [--no-followers]

  * Reads   resources/<notes-slug>/index.html  (e.g. igcse-biology-notes)
  * Writes  resources/<notes-slug>/index.html  (notes only)
            resources/<pp-slug>/index.html      (past papers only; pp-slug = notes slug with "-notes" -> "-past-papers")
  * Every notes section whose badge says "Topic N" (or "Topic N.M") gets a link box under its header and one at its end
    pointing to the past-paper section(s) whose badge ends "Topic N"; every past-paper section gets a "Revise the notes
    first" box pointing back to the first notes section of that topic (none if the topic has no notes yet).
  * In-page links that now cross pages (href="#pp-..." in the notes, href="#<notes-section>" in the past papers) are
    rewritten to the other page. Old #pp-... links to the notes page are forwarded to the new page.
  * The past-papers page can open a sub-topic h3 id (e.g. #pp-2-3) directly, so search hits go to the exact sub-topic.
  * Followers (skip with --no-followers): search-index PAGES entry, sitemap entry, resources hub card, DEPLOY.md line,
    then re-runs the hub style layer and the search index builder.

Refuses to run if the notes page has no past-paper sections (already split, or nothing to split). Only touches the
files listed above. --root points at a copy of the repo for a dry run.
"""
import argparse, collections, html, os, re, subprocess, sys

ap = argparse.ArgumentParser()
ap.add_argument('slug', help='notes page folder under resources/, e.g. igcse-biology-notes')
ap.add_argument('--root', default=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))
ap.add_argument('--no-followers', action='store_true', help='only write the two pages')
a = ap.parse_args()

ROOT, NOTES = a.root, a.slug
if not NOTES.endswith('-notes'):
    sys.exit('slug must end in -notes (e.g. igcse-biology-notes)')
PP = NOTES[:-len('-notes')] + '-past-papers'
BASE = 'https://paulamikki1-boop.github.io/paula-tutor-profile/resources/'
src_path = os.path.join(ROOT, 'resources', NOTES, 'index.html')
page = open(src_path).read()
SUBJ = NOTES[len('igcse-'):-len('-notes')]

# ------------------------------------------------------------------ split the page into parts
m0 = page.index('<main class="main">') + len('<main class="main">')
m1 = page.index('</main>')
head, main, tail = page[:m0], page[m0:m1], page[m1:]
starts = list(re.finditer(r'<div class="section([^"]*)" id="sec-([^"]+)">', main))
if not starts:
    sys.exit('no sections found')
pre = main[:starts[0].start()]
sections = []  # dicts: id, cls, html (from its start to the next section start), pp, topic, title, refs
for i, m in enumerate(starts):
    chunk = main[m.start():starts[i + 1].start() if i + 1 < len(starts) else len(main)]
    sid = m.group(2)
    badge = re.search(r'class="form-badge">([^<]*)', chunk)
    badge = html.unescape(badge.group(1)).strip() if badge else ''
    title = re.search(r'<h2>(.*?)</h2>', chunk, re.S)
    is_pp = sid.startswith('pp-')
    if is_pp:
        t = re.search(r'Topic (\d+)\s*$', badge)
    else:
        t = re.match(r'Topic (\d+)(?:\.\d+)?\b', badge)
    sections.append(dict(id=sid, html=chunk, pp=is_pp, topic=int(t.group(1)) if t else None,
                         title=title.group(1).strip() if title else sid, refs=chunk.count('class="pp-ref"')))
pps = [s for s in sections if s['pp']]
notes = [s for s in sections if not s['pp']]
if not pps:
    sys.exit(f'{NOTES}: no past-paper sections (ids "pp-...") found; already split or nothing to split.')
TOTAL = sum(s['refs'] for s in pps)
print(f'{NOTES}: {len(notes)} notes sections, {len(pps)} past-paper sections, {TOTAL} questions')
for s in pps:
    if s['topic'] is None:
        sys.exit(f'past-paper section {s["id"]} has no "Topic N" badge; cannot map it to the notes')

pp_by_topic = collections.defaultdict(list)
for s in pps:
    pp_by_topic[s['topic']].append(s)
notes_by_topic = collections.defaultdict(list)
for s in notes:
    if s['topic'] is not None:
        notes_by_topic[s['topic']].append(s)

# ------------------------------------------------------------------ names, labels
nav0 = head.index('<nav class="sidebar">'); nav1 = head.index('</nav>', nav0)
NAV = head[nav0:nav1]
H1 = re.search(r'<h1>(.*?)</h1>', NAV).group(1)                     # e.g. IGCSE Biology Notes
NAME = re.sub(r'\s*Notes$', '', H1)                                 # IGCSE Biology
CODE = re.search(r'\b(0\d{3})\b', re.search(r'class="syllabus">(.*?)<', NAV).group(1))
CODE = CODE.group(1) if CODE else ''
first_pp_nav = re.search(r'  <div class="nav-item[^"]*" data-section="pp-', NAV)
lab = None
for lab in re.finditer(r'  <div class="nav-section-label">(.*?)</div>\n', NAV[:first_pp_nav.start()]):
    pass
PPLABEL = lab.group(1) if lab else 'Topical Past Papers'            # "Topical Past Papers" / "Past-Paper Examples"
PPLABEL_TXT = html.unescape(PPLABEL)

# ------------------------------------------------------------------ CSS shared by both pages
CSS = '''/* >>> split-past-papers: link boxes between the notes page and the past-papers page */
.pp-link-box { display: flex; align-items: center; gap: 14px; margin: 0 0 28px; padding: 14px 18px; background: #fff; border: 1px solid #e3e9f2; border-left: 4px solid #4a90d9; border-radius: 12px; text-decoration: none; color: inherit; font-style: normal; }
.pp-link-box:hover { border-color: #4a90d9; }
.pp-link-box .pp-link-text { flex: 1; font-size: 14.5px; line-height: 1.5; }
.pp-link-box .pp-link-text strong { display: block; color: #0a1628; font-size: 15.5px; }
.pp-link-box .pp-link-go { flex-shrink: 0; font-weight: 600; color: #4a90d9; white-space: nowrap; }
.pp-link-box.end { margin: 28px 0 0; }
.side-link { display: block; margin: 14px 12px 6px; padding: 12px 14px; border-radius: 14px; background: rgba(74,144,217,0.16); border: 1px solid rgba(74,144,217,0.45); color: #fff; text-decoration: none; transition: background 0.15s; }
.side-link:hover { background: rgba(74,144,217,0.28); }
.side-link strong { display: block; font-size: 14px; }
.side-link span { display: block; font-size: 12px; color: #c9d6e8; margin-top: 2px; }
@media (max-width: 600px) { .pp-link-box { flex-direction: column; align-items: flex-start; gap: 6px; } }
@media print { .pp-link-box, .side-link { display: none !important; } }
/* <<< split-past-papers */
'''
def add_css(h):
    if '/* >>> split-past-papers' in h:
        return h
    marker = '/* >>> hub-style layer'
    if marker in h:
        return h.replace(marker, CSS + marker, 1)
    return h.replace('</style>', CSS + '</style>', 1)

# ------------------------------------------------------------------ link boxes
def notes_boxes(s):
    targets = pp_by_topic.get(s['topic'])
    if not targets:
        return '', ''
    t = targets[0]
    q = sum(x['refs'] for x in targets)
    href = f'../{PP}/#{t["id"]}'
    plain = re.sub(r'<[^>]+>', '', t['title'])
    plain = re.sub(r'^(Past[- ]Paper (Questions|Examples)?:?\s*)', '', plain).strip() or f'Topic {s["topic"]}'
    qs = f'{q} real exam question{"s" if q != 1 else ""}'
    top = (f'    <a class="pp-link-box" href="{href}"><span class="pp-link-text"><strong>{PPLABEL} for this topic</strong>'
           f'{qs} on {plain}, with model answers.</span><span class="pp-link-go">Practise &rarr;</span></a>\n')
    end = (f'    <a class="pp-link-box end" href="{href}"><span class="pp-link-text"><strong>Test yourself on {plain}</strong>'
           f'{qs} on this topic, with full-mark model answers.</span><span class="pp-link-go">Topic {s["topic"]} past papers &rarr;</span></a>\n')
    return top, end

def pp_box(s):
    targets = notes_by_topic.get(s['topic'])
    if not targets:
        return ''
    t = targets[0]
    return (f'    <a class="pp-link-box" href="../{NOTES}/#{t["id"]}"><span class="pp-link-text"><strong>Revise the notes first</strong>'
            f'{re.sub(r"<[^>]+>", "", t["title"])} &mdash; the notes for this topic.</span>'
            f'<span class="pp-link-go">Topic {s["topic"]} notes &rarr;</span></a>\n')

def insert_top(chunk, box):
    if not box:
        return chunk
    i = chunk.index('<div class="section-header">')
    j = chunk.index('</div>', i) + len('</div>')
    k = chunk.index('\n', j) + 1 if '\n' in chunk[j:j + 2] else j
    return chunk[:k] + box + chunk[k:]

def insert_end(chunk, box):
    if not box:
        return chunk
    # the section's own closing </div> is the last </div> before any trailing comments
    body = re.sub(r'(\s*<!--[^>]*-->\s*)*$', '', chunk)
    last = body.rfind('</div>')
    return chunk[:last] + box.lstrip() + '  ' + chunk[last:]

# ------------------------------------------------------------------ cross-page links
notes_ids, pp_ids = set(), set()
for s in sections:
    ids = set(re.findall(r'\sid="([^"]+)"', s['html'])) | {s['id']}
    (pp_ids if s['pp'] else notes_ids).update(ids)

def relink(chunk, other_ids, other_slug):
    def fix(m):
        tag, target = m.group(0), m.group(1)
        if target not in other_ids:
            return tag
        tag = tag.replace(f'href="#{target}"', f'href="../{other_slug}/#{target}"')
        return re.sub(r'\s+onclick="[^"]*"', '', tag)
    return re.sub(r'<a\b[^>]*\shref="#([^"]+)"[^>]*>', fix, chunk)

def clean_comments(chunk):
    return re.sub(r'\s*<!-- /?(PAST PAPERS|PP)[^>]*-->', '', chunk)

# ------------------------------------------------------------------ sidebar
def nav_blocks(nav):
    """(start, end) spans of each nav item (plus its .subnav list, if any) keyed by data-section."""
    out = {}
    for m in re.finditer(r'  <div class="nav-item[^"]*" data-section="([^"]+)"[^>]*>.*?\n  </div>\n', nav, re.S):
        end = m.end()
        sub = re.match(r'  <div class="subnav"[^>]*>.*?\n  </div>\n', nav[end:], re.S)
        if sub:
            end += sub.end()
        out[m.group(1)] = (m.start(), end)
    return out

blocks = nav_blocks(NAV)
pp_spans = [blocks[s['id']] for s in pps if s['id'] in blocks]
g0, g1 = min(x[0] for x in pp_spans), max(x[1] for x in pp_spans)
if lab and lab.end() <= g0 and not re.search(r'data-section="(?!pp-)', NAV[lab.end():g0]):
    g0 = lab.start()                                            # take the group label too
for marker in ('  <!-- PP-NAV -->\n',):
    if NAV[:g0].endswith(marker):
        g0 -= len(marker)
tail_marker = re.match(r'  <!-- /PP-NAV -->\n', NAV[g1:])
if tail_marker:
    g1 += tail_marker.end()
between = NAV[g0:g1]
stray = [d for d in re.findall(r'data-section="([^"]+)"', between) if not d.startswith('pp-')]
if stray:
    sys.exit(f'non-past-paper nav items inside the past-paper group: {stray}')
pp_group = re.sub(r'  <!-- /?PP-NAV -->\n', '', between)
notes_nav = NAV[:g0] + NAV[g1:]
hdr_end = NAV.index('\n  </div>', NAV.index('<div class="sidebar-header">')) + len('\n  </div>')
promo = re.search(r'\n  <a class="pdf-promo".*?</a>', NAV, re.S)
after_top = promo.end() if promo else hdr_end
assert after_top <= g0, 'sidebar header/promo found after the past-paper group'

# notes sidebar: add the box to the past-papers page (header and promo come before the removed group)
notes_nav = (notes_nav[:after_top] + f'\n  <a class="side-link" href="../{PP}/">\n    <strong>{PPLABEL} &rarr;</strong>\n'
             f'    <span>{TOTAL} real exam questions by topic, with model answers</span>\n  </a>' + notes_nav[after_top:])
# past-papers sidebar: header (+ shop promo), back box, then the past-paper group only
pp_nav = (NAV[:after_top] + f'\n  <a class="side-link" href="../{NOTES}/">\n    <strong>&larr; Back to the notes</strong>\n'
          f'    <span>All topics, explanations and worked examples</span>\n  </a>\n\n' + pp_group)
pp_nav = pp_nav.replace(f'<h1>{H1}</h1>', f'<h1>{NAME} Past Papers</h1>', 1)
pp_nav = re.sub(r'(<div class="nav-item) active(")', r'\1\2', pp_nav)
pp_nav = pp_nav.replace(f'<div class="nav-item" data-section="{pps[0]["id"]}"', f'<div class="nav-item active" data-section="{pps[0]["id"]}"', 1)
# if a past-paper item was the active one on the notes page, make the first notes item active instead
if not re.search(r'<div class="nav-item active"', notes_nav):
    notes_nav = notes_nav.replace(f'<div class="nav-item" data-section="{notes[0]["id"]}"', f'<div class="nav-item active" data-section="{notes[0]["id"]}"', 1)

# ------------------------------------------------------------------ build the notes page
nb = [pre]
for s in notes:
    c = s['html']
    top, end = notes_boxes(s)
    c = insert_end(insert_top(c, top), end)
    nb.append(clean_comments(relink(c, pp_ids, PP)))
notes_main = ''.join(nb)
if not re.search(r'<div class="section active"', notes_main):
    notes_main = notes_main.replace(f'<div class="section" id="sec-{notes[0]["id"]}">', f'<div class="section active" id="sec-{notes[0]["id"]}">', 1)
notes_head = add_css(head[:nav0] + notes_nav + head[nav1:])
FORWARD = (f'<script>/* past papers moved to their own page: forward old #pp-... links */'
           f'if (/^#pp-/.test(location.hash)) location.replace("../{PP}/" + location.search + location.hash);</script>\n')
if 'past papers moved to their own page' not in notes_head:
    notes_head = re.sub(r'(<body[^>]*>\n)', lambda m: m.group(1) + FORWARD, notes_head, count=1)
notes_page = notes_head + notes_main + tail

# ------------------------------------------------------------------ build the past-papers page
pb = []
for i, s in enumerate(pps):
    c = insert_top(s['html'], pp_box(s))
    c = re.sub(r'<div class="section[^"]*" id="sec-', '<div class="section active" id="sec-' if i == 0 else '<div class="section" id="sec-', c, count=1)
    pb.append(clean_comments(relink(c, notes_ids, NOTES)))
pp_main = '\n' + ''.join(pb)
desc = (f'{TOTAL} real Cambridge {NAME} ({CODE}) past-paper questions, sorted by syllabus topic, each quoted with its '
        f'paper reference and an original full-mark model answer.')
ph = head[:nav0] + pp_nav + '\n' + head[nav1:]
ph = re.sub(r'<title>.*?</title>', f'<title>{NAME} {PPLABEL} by Topic (Cambridge {CODE}) | Paula — IGCSE &amp; A Level Tutor</title>', ph, count=1)
ph = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + desc, ph, count=1)
ph = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + desc, ph, count=1)
ph = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + f'{NAME} {PPLABEL} — Free Study Resource', ph, count=1)
ph = ph.replace(f'{BASE}{NOTES}/"', f'{BASE}{PP}/"')
bc = re.search(r'(<div class="breadcrumbs">.*?&rsaquo;\s*)([^<&]*?)(\s*</div>)', ph, re.S)
if bc:
    ph = ph[:bc.start(2)] + f'<a href="../{NOTES}/">{bc.group(2).strip()}</a> &rsaquo; {PPLABEL}' + ph[bc.end(2):]
ph = add_css(ph)
pt = tail
pt = re.sub(r'(\{ "@type": "ListItem", "position": 3, "name": ")([^"]*)(" \})',
            lambda m: f'{m.group(1)}{m.group(2)}", "item": "{BASE}{NOTES}/" }},\n            {{ "@type": "ListItem", "position": 4, "name": "{PPLABEL_TXT}" }}', pt, count=1)
pt = re.sub(r'("@type": "LearningResource",\s*"name": ")[^"]*', lambda m: m.group(1) + f'{html.unescape(NAME)} {PPLABEL_TXT} (Cambridge {CODE})', pt, count=1)
pt = re.sub(r'("@type": "LearningResource",.*?"description": ")[^"]*', lambda m: m.group(1) + desc, pt, count=1, flags=re.S)
# open a sub-topic h3 hash (e.g. #pp-2-3) directly, unless the page already can (sub-topic menu pages)
OPEN_H3 = '''<script>/* split-past-papers: open a sub-topic heading from the URL hash */
(function () {
  function openHash() {
    var h = location.hash.slice(1);
    if (!h || document.getElementById('sec-' + h)) return;
    var el = document.getElementById(h);
    if (!el || el.tagName !== 'H3') return;
    var sec = el.closest('.section');
    if (!sec) return;
    if (!sec.classList.contains('active')) showSection(sec.id.replace(/^sec-/, ''), true);
    setTimeout(function () { el.scrollIntoView({ block: 'start' }); }, 30);
  }
  openHash();
  window.addEventListener('hashchange', openHash);
  // (search-index marker: el.tagName === 'H3')
})();
</script>
'''
if "el.tagName === 'H3'" not in pt:
    pt = pt.replace('<script src="../search.js"></script>', OPEN_H3 + '    <script src="../search.js"></script>', 1)
    assert 'openHash' in pt, 'could not find <script src="../search.js"> to add the hash opener'
pp_page = ph + pp_main + pt

# ------------------------------------------------------------------ checks before writing
def ids_of(p):
    return re.findall(r'\sid="([^"]+)"', p)
for name, p in (('notes', notes_page), ('past papers', pp_page)):
    dup = [k for k, v in collections.Counter(ids_of(p)).items() if v > 1]
    if dup:
        sys.exit(f'{name} page would have duplicate ids: {dup[:5]}')
assert notes_page.count('class="pp-ref"') == 0 or 'pp-ref' not in notes_main, 'past-paper questions left in notes'
assert pp_page.count('class="pp-ref"') == TOTAL, 'question count changed'
assert 'id="sec-pp-' not in notes_main
pp_all = set(ids_of(pp_page))
bad = [h for h in set(re.findall(r'href="#([^"]+)"', pp_main)) if h not in pp_all and f'sec-{h}' not in pp_all]
if bad:
    print('WARN: past-papers page has in-page links with no target:', bad[:8])

os.makedirs(os.path.join(ROOT, 'resources', PP), exist_ok=True)
open(src_path, 'w').write(notes_page)
open(os.path.join(ROOT, 'resources', PP, 'index.html'), 'w').write(pp_page)
linked = sum(1 for s in notes if pp_by_topic.get(s['topic']))
print(f'wrote resources/{NOTES}/index.html ({linked} notes sections linked) and resources/{PP}/index.html '
      f'({len(pps)} sections, {sum(1 for s in pps if notes_by_topic.get(s["topic"]))} with a link back)')
missing = sorted({s['topic'] for s in pps if not notes_by_topic.get(s['topic'])})
if missing:
    print(f'note: topics with past papers but no notes section (no link back): {missing}')

if a.no_followers:
    sys.exit(0)

# ------------------------------------------------------------------ followers
def edit(path, fn):
    p = os.path.join(ROOT, path); s = open(p).read(); n = fn(s)
    if n != s:
        open(p, 'w').write(n); print('updated', path)

SUBJECT_LABEL = re.search(r'\("([^"]+)", "%s"\)' % re.escape(NOTES), open(os.path.join(ROOT, 'tools/build-search-index.py')).read())
SUBJECT_LABEL = SUBJECT_LABEL.group(1) if SUBJECT_LABEL else SUBJ.title()
edit('tools/build-search-index.py', lambda s: s if f'"{PP}"' in s else
     s.replace(f'    ("{SUBJECT_LABEL}", "{NOTES}"),\n', f'    ("{SUBJECT_LABEL}", "{NOTES}"),\n    ("{SUBJECT_LABEL}", "{PP}"),\n', 1))

def sitemap(s):
    if f'/{PP}/' in s:
        return s
    m = re.search(r'    <url>\n        <loc>[^<]*/%s/</loc>.*?</url>\n' % re.escape(NOTES), s, re.S)
    if not m:
        print('WARN: no sitemap entry for the notes page; add one for the past-papers page by hand'); return s
    new = m.group(0).replace(f'/{NOTES}/', f'/{PP}/')
    return s[:m.end()] + new + s[m.end():]
edit('sitemap.xml', sitemap)

def hub(s):
    if f'href="../resources/{PP}/"' in s:
        return s
    m = re.search(r'            <a class="card" href="\.\./resources/%s/".*?</a>\n\n' % re.escape(NOTES), s, re.S)
    if not m:
        print('WARN: no resources hub card for the notes page; add one for the past-papers page by hand'); return s
    card = m.group(0).replace(f'/{NOTES}/', f'/{PP}/')
    card = re.sub(r'\s*<span class="tag tag-pdf">[^<]*</span>', '', card)
    card = re.sub(r'<h2>.*?</h2>', f'<h2>{NAME} {PPLABEL}</h2>', card, count=1)
    card = re.sub(r'<p class="card-desc">.*?</p>', f'<p class="card-desc">{TOTAL} real Cambridge {CODE} past-paper questions, sorted by topic, each with its paper reference and a full-mark model answer.</p>', card, count=1)
    return s[:m.end()] + card + s[m.end():]
edit('resources/index.html', hub)

def deploy(s):
    if f'{PP}/' in s:
        return s
    m = re.search(r'│   ├── %s/\n│   │   └── index\.html[^\n]*\n' % re.escape(NOTES), s)
    if not m:
        print('WARN: no DEPLOY.md line for the notes page; add one by hand'); return s
    line = f'│   ├── {PP}/\n│   │   └── index.html                          — {PPLABEL_TXT} ({TOTAL} questions by topic; each unit links back to its notes)\n'
    return s[:m.end()] + line + s[m.end():]
edit('DEPLOY.md', deploy)

for cmd in (['python3', '.claude/skills/paula-web-design/scripts/apply_hub_layer.py'], ['python3', 'tools/build-search-index.py']):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    out = [l for l in r.stdout.splitlines() if not l.startswith('ok ')]
    print('$', ' '.join(cmd[1:]), '->', ' | '.join(out[-3:]) or 'ok', r.stderr.strip()[-300:])
print('done. Next: browser check (check_split.js), update CLAUDE.md, review git diff.')
