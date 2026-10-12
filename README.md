# humor-decider

An unofficial fan project: a small model that rates a joke on seven comedy traits, inspired by an absurdist late-night style. **Not affiliated with or endorsed by Conan O'Brien. None of his material was used for training.**

It is a LoRA fine-tune of [Strands Decider 2B](https://github.com/strands-labs/strands-decider) (Qwen3.5-2B-Base), a "decision model" that cannot write text, only answer typed yes/no questions with a probability.

Weights and model card: https://huggingface.co/anandamri/humor-decider-2b

## The seven traits
Self-deprecating, absurd escalation, mock outrage, undercuts its own joke, silly tangent, overcommits to the bit, silly button. `rubric.json` holds each question with true/false criteria. The traits were drafted with an AI assistant and not checked against any comedian's actual material.

## Results (single runs; read the caveats)

Trait probes: 700 LLM-written jokes, labels by construction, written by the same LLM and templates as the training data (an in-distribution score).

| model | mean AUROC | mean Brier |
| --- | --- | --- |
| Strands Decider v21 (stock) | 0.946 | 0.156 |
| same recipe, no joke rows (control) | 0.934 | 0.183 |
| this model | 0.998 | 0.027 |

External check on one trait: `self_deprecating` on the Humour Styles dataset (Kenneth, Khosmood, Edalat 2024; 1,463 texts, mostly website-tag labels). Not redistributed here, not trained on.

| model | AUROC, all others | AUROC, other styles only |
| --- | --- | --- |
| stock | 0.778 | 0.731 |
| control | 0.728 | 0.697 |
| this model | 0.865 | 0.832 |

## Caveats
- The probe score is in-distribution. Only one trait has an external check.
- The rubric misses topical news-hook jokes, which score low on all seven.
- Calibration on real jokes is unmeasured; outputs are very decisive.
- Negated yes/no questions are not read reliably. Ask positively, with the true/false criteria.
- One seed per model; differences under ~0.05 AUROC are within run-to-run variation.

## Contents
- `rubric.json`: the seven questions.
- `scripts/gen3.py`: generates trait-labelled jokes from an OpenAI-compatible server. The training jokes themselves are not included.
- `scripts/convert.py`: turns them into Strands training rows. `cmp.py`, `zs.py`, `score.py`: probe evaluation. `ext_eval.py`: the external check (needs the dataset).
- `data/probe*.jsonl`: the 812 probe jokes (LLM-written, labels unchecked by a person).
- `demo/`: a local web demo. It expects two servers (stock on 8101, tuned on 8103) and the container layout `/work/conan`; edit paths to taste.

## License and credits
Apache-2.0. Built on Strands Decider (strands-labs) and Qwen3.5-2B-Base. Jokes were generated with Gemma 4.
