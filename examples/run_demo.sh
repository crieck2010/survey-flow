#!/usr/bin/env bash
# Offline end-to-end demo: synthetic field -> frames -> manifest.
# No downloads, no survey-currents install needed.
set -euo pipefail
OUT="${1:-demo_out}"
export OUT
python -m pip install -e ".[render]" -q 2>/dev/null || true
survey-flow demo --out "$OUT" --frames 12 --particles 400 --style reel-dark
echo "---"
ls "$OUT" "$OUT/frames" | head -20
python3 - <<'EOF'
import json, os
out = os.environ.get("OUT", "demo_out")
with open(os.path.join(out, "manifest.json")) as fh:
    m = json.load(fh)
print(f"manifest: schema={m['schema']} n_frames={m['n_frames']} fps={m['fps']}")
EOF
