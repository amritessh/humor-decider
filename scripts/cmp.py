import json, sys, urllib.request as u
import numpy as np
R = json.load(open('/work/conan/rubric.json'))
qs = {k: {'type': 'noul', **v} for k, v in R['noul'].items()}
def load(f): return [json.loads(l) for l in open(f)]
def score(port, rows):
    out = []
    for r in rows:
        b = json.dumps({'state': r['joke'], 'questions': qs}).encode()
        a = json.load(u.urlopen(u.Request(f'http://localhost:{port}/v1/systemone', b, {'content-type': 'application/json'})))['answers']
        out.append({k: a[k]['noul'] for k in qs})
    return out
def auc(P, N): return sum((p > n) + 0.5 * (p == n) for p in P for n in N) / (len(P) * len(N))
def lg(p): p = np.clip(p, 1e-4, 1 - 1e-4); return np.log(p / (1 - p))
def platt(p, y):
    z = lg(np.array(p)); y = np.array(y, float); a, b = 1.0, 0.0
    for _ in range(50):
        s = 1 / (1 + np.exp(-(a * z + b))); w = s * (1 - s)
        g = np.array([((s - y) * z).sum(), (s - y).sum()])
        H = np.array([[(w * z * z).sum() + 1e-6, (w * z).sum()], [(w * z).sum(), w.sum() + 1e-6]])
        st = np.linalg.solve(H, g); a, b = a - st[0], b - st[1]
        if abs(st).max() < 1e-6: break
    return a, b
v1, v2 = load('/work/conan/probe.jsonl'), load('/work/conan/probe2.jsonl')
for spec in sys.argv[1:]:
    name, port = spec.split('=')
    s1, s2 = score(port, v1), score(port, v2)
    print(f'== {name}'); print(f"{'trait':18} AUROC  Brier  Brier+platt")
    tot = [0, 0, 0]
    for t in qs:
        i1 = [i for i, r in enumerate(v1) if r['trait'] == t]; i2 = [i for i, r in enumerate(v2) if r['trait'] == t]
        y1 = [v1[i]['present'] for i in i1]; y2 = np.array([v2[i]['present'] for i in i2], float)
        p1 = [s1[i][t] for i in i1]; p2 = np.array([s2[i][t] for i in i2])
        a, b = platt(p1, y1); pp = 1 / (1 + np.exp(-(a * lg(p2) + b)))
        au = auc(p2[y2 == 1], p2[y2 == 0]); br = ((p2 - y2) ** 2).mean(); bp = ((pp - y2) ** 2).mean()
        tot = [tot[0] + au, tot[1] + br, tot[2] + bp]
        print(f'{t:18} {au:.3f}  {br:.3f}  {bp:.3f}')
    n = len(qs); print(f"{'MEAN':18} {tot[0]/n:.3f}  {tot[1]/n:.3f}  {tot[2]/n:.3f}")
