/* Show / hide answer buttons for past-paper questions (every page with span.pp-ref).
   In each past-paper example-block the question is the first paragraph that is entirely bold; everything after it
   (model answer, diagrams) plus the "Why this scores" box that follows the block is the answer. Answers start hidden.
   Each past-paper section also gets one "Show all answers" switch. Printing always shows the answers. */
(function () {
  var css = [
    '.pp-answer-toggle{display:inline-flex;align-items:center;gap:8px;margin:4px 0 14px;padding:8px 16px;border-radius:999px;',
    'border:1px solid var(--accent,#4a90d9);background:#fff;color:var(--blue,#1e3a5f);font:600 13.5px/1.2 "DM Sans",system-ui,sans-serif;',
    'font-style:normal;cursor:pointer;transition:background .15s,color .15s}',
    '.pp-answer-toggle:hover{background:var(--sky,#e8f0fe)}',
    '.pp-answer-toggle[aria-expanded="true"]{background:var(--sky,#e8f0fe)}',
    '.pp-answer-toggle:focus-visible{outline:2px solid var(--accent,#4a90d9);outline-offset:2px}',
    '.pp-answer-toggle .pp-caret{display:inline-block;font-size:11px;transition:transform .15s}',
    '.pp-answer-toggle[aria-expanded="true"] .pp-caret{transform:rotate(90deg)}',
    '.pp-answer[hidden],.pp-why[hidden]{display:none!important}',
    '.pp-all-bar{display:flex;justify-content:flex-end;margin:0 0 18px}',
    '.pp-all-toggle{margin:0}',
    '@media print{.pp-answer-toggle,.pp-all-bar{display:none!important}.pp-answer[hidden],.pp-why[hidden]{display:block!important}}'
  ].join('');
  var st = document.createElement('style');
  st.textContent = css;
  document.head.appendChild(st);

  var n = 0;
  function setOpen(btn, open) {
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    btn.querySelector('.pp-label').textContent = open ? 'Hide answer' : 'Show answer';
    (btn._parts || []).forEach(function (el) { el.hidden = !open; });
  }

  // A question paragraph is bold, optionally followed by its mark, e.g. "<strong>(b) Prepare …</strong> [5]".
  function isQuestion(k) {
    if (k.tagName !== 'P' || k.classList.contains('pp-stimulus')) return false;
    var s = k.firstElementChild;
    if (!s || s.tagName !== 'STRONG') return false;
    var rest = k.textContent.replace(s.textContent, '');
    return /^\s*(\[\d+\])?\s*$/.test(rest);
  }
  // Multi-part blocks (Accounting) print each part as its own question: "(a) …", "(c)(ii) …"
  function isPart(k) {
    return k.tagName === 'P' && !k.classList.contains('pp-stimulus') && k.firstElementChild &&
      k.firstElementChild.tagName === 'STRONG' && k.firstChild === k.firstElementChild &&
      /^\s*\((?:[a-h]|[ivx]+)\)/.test(k.firstElementChild.textContent);
  }
  // "<strong>(i)</strong> question<br>Answer: …" in one paragraph: move the answer into a paragraph of its own
  function splitInlineAnswer(p) {
    var brs = p.querySelectorAll(':scope > br');
    for (var i = 0; i < brs.length; i++) {
      var next = brs[i].nextSibling;
      if (next && next.nodeType === 3 && /^\s*Answer:/.test(next.textContent)) {
        var ans = document.createElement('p');
        while (brs[i].nextSibling) ans.appendChild(brs[i].nextSibling);
        p.removeChild(brs[i]);
        p.parentNode.insertBefore(ans, p.nextSibling);
        return;
      }
    }
  }

  document.querySelectorAll('.example-block').forEach(function (block) {
    if (!block.querySelector('.pp-ref')) return;
    Array.prototype.slice.call(block.children).forEach(function (k) { if (isPart(k)) splitInlineAnswer(k); });
    var kids = Array.prototype.slice.call(block.children), starts = [];
    for (var i = 0; i < kids.length; i++) {
      if (!starts.length ? (isQuestion(kids[i]) || isPart(kids[i])) : isPart(kids[i])) starts.push(i);
    }
    if (!starts.length) return;
    var btns = [];
    starts.forEach(function (q, j) {
      var end = j + 1 < starts.length ? starts[j + 1] : kids.length;
      var ans = kids.slice(q + 1, end);
      if (!ans.length) return;
      var wrap = document.createElement('div');
      wrap.className = 'pp-answer';
      wrap.id = 'pp-ans-' + (++n);
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'pp-answer-toggle';
      btn.setAttribute('aria-controls', wrap.id);
      btn.innerHTML = '<span class="pp-caret" aria-hidden="true">&#9656;</span><span class="pp-label">Show answer</span>';
      block.insertBefore(btn, ans[0]);
      block.insertBefore(wrap, ans[0]);
      ans.forEach(function (k) { wrap.appendChild(k); });
      btn._parts = [wrap];
      btns.push(btn);
    });
    if (!btns.length) return;
    var why = block.nextElementSibling, last = btns[btns.length - 1];
    if (why && why.classList.contains('tip-box') && /why this scores/i.test((why.querySelector('.tip-label') || {}).textContent || '')) {
      why.classList.add('pp-why');
      last._parts.push(why);
    }
    btns.forEach(function (btn) {
      setOpen(btn, false);
      btn.addEventListener('click', function () { setOpen(btn, btn.getAttribute('aria-expanded') !== 'true'); });
    });
  });

  // One "Show all answers" switch per section that has past-paper questions
  document.querySelectorAll('.section').forEach(function (sec) {
    var btns = sec.querySelectorAll('.pp-answer-toggle');
    if (btns.length < 2) return;
    var bar = document.createElement('div');
    bar.className = 'pp-all-bar';
    var all = document.createElement('button');
    all.type = 'button';
    all.className = 'pp-answer-toggle pp-all-toggle';
    all.setAttribute('aria-pressed', 'false');
    all.innerHTML = '<span class="pp-label">Show all answers</span>';
    all.addEventListener('click', function () {
      var open = all.getAttribute('aria-pressed') !== 'true';
      all.setAttribute('aria-pressed', open ? 'true' : 'false');
      all.querySelector('.pp-label').textContent = open ? 'Hide all answers' : 'Show all answers';
      btns.forEach(function (b) { setOpen(b, open); });
    });
    bar.appendChild(all);
    // After the "Jump to" line if the section has one, otherwise just above the first sub-topic heading / question
    var jump = sec.querySelector('.pp-jump');
    var first = btns[0].closest('.example-block');
    var h = sec.querySelector('h3');
    if (jump) jump.parentNode.insertBefore(bar, jump.nextSibling);
    else if (h && (h.compareDocumentPosition(first) & Node.DOCUMENT_POSITION_FOLLOWING)) h.parentNode.insertBefore(bar, h);
    else first.parentNode.insertBefore(bar, first);
  });
})();
