# Calibration — dualrunway-ops-ledger-video

Deterministic F1 scorer (`steps/solve/tests/judge.py`). A task clears the bar when
**every real agent scores below 0.10** and a real attempt takes **more than 50
tool-call turns**. Oracle must be 1.0 and an empty attempt near 0.

Single-modality sibling of `dualrunway-ops-ledger`: same recording, same masked video
byte-for-byte, no tower audio. `callsign` is replaced by `airline` because a flight
number exists nowhere in the picture — the operator has to be read off the livery.

| run | score | notes |
|---|---|---|
| oracle | **1.0** | — |
| empty / null | **0.0** | — |
| Codex CLI (GPT 5.6 Sol) | **0.0526** | 63 submitted, 3 correct, ran the full 7375 s |
| **Claude Code CLI (Opus 5)** | **0.3308** | **82 submitted, 22 correct — 3.3x over the bar** |

Status: **FAILS THE BAR. Do not open a PR for this task.** Opus 5 reconstructs 43% of
the ledger (recall 0.431, precision 0.268) and finished in 84 minutes without using its
budget. The 6x spread between the two agents is the tell: this measures agent capability,
not a task floor. Codex scores low because it cannot pin the moment, not because the
judgement is hard.

Kept in the repository as a **negative result**, because it is the cleanest available
evidence that the audio channel in the sibling task is load-bearing rather than
decorative. Same recording, same masked frames, same aircraft; remove the radio and a
strong agent goes from 0.0 to 0.33.

## Why this variant exists, and why it is the harder one to justify

The audio+video task's difficulty is concentrated in two places: the callsign, which
only the radio carries, and the 105 s offset between two unsynchronised files. Remove
the audio and both disappear. What is left — when did an operation happen, was it a
landing or a takeoff, what family is the airframe — is low-entropy, and the traffic mix
makes it worse: 84% of operations are arrivals and 59% of the aircraft are B737s.

Measured against a real agent's video-side detections (114 operations found by Opus 5 on
the audio+video task, which is exactly the work a video-only agent does):

| fields required | TOL=45 | TOL=25 | TOL=15 |
|---|---|---|---|
| time + operation + aircraft_type | 0.380 | 0.356 | 0.282 |
| time + operation | 0.528 | 0.479 | 0.380 |
| time only | 0.552 | 0.515 | 0.405 |

A three-field video-only ledger is **not viable at the 0.10 bar** — and "detect an
operation, then answer `landing` + `B737-family` for every row" alone scores 0.282.

`airline` is the field that makes it defensible. It is genuinely recoverable from this
footage — the agents on the sibling task spontaneously reported reading "Southwest heart,
Frontier tails, Delta, United, Alaska, American, KLM titles" off night silhouettes — and
its largest class is 45%, against 59% and 84% for the other two. Adding it drops the
all-majority-guess strategy from 0.380 to:

| strategy | TOL=45 | TOL=20 | TOL=15 |
|---|---|---|---|
| detect, then guess `landing` + `B737-family` + `SWA` | 0.206 | 0.182 | 0.158 |
| operation and type judged perfectly, airline guessed `SWA` | 0.218 | 0.194 | — |

TOL is 20 s here rather than the sibling's 45 s. That task's tolerance had to absorb the
offset between two files; here there is one file and the moment is read straight off it.

**The projection was right and the variant fails.** Codex came in at 0.0526, below the
projection, because it could not pin the moment — 63 submissions, the first four all
`B737-family` + `SWA` (the majority-guess strategy verbatim), 3 matches. Opus 5 came in
at **0.3308**. Its airline distribution (SWA 43, DAL 7, FFT 6, UAL 6, AAL 5) tracks the
ground truth's shape (SWA 23, DAL 6, AAL 6, FFT 4, AAY 4), so it is genuinely reading
liveries off night silhouettes, not guessing the majority class. Its 22 correct rows have
timing errors of 1-15 s, half of them inside 5 s.

### Every tightening lever, and why none of them work

To put Opus under 0.10 with 82 submissions against 51 ground-truth rows, its 22 correct
answers have to fall to 6 — a 73% cut. Measured or derived:

