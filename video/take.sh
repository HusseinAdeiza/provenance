#!/usr/bin/env bash
# take.sh — record ONE clean take: fresh stack -> x11grab -> recorder -> stop grab.
# Usage: ./video/take.sh
set -uo pipefail
cd "$(dirname "$0")/.."
export PATH="$HOME/.daml/bin:$PATH"
FF=/root/.hermes/tools/ffmpeg-9.0.1-linux-x64/bin/ffmpeg

echo "── reset stack (fresh ledger = clean demo state) ──"
for port in 6865 7575 8090; do
  PID=$(ss -ltnp 2>/dev/null | grep ":$port " | grep -oE 'pid=[0-9]+' | head -1 | cut -d= -f2)
  [ -n "$PID" ] && kill $PID 2>/dev/null
done
pkill -f "ffmpeg.*x11grab" 2>/dev/null
sleep 3

rm -f /tmp/canton-port.txt /tmp/prov_take.mp4 /tmp/prov_rec_ready /tmp/prov_rec_done
daml build 2>&1 | tail -1
nohup daml sandbox --dar .daml/dist/provenance-0.1.0.dar --port-file /tmp/canton-port.txt > /tmp/sb.log 2>&1 &
# wait for the sandbox to report ready AND the port file to be populated
for i in $(seq 1 60); do
  grep -q "sandbox is ready" /tmp/sb.log 2>/dev/null && [ -s /tmp/canton-port.txt ] && break
  sleep 1
done
if ! grep -q "sandbox is ready" /tmp/sb.log 2>/dev/null || [ ! -s /tmp/canton-port.txt ]; then
  echo "ABORT: sandbox never became ready"; tail -5 /tmp/sb.log; exit 1
fi
PORT=$(cat /tmp/canton-port.txt); sleep 4
daml script --dar .daml/dist/provenance-0.1.0.dar --script-name ListParties:run \
  --ledger-host 127.0.0.1 --ledger-port "$PORT" 2>&1 | grep -oE "held_cid=[a-f0-9]{12}" | head -1
nohup daml json-api --ledger-host 127.0.0.1 --ledger-port "$PORT" \
  --address 127.0.0.1 --http-port 7575 > /tmp/ja.log 2>&1 &
for i in $(seq 1 40); do grep -q "Started server" /tmp/ja.log 2>/dev/null && break; sleep 1; done
grep -q "Started server" /tmp/ja.log || { echo "ABORT: json-api never started"; tail -5 /tmp/ja.log; exit 1; }
nohup python3 ui/server.py > /tmp/uisrv.log 2>&1 &
for i in $(seq 1 15); do
  curl -s --max-time 3 -o /dev/null http://127.0.0.1:8090/ && break; sleep 1
done
# HEALTH GATE: parties must exist and all three role views must load, or abort.
# Recording a stack without bootstrapped parties produces a broken take.
# The first /api/state call does package discovery (~37 packages) and can take
# 20s+ — retry rather than racing the warm-up.
for attempt in 1 2 3 4 5 6; do
  HEALTH=$(curl -s --max-time 45 http://127.0.0.1:8090/api/state)
  echo "$HEALTH" | python3 -c "
import sys,json
try: d=json.load(sys.stdin)
except Exception: sys.exit(1)
if 'error' in d: print('  state error:',d['error']); sys.exit(1)
v=d.get('views',{})
if not all(v.get(r) for r in ('Issuer','Holder','Auditor')): sys.exit(1)
print('  health OK: parties + all three role views present')
" && break
  echo "  health gate retry $attempt…"; sleep 5
done
echo "$HEALTH" | python3 -c "
import sys,json
d=json.load(sys.stdin); v=d.get('views',{})
assert all(v.get(r) for r in ('Issuer','Holder','Auditor')), 'views incomplete'
" || { echo "ABORT: stack unhealthy after retries"; exit 1; }
echo "── stack ready ──"

# one honest release beforehand? NO — the take performs it on camera.
pgrep Xvfb >/dev/null || { Xvfb :77 -screen 0 1920x1080x24 -ac > /tmp/xvfb.log 2>&1 & sleep 3; }

echo "── x11grab ──"
$FF -hide_banner -loglevel error -y -f x11grab -video_size 1920x1080 -framerate 25 \
  -i :77 -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p /tmp/prov_take.mp4 &
GRAB=$!
sleep 2

echo "── recorder ──"
cd video
DISPLAY=:77 CHROME=/root/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome \
  node record_provenance.mjs
cd ..

echo "── stop grab (SIGINT to the real ffmpeg, wait for moov) ──"
kill -INT $GRAB 2>/dev/null
for i in $(seq 1 20); do
  $FF -i /tmp/prov_take.mp4 2>&1 | grep -q Duration && break
  sleep 1
done
$FF -i /tmp/prov_take.mp4 2>&1 | grep -E "Duration|Video:" | head -2
ls -la /tmp/prov_take.mp4
echo "── done ──"
