/* Shared search for the resources hub and the notes pages.
   Uses resources/search-index.json (rebuild with tools/build-search-index.py). */
(function () {
  var script = document.currentScript;
  var BASE = script.src.replace(/search\.js(\?.*)?$/, '');   // URL of /resources/
  var index = null, loading = null;

  function load() {
    if (index) return Promise.resolve(index);
    if (!loading) loading = fetch(BASE + 'search-index.json').then(function (r) { return r.json(); })
      .then(function (d) { index = d; return d; });
    return loading;
  }

  function esc(s) { return s.replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function words(q) { return q.toLowerCase().split(/\s+/).filter(function (w) { return w.length > 1; }); }

  // Rank: whole phrase in heading > phrase in text > all words present
  function search(q, subject) {
    var phrase = q.trim().toLowerCase(), ws = words(q), out = [];
    if (phrase.length < 2) return out;
    index.forEach(function (e) {
      if (subject && e.s !== subject) return;
      var head = (e.t + ' ' + e.h).toLowerCase(), body = e.x.toLowerCase(), score = 0;
      if (head.indexOf(phrase) >= 0) score = 100;
      else if (body.indexOf(phrase) >= 0) score = 60;
      else if (ws.length && ws.every(function (w) { return head.indexOf(w) >= 0 || body.indexOf(w) >= 0; })) score = 20;
      if (!score) return;
      ws.forEach(function (w) { if (head.indexOf(w) >= 0) score += 5; });
      if (!/^(Worked Examples|Model Answers)/.test(e.t)) score += 3;   // prefer the notes over practice answers
      out.push({ e: e, score: score });
    });
    out.sort(function (a, b) { return b.score - a.score; });
    return out;
  }

  function snippet(text, q) {
    var lower = text.toLowerCase(), phrase = q.trim().toLowerCase(), at = lower.indexOf(phrase), len = phrase.length;
    if (at < 0) { var w = words(q)[0] || ''; at = lower.indexOf(w); len = w.length; }
    if (at < 0) at = 0;
    var start = Math.max(0, at - 60), s = text.slice(start, start + 180);
    var out = (start ? '…' : '') + esc(s) + (start + 180 < text.length ? '…' : '');
    words(q).forEach(function (w) {
      out = out.replace(new RegExp('(' + w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi'), '<mark>$1</mark>');
    });
    return out;
  }

  function resultHTML(r, q, sameSubject) {
    var e = r.e, href = BASE + e.u + '?q=' + encodeURIComponent(q.trim()) + '#' + e.id;
    return '<a class="sr-item" href="' + href + '">' +
      (sameSubject ? '' : '<span class="sr-subject">' + esc(e.s) + '</span>') +
      '<span class="sr-title">' + esc(e.t) + (e.h ? ' <span class="sr-sep">›</span> ' + esc(e.h) : '') + '</span>' +
      '<span class="sr-snippet">' + snippet(e.x, q) + '</span></a>';
  }

  function attach(input, box, subject, limit) {
    var timer;
    function run() {
      var q = input.value;
      if (q.trim().length < 2) { box.innerHTML = ''; box.hidden = true; return; }
      load().then(function () {
        var res = search(q, subject);
        box.hidden = false;
        box.innerHTML = res.length
          ? '<div class="sr-count">' + res.length + ' result' + (res.length === 1 ? '' : 's') + '</div>' +
            res.slice(0, limit).map(function (r) { return resultHTML(r, q, !!subject); }).join('')
          : '<div class="sr-empty">No matches for “' + esc(q.trim()) + '”. Try a shorter phrase.</div>';
      });
    }
    input.addEventListener('focus', load);
    input.addEventListener('input', function () { clearTimeout(timer); timer = setTimeout(run, 150); });
    input.addEventListener('keydown', function (ev) {
      if (ev.key === 'Enter') { var first = box.querySelector('.sr-item'); if (first) location.href = first.href; }
      if (ev.key === 'Escape') { input.value = ''; run(); }
    });
    return run;
  }

  var css = document.createElement('style');
  css.textContent =
    '.sr-wrap{position:relative}' +
    '.sr-input{width:100%;font:inherit;font-size:.95rem;padding:.7rem .9rem .7rem 2.4rem;border:1.5px solid #d0d8e4;border-radius:8px;background:#fff url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'18\' height=\'18\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'%234a5568\' stroke-width=\'2\'%3E%3Ccircle cx=\'11\' cy=\'11\' r=\'7\'/%3E%3Cpath d=\'M21 21l-4.3-4.3\'/%3E%3C/svg%3E") no-repeat .75rem center;color:#0a1628}' +
    '.sr-input:focus{outline:2px solid #4a90d9;outline-offset:1px;border-color:#4a90d9}' +
    '.sr-results{margin-top:.5rem;background:#fff;border:1px solid #dde4ee;border-radius:8px;box-shadow:0 6px 20px rgba(10,22,40,.08);max-height:60vh;overflow:auto}' +
    '.sr-count,.sr-empty{font-size:.8rem;color:#4a5568;padding:.6rem .9rem}' +
    '.sr-item{display:block;padding:.65rem .9rem;border-top:1px solid #eef2f7;text-decoration:none;color:#0a1628}' +
    '.sr-item:hover,.sr-item:focus{background:#f5f8fc}' +
    '.sr-subject{display:inline-block;font-size:.68rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;background:#e8f0fe;color:#1e3a5f;border-radius:3px;padding:.05rem .4rem;margin-right:.4rem;vertical-align:1px}' +
    '.sr-title{font-weight:600;font-size:.92rem}.sr-sep{color:#4a90d9}' +
    '.sr-snippet{display:block;font-size:.83rem;color:#4a5568;margin-top:.2rem;line-height:1.5}' +
    '.sr-snippet mark,mark.sr-hit{background:#fff1a8;color:inherit;padding:0 1px;border-radius:2px}' +
    '.sidebar .sr-wrap{padding:0 16px 12px}.sidebar .sr-input{font-size:.85rem;padding:.55rem .7rem .55rem 2.2rem;background-position:.6rem center}' +
    '.sidebar .sr-results{max-height:50vh}';
  document.head.appendChild(css);

  // ---- Resources hub: search across every subject ----
  var hub = document.getElementById('site-search');
  if (hub) {
    var hubBox = document.getElementById('site-search-results');
    var runHub = attach(hub, hubBox, null, 30);
    var q0 = new URLSearchParams(location.search).get('q');
    if (q0) { hub.value = q0; runHub(); }
    hub.addEventListener('input', function () {
      var p = new URLSearchParams(location.search);
      if (hub.value.trim()) p.set('q', hub.value.trim()); else p.delete('q');
      var qs = p.toString(); history.replaceState(null, '', location.pathname + (qs ? '?' + qs : ''));
    });
  }

  // ---- Notes pages: search box in the sidebar + highlight the searched words ----
  var header = document.querySelector('.sidebar .sidebar-header');
  if (header) {
    var subject = { 'igcse-biology-notes': 'Biology', 'igcse-chemistry-notes': 'Chemistry', 'igcse-economics-notes': 'Economics',
                    'igcse-accounting-notes': 'Accounting', 'igcse-english-writing-forms': 'English' }[location.pathname.split('/').filter(Boolean).slice(-1)[0]];
    var wrap = document.createElement('div');
    wrap.className = 'sr-wrap';
    wrap.innerHTML = '<input class="sr-input" type="search" placeholder="Search these notes…" aria-label="Search these notes"><div class="sr-results" hidden></div>';
    header.insertAdjacentElement('afterend', wrap);
    attach(wrap.querySelector('input'), wrap.querySelector('.sr-results'), subject, 15);

    function highlight() {
      var q = new URLSearchParams(location.search).get('q');
      var sec = document.querySelector('.section.active');
      if (!q || !sec) return;
      document.querySelectorAll('mark.sr-hit').forEach(function (m) { m.replaceWith(document.createTextNode(m.textContent)); });
      var phrase = q.toLowerCase(), first = null, ws = words(q);
      var needles = [phrase].concat(ws);
      for (var n = 0; n < needles.length && !first; n++) {
        var needle = needles[n];
        var walker = document.createTreeWalker(sec, NodeFilter.SHOW_TEXT, null), node, hits = [];
        while ((node = walker.nextNode())) {
          if (node.parentNode.closest('svg,script,style')) continue;
          if (node.nodeValue.toLowerCase().indexOf(needle) >= 0) hits.push(node);
        }
        hits.forEach(function (tn) {
          var v = tn.nodeValue, i = v.toLowerCase().indexOf(needle);
          var mid = tn.splitText(i); mid.splitText(needle.length);
          var mk = document.createElement('mark'); mk.className = 'sr-hit'; mk.textContent = mid.nodeValue;
          mid.replaceWith(mk); if (!first) first = mk;
        });
      }
      if (first) setTimeout(function () { first.scrollIntoView({ block: 'center' }); }, 50);
    }
    window.addEventListener('hashchange', function () { setTimeout(highlight, 0); });
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', highlight); else setTimeout(highlight, 0);
  }
})();
