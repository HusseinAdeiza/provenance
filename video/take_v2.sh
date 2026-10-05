#!/usr/bin/env bash
# take_v2.sh A|B — record one product-act take cleanly.
# Order matters: x11grab starts first (so nothing is missed), then the recorder
# drives Chrome on :77. SIGINT goes to the REAL ffmpeg pid (not the wrapper) so
# the moov atom is written. Aborts unless the stack is healthy first.
set -uo pipefail
TAKE="${1:?usage: take_v2.sh A|B}"
cd "$(dirname "$0")"
FF=/root/.hermes/tools/ffmpeg-9.0.1-linux-x64/bin/ffmpeg
OUT="/tmp/prov_v2_${TAKE}.mp4"

# ── health gate ─────────────────────────────────────────────────────────────
STATE=$(curl -s --max-time 20 http://127.0.0.1:8090/api/state) || { echo "ABORT: UI down"; exit 1; }
echo "$STATE" | python3 -c "
import sys,json
d=json.load(sys.stdin)
assert all(d['views'].get(r) for r in ('Issuer','Holder','Auditor')), 'a role view is empty'
assert d['strangerVisibleHolds']==0, 'stranger sees contracts'
held=[c for c in d['views']['Issuer'] if c['template']=='HeldPayment']
assert held, 'no HeldPayment to act on — re-bootstrap'
print(f'  health OK — {len(held)} held contract(s) available')
" || { echo "ABORT: stack unhealthy"; exit 1; }

pgrep -c Xvfb >/dev/null || { echo "ABORT: Xvfb not running"; exit 1; }

rm -f "$OUT" /tmp/prov_v2_ready_$TAKE /tmp/prov_v2_done_$TAKE

# ── screen capture ──────────────────────────────────────────────────────────
$FF -hide_banner -loglevel error -y -f x11grab -video_size 1920x1080 -framerate 30 \
  -i :77 -c:v libx264 -preset veryfast -crf 16 -pix_fmt yuv420p "$OUT" &
GRAB=$!
sleep 3

# ── drive the browser ───────────────────────────────────────────────────────
DISPLAY=:77 CHROME=/root/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome \
  node record_v2.mjs "$TAKE"
RC=$?

# ── stop capture cleanly ────────────────────────────────────────────────────
kill -INT $GRAB 2>/dev/null
for i in $(seq 1 30); do
  $FF -i "$OUT" 2>&1 | grep -q Duration && break
  sleep 1
done
echo "── take $TAKE (recorder rc=$RC) ──"
$FF -i "$OUT" 2>&1 | grep -E "Duration|Video:" | head -2
ls -la "$OUT"
[ $RC -eq 0 ] || exit $RC