| lever | effect | verdict |
|---|---|---|
| TOL 20 → 10 s | 0.331 → 0.316 | no effect; its errors are already 1-15 s |
| TOL → 5 s | 0.181 | still over, and approaching the precision of the ground truth itself |
| TOL → 3 s | 0.090 | **invalid** — the scoring window would be tighter than the ±12 s the ADS-B-derived times are actually known to |
| add `runway` | would need the agent to be ≤31% accurate on it; guessing the majority runway alone is 77% | **arithmetically impossible** |
| require aircraft variant (737-700 / -800 / MAX 8) | large enough effect | winglet geometry is unreadable in night silhouette, so the ground truth stops being recoverable |
| aircraft re-identification (link a departure to the same airframe's earlier arrival) | right difficulty profile | only **3** airframes in the observable set do both, and all three are Southwest 737s — no usable ground truth, and arguably unsolvable |
| keep only the dimmest events (filter ground truth by measured contour density) | floor at **0.18** — Opus still gets 9 of the 16 darkest | and the filter runs backwards: it deliberately keeps the events that are hardest to see, which degrades ground-truth recoverability rather than improving the task |

Stacking the last two (dimmest events plus TOL = 5 s) grazes 0.10, but that number is the
product of two filters that are each independently indefensible. It would not mean the
task got harder.

### Two further designs, both measured, both rejected

**Finer type vocabulary** (`B737-NG` / `B737-MAX` / `A320ceo-family` / `A320neo-family`
instead of family labels). The distribution improves — largest class 47% rather than 59%
— and GPT 5.6 Sol scored 0.1406 on it, still over. But its answers give the design away:
65 of its 77 rows are `B737-NG` and it reported **zero** `B737-MAX`, `B757`, `E-Jet`,
`ERJ` or `A330`, against a ground truth that contains 7, 4, 2, 2 and 1 of them. It was
not distinguishing anything; it answered the majority class 84% of the time.

That matches what the frames show. Tight full-resolution crops of a MAX 8 and a 737-700
were taken at both phases: on approach the landing-light flare sits exactly over the wing
root and washes the wing out entirely, and on rollout the PTZ pan smears the wing into a
motion blur. MAX-vs-NG rests on winglet shape (split-tip vs blended) and neo-vs-ceo on
sharklets vs wingtip fences. **None of it is readable here**, so 14% of the ground truth
would be unobservable. The variant is worse than the family-level one: it fails the bar
*and* breaks recoverability.

**Dropping the dominant class** (score only the non-737 operations, 20 rows: A320-family
11, B757 4, regional-jet 4, A330 1, all separable by size, proportion and engine
placement rather than winglets). This kills majority-guessing outright:

| agent | full ledger (51) | non-737 only (20) |
|---|---|---|
| GPT 5.6 Sol | 0.1875 | **0.0625** |
| Claude Opus 5 | 0.3308 | **0.2979** |

And that split is the whole story. Filtering only removes GPT's guessing target. Opus is
genuinely reading the picture — it still hits 7 of the 20 hardest rows — so no
ground-truth filter touches it. Its ~35-43% per-row accuracy on this footage is a
capability, not a loophole, and F1 is scale-invariant to how much ledger you remove.

The camera is what defeats it: a PTZ operator who follows each aircraft hands the agent a
well-framed, tracked shot of every one. Livery and family are then ordinary visual work
for a capable model. There is no honest knob that changes that.

## Ground truth

51 operations, from the same capture and the same airframe-identity join as the sibling
task (OpenSky state vectors → icao24 → registration → the camera's own tracking panel,
which is masked out of the shipped video). `airline` is the operator behind that
registration.

The sibling task's audibility filter does not apply here — no callsign is scored — so
this ledger keeps the two operations that were dropped there for never being spoken, and
excludes the general-aviation aircraft that carry no airline at all.

Distribution: SWA 23, DAL 6, AAL 6, FFT 4, AAY 4, UAL 2, ASA 2, JSX 2, SKW 1, QXE 1.
