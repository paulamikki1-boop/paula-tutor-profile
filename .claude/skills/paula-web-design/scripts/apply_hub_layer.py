#!/usr/bin/env python3
"""Apply (or refresh) the hub-style layer on the tutor site's inner pages.

Every notes, hub, marking, shop and guide page carries its own <style> block. This appends
styles/hub-pages-layer.css to the end of that block (replacing an earlier copy) and swaps the
Google Fonts link to DM Sans + DM Mono. It never touches page content. Run from the repo root:

    python3 .claude/skills/paula-web-design/scripts/apply_hub_layer.py
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
LAYER = (pathlib.Path(__file__).resolve().parents[1] / 'styles' / 'hub-pages-layer.css').read_text(encoding='utf-8').strip()
FONTS = ('<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&'
         'family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&display=swap" rel="stylesheet">')
SKIP = {'index.html', 'resources/_template-pdf.html'}   # homepage has its own full stylesheet; PDF template is print-only

pages = sorted(p for p in ROOT.rglob('*.html')
               if not any(part.startswith('.') or part == 'hub-draft' for part in p.relative_to(ROOT).parts)
               and str(p.relative_to(ROOT)) not in SKIP)
for p in pages:
    s = p.read_text(encoding='utf-8')
    if s.count('</style>') != 1:
        print('SKIPPED (expected one <style> block):', p.relative_to(ROOT)); continue
    s = re.sub(r'\n?/\* >>> hub-style layer.*?/\* <<< hub-style layer \*/\n?', '\n', s, flags=re.S)
    s = s.replace('</style>', LAYER + '\n</style>', 1)
    s, n = re.subn(r'<link[^>]*href="https://fonts\.googleapis\.com/css2[^"]*"[^>]*>', FONTS, s, count=1)
    if n != 1:
        print('WARNING: no Google Fonts link found in', p.relative_to(ROOT))
    p.write_text(s, encoding='utf-8')
    print('ok', p.relative_to(ROOT))
