import json, sys, urllib.request as u
R = json.load(open('/work/conan/rubric.json'))
qs = {}
for k, v in R['noul'].items(): qs[k] = {'type': 'noul', **v}
for k, v in R['score'].items(): qs[k] = {'type': 'score', **v}
for k, v in R['choice'].items(): qs[k] = {'type': 'choice', **v}
for line in open(sys.argv[1]):
    j = line.strip()
    if not j: continue
    b = json.dumps({'state': j, 'questions': qs}).encode()
    a = json.load(u.urlopen(u.Request('http://localhost:8000/v1/systemone', b, {'content-type': 'application/json'})))['answers']
    print(j[:70])
    print('  ' + ' '.join(f"{k}={a[k]['noul']:.2f}" for k in R['noul']))
    c, h = a['conan_fit'], a['host_style']
    print(f"  fit={c['score']:.2f} (conf {c['confidence']:.2f})  style={h['choice']} (conf {h['confidence']:.2f})")
