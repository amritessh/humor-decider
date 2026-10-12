import json, sys, urllib.request as u
port, probe = sys.argv[1], sys.argv[2]
R = json.load(open('/work/conan/rubric.json'))
qs = {k: {'type': 'noul', **v} for k, v in R['noul'].items()}
rows = [json.loads(l) for l in open(probe)]
def post(j):
    b = json.dumps({'state': j, 'questions': qs}).encode()
    return json.load(u.urlopen(u.Request(f'http://localhost:{port}/v1/systemone', b, {'content-type': 'application/json'})))['answers']
def auc(P, N):
    return sum((p > n) + 0.5 * (p == n) for p in P for n in N) / (len(P) * len(N))
post(rows[0]['joke'])
for r in rows:
    a = post(r['joke']); r['p'] = {k: a[k]['noul'] for k in qs}
print(f"{'trait':18} AUROC  Brier  mean_p+  mean_p-")
for t in qs:
    s = [r for r in rows if r['trait'] == t]
    P = [r['p'][t] for r in s if r['present']]; N = [r['p'][t] for r in s if not r['present']]
    br = sum((r['p'][t] - r['present']) ** 2 for r in s) / len(s)
    print(f"{t:18} {auc(P, N):.2f}   {br:.3f}  {sum(P)/len(P):.2f}     {sum(N)/len(N):.2f}")
