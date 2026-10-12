import json, time, urllib.request as u
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
R = json.load(open('/work/conan/rubric.json'))
QS = {k: {'type': 'noul', **v} for k, v in R['noul'].items()}
LABEL = {'self_deprecating': 'Self-deprecating', 'absurd_escalation': 'Absurd escalation', 'mock_outrage': 'Mock outrage',
         'undercuts_itself': 'Undercuts its own joke', 'silly_tangent': 'Silly tangent', 'overcommits': 'Overcommits to the bit', 'silly_button': 'Silly button'}
EXTRA = {
 'topical_hook': {'instructions': 'Does the joke start from a news story or current event?', 'criteria': {'true': 'the setup refers to a news item, announcement, report or current event', 'false': 'the setup is not based on news or a current event'}},
 'reframe_punchline': {'instructions': 'Does the punchline reframe the setup with a cynical or insulting twist?', 'criteria': {'true': 'the punchline recasts the premise as something worse, dumber or more cynical than it first appeared', 'false': 'the punchline does not recast the premise'}},
}
QS.update({k: {'type': 'noul', **v} for k, v in EXTRA.items() if k != 'reframe_punchline'})
LABEL.update({'topical_hook': 'Topical news hook (zero-shot)', 'reframe_punchline': 'Cynical reframe (untrained)'})
def call(port, joke):
    b = json.dumps({'state': joke, 'questions': QS}).encode()
    a = json.load(u.urlopen(u.Request(f'http://localhost:{port}/v1/systemone', b, {'content-type': 'application/json'}), timeout=60))['answers']
    return {k: a[k]['noul'] for k in QS}
