import json, urllib.request as u
import numpy as np, openpyxl
R = json.load(open('/work/conan/rubric.json'))['noul']['self_deprecating']
q = {'sd': {'type': 'noul', **R}}
ws = openpyxl.load_workbook('/work/Two_Model_Humour_Style/humour_styles_dataset/Humour_style.xlsx', read_only=True).active
rows = []
for r in ws.iter_rows(values_only=True):
    t = next((c for c in r if isinstance(c, str) and len(c) > 3), None)
    l = next((int(c) for c in r if isinstance(c, (int, float)) and not isinstance(c, bool) and c in (0, 1, 2, 3, 4)), None)
    if t and l is not None: rows.append((t.strip(), l))
y = np.array([l for _, l in rows])
print('rows', len(rows), 'label counts', {int(k): int((y == k).sum()) for k in range(5)})
def score(port):
    out = []
    for t, _ in rows:
        b = json.dumps({'state': t[:3000], 'questions': q}).encode()
        out.append(json.load(u.urlopen(u.Request(f'http://localhost:{port}/v1/systemone', b, {'content-type': 'application/json'})))['answers']['sd']['noul'])
    return np.array(out)
def auc(p, pos, neg):
    a, b = p[pos], p[neg]
    return ((a[:, None] > b[None, :]).mean() + 0.5 * (a[:, None] == b[None, :]).mean())
for name, port in (('stock v21', 8101), ('control', 8102), ('tuned', 8103)):
    p = score(port)
    print('== %s | self-dep vs all others AUROC %.3f | vs other humour styles only (no neutral) %.3f' % (name, auc(p, y == 1, y != 1), auc(p, y == 1, np.isin(y, [0, 2, 3]))))
    print('   mean p by label  enh %.2f  self-dep %.2f  affil %.2f  aggr %.2f  neutral %.2f' % tuple(p[y == k].mean() for k in range(5)))
