#!/usr/bin/env python3
"""Grade a video-only runway-operations ledger. Pure Python stdlib, deterministic.

Single-modality sibling of dualrunway-ops-ledger: same recording, no tower audio, and
`callsign` replaced by `airline` because a flight number exists nowhere in the picture.
The agent must read the operator off the livery instead -- Frontier's animal tails,
Southwest's heart, Delta's widget -- on night footage where the aircraft is a silhouette
against terminal lights.

reward = F1. A true positive needs operation, aircraft_type, airline and a video_time
within TOL, all at once.
"""
import argparse
import json
import re
from pathlib import Path

# 20 s, not the 45 s its audio+video sibling uses. That task's tolerance had to absorb
# the offset between two unsynchronised files; here there is only one file and the agent
# reads the moment straight off it. Measured on a real agent's video-side detections,
# timing error on correctly-found operations was 0-15 s.
TOL = 20

VALID_OPERATIONS = {"landing", "takeoff"}
VALID_TYPES = {
    "A220", "A320-family", "A330", "A340", "A350", "A380",
    "B737-family", "B747", "B757", "B767", "B777", "B787",
    "regional-jet", "other",
}

# Same capture and the same airframe-identity join as the sibling task: OpenSky
# state-vector log -> icao24 -> registration -> the camera's own tracking panel (masked
# out of the shipped video). `airline` is the operator behind that registration.
GROUND_TRUTH = [
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


def norm(s):
    return re.sub(r"[^A-Z0-9]", "", str(s).upper())


def video_time_secs(v):
    v = str(v).strip()
    try:
        parts = [int(p) for p in v.split(":")]
        while len(parts) < 3:
            parts.insert(0, 0)
        h, m, s = parts[-3:]
        return h * 3600 + m * 60 + s
    except (ValueError, AttributeError):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solution", required=True, type=Path)
    ap.add_argument("--reward-json", required=True, type=Path)
    ap.add_argument("--reward-txt", required=True, type=Path)
    args = ap.parse_args()

    reason, preds = "ok", []
    try:
        sol = json.loads(args.solution.read_text())
        preds = sol.get("operations", [])
        if not isinstance(preds, list):
            raise ValueError("operations is not a list")
    except Exception as exc:  # noqa: BLE001
        reason, preds = f"unreadable solution.json: {exc}", []

    used = [False] * len(GROUND_TRUTH)
    tp = 0
    for pr in preds:
        if not isinstance(pr, dict):
            continue
        pt = video_time_secs(pr.get("video_time"))
        if pt is None:
            continue
        for i, g in enumerate(GROUND_TRUTH):
            if used[i]:
                continue
            gt_t = video_time_secs(g["video_time"])
            if (str(pr.get("operation", "")).strip().lower() == g["operation"]
                    and str(pr.get("aircraft_type", "")).strip() == g["aircraft_type"]
                    and norm(pr.get("airline", "")) == norm(g["airline"])
                    and gt_t is not None and abs(pt - gt_t) <= TOL):
                used[i] = True
                tp += 1
                break

    n_pred, n_gt = len(preds), len(GROUND_TRUTH)
    precision = tp / n_pred if n_pred else 0.0
    recall = tp / n_gt if n_gt else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0

    details = {"reason": reason, "n_ground_truth": n_gt, "n_predicted": n_pred,
               "true_positives": tp, "precision": round(precision, 4),
               "recall": round(recall, 4), "f1": round(f1, 4),
               "video_time_tolerance_s": TOL}
    args.reward_json.parent.mkdir(parents=True, exist_ok=True)
    args.reward_json.write_text(json.dumps({"reward": round(f1, 4), "details": details}, indent=2))
    args.reward_txt.write_text(f"{round(f1, 4)}\n")


if __name__ == "__main__":
    main()
