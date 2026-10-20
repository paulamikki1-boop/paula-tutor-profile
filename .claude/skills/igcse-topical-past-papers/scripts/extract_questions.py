#!/usr/bin/env python3
"""Extract every marked question part from Cambridge question-paper text files into questions.json.

Usage: extract_questions.py PAPERS_DIR [--code 0455]

Reads PAPERS_DIR/<code>_<s><yy>_qp_<comp>.txt (made by download_papers.py) and writes PAPERS_DIR/questions.json:
a list of {id, session, file, component, q, part, sub, marks, question, stem, stimulus, refers_to_figure}.
Works for one-letter parts (Economics/Business: "(a) ... [4]") and nested parts (Sciences: "(b) ... (ii) ... [2]").
"""
import glob, json, os, re, sys

SESS = {'m': ('F/M', 'February/March'), 's': ('M/J', 'May/June'), 'w': ('O/N', 'October/November')}
JUNK_LINE = re.compile(r'©|UCLES|Cambridge University Press|\[Turn over|Permission to reproduce|BLANK PAGE|'
                       r'DO NOT WRITE IN THIS MARGIN|^\s{6,}\d+\s*$|^\s*\*[\d ]+\*\s*$|[Ā-ſ]{3,}|^\s*[,.]\s*,?\s*$')
ROMAN = r'(?:i{1,3}|iv|vi{0,3}|ix|x)'
MARK = re.compile(r'\[(\d{1,2})\]')
# Part markers only count at the start of a line (or a roman straight after a letter), so '(ii)' quoted inside
# a sentence such as 'the value calculated in (ii)' is not mistaken for a new part.
TOKEN = re.compile(rf'(?m)^[ \t]*(?:\d{{1,2}}[ \t]+)?\(([a-h])\)|(?:^[ \t]*|(?<=\)) {{0,6}})\(({ROMAN})\)|\[(\d{{1,2}})\]')
FIG = re.compile(r'\b(?:Fig\.|Figure|Table|graph|chart)')


