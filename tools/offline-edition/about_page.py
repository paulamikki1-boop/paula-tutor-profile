"""Build the 'About Paula' view for an offline copy from the live homepage (index.html).

The view looks like the homepage (hero with photo, About Me, own results, subjects, approach, student results,
reviews, contact) but leaves out everything about the free website: no Notes/Resources/Marking/Shop links, no
marking card or "past papers marked" badge, no "Free notes" subject links, no portfolio link. Images are shrunk so the
file stays small. All CSS is scoped under #about-view so it cannot clash with the notes page styles.
"""
import base64, io, re

try:
    from PIL import Image
except ImportError:  # images are then kept at full size
    Image = None

FORBIDDEN = re.compile(r'free (notes|revision|study)|github\.io|resources/|marking/|shop/|payhip|past papers marked', re.I)


def _shrink(m):
    kind, data = m.group(1), m.group(2)
    if Image is None or len(data) < 60_000:
        return m.group(0)
    try:
        im = Image.open(io.BytesIO(base64.b64decode(data)))
        im = im.convert('RGB')
        im.thumbnail((900, 900))
        buf = io.BytesIO()
        im.save(buf, 'JPEG', quality=72, optimize=True)
        return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return m.group(0)


def _scope_css(css):
    """Prefix every selector with #about-view; drop the homepage's own nav rules."""
    out = []
    def scope_rules(block):
        res = []
        for m in re.finditer(r'([^{}]+)\{([^{}]*)\}', block):
            sels, body = m.group(1).strip(), m.group(2)
            new = []
            for sel in sels.split(','):
                sel = sel.strip()
                if not sel:
                    continue
                if re.match(r'(nav\b|\.nav|\.brand|\.hub-link|html\b)', sel):
                    continue
                if sel == ':root' or sel == 'body':
                    new.append('#about-view')
                elif sel == '*':
                    new.append('#about-view, #about-view *')
                elif sel.startswith(':focus-visible'):
                    new.append('#about-view ' + sel)
                else:
                    new.append('#about-view ' + sel)
            if new:
                res.append(', '.join(new) + ' {' + body + '}')
        return '\n'.join(res)
    i = 0
    for m in re.finditer(r'@media[^{]+\{((?:[^{}]*\{[^{}]*\})*)\s*\}', css):
        out.append(scope_rules(css[i:m.start()]))
        inner = scope_rules(m.group(1))
        if inner:
            out.append(css[m.start():css.index('{', m.start())] + '{\n' + inner + '\n}')
        i = m.end()
    out.append(scope_rules(css[i:]))
    return '\n'.join(out)


def build(index_html, notes_line):
    """Return (css, html, js) for the about view. notes_line: short HTML sentence about the notes in this copy."""
    css = index_html[index_html.index('<style>') + 7:index_html.index('</style>')]
    body = index_html[index_html.index('<div class="wrap">'):index_html.index('<div class="lightbox"')]
    lightbox = re.search(r'<div class="lightbox".*?</div>', index_html, re.S).group(0)

    # remove the free-site and marking bits
    body = re.sub(r'\s*<a class="card card-dark" href="marking/">.*?</a>', '', body, flags=re.S)
    body = body.replace('<div class="duo">', '<div class="duo solo">', 1)
    body = re.sub(r'\s*<div class="chip chip-b">.*?</div>', '', body, flags=re.S)
    body = re.sub(r'<a href="resources/"[^>]*>.*?</a>', '', body, flags=re.S)   # "Browse free notes"
    sub = re.search(r'<section id="subjects">.*?</section>', body, re.S)
    if sub:
        s = sub.group(0)
        s = re.sub(r'<a class="subject-card" href="[^"]*">(.*?)</a>', r'<div class="subject-card">\1</div>', s, flags=re.S)
        s = re.sub(r'<div class="subject-notes">.*?</div>', '', s, flags=re.S)
        s = re.sub(r'(<div class="section-head">.*?</div>)\s*<p>.*?</p>', r'\1', s, count=1, flags=re.S)
        body = body.replace(sub.group(0), s)
    body = re.sub(r'\s*&nbsp;&middot;&nbsp;\s*<a href="https://paulamikki1-boop\.github\.io/[^"]*">.*?</a>', '', body, flags=re.S)
    # a short line about these notes, under the hero
    body = body.replace('<div class="strip"', f'<div class="notes-about"><span class="kicker">About these notes</span><p>{notes_line}</p></div>\n  <div class="strip"', 1)
    body = re.sub(r'data:image/(\w+);base64,([A-Za-z0-9+/=]+)', _shrink, body)

    left = FORBIDDEN.findall(re.sub(r'data:image/[^"]+', '', body))
    if left:
        raise SystemExit(f'about page still mentions the website: {left[:5]}')

    scoped = _scope_css(css)
    scoped += '''
#about-view { display: block; position: relative; overflow: hidden; }
#about-view h1, #about-view h2, #about-view h3 { border: 0; padding: 0; }
#about-view .duo.solo { grid-template-columns: 1fr; }
#about-view .notes-about { background: #fff; border: 1px solid var(--line); border-radius: 16px; padding: 18px 24px; margin-bottom: 14px; }
#about-view .notes-about p { margin-top: 6px; font-size: 16px; color: var(--body); }
#about-view .wrap { padding-top: 8px; }
body:not(.show-about) #about-view { display: none !important; }
body.show-about .hamburger, body.show-about .notes-layout, body.show-about .cta-section, body.show-about .footer { display: none !important; }
'''
    html = f'<div id="about-view">\n<div class="backdrop" aria-hidden="true"></div>\n{body}\n{lightbox}\n</div>\n'
    js = '''<script>/* offline copy: Home shows the About page, everything else shows the notes */
function openLightbox(el) { var img = el.querySelector('img'); document.getElementById('lightbox-img').src = img.src; document.getElementById('lightbox').classList.add('active'); }
function closeLightbox() { document.getElementById('lightbox').classList.remove('active'); }
document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeLightbox(); });
function sendWhatsApp() {
  var name = document.getElementById('msg-name').value.trim(), subject = document.getElementById('msg-subject').value.trim(), text = document.getElementById('msg-text').value.trim();
  var message = 'Hi Paula!'; if (name) message += ' My name is ' + name + '.'; if (subject) message += ' I am interested in tutoring for ' + subject + '.'; if (text) message += ' ' + text;
  window.open('https://wa.me/60103686902?text=' + encodeURIComponent(message), '_blank');
}
(function () {
  var view = document.getElementById('about-view');
  function route() {
    var h = location.hash.slice(1), el = h && document.getElementById(h);
    var inAbout = h === 'home' || (el && view.contains(el));
    document.body.classList.toggle('show-about', !!inAbout);
    if (inAbout) { if (h === 'home') window.scrollTo(0, 0); else setTimeout(function () { el.scrollIntoView(); }, 20); }
    else if (h === 'notes') {
      var first = document.querySelector('.nav-item.active[data-section]') || document.querySelector('.nav-item[data-section]');
      showSection(first.dataset.section);
      window.scrollTo(0, 0);
    }
  }
  route();
  window.addEventListener('hashchange', route);
})();
</script>
'''
    return scoped, html, js
