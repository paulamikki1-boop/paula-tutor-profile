const { chromium } = require('playwright'); const fs=require('fs'); const path=require('path');
(async () => {
  const [dir,out]=process.argv.slice(2);
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await b.newPage({deviceScaleFactor:3});
  for (const f of fs.readdirSync(dir).filter(f=>f.endsWith('.svg')).sort()) {
    const svg=fs.readFileSync(path.join(dir,f),'utf8').replace(/<\?xml[^>]*>/,'');
    const vb=svg.match(/viewBox="([\d. -]+)"/)[1].split(/\s+/).map(Number);
    fs.writeFileSync('_s.html',`<html><head><style>@font-face{font-family:'DM Sans';font-weight:400;src:url(dm400.ttf)}@font-face{font-family:'DM Sans';font-weight:500 600;src:url(dm500.ttf)}@font-face{font-family:'DM Sans';font-weight:700;src:url(dm700.ttf)}body{margin:0;background:#fff}#w{width:${vb[2]*1.4}px;padding:10px;color:#0a1628}svg{width:100%;height:auto;display:block}</style></head><body><div id="w">${svg}</div></body></html>`); await p.goto('file://'+process.cwd()+'/_s.html');
    await p.evaluate(()=>document.fonts.ready);
    await (await p.$('#w')).screenshot({path:path.join(out,f.replace('.svg','.png'))});
    fs.copyFileSync(path.join(dir,f),path.join(out,f));
  }
  await b.close();
})();
