task: agentic_vbench_understanding/dualrunway-ops-ledger-video

cognitive_level: understanding
# Detecting and characterising every runway operation across 2.5 hours of night PTZ
# footage, from a camera that follows aircraft one at a time and looks away in between.

modalities_required:
  video: everything. This is the single-modality sibling of dualrunway-ops-ledger --
    same recording, same masked video, audio removed. There is no second channel.

question: >
  Reconstruct the ledger of runway operations visible in the video: for each, the
  video-timeline moment, landing vs takeoff, the aircraft family, and the operating
  airline read from the livery.
output_schema: >
  {"operations": [{"video_time": "hh:mm:ss", "operation": "landing"|"takeoff",
  "aircraft_type": <14-way closed vocab>, "airline": "ICAO3"}, ...]},
  video_time tolerance 20 s (TOL in judge.py).

ground_truth:
  source: >
    Same OpenSky state-vector capture and the same icao24 -> registration -> on-screen
    tracking panel join as the sibling task; `airline` is the operator behind that
    registration. 51 operations. The sibling's audibility filter does not apply (no
    callsign is scored), so the two rows dropped there for never being spoken are kept
    here; general-aviation aircraft with no airline are excluded.
  tier: machine-truth (identity, operation, time) + human-verified (observability).

scorer:
  metric: F1; a TP needs operation, aircraft_type, airline and video_time within 20 s.
  oracle_reward: 1.0 (measured)
  null_reward: 0.0 (measured)

difficulty:
  strong_agent_reward: NOT MEASURED -- one mid-run snapshot only (Codex 0.0526 at ~40
    min). The run never finished.
  known_risk: >
    This variant is the weaker of the two and the SPEC should say so. Removing the audio
    removes both of the sibling task's difficulty sources -- the callsign and the 105 s
    inter-file offset. What remains is low-entropy: 84% of operations are arrivals, 59%
    of airframes are B737s. Measured against a real agent's video-side detections, a
    three-field ledger scores 0.380 at TOL=45 and 0.282 even at TOL=15, and pure
    majority-guessing on both categorical fields scores 0.282. Adding `airline` (largest
    class 45%) brings the majority-guess strategy down to 0.182 at TOL=20 -- better, but
    still above the 0.10 bar on paper. Any final number under 0.10 will owe more to the
    agents' inability to pin the operation moment than to the judgement being hard.

input:
  url: >
    https://huggingface.co/datasets/xuanmiao-31/dualrunway-ops-ledger/resolve/main/runway.mp4
    Identical file to the sibling task, same SHA256.
  sha256: fc873ab0777d823f7d1c4b5356df21eebca083f66803db4861b414d360111304
  length_min: 153.9 (9235.0 s)
  resolution: 2096x1178, night, two overlay regions masked to black
