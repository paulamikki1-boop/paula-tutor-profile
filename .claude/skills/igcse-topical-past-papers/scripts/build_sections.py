#!/usr/bin/env python3
"""Validate the writers' answer files and insert one 'Topical Past Papers' section per syllabus topic into a notes page.

Usage: build_sections.py CONFIG.json [--check]

CONFIG keys (see references/config-example.json):
  page            notes page to edit, e.g. resources/igcse-physics-notes/index.html (relative to the repo root / cwd)
  papers_dir      folder with the .txt papers and questions.json (from download_papers.py + extract_questions.py)
  answers_dir     folder with the writers' <key>.json files
  code, subject   e.g. "0625", "Physics"
  paper_label     how the questions are described, e.g. "Paper 4 (Extended Theory)"
  years           e.g. "2020&ndash;2025"
  units           [{"num": "1", "title": "Motion, Forces and Energy", "nav": "Motion, Forces &amp; Energy"}, ...]
  marking_subject subject name for the ../../marking/ "Get it marked" link, or null to leave the link out
  example_ref     a reference to explain in the how-to box, e.g. "0625/42/M/J/24 Q2(b)(ii)"

--check validates and prints problems without touching the page. Re-running replaces sections it built before.
"""
import glob, html, json, re, sys, urllib.parse

cfg = json.load(open(sys.argv[1], encoding='utf-8'))
CHECK_ONLY = '--check' in sys.argv


def norm(s):
    s = html.unescape(s).replace('‑', '-').replace(' ', ' ')
    return re.sub(r'\s+', ' ', s).strip()


questions = {q['id']: q for q in json.load(open(f"{cfg['papers_dir']}/questions.json", encoding='utf-8'))}
_papers = {}


def paper_text(file):
    """Question paper plus its insert (case studies and source booklets live in the insert)."""
    if file not in _papers:
        t = ''
        for f in (file, file.replace('_qp_', '_in_')):
            try:
                t += ' ' + open(f"{cfg['papers_dir']}/{f}.txt", encoding='utf-8', errors='replace').read()
            except FileNotFoundError:
                pass
        _papers[file] = norm(t)
    return _papers[file]


def verbatim(text, file):
    """Every sentence / '…'-separated fragment must appear word for word in the paper (whitespace collapsed)."""
    plain = norm(re.sub(r'<[^>]+>', '', text))  # e.g. 10<sup>11</sup> is flattened to '1011' in the paper text
    frags = [f.strip(' .') for f in re.split(r'…|(?<=[.?!])\s+', plain) if len(f.strip(' .')) > 3]
    return all(f in paper_text(file) for f in frags)


page = open(cfg['page'], encoding='utf-8').read()
done_elsewhere = set(re.findall(r'<span class="pp-ref">([^<]+)</span>', page))
problems, subtopics, seen = [], {}, set()
for f in sorted(glob.glob(f"{cfg['answers_dir']}/*.json")):
    data = json.load(open(f, encoding='utf-8'))
    for st in data['subtopics']:
        items = []
        for it in st['items']:
            tag = f"{data.get('key', f)} {st['code']} {it.get('id')}"
            q = questions.get(it.get('id'))
            if not q:
                problems.append(f'{tag}: id not in questions.json, dropped'); continue
            if it['id'] in seen:
                problems.append(f'{tag}: chosen twice, kept the first'); continue
            if not verbatim(it['question'], q['file']):
                problems.append(f'{tag}: question wording not found in the paper, dropped'); continue
            if it.get('marks') != q['marks'] or it.get('session') != q['session']:
                problems.append(f'{tag}: marks/session corrected from questions.json')
            if it.get('stimulus') and not verbatim(it['stimulus'], q['file']):
                problems.append(f'{tag}: stimulus not verbatim, removed'); it['stimulus'] = None
            if not it.get('answer') or not it.get('why'):
                problems.append(f'{tag}: missing answer or why, dropped'); continue
            seen.add(it['id'])
            items.append(dict(it, marks=q['marks'], session=q['session']))
        if items:
            subtopics.setdefault(st['code'], dict(st, items=[]))['items'] += items

for st in subtopics.values():
    st['items'].sort(key=lambda i: i['marks'])
n_q = sum(len(s['items']) for s in subtopics.values())
print(f'{len(subtopics)} sub-topics, {n_q} questions')
for p in problems:
    print('  !', p)
if CHECK_ONLY:
    sys.exit()


def code_key(c):
    return [int(x) if x.isdigit() else x for x in re.split(r'[.]', c)]


def mark_link(q, marks):
    if not cfg.get('marking_subject'):
        return ''
    service = 'Essay+%2F+extended+answer' if marks >= 8 else 'Single+question'
    text = urllib.parse.quote_plus(f"{norm(re.sub(r'<[^>]+>', '', q))} [{marks}]")
    subj = urllib.parse.quote_plus(cfg['marking_subject'])
    return (f'    <a class="mark-link" href="../../marking/?subject={subj}&amp;service={service}&amp;q={text}">'
            'Written your own answer? Get it marked &rarr;</a>\n')


def block(it):
    m = it['marks']
    out = (f'    <div class="example-block"><div class="ex-label"><span class="pp-ref">{it["id"]}</span> &middot; '
           f'{it["session"]} &middot; [{m} mark{"s" if m > 1 else ""}]</div>\n')
    if it.get('stimulus'):
        out += f'    <p class="pp-stimulus"><span>Source material:</span> {it["stimulus"]}</p>\n'
    q = it['question'] if re.search(r'<su[bp]>', it['question']) else html.escape(norm(it['question']), quote=False)
    out += f'    <p><strong>{q}</strong></p>\n'
    out += ''.join(f'    {p}\n' for p in it['answer'])
    if it.get('diagram'):
        out += f'    {it["diagram"]}\n'
    out += '    </div>\n'
    out += f'    <div class="tip-box"><div class="tip-label">Why this scores</div>{it["why"]}</div>\n'
    return out + mark_link(it['question'], m) + '  \n'


