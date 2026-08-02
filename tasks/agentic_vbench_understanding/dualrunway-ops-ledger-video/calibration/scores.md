# Calibration — dualrunway-ops-ledger-video

Deterministic F1 scorer (`steps/solve/tests/judge.py`). A task clears the bar when
**every real agent scores below 0.10** and a real attempt takes **more than 50
tool-call turns**. Oracle must be 1.0 and an empty attempt near 0.

Single-modality sibling of `dualrunway-ops-ledger`: same recording, same masked video
byte-for-byte, no tower audio. `callsign` is replaced by `airline` because a flight
number exists nowhere in the picture — the operator has to be read off the livery.

| run | score | rollout (tool-call turns) |
|---|---|---|
| oracle | **1.0** | — |
| empty / null | **0.0** | — |
| Codex CLI (GPT 5.6 Sol) | **0.0526** (snapshot) | _pending_ |
| Claude Code CLI (Opus 5) | _pending_ | _pending_ |
| Antigravity (Gemini 3.5 Flash / 3.1 Pro) | _to run_ | _to run_ |

Status: **NOT CALIBRATED.** Oracle and null are real measurements. The Codex number is a
mid-run snapshot taken at ~40 min, not a final score, and the node became unreachable
before either agent finished. Do not treat this table as calibration evidence yet.

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

**This is still above 0.10 on paper**, and that gap is the honest risk in this variant.
The mid-run Codex snapshot came in at 0.0526 — below the projection — because the
projection assumes operation detection is as accurate as Opus 5 managed with three hours
and both channels. In practice the agent could not pin the moment: it submitted 63
operations, its first four all `B737-family` + `SWA` (exactly the majority-guess
strategy), and only 3 matched. If the final numbers hold under 0.10, the reason will be
**detection accuracy, not judgement difficulty** — a weaker foundation than the sibling
task's, and it should be described that way rather than presented as a design success.

## Ground truth

51 operations, from the same capture and the same airframe-identity join as the sibling
task (OpenSky state vectors → icao24 → registration → the camera's own tracking panel,
which is masked out of the shipped video). `airline` is the operator behind that
registration.

The sibling task's audibility filter does not apply here — no callsign is scored — so
this ledger keeps the two operations that were dropped there for never being spoken, and
excludes the general-aviation aircraft that carry no airline at all.

Distribution: SWA 23, DAL 6, AAL 6, FFT 4, AAY 4, UAL 2, ASA 2, JSX 2, SKW 1, QXE 1.
