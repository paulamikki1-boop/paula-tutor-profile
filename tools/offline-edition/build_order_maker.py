#!/usr/bin/env python3
"""Build Order-Maker.html: one file Paula keeps on her laptop to make buyer copies with no tokens and no internet.

    python3 tools/offline-edition/build_order_maker.py --out ~/Desktop

It makes a master copy of every subject (make_offline.py --master), packs them into one HTML page (gzip + base64;
photos shared between subjects are stored once) and adds a small form: pick the subject, type the buyer's name and
the order number, click "Make copy" and the browser saves the personalised file. The result is byte-for-byte the
same as running make_offline.py with that name and order. Re-run this after the notes change.
"""
import argparse, base64, collections, datetime, gzip, html, json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
SUBJECTS = ['chemistry', 'biology', 'physics', 'economics', 'business', 'accounting', 'english-writing-forms']

ap = argparse.ArgumentParser()
ap.add_argument('--out', required=True, help='folder for Order-Maker.html (outside the repo)')
a = ap.parse_args()
out_dir = os.path.abspath(os.path.expanduser(a.out))
if out_dir == REPO or out_dir.startswith(REPO + os.sep):
    sys.exit('--out must be outside the repository')

tmp = tempfile.mkdtemp(prefix='order-maker-')
masters = {}
for s in SUBJECTS:
    r = subprocess.run([sys.executable, os.path.join(HERE, 'make_offline.py'), s, '--master', '--out', tmp], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f'{s}: {r.stderr.strip() or r.stdout.strip()}')
    masters[s] = open(os.path.join(tmp, f'master-{s}.html')).read()
shutil.rmtree(tmp, ignore_errors=True)

# photos and other big embedded files that appear in more than one subject are stored once
uris = collections.Counter()
for doc in masters.values():
    uris.update(set(re.findall(r'data:image/(?:jpeg|png|webp);base64,[A-Za-z0-9+/=]{20000,}', doc)))
