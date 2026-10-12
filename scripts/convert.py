import json, random, collections
random.seed(7)
R = json.load(open('/work/conan/rubric.json'))['noul']
NEGQ = {
 'self_deprecating': "Is the speaker avoiding making fun of themselves?",
 'absurd_escalation': "Does the joke stay plausible instead of escalating to an absurd extreme?",
 'mock_outrage': "Is the speaker free of exaggerated outrage over something small?",
 'undercuts_itself': "Is the joke delivered without the speaker commenting on or deflating it?",
 'silly_tangent': "Does the joke stay on topic without veering into a non sequitur?",
 'overcommits': "Does the joke end at its natural stopping point?",
 'silly_button': "Does the joke end on its main punchline with no separate closing line?",
}
def tf(v):
    s = str(v).strip().lower()
    return 1 if s == 'true' else 0 if s == 'false' else None
rows, kept, dropped, jokes = [], collections.Counter(), collections.Counter(), 0
for line in open('/work/conan/train_raw.jsonl'):
    try: r = json.loads(line)
    except Exception: continue
    j = (r.get('joke') or '').strip()
    if not j: continue
    jokes += 1
    for t, spec in R.items():
        want = r['intended'][t]; got = tf(r['verified'].get(t))
        if got is None or got != want or (t == 'overcommits' and r.get('n_sent') != 5):
            dropped[t] += 1; continue
        c = spec['criteria']
        rows.append({'kind': 'noul', 'state': j, 'instructions': spec['instructions'], 'options': [['false', c['false']], ['true', c['true']]], 'label': want, 'task': 'conan:' + t, 'weight': 1.0, 'instruction_variants': []})
        rows.append({'kind': 'noul', 'state': j, 'instructions': NEGQ[t], 'options': [['false', c['true']], ['true', c['false']]], 'label': 1 - want, 'task': 'conan:' + t + ':flip', 'weight': 1.0, 'instruction_variants': []})
        kept[t] += 1
out = rows * 3
random.shuffle(out)
with open('/work/strands-decider/data/conan_v1.jsonl', 'w') as f:
    for r in out: f.write(json.dumps(r) + '\n')
print('jokes', jokes, 'rows written', len(out)); print('kept', dict(kept)); print('dropped', dict(dropped))