CREDIT = (f'    <p class="pp-credit">Questions &copy; UCLES / Cambridge University Press &amp; Assessment, Cambridge IGCSE '
          f'{cfg["subject"]} {cfg["code"]} {cfg["paper_label"]}, reproduced for revision purposes with references. The model '
          'answers and commentary are original and are not official Cambridge mark schemes.</p>\n')
ex = cfg.get('example_ref', '')
HOWTO = ('    <div class="tip-box"><div class="tip-label">How to use this page</div>Cover the answer, write your own in timed '
         'conditions (about 1&frac12; minutes per mark), then compare.'
         + (f' <strong>{ex}</strong> is the paper reference: syllabus/component/session/year, then question and part.' if ex else '')
         + ' F/M = February/March, M/J = May/June, O/N = October/November.</div>\n')

sections, nav = {}, []
for u in cfg['units']:
    codes = sorted((c for c in subtopics if c.split('.')[0] == u['num']), key=code_key)
    if not codes:
        continue
    n = sum(len(subtopics[c]['items']) for c in codes)
    anchor = lambda c: 'pp-' + re.sub(r'[^0-9a-z]+', '-', c.lower())
    jump = ' &middot; '.join(
        f'<a href="#{anchor(c)}" onclick="document.getElementById(\'{anchor(c)}\').scrollIntoView();return false;">'
        f'{c} {subtopics[c]["title"]}</a>' for c in codes)
    s = (f'  <!-- PAST PAPERS: UNIT {u["num"]} -->\n  <div class="section" id="sec-pp-unit{u["num"]}">\n'
         f'    <div class="section-header">\n      <span class="form-badge">Topical Past Papers &middot; Topic {u["num"]}</span>\n'
         f'      <h2>Past Paper Questions: {u["title"]}</h2>\n'
         f'      <p class="purpose">{n} real Cambridge IGCSE {cfg["subject"]} {cfg["paper_label"]} questions from {cfg["years"]}, '
         'sorted by sub-topic, each with its exact paper reference and a full-mark exemplar answer. The questions are quoted '
         'exactly; the model answers are my own, written to the published mark schemes and the advice in the examiner '
         'reports.</p>\n    </div>\n  \n' + HOWTO + '  \n'
         f'    <p class="pp-jump"><strong>Jump to:</strong> {jump}</p>\n  \n')
    for c in codes:
        st = subtopics[c]
        s += f'    <h3 id="{anchor(c)}">{c} {st["title"]}</h3>\n'
        if st.get('intro'):
            s += f'    <p>{st["intro"]}</p>\n'
        if st.get('pitfall'):
            s += f'    <div class="mistake-box"><div class="mistake-label">What examiners keep seeing</div>{st["pitfall"]}</div>\n'
        s += '  \n' + ''.join(block(it) for it in st['items'])
    s += CREDIT + f'  </div>\n  <!-- /PAST PAPERS: UNIT {u["num"]} -->\n\n'
    sections[u['num']] = s
    nav.append(f'  <div class="nav-item" data-section="pp-unit{u["num"]}" onclick="showSection(\'pp-unit{u["num"]}\')">\n'
               f'    <div class="nav-icon">{u["num"]}</div> {u.get("nav", u["title"])}\n  </div>\n')

# Replace sections built on an earlier run, then add the rest before </main>.
for num, s in sections.items():
    pat = re.compile(rf'  <!-- PAST PAPERS: UNIT {re.escape(num)} -->.*?<!-- /PAST PAPERS: UNIT {re.escape(num)} -->\n\n', re.S)
    if pat.search(page):
        page = pat.sub(lambda _: s, page, count=1)
    else:
        assert page.count('</main>') == 1, 'page must have exactly one </main>'
        page = page.replace('</main>', s + '</main>', 1)

# Sidebar: one "Topical Past Papers" group, rebuilt each run.
page = re.sub(r'  <!-- PP-NAV -->.*?<!-- /PP-NAV -->\n', '', page, flags=re.S)
group = '  <!-- PP-NAV -->\n  <div class="nav-section-label">Topical Past Papers</div>\n' + ''.join(nav) + '  <!-- /PP-NAV -->\n'
assert page.count('</nav>') >= 1
i = page.index('</nav>')
page = page[:i] + group + page[i:]

CSS = '''
/* Topical past papers (added by the igcse-topical-past-papers skill) */
.example-block .ex-label .pp-ref { text-transform: none; }
.example-block .pp-stimulus { font-style: normal; font-size: 14px; color: var(--text-muted); border-left: 3px solid var(--border); padding-left: 12px; margin-bottom: 12px; }
.example-block .pp-stimulus span { font-weight: 700; text-transform: uppercase; font-size: 11px; letter-spacing: 0.06em; }
.pp-jump { font-size: 14px; line-height: 1.9; }
.pp-jump a { color: var(--accent); }
.pp-credit { font-size: 12px; color: var(--text-muted); margin-top: 24px; }
'''
if '.mark-link {' not in page:
    CSS += ('.mark-link { display: inline-block; margin: -4px 0 20px; font-size: 13px; font-weight: 600; color: var(--accent); '
            'text-decoration: none; border-bottom: 1px solid currentColor; }\n')
if '.pp-credit {' not in page:
    i = page.index('</style>')
    page = page[:i] + CSS + page[i:]
open(cfg['page'], 'w', encoding='utf-8').write(page)
print(f'wrote {len(sections)} topic sections to {cfg["page"]}')
