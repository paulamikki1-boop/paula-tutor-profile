#!/usr/bin/env python3
"""Download Cambridge question papers, mark schemes, inserts and examiner reports from PapaCambridge, then pdftotext them.

Usage: download_papers.py OUT_DIR --code 0455 --years 2020-2025 --components 21,22,23 [--sessions m,s,w]

Files land as OUT_DIR/<code>_<s><yy>_<type>_<comp>.pdf/.txt (types qp, ms, in) plus OUT_DIR/<code>_<s><yy>_er.txt and one _er_<comp>.txt per component.
Files that do not exist on the server (e.g. February/March is usually only variant 2) are skipped quietly.
Needs network access to pastpapers.papacambridge.com and the `pdftotext` command (poppler-utils).
"""
import argparse, os, re, subprocess, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE = 'https://pastpapers.papacambridge.com/directories/CAIE/CAIE-pastpapers/upload'


def fetch(out, name):
    pdf, txt = f'{out}/{name}.pdf', f'{out}/{name}.txt'
    if os.path.exists(txt):
        return name, 'cached'
    try:
        with urllib.request.urlopen(f'{BASE}/{name}.pdf', timeout=60) as r:
            data = r.read()
    except Exception:
        return name, 'missing'
    if not data.startswith(b'%PDF'):
        return name, 'missing'
    open(pdf, 'wb').write(data)
    subprocess.run(['pdftotext', '-layout', pdf, txt], stderr=subprocess.DEVNULL, check=False)
    return name, 'ok' if os.path.exists(txt) else 'pdftotext failed'


def split_reports(out, code, reports):
    """Examiner reports cover every component and each restarts at 'Question 1'. Write one file per component
    (<code>_<s><yy>_er_<comp>.txt) by cutting at the 'Paper <code>/<comp>' headings."""
    for name in reports:
        t = open(f'{out}/{name}.txt', encoding='utf-8', errors='replace').read()
        heads = [(m.start(), m.group(1)) for m in re.finditer(rf'^\s*Paper\s+{code}/(\d\d)\b', t, re.M)]
        parts = {}
        for k, (pos, comp) in enumerate(heads):
            end = heads[k + 1][0] if k + 1 < len(heads) else len(t)
            parts[comp] = parts.get(comp, '') + t[pos:end]
        for comp, text in parts.items():
            open(f'{out}/{name}_{comp}.txt', 'w', encoding='utf-8').write(text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('--code', required=True)
    ap.add_argument('--years', default='2020-2025')
    ap.add_argument('--components', required=True, help='comma list, e.g. 21,22,23 or 41,42,43')
    ap.add_argument('--sessions', default='m,s,w')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    y0, y1 = (int(x) for x in a.years.split('-'))
    names = []
    for y in range(y0, y1 + 1):
        yy = f'{y % 100:02d}'
        for s in a.sessions.split(','):
            names.append(f'{a.code}_{s}{yy}_er')
            for c in a.components.split(','):
                names += [f'{a.code}_{s}{yy}_{t}_{c}' for t in ('qp', 'ms', 'in')]
    with ThreadPoolExecutor(6) as ex:
        results = list(ex.map(lambda n: fetch(a.out, n), names))
    got = [n for n, st in results if st in ('ok', 'cached')]
    split_reports(a.out, a.code, [n for n in got if n.endswith('_er')])
    qps = [n for n in got if '_qp_' in n]
    print(f'{len(got)} files ({len(qps)} question papers, {sum("_ms_" in n for n in got)} mark schemes, '
          f'{sum("_in_" in n for n in got)} inserts, {sum(n.endswith("_er") for n in got)} examiner reports)')
    no_ms = [q for q in qps if q.replace('_qp_', '_ms_') not in got]
    if no_ms:
        print('question papers with no mark scheme (do not use them):', ', '.join(no_ms))
    if not qps:
        sys.exit('No question papers downloaded: check the subject code, components and network access.')


if __name__ == '__main__':
    main()