def clean(text):
    """Collapse whitespace and drop answer lines, 'mass = ....... kg' blanks and 'Reason 1:' style labels."""
    text = re.sub(r'(?:\b[\w ()]{1,30}=[ \t]*)?\.{4,}(?:[ \t]*[A-Za-z/%°]{1,5}(?![\w:]))?', ' ', text)
    text = re.sub(r'\b(?:Reason|Explanation|Advantage|Disadvantage|Method|Point|Answer|Working)\s*\d?\s*:', ' ', text)
    text = re.sub(r'\[Total:\s*\d+\]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def find_start(t, n, pos):
    """Start of question n: '<n> (a)' if the question opens with a part, otherwise the last '<n>   Prose…' line
    before that question's first '(a)'. Taking the last one skips chart axis ticks such as '1   Inflation rate'."""
    # The number may be followed by 2+ spaces, by one space when it has two digits ('10 Carbon-14 …'), or stand alone
    # on its line with the text on the next line. (Page numbers are indented, so JUNK_LINE drops them first.)
    direct = re.compile(rf'^[ \t]*{n}\s+(?=\(a\))', re.M)
    prose = re.compile(rf'^[ \t]*{n}(?:[ \t]{{2,}}|(?<=\d\d) |[ \t]*\n[ \t]*)(?=[A-Za-z‘“"])', re.M)
    first_a = re.compile(r'^[ \t]*(?:\d{1,2}[ \t]+)?\(a\)', re.M)
    m = direct.search(t, pos)
    cands, k = [], pos
    while True:
        c = prose.search(t, k)
        if not c or (m and c.start() > m.start()):
            break
        a = first_a.search(t, c.end())
        if a and not t[a.start():a.end()].strip().startswith(str(n)):
            cands.append(c)
        k = c.end()
    if cands:
        # keep the last prose candidate whose first following '(a)' is the same as the earliest candidate's
        target = first_a.search(t, cands[0].end()).start()
        best = [c for c in cands if first_a.search(t, c.end()).start() == target][-1]
        return best if not m or best.start() < m.start() else m
    return m


def split_questions(t):
    """Find question starts in order (1, 2, 3 ...); question numbers may be indented, as in Science papers."""
    starts, n, pos = [], 1, 0
    while True:
        m = find_start(t, n, pos)
        if not m and n == 1:  # unnumbered Question 1: carry on from Question 2
            n = 2
            continue
        if not m:
            break
        starts.append((n, m.start(), m.end()))
        pos, n = m.end(), n + 1
    # Some papers print Question 1's parts with no '1' (e.g. after 'Answer all parts of Question 1').
    if not starts or starts[0][0] != 1:
        first_part = re.search(r'(?m)^[ \t]*\(a\)', t)
        if first_part and (not starts or first_part.start() < starts[0][1]):
            starts.insert(0, (1, first_part.start(), first_part.start()))
    out = {}
    for k, (n, s, e) in enumerate(starts):
        end = starts[k + 1][1] if k + 1 < len(starts) else len(t)
        out[n] = t[e:end]
    preamble = t[:starts[0][1]] if starts else ''
    return out, preamble


def parse_question(body):
    """Walk (a)/(i)/[n] tokens; each [n] closes one leaf whose text runs from the previous token."""
    leaves, letter, roman, last = [], None, None, 0
    stem, letter_stem = None, ''
    for m in TOKEN.finditer(body):
        if m.group(1):
            if stem is None:
                stem = body[:m.start()]
            letter, roman, last, letter_stem = m.group(1), None, m.end(), ''
        elif m.group(2):
            if roman is None and letter:
                letter_stem = body[last:m.start()]
            roman, last = m.group(2), m.end()
        else:
            leaves.append(dict(part=letter, sub=roman, marks=int(m.group(3)), raw=body[last:m.start()],
                               letter_stem=letter_stem if roman else ''))
            last = m.end()
    return (stem if stem is not None else ''), leaves


def main():
    papers = sys.argv[1]
    code = sys.argv[sys.argv.index('--code') + 1] if '--code' in sys.argv else '*'
    out, seen = [], set()
    for f in sorted(glob.glob(f'{papers}/{code}_*_qp_*.txt')):
        name = os.path.basename(f)[:-4]
        subj, sy, _, comp = name.split('_')
        s, yy = sy[0], sy[1:]
        if s not in SESS:
            continue
        raw = open(f, encoding='utf-8', errors='replace').read()
        # Some papers print a control character (e.g. BEL \x07) after the question number; it hides the number.
        raw = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', ' ', raw)
        # Barcode text ('ĬÎÆĂÈđ…') can share a line with a part label such as '1 (b)'; blank it out.
        raw = re.sub(r'\S*[Ā-ſ]{3,}\S*', ' ', raw)
        t = '\n'.join(l for l in raw.splitlines() if not JUNK_LINE.search(l))
        insert = f'{papers}/{subj}_{sy}_in_{comp}.txt'
        source = clean(open(insert, encoding='utf-8', errors='replace').read()) if os.path.exists(insert) else ''
        questions, preamble = split_questions(t)
        # Section A source material (e.g. Economics Paper 2) sits before Question 1, after the cover instructions.
        cut = max(preamble.rfind('Section A'), preamble.rfind('Source material'), preamble.rfind('INFORMATION'))
        preamble = clean(preamble[cut:]) if cut >= 0 else ''
        for qn, body in questions.items():
            stem, leaves = parse_question(body)
            stem = clean(stem)
            for lf in leaves:
                if not lf['part']:
                    continue
                q = clean(lf['raw'])
                ref = f"{subj}/{comp}/{SESS[s][0]}/{yy} Q{qn}({lf['part']})" + (f"({lf['sub']})" if lf['sub'] else '')
                num = re.match(r'(\d)\.\s', q)
                if num:  # numbered sub-sub-parts, e.g. Q8(a)(ii) 1. and 2.
                    ref += f' {num.group(1)}.'
                k = 2
                while ref in seen:
                    ref, k = re.sub(r' \[\d+\]$', '', ref) + f' [{k}]', k + 1
                seen.add(ref)
                ctx = ' '.join(x for x in (stem, clean(lf['letter_stem'])) if x)
                out.append(dict(id=ref, session=f'{SESS[s][1]} 20{yy}', file=name, component=comp, q=qn,
                                part=lf['part'], sub=lf['sub'], marks=lf['marks'], question=q,
                                stem=clean(lf['letter_stem']) or None,
                                stimulus=(ctx or source or (preamble if qn == 1 else ''))[:3000],
                                refers_to_figure=bool(FIG.search(q + ' ' + ctx))))
    json.dump(out, open(f'{papers}/questions.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    by_file = {}
    for o in out:
        by_file[o['file']] = by_file.get(o['file'], 0) + 1
    print(f'{len(out)} question parts from {len(by_file)} papers')
    counts = sorted(by_file.items(), key=lambda kv: kv[1])
    print('fewest parts (check these papers by hand if a count looks low):', counts[:5])


if __name__ == '__main__':
    main()
