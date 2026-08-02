#!/bin/bash
# Pre-agent stage: place the video. This variant ships no audio track.
set -euo pipefail

mkdir -p /workspace/materials /workspace/output /workspace/work
ln /baked/runway.mp4 /workspace/materials/runway.mp4 2>/dev/null || cp /baked/runway.mp4 /workspace/materials/runway.mp4

mkdir -p /logs/artifacts
ls -la /workspace/materials/ > /logs/artifacts/materials-listing.txt

rm -- "$0"
