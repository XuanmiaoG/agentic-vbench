# Runway Operations Ledger (video only)

You are given one file:

- `/workspace/materials/runway.mp4` — silent video (no audio track), recorded at night
  from a camera near a real airport's dual-runway complex.

Two rectangular regions of the frame are blanked to black for the whole video. Nothing
you need is inside them; do not spend time on them.

The camera is a **moving PTZ camera operated by a person**: it pans and zooms to follow
individual aircraft, and it also wanders off to look at the city between them. It does
not sit still on the runway, and it does not catch every aircraft that uses it.

Reconstruct the ledger of the runway operations in the video — every aircraft that
either **lands** (main gear touches down) or **takes off** (lifts off during the
departure roll).

**The ledger covers the whole recording.** The video runs over two and a half hours and
the traffic is steady throughout: there are dozens of operations, spread from the first
minutes to the last. A ledger built from the opening stretch and then declared finished
is not a ledger — plan your time so that every part of the recording gets looked at.

For each operation, report:

- `video_time` — the timestamp (`hh:mm:ss` from the start of the file): for a landing,
  the touchdown; for a takeoff, the liftoff.
- `operation` — exactly one of: `landing`, `takeoff`.
- `aircraft_type` — the aircraft family, from this closed vocabulary only (pick the
  closest match; do not invent new labels):
  `A220`, `A320-family`, `A330`, `A340`, `A350`, `A380`, `B737-family`, `B747`,
  `B757`, `B767`, `B777`, `B787`, `regional-jet`, `other`.
- `airline` — the operator's ICAO 3-letter code, read from the aircraft's **livery**:
  tail markings, fuselage titles, colour scheme. Use this table:

  | livery / titles | ICAO | livery / titles | ICAO |
  |---|---|---|---|
  | Southwest | SWA | American | AAL |
  | Delta | DAL | United | UAL |
  | Alaska | ASA | JetBlue | JBU |
  | Spirit | NKS | Frontier | FFT |
  | Allegiant | AAY | Sun Country | SCX |
  | SkyWest | SKW | Horizon Air | QXE |
  | Envoy | ENY | Republic | RPA |
  | Mesa | ASH | Endeavor | EDV |
  | JSX | JSX | Breeze | MXY |
  | Air Canada | ACA | WestJet | WJA |
  | Copa | CMP | Aeromexico | AMX |
  | KLM | KLM | British Airways | BAW |
  | Lufthansa | DLH | Air France | AFR |
  | FedEx | FDX | UPS | UPS |

  An operator not in this table: give the ICAO code you believe is correct. Do not guess
  a carrier whose livery you did not actually see.

## What to submit

Write `/workspace/output/solution.json` in exactly this shape:

```json
{
  "operations": [
    {"video_time": "00:14:32", "operation": "landing", "aircraft_type": "B737-family", "airline": "SWA"},
    {"video_time": "00:19:05", "operation": "takeoff", "aircraft_type": "A320-family", "airline": "AAY"}
  ]
}
```

- One entry per runway operation, in any order.
- `video_time` tolerance: within about 20 seconds of the real moment.
- **Write this file early and keep overwriting it.** As soon as you have one complete
  operation, write it, and rewrite the file each time you complete another. There is a
  time limit; whatever is in the file when the session ends is what gets graded.
- An entry with a missing or empty field counts against you exactly like a wrong one. If
  you cannot identify an aircraft, leave that operation out entirely.

## Rules

- Stay inside this working directory. Do not read, write, or search outside it.
- No internet access is available and none is needed. Do not rely on memory or general
  knowledge of any specific airport or carrier schedule — every entry must be justified
  by something you directly observed in `runway.mp4`. Do not guess.
- Count only completed runway operations: landings (touchdown) and takeoffs (liftoff).
  Do not report go-arounds, rejected takeoffs, aircraft only taxiing or holding, or
  aircraft that merely cross a runway.
- `ffmpeg`/`ffprobe` are available for seeking and sampling the video.
- **There is no network, so `pip install` will not work.** Already installed: `numpy`
  and `av` (PyAV — decodes video frames directly into numpy arrays). `PIL`, `cv2` and
  `scipy` are not installed; do not plan around them.