shared = [u for u, n in uris.items() if n > 1]
subjects = []
for s, doc in masters.items():
    for i, u in enumerate(shared):
        doc = doc.replace(u, f'QQASSET{i}QQ')
    h1 = re.search(r'<nav class="sidebar">.*?<h1>(.*?)</h1>', doc, re.S).group(1)   # the notes title, not the About page headline
    subjects.append(dict(key=s, h1=html.unescape(h1), questions=doc.count('class="pp-ref"'),
                         kb=len(masters[s]) // 1024, data=base64.b64encode(gzip.compress(doc.encode(), 9)).decode()))

def font(name):
    return base64.b64encode(open(os.path.join(HERE, 'fonts', name), 'rb').read()).decode()

built = datetime.date.today().strftime('%d %b %Y')
options = '\n'.join(f'<option value="{x["key"]}">{html.escape(x["h1"])}'
                    f'{f" ({x["questions"]} past-paper questions)" if x["questions"] else ""}</option>' for x in subjects)
meta = json.dumps({x['key']: {'h1': x['h1']} for x in subjects})
blocks = '\n'.join(f'<script type="text/plain" id="m-{x["key"]}">{x["data"]}</script>' for x in subjects)
assets = '\n'.join(f'<script type="text/plain" id="a-{i}">{u}</script>' for i, u in enumerate(shared))

page = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex">
<title>Order Maker | Paula's notes</title>
<style>
@font-face {{ font-family: 'DM Sans'; font-weight: 100 1000; src: url(data:font/woff2;base64,{font('DMSans-latin-var.woff2')}) format('woff2'); }}
@font-face {{ font-family: 'DM Mono'; font-weight: 400; src: url(data:font/woff2;base64,{font('DMMono-400.woff2')}) format('woff2'); }}
:root {{ --navy: #0a1628; --blue: #1e3a5f; --accent: #4a90d9; --deep: #2563eb; --sky: #e8f0fe; --line: #e1e7f0; --muted: #5d6b80; --green: #0a7b5e; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: 'DM Sans', system-ui, sans-serif; background: #f5f7fb; color: #46546a; min-height: 100vh; padding: 40px 16px; }}
.card {{ max-width: 560px; margin: 0 auto; background: #fff; border: 1px solid var(--line); border-radius: 24px; padding: 32px; box-shadow: 0 12px 32px -12px rgba(10,22,40,.14); }}
.brand {{ display: flex; align-items: center; gap: 10px; font-weight: 700; color: var(--navy); font-size: 17px; }}
.mark {{ width: 30px; height: 30px; border-radius: 9px; background: linear-gradient(135deg, var(--deep), var(--green)); color: #fff; display: grid; place-items: center; font-size: 14px; }}
h1 {{ font-size: 30px; letter-spacing: -.02em; color: var(--navy); margin: 22px 0 6px; }}
p.lead {{ font-size: 15.5px; margin-bottom: 22px; }}
label {{ display: block; font-family: 'DM Mono', monospace; font-size: 12px; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); margin: 16px 0 6px; }}
select, input {{ width: 100%; font: inherit; font-size: 16px; color: var(--navy); background: #f5f7fb; border: 1px solid var(--line); border-radius: 12px; padding: 12px 14px; }}
select:focus, input:focus {{ outline: none; border-color: var(--accent); background: #fff; box-shadow: 0 0 0 3px rgba(74,144,217,.18); }}
button {{ width: 100%; margin-top: 22px; font: inherit; font-weight: 600; font-size: 16px; color: #fff; background: var(--navy); border: 0; border-radius: 12px; padding: 14px; cursor: pointer; }}
button:hover {{ background: #14274a; }}
button:disabled {{ opacity: .6; cursor: wait; }}
.status {{ margin-top: 16px; font-size: 14.5px; min-height: 22px; }}
.status.ok {{ color: var(--green); }} .status.err {{ color: #b42318; }}
.made {{ margin-top: 18px; padding: 14px 16px; background: var(--sky); border-radius: 12px; font-size: 14px; display: none; }}
.made a {{ color: var(--deep); font-weight: 600; }}
.foot {{ max-width: 560px; margin: 18px auto 0; font-size: 13px; color: var(--muted); line-height: 1.55; }}
</style>
</head>
<body>
<div class="card">
  <div class="brand"><span class="mark">P</span>Paula &middot; Order Maker</div>
  <h1>Make a buyer&rsquo;s copy</h1>
  <p class="lead">Choose the subject, type the buyer&rsquo;s name and Shopee order number, then save the file and send it to the buyer. Works offline; nothing is sent anywhere.</p>
  <label for="subject">Subject</label>
  <select id="subject">{options}</select>
  <label for="buyer">Buyer&rsquo;s name</label>
  <input id="buyer" autocomplete="off" placeholder="e.g. Aisha Rahman">
  <label for="order">Order number</label>
  <input id="order" autocomplete="off" placeholder="e.g. 2611220001">
  <button id="make" type="button">Make copy</button>
  <div class="status" id="status"></div>
  <div class="made" id="made"></div>
</div>
<p class="foot">Notes version: {built}. When you update your notes, ask Claude to rebuild the Order Maker so new copies include the changes. Each copy shows your &copy; and the buyer&rsquo;s name and order number on every page.</p>
{blocks}
{assets}
<script>
var META = {meta};
function esc(s) {{ return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#x27;'); }}
// same encoding as Python urllib.parse.quote(s, safe="=:/,'%() .#")
function pyquote(s) {{
  return encodeURIComponent(s).replace(/%(3D|3A|2F|2C|25|20|23)/g, function (m) {{ return decodeURIComponent(m); }})
    .replace(/[!*]/g, function (c) {{ return '%' + c.charCodeAt(0).toString(16).toUpperCase(); }});
}}
function tidy(s) {{ return s.replace(/\\s+/g, ' ').trim(); }}
async function unpack(key) {{
  var b64 = document.getElementById('m-' + key).textContent.trim();
  var bytes = Uint8Array.from(atob(b64), function (c) {{ return c.charCodeAt(0); }});
  var stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));
  var doc = await new Response(stream).text();
  return doc.replace(/QQASSET(\\d+)QQ/g, function (m, i) {{ return document.getElementById('a-' + i).textContent.trim(); }});
}}
function personalise(doc, buyer, order) {{
  // inside the watermark picture the text is URL-encoded; everywhere else it is plain HTML
  var parts = doc.split(/(data:image\\/svg\\+xml;utf8,[^"]*)/);
  return parts.map(function (p, i) {{
    if (i % 2) return p.split('QQBUYERQQ').join(pyquote(esc(buyer))).split('QQORDERQQ').join(pyquote(esc(order)));
    return p.split('QQBUYERQQ').join(esc(buyer)).split('QQORDERQQ').join(esc(order));
  }}).join('');
}}
function fileName(key, buyer, order) {{
  var safe = buyer.replace(/[^A-Za-z0-9]+/g, '-').replace(/^-+|-+$/g, '') || 'buyer';
  return META[key].h1.replace(/ /g, '-') + '-' + safe + '-' + order.replace(/[^A-Za-z0-9]+/g, '') + '.html';
}}
document.getElementById('make').addEventListener('click', async function () {{
  var st = document.getElementById('status'), made = document.getElementById('made'), btn = this;
  var key = document.getElementById('subject').value, buyer = tidy(document.getElementById('buyer').value), order = tidy(document.getElementById('order').value);
  st.className = 'status'; made.style.display = 'none';
  if (!buyer || !order) {{ st.className = 'status err'; st.textContent = 'Please type the buyer\\u2019s name and the order number.'; return; }}
  if (typeof DecompressionStream === 'undefined') {{ st.className = 'status err'; st.textContent = 'This browser is too old. Please open the Order Maker in an up-to-date Chrome, Edge or Safari.'; return; }}
  btn.disabled = true; st.textContent = 'Making the copy\\u2026';
  try {{
    var doc = personalise(await unpack(key), buyer, order);
    var name = fileName(key, buyer, order);
    var url = URL.createObjectURL(new Blob([doc], {{ type: 'text/html' }}));
    var a = document.createElement('a'); a.href = url; a.download = name; document.body.appendChild(a); a.click(); a.remove();
    st.className = 'status ok'; st.textContent = 'Saved: ' + name;
    made.innerHTML = 'Check your Downloads folder. <a href="' + url + '" target="_blank" rel="noopener">Preview this copy</a>';
    made.style.display = 'block';
  }} catch (e) {{ st.className = 'status err'; st.textContent = 'Something went wrong: ' + e.message; }}
  btn.disabled = false;
}});
</script>
</body>
</html>
'''
os.makedirs(out_dir, exist_ok=True)
path = os.path.join(out_dir, 'Order-Maker.html')
open(path, 'w').write(page)
print(f'{path}  ({len(page) // 1024} KB, {len(subjects)} subjects, {len(shared)} shared photos)')
