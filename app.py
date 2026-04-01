from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import html
from resolve import resolve

HOST='0.0.0.0'
PORT=4050

INDEX='''<!doctype html>
<html><head><meta charset="utf-8"><title>shortlink_resolver</title>
<style>
body{font-family:Arial,sans-serif;max-width:1280px;margin:40px auto;padding:0 16px}
textarea{width:100%;min-height:180px;padding:12px;box-sizing:border-box}
button{padding:10px 14px;margin-top:12px;cursor:pointer}
pre{background:#111;color:#eee;padding:12px;white-space:pre-wrap}
.muted{color:#666}
.result-item{border:1px solid #ddd;border-radius:8px;padding:12px;margin:12px 0}
.result-head{font-size:12px;color:#666;margin-bottom:8px;word-break:break-all}
.result-link{background:#111;color:#fff;padding:10px;border-radius:6px;word-break:break-all;margin:8px 0}
.actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
.copy-btn,.open-btn,.copy-all-btn{margin-top:0}
.ok{color:#0a7d22;font-weight:bold}
.err{color:#b42318;font-weight:bold}
.layout{display:grid;grid-template-columns:1.3fr 0.9fr;gap:20px;align-items:start;margin-top:24px}
.aggregate{border:1px solid #ddd;border-radius:8px;padding:12px;position:sticky;top:20px}
.aggregate textarea{min-height:420px}
@media (max-width: 900px){.layout{grid-template-columns:1fr}.aggregate{position:static}}
</style>
<script>
function copyResultText(resultId, btn) {
  const el = document.getElementById(resultId);
  if (!el) { alert('Result target not found'); return; }
  const text = (el.innerText || el.textContent || '').trim();
  doCopy(text, btn);
}
function copyAllResults(btn) {
  const el = document.getElementById('all-results');
  if (!el) { alert('All results box not found'); return; }
  const text = (el.value || '').trim();
  if (!text) { alert('No results to copy'); return; }
  doCopy(text, btn);
}
function doCopy(text, btn) {
  function copied() {
    const old = btn.textContent;
    btn.textContent = 'Copied';
    setTimeout(() => btn.textContent = old, 1200);
  }
  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(text).then(copied).catch(() => fallbackCopy(text, copied));
  } else {
    fallbackCopy(text, copied);
  }
}
function fallbackCopy(text, onok) {
  const ta = document.createElement('textarea');
  ta.value = text;
  ta.setAttribute('readonly', '');
  ta.style.position = 'absolute';
  ta.style.left = '-9999px';
  document.body.appendChild(ta);
  ta.select();
  ta.setSelectionRange(0, text.length);
  try {
    const ok = document.execCommand('copy');
    document.body.removeChild(ta);
    if (ok) onok(); else window.prompt('Copy this text:', text);
  } catch (e) {
    document.body.removeChild(ta);
    window.prompt('Copy this text:', text);
  }
}
</script>
</head><body>
<h1>shortlink_resolver</h1>
<p class="muted">Paste satu atau banyak shortlink, satu link per baris.</p>
<form method="post" action="/resolve">
<textarea name="urls" placeholder="https://savetub.com/u4O54dM&#10;https://savetub.com/xxxxx">__URLS__</textarea>
<button type="submit">Submit</button>
</form>
__CONTENT__
</body></html>'''

class H(BaseHTTPRequestHandler):
    def _send(self, body, status=200):
        data=body.encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type','text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def render(self, urls='', content=''):
        return INDEX.replace('__URLS__', urls).replace('__CONTENT__', content)

    def do_GET(self):
        self._send(self.render())

    def do_POST(self):
        if self.path != '/resolve':
            self._send('Not found',404); return
        length=int(self.headers.get('Content-Length','0'))
        body=self.rfile.read(length).decode('utf-8')
        raw=parse_qs(body).get('urls',[''])[0]
        urls=[u.strip() for u in raw.splitlines() if u.strip()]
        blocks=[]
        final_links=[]
        for idx, url in enumerate(urls, start=1):
            try:
                final=resolve(url)
                final_links.append(final)
                esc_final=html.escape(final)
                esc_url=html.escape(url)
                href=html.escape(final, quote=True)
                result_id=f'result-link-{idx}'
                blocks.append(f'''<div class="result-item">
<div class="result-head"><span class="ok">[OK]</span> {esc_url}</div>
<div class="result-link" id="{result_id}">{esc_final}</div>
<div class="actions">
<button class="copy-btn" type="button" onclick="copyResultText('{result_id}', this)">Copy link #{idx}</button>
<a href="{href}" target="_blank" rel="noopener noreferrer"><button class="open-btn" type="button">Open in new tab</button></a>
</div>
</div>''')
            except Exception as e:
                esc_err=html.escape(str(e))
                esc_url=html.escape(url)
                blocks.append(f'''<div class="result-item">
<div class="result-head"><span class="err">[ERR]</span> {esc_url}</div>
<pre>{esc_err}</pre>
</div>''')
        left=''.join(blocks) if blocks else ''
        agg_text='\n'.join(final_links)
        right=''
        if final_links:
            right=f'''<div class="aggregate">
<h3>Final Links Only</h3>
<textarea id="all-results" readonly>{html.escape(agg_text)}</textarea>
<div class="actions">
<button class="copy-all-btn" type="button" onclick="copyAllResults(this)">Copy All Results</button>
</div>
</div>'''
        content = f'<div class="layout"><div>{left}</div><div>{right}</div></div>' if (left or right) else ''
        self._send(self.render(urls=html.escape(raw), content=content))

HTTPServer((HOST,PORT),H).serve_forever()
