#!/usr/bin/env bash
# Sets up the render kit's Python env and derived assets outside git.
#   render/setup.sh            venv + fonts + textures + K04 bakes
# OUT defaults to /home/user/kinetiq-render-out (never inside the repo).
set -euo pipefail
KIT="$(cd "$(dirname "$0")" && pwd)"
OUT="${KQ_RENDER_OUT:-/home/user/kinetiq-render-out}"
PY311="${PY311:-python3.11}"
mkdir -p "$OUT"
if [ ! -x "$OUT/bpyenv/bin/python" ]; then
  "$PY311" -m venv "$OUT/bpyenv"
  "$OUT/bpyenv/bin/pip" install -q -r "$KIT/requirements.txt"
fi
"$OUT/bpyenv/bin/python" -c "import bpy; print('bpy', bpy.app.version_string)"
export KQ_RENDER_OUT="$OUT"
exec "$OUT/bpyenv/bin/python" "$KIT/prepare_assets.py" "$@"
