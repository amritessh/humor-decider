import json, random, re, sys, urllib.request as u
random.seed(3)
B = 'http://localhost:5206/v1'
M = json.load(u.urlopen(B + '/models'))['data'][0]['id']
POS = {
 'self_deprecating': "mocks the speaker's own looks, height, age, or competence",
 'absurd_escalation': "starts from an ordinary premise and escalates into something absurd and implausible",
 'mock_outrage': "has the speaker react with wildly exaggerated outrage over something trivial",
 'undercuts_itself': "has the speaker comment on or deflate their own joke, such as admitting it is weak",
 'silly_tangent': "veers into an oddly specific, unexpected non sequitur",
 'overcommits': "keeps going well past the natural punchline, with each sentence sillier than the last",
 'silly_button': "ends with a separate short goofy tag line after the main punchline",
}
NEG = {
 'self_deprecating': "makes someone or something other than the speaker the target, so the speaker is not mocked",
 'absurd_escalation': "stays plausible and grounded, a mild observation",
 'mock_outrage': "has no outrage or anger and keeps a calm tone",
 'undercuts_itself': "is delivered straight with no comment on the joke itself",
 'silly_tangent': "stays strictly on topic with no tangent",
 'overcommits': "stops right at its first natural punchline",
 'silly_button': "ends on the main punchline with no extra tag line",
}
NEG5 = "consists of separate ordinary observations in the same tone, none escalating or building on the last"
Q = {
 'self_deprecating': "Does the speaker make fun of themselves?",
 'absurd_escalation': "Does the joke start from a normal premise and push it to an absurd extreme?",
 'mock_outrage': "Does the speaker overreact with exaggerated outrage over something small?",
 'undercuts_itself': "Does the speaker comment on or deflate their own joke?",
 'silly_tangent': "Does the joke veer into an oddly specific non sequitur?",
 'overcommits': "Does the joke keep going past its natural stopping point, getting sillier?",
 'silly_button': "Does the joke end with a separate goofy closing line after its main punchline?",
}
topics = "libraries,umbrellas,parking tickets,yoga classes,sandwiches,snow days,group projects,lost luggage,thermostats,gas stations,fire drills,escape rooms,cruise ships,tattoo shops,lawn care,passwords,software updates,spam calls,bake sales,marathons,theme parks,babysitters,garage doors,vending machines,bookstores,ride shares,subway musicians,power outages,jury duty,middle school dances,voicemail,hot tubs,flea markets,recycling,break rooms,conference badges,fantasy football,scented candles,assembling furniture,carpools,pizza delivery,barbershops,rental cars,car washes,soup,sleep schedules,alarm clocks,reply-all emails,standing desks,wedding registries,ice cream trucks,tailgating,thrift stores,board games,sourdough starters,drive-throughs,snowblowers,lottery tickets,trivia night,coupons,library fines,home inspections,open houses,the post office,summer camp,fishing trips,ski lodges,tourist traps,museum gift shops,hospital waiting rooms,bank lines,buffets,pickup trucks,bicycles,jogging,nap time,grocery carts,garden gnomes,birdwatching,magic shows,talent shows,parades,county fairs,mini golf,aquariums,flight delays,hotel breakfast,selfies,robot vacuums,microwaves,leftovers,shoes,socks,sunglasses,backpacks,suitcases,raincoats,laundromats".split(',')
def chat(p, t):
    b = json.dumps({'model': M, 'messages': [{'role': 'user', 'content': p}], 'temperature': t, 'max_tokens': 400}).encode()
    r = json.load(u.urlopen(u.Request(B + '/chat/completions', b, {'content-type': 'application/json'}), timeout=180))
    return r['choices'][0]['message']['content'].strip()
keys = list(POS)
done = 0
for topic in topics:
    for _ in range(8):
        n = random.choice([2, 3, 5])
        elig = [k for k in keys if k != 'overcommits' or n == 5]
        inc = set(random.sample(elig, random.choice([0, 1, 1, 2, 2, 3])))
        lines = [f"- The joke {POS[k]}." for k in inc]
        for k in keys:
            if k in inc: continue
            d = NEG5 if (k == 'overcommits' and n == 5) else NEG[k]
            lines.append(f"- The joke {d}.")
        p = f"Write ONE original late-night monologue joke about {topic}, in exactly {n} sentences. Requirements:\n" + "\n".join(lines) + "\nIt should be funny. Do not imitate or reproduce any real comedian's actual jokes. Output only the joke text."
        try:
            j = chat(p, 1.0)
            if not j: continue
            vp = "Read this joke and answer each question with true or false. Reply with only a JSON object, no other text.\n\nJoke: " + j + "\n\n" + "\n".join(f'"{k}": {q}' for k, q in Q.items())
            m = re.search(r'\{.*\}', chat(vp, 0.0), re.S)
            v = json.loads(m.group(0)) if m else {}
        except Exception as e:
            print('skip', topic, e, file=sys.stderr, flush=True); continue
        print(json.dumps({'joke': j, 'n_sent': n, 'topic': topic, 'intended': {k: int(k in inc) for k in keys}, 'verified': {k: v.get(k) for k in keys}}), flush=True)
        done += 1
    print('topic', topic, 'total', done, file=sys.stderr, flush=True)