PAGE = r"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Conan-o-meter</title>
<style>
:root{--bg:#fafafa;--fg:#1a1a1a;--mut:#777;--card:#fff;--bd:#e3e3e3;--acc:#e8590c;--stock:#9aa0a6}
@media(prefers-color-scheme:dark){:root{--bg:#141414;--fg:#eee;--mut:#999;--card:#1e1e1e;--bd:#333;--stock:#6b7076}}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.4 system-ui,sans-serif}
main{max-width:760px;margin:0 auto;padding:20px}
textarea{width:100%;box-sizing:border-box;min-height:90px;padding:10px;border:1px solid var(--bd);border-radius:8px;background:var(--card);color:var(--fg);font:inherit}
button{padding:8px 14px;border:1px solid var(--bd);border-radius:8px;background:var(--card);color:var(--fg);cursor:pointer;font:inherit}
button.go{background:var(--acc);color:#fff;border-color:var(--acc)}
.row{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0;align-items:center}
.card{background:var(--card);border:1px solid var(--bd);border-radius:10px;padding:14px;margin-top:14px}
.meter{font-size:44px;font-weight:700;color:var(--acc)}
.t{margin:12px 0}.lab{display:flex;justify-content:space-between;font-size:14px}
.bar{height:9px;background:var(--bd);border-radius:5px;margin-top:3px;overflow:hidden}.bar>i{display:block;height:100%}
.tuned{background:var(--acc)}.stock{background:var(--stock)}.mut,small{color:var(--mut)}
</style></head><body><main>
<h1>Conan-o-meter</h1>
<div class="mut">Paste a joke. Two models score seven comedy traits: a stock decision model, and one fine-tuned on a Conan-style rubric.</div>
<div class="row"><textarea id="j" placeholder="Type or paste a joke..."></textarea></div>
<div class="row"><button class="go" id="go">Score it</button><span id="ex"></span></div>
<div id="out"></div>
<p><small>Unofficial fan project. Not affiliated with or endorsed by Conan O'Brien. Scores are model outputs and are often confidently wrong; that is part of the fun.</small></p>
<script>
const EX=["I'm so pale my shadow files for a restraining order.","Airline pilots announce the weather like it's a personal surprise.","My cooking is so bad the smoke alarm sings along.","Why don't scientists trust atoms? They make up everything."];
const $=id=>document.getElementById(id);
function bar(cls,p){const b=document.createElement('div');b.className='bar';const i=document.createElement('i');i.className=cls;i.style.width=Math.round(p*100)+'%';b.appendChild(i);return b;}
async function go(){
 const joke=$('j').value.trim(); if(!joke) return;
 $('out').textContent='Scoring...';
 let d;
 try{const r=await fetch('/api/score',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({joke})});d=await r.json();if(d.error)throw new Error(d.error);}
 catch(e){$('out').textContent='Error: '+e.message;return;}
 const out=$('out');out.textContent='';
 const T7=d.traits.slice(0,7),n=7,avg=T7.reduce((s,t)=>s+t.tuned,0)/n,avgS=T7.reduce((s,t)=>s+t.stock,0)/n;
 const card=document.createElement('div');card.className='card';
 const a=document.createElement('div');a.className='mut';a.textContent='Conan-o-meter (average of the 7 tuned-model traits)';
 const m=document.createElement('div');m.className='meter';m.textContent=Math.round(avg*100)+'%';
 const s=document.createElement('div');s.className='mut';s.textContent='stock model average: '+Math.round(avgS*100)+'%  |  scored in '+d.ms+' ms';
 card.append(a,m,s);
 d.traits.forEach(t=>{
  const w=document.createElement('div');w.className='t';
  const l=document.createElement('div');l.className='lab';
  const nm=document.createElement('span');nm.textContent=t.label;
  const v=document.createElement('span');v.className='mut';v.textContent='stock '+Math.round(t.stock*100)+'%  |  tuned '+Math.round(t.tuned*100)+'%';
  l.append(nm,v);w.append(l,bar('stock',t.stock),bar('tuned',t.tuned));card.appendChild(w);
 });
 const f=document.createElement('button');f.textContent='The model got this wrong';
 f.onclick=async()=>{const note=prompt('What did it get wrong? (optional)')||'';await fetch('/api/flag',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({joke,traits:d.traits,note})});f.textContent='Saved to the failure gallery';f.disabled=true;};
 card.appendChild(f);out.appendChild(card);
}
$('go').onclick=go;
EX.forEach((e,i)=>{const b=document.createElement('button');b.textContent='Example '+(i+1);b.onclick=()=>{$('j').value=e;go();};$('ex').appendChild(b);});
</script></main></body></html>"""
class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _send(self, code, body, ctype='application/json'):
        b = body.encode() if isinstance(body, str) else body
        self.send_response(code); self.send_header('content-type', ctype + '; charset=utf-8'); self.send_header('content-length', str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        if self.path in ('/', '/index.html'): self._send(200, PAGE, 'text/html')
        else: self._send(404, '{"error":"not found"}')
    def do_POST(self):
        try:
            d = json.loads(self.rfile.read(int(self.headers.get('content-length', 0))) or b'{}')
            joke = (d.get('joke') or '').strip()[:2000]
            if not joke: return self._send(400, '{"error":"empty joke"}')
            if self.path == '/api/score':
                t0 = time.time(); tuned = call(8103, joke); stock = call(8101, joke)
                tr = [{'key': k, 'label': LABEL[k], 'stock': stock[k], 'tuned': tuned[k]} for k in QS]
                self._send(200, json.dumps({'traits': tr, 'ms': int((time.time() - t0) * 1000)}))
            elif self.path == '/api/flag':
                with open('/work/conan/fails.jsonl', 'a') as f: f.write(json.dumps({'joke': joke, 'traits': d.get('traits'), 'note': d.get('note', ''), 't': time.time()}) + '\n')
                self._send(200, '{"ok":true}')
            else: self._send(404, '{"error":"not found"}')
        except Exception as e:
            self._send(500, json.dumps({'error': str(e)}))
ThreadingHTTPServer(('0.0.0.0', 8000), H).serve_forever()
