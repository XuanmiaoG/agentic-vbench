FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# No ASR model here: this variant ships no audio. numpy + PyAV are what the agent needs
# to pull frames into arrays; the grader is pure stdlib.
RUN pip install --no-cache-dir numpy av

# Same masked, metadata-stripped video as the audio+video sibling task, byte for byte.
# The camera's on-screen tracking panel names the aircraft and states its type, so it is
# painted black in the uploaded file -- otherwise two of the three scored fields would
# be free.
ARG MATERIALS_VIDEO_URL=https://huggingface.co/datasets/xuanmiao-31/dualrunway-ops-ledger/resolve/main/runway.mp4
ARG MATERIALS_VIDEO_SHA256=fc873ab0777d823f7d1c4b5356df21eebca083f66803db4861b414d360111304
RUN mkdir -p /baked \
 && curl --fail --silent --show-error --location --retry 5 --retry-delay 3 \
      "$MATERIALS_VIDEO_URL" -o /baked/runway.mp4 \
 && echo "${MATERIALS_VIDEO_SHA256}  /baked/runway.mp4" | sha256sum -c - \
 && test -s /baked/runway.mp4

WORKDIR /workspace
RUN mkdir -p /workspace/materials /workspace/output /workspace/work
