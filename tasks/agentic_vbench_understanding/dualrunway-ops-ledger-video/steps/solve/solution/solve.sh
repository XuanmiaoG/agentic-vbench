#!/bin/bash
# Oracle for the video-only ledger. Verified answer key, never shipped into the agent's
# image. Must stay identical in content to GROUND_TRUTH in tests/judge.py.
set -euo pipefail
mkdir -p /workspace/output
python3 - <<'PY'
import json
from pathlib import Path

OPERATIONS = [
    {"video_time": "00:03:51", "operation": "landing", "aircraft_type": "regional-jet", "airline": "SKW"},
    {"video_time": "00:08:51", "operation": "landing", "aircraft_type": "A320-family", "airline": "FFT"},
    {"video_time": "00:10:35", "operation": "landing", "aircraft_type": "B737-family", "airline": "SWA"},
    {"video_time": "00:12:07", "operation": "landing", "aircraft_type": "B757", "airline": "DAL"},
    {"video_time": "00:13:29", "operation": "landing", "aircraft_type": "B737-family", "airline": "UAL"},
    {"video_time": "00:17:17", "operation": "landing", "aircraft_type": "A320-family", "airline": "FFT"},
    {"video_time": "00:20:11", "operation": "landing", "aircraft_type": "B737-family", "airline": "ASA"},
    {"video_time": "00:30:13", "operation": "landing", "aircraft_type": "regional-jet", "airline": "QXE"},
    {"video_time": "00:35:33", "operation": "landing", "aircraft_type": "A320-family", "airline": "AAL"},
    {"video_time": "00:38:25", "operation": "landing", "aircraft_type": "regional-jet", "airline": "JSX"},
    {"video_time": "00:40:44", "operation": "takeoff", "aircraft_type": "regional-jet", "airline": "JSX"},
    {"video_time": "00:41:09", "operation": "landing", "aircraft_type": "B737-family", "airline": "SWA"},
    {"video_time": "00:46:03", "operation": "landing", "aircraft_type": "B737-family", "airline": "SWA"},
    {"video_time": "00:55:35", "operation": "landing", "aircraft_type": "B737-family", "airline": "SWA"},
    {"video_time": "00:57:11", "operation": "landing", "aircraft_type": "B737-family", "airline": "SWA"},
    {"video_time": "01:00:27", "operation": "landing", "aircraft_type": "B737-family", "airline": "SWA"},
    {"video_time": "01:05:34", "operation": "landing", "aircraft_type": "B737-family", "airline": "SWA"},
    {"video_time": "01:13:15", "operation": "landing", "aircraft_type": "A320-family", "airline": "AAY"},
    {"video_time": "01:25:11", "operation": "landing", "aircraft_type": "B737-family", "airline": "AAL"},
    {"video_time": "01:26:05", "operation": "landing", "aircraft_type": "A320-family", "airline": "AAY"},
    {"video_time": "01:26:26", "operation": "landing", "aircraft_type": "B737-family", "airline": "SWA"},
    {"video_time": "01:28:15", "operation": "landing", "aircraft_type": "B757", "airline": "DAL"},
    {"video_time": "01:29:51", "operation": "landing", "aircraft_type": "A330", "airline": "ASA"},
    {"video_time": "01:31:42", "operation": "landing", "aircraft_type": "B737-family", "airline": "SWA"},
    {"video_time": "01:36:03", "operation": "landing", "aircraft_type": "B737-family", "airline": "SWA"},
    {"video_time": "01:37:35", "operation": "landing", "aircraft_type": "B737-family", "airline": "SWA"},
    {"video_time": "01:39:58", "operation": "takeoff", "aircraft_type": "A320-family", "airline": "AAL"},
    {"video_time": "01:42:21", "operation": "landing", "aircraft_type": "B737-family", "airline": "DAL"},
    {"video_time": "01:43:53", "operation": "landing", "aircraft_type": "B737-family", "airline": "SWA"},
    {"video_time": "01:45:20", "operation": "landing", "aircraft_type": "A320-family", "airline": "AAY"},
    {"video_time": "01:46:31", "operation": "landing", "aircraft_type": "B737-family", "airline": "SWA"},
    {"video_time": "01:46:58", "operation": "takeoff", "aircraft_type": "B737-family", "airline": "SWA"},
    {"video_time": "01:48:03", "operation": "landing", "aircraft_type": "A320-family", "airline": "AAL"},
    {"video_time": "01:49:39", "operation": "landing", "aircraft_type": "B737-family", "airline": "SWA"},
    {"video_time": "01:50:51", "operation": "landing", "aircraft_type": "A320-family", "airline": "FFT"},
    {"video_time": "01:54:20", "operation": "takeoff", "aircraft_type": "B737-family", "airline": "SWA"},
    {"video_time": "01:58:03", "operation": "landing", "aircraft_type": "A320-family", "airline": "AAY"},
    {"video_time": "02:02:50", "operation": "takeoff", "aircraft_type": "B737-family", "airline": "SWA"},
    {"video_time": "02:07:01", "operation": "landing", "aircraft_type": "B757", "airline": "DAL"},
    {"video_time": "02:08:49", "operation": "takeoff", "aircraft_type": "B737-family", "airline": "AAL"},
    {"video_time": "02:10:59", "operation": "landing", "aircraft_type": "B737-family", "airline": "AAL"},
    {"video_time": "02:11:31", "operation": "takeoff", "aircraft_type": "B737-family", "airline": "SWA"},
    {"video_time": "02:13:29", "operation": "landing", "aircraft_type": "B737-family", "airline": "SWA"},
    {"video_time": "02:18:28", "operation": "landing", "aircraft_type": "A320-family", "airline": "FFT"},
    {"video_time": "02:19:51", "operation": "landing", "aircraft_type": "B737-family", "airline": "UAL"},
    {"video_time": "02:21:42", "operation": "landing", "aircraft_type": "B737-family", "airline": "SWA"},
    {"video_time": "02:23:42", "operation": "landing", "aircraft_type": "B737-family", "airline": "SWA"},
    {"video_time": "02:26:19", "operation": "landing", "aircraft_type": "B737-family", "airline": "DAL"},
    {"video_time": "02:27:07", "operation": "takeoff", "aircraft_type": "B757", "airline": "DAL"},
    {"video_time": "02:28:35", "operation": "landing", "aircraft_type": "B737-family", "airline": "SWA"},
    {"video_time": "02:33:25", "operation": "landing", "aircraft_type": "B737-family", "airline": "SWA"},]

Path("/workspace/output/solution.json").write_text(
    json.dumps({"operations": OPERATIONS}, indent=2))
PY
echo "oracle: wrote /workspace/output/solution.json"
