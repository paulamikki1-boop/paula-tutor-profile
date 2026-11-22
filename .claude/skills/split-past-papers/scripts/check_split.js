// Browser check for a split notes / past-papers pair.
//   node check_split.js http://localhost:8765/resources/ igcse-biology-notes [screenshot-dir]
// Serve the repo root first:  python3 -m http.server 8765
// Checks at desktop and phone width: every sidebar section opens, no sideways scroll, no console errors,
// notes -> past papers and past papers -> notes link boxes land on the right section, old #pp-... links on the
// notes page forward, and a sub-topic heading hash (#pp-x-y) opens on the past-papers page.
const { chromium, devices } = require('playwright');
const [BASE, NOTES, SHOTS] = process.argv.slice(2);
if (!BASE || !NOTES) { console.error('usage: node check_split.js <base-url-of-resources/> <notes-slug> [screenshot-dir]'); process.exit(2); }
const PP = NOTES.replace(/-notes$/, '-past-papers');
const N = BASE + NOTES + '/', P = BASE + PP + '/';
let failures = 0;
const fail = (...m) => { failures++; console.log('  FAIL', ...m); };

(async () => {
  const b = await chromium.launch();
  for (const mode of ['desktop', 'phone']) {
    const ctx = mode === 'desktop' ? await b.newContext({ viewport: { width: 1366, height: 900 } }) : await b.newContext({ ...devices['iPhone 13'] });
    const p = await ctx.newPage(); const errs = [];
    p.on('pageerror', e => errs.push(e.message));
    p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
    const active = () => p.$eval('.section.active', e => e.id).catch(() => null);
    for (const U of [N, P]) {
      await p.goto(U); await p.waitForTimeout(300);
      const secs = await p.$$eval('.nav-item[data-section]', a => a.map(e => e.dataset.section));
      for (const s of secs) {
        await p.goto(U + '#' + s); await p.waitForTimeout(80);
        const r = await p.evaluate(() => ({ id: (document.querySelector('.section.active') || {}).id, sw: document.documentElement.scrollWidth, w: innerWidth }));
        if (r.id !== 'sec-' + s) fail(mode, U, '#' + s, 'opened', r.id);
        if (r.sw > r.w + 1) fail(mode, U, '#' + s, 'scrolls sideways', r.sw, '>', r.w);
      }
      console.log(mode, U.replace(BASE, ''), secs.length, 'sections opened');
    }
    // notes -> past papers, for every notes section that has a link box
    await p.goto(N); await p.waitForTimeout(200);
    const boxed = await p.$$eval('.section', ss => ss.filter(s => s.querySelector('a.pp-link-box')).map(s => [s.id.slice(4), s.querySelector('a.pp-link-box').getAttribute('href')]));
    for (const [sid, href] of boxed) {
      await p.goto(N + '#' + sid); await p.waitForTimeout(120);
      await p.click('.section.active a.pp-link-box >> nth=0'); await p.waitForTimeout(400);
      const want = 'sec-' + href.split('#')[1];
      if ((await active()) !== want || !p.url().includes(PP)) fail(mode, 'notes box', sid, '->', p.url(), await active());
    }
    console.log(mode, 'notes -> past papers boxes', boxed.length, 'checked');
    // past papers -> notes
    await p.goto(P); await p.waitForTimeout(200);
    const back = await p.$$eval('.section', ss => ss.filter(s => s.querySelector('a.pp-link-box')).map(s => [s.id.slice(4), s.querySelector('a.pp-link-box').getAttribute('href')]));
    for (const [sid, href] of back) {
      await p.goto(P + '#' + sid); await p.waitForTimeout(120);
      await p.click('.section.active a.pp-link-box'); await p.waitForTimeout(400);
      const want = 'sec-' + href.split('#')[1];
      if ((await active()) !== want || !p.url().includes(NOTES)) fail(mode, 'back box', sid, '->', p.url(), await active());
    }
    console.log(mode, 'past papers -> notes boxes', back.length, 'checked');
    // old links forward, and sub-topic heading hashes open
    await p.goto(P); await p.waitForTimeout(200);
    const units = await p.$$eval('.nav-item[data-section]', a => a.map(e => e.dataset.section));
    const h3 = await p.$$eval('.section h3[id^="pp-"]', a => a.map(e => [e.id, e.closest('.section').id]));
    const tests = [[units[units.length - 1], 'sec-' + units[units.length - 1]]].concat(h3.length ? [h3[Math.floor(h3.length / 2)]] : []);
    for (const [h, sec] of tests) {
      await p.goto(N + '#' + h); await p.waitForTimeout(900);
      if (!p.url().includes(PP + '/') || (await active()) !== sec) fail(mode, 'old link #' + h, '->', p.url(), await active());
      else console.log(mode, 'old link #' + h, 'forwards ok');
    }
    if (SHOTS) {
      await p.goto(N + '#' + (boxed[0] || [''])[0]); await p.waitForTimeout(300);
      await p.screenshot({ path: `${SHOTS}/${NOTES}-${mode}.png` });
      await p.goto(P); await p.waitForTimeout(300);
      await p.screenshot({ path: `${SHOTS}/${PP}-${mode}.png` });
    }
    if (errs.length) fail(mode, 'console errors', errs.slice(0, 3));
    await ctx.close();
  }
  await b.close();
  console.log(failures ? `${failures} FAILURE(S)` : 'ALL CHECKS PASSED');
  process.exit(failures ? 1 : 0);
})();
