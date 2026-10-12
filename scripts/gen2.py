import json, sys, urllib.request as u
B = 'http://localhost:5206/v1'
M = json.load(u.urlopen(B + '/models'))['data'][0]['id']
T = {
 'self_deprecating': ("mocks the speaker's own looks, height, age, or competence", "makes someone or something other than the speaker the target, so the speaker is not mocked"),
 'absurd_escalation': ("starts from an ordinary premise and escalates into something absurd and implausible", "stays plausible and grounded, a mild observation"),
 'mock_outrage': ("has the speaker react with wildly exaggerated outrage over something trivial", "has no outrage or anger and keeps a calm tone"),
 'undercuts_itself': ("has the speaker comment on or deflate their own joke, such as admitting it is weak", "is delivered straight with no comment on the joke itself"),
 'silly_tangent': ("veers into an oddly specific, unexpected non sequitur", "stays strictly on topic with no tangent"),
 'overcommits': ("keeps going well past the natural punchline, with each sentence sillier than the last", "consists of five separate ordinary observations in the same tone, none escalating or building on the last"),
 'silly_button': ("ends with a separate short goofy tag line after the main punchline", "ends on the main punchline with no extra tag line"),
}
topics = ['parking lots','group chats','hotels','coffee shops','self-checkout machines','family reunions','weddings','traffic','online shopping','houseplants','job interviews','public transit','moving apartments','the DMV','video calls','streaming services','birthday parties','haircuts','dentist visits','camping','road trips','neighbors','tax season','smart speakers','wedding toasts','laundry','pets','dieting','retirement','cell phone plans','movie theaters','elevators','school pickup','karaoke','home repairs','newsletters','car dealerships','fitness trackers','farmers markets','customer service hotlines','long weekends','sunscreen','garage sales','podcasts','mattress stores','zoo visits','bowling','potluck dinners','delivery apps','time zones']
n = 0
for t, (pos, neg) in T.items():
    for topic in topics:
        for present, d in ((1, pos), (0, neg)):
            ns = 'exactly 5 sentences' if t == 'overcommits' else '2-3 sentences'
            suf = '' if present else ' It should still be funny and similar in tone and length, just without that quality.'
            p = f"Write ONE original late-night monologue joke about {topic}, in {ns}. The joke must be one that {d}.{suf} Do not imitate or reproduce any real comedian's actual jokes. Output only the joke text."
            body = json.dumps({'model': M, 'messages': [{'role': 'user', 'content': p}], 'temperature': 1.0, 'max_tokens': 300}).encode()
            try:
                r = json.load(u.urlopen(u.Request(B + '/chat/completions', body, {'content-type': 'application/json'}), timeout=120))
                j = r['choices'][0]['message']['content'].strip()
                if not j: continue
                print(json.dumps({'trait': t, 'present': present, 'topic': topic, 'joke': j}), flush=True)
                n += 1
            except Exception as e:
                print('skip', t, topic, present, e, file=sys.stderr, flush=True)
    print('done trait', t, n, file=sys.stderr, flush=True)
