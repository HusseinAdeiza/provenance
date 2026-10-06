#!/usr/bin/env bash
# entrypoint.sh — boot the whole Provenance demo as ONE service.
#
# Order matters and is not negotiable:
#   1. canton sandbox      — in-memory ledger, uploads the .dar
#   2. ListParties:run     — allocates the three parties + creates the first
#                            held payment (two-party create). Without this the
#                            UI has nothing to show and package discovery fails.
#   3. json-api            — Canton Ledger API v1 on 7575
#   4. ui/server.py        — the roles UI on $PORT (what visitors actually hit)
#
# Every stage waits for a real readiness signal rather than a sleep, and the
# script fails loudly if any stage never comes up — a demo that half-boots and
# serves an empty page is worse than one that refuses to start.
set -uo pipefail
cd "$(dirname "$0")/.."
export PATH="$HOME/.daml/bin:/opt/daml/bin:$PATH"

PORT="${PORT:-8090}"
LEDGER_PORT="${LEDGER_PORT:-6865}"
JSON_PORT="${JSON_PORT:-7575}"
DAR=".daml/dist/provenance-${PROVENANCE_VERSION:-0.1.0}.dar"

log() { echo "[entrypoint] $*"; }
die() { echo "[entrypoint] FATAL: $*" >&2; exit 1; }

wait_for_log() { # file needle seconds
  local f="$1" needle="$2" max="${3:-90}" i=0
  while [ $i -lt "$max" ]; do
    grep -q "$needle" "$f" 2>/dev/null && return 0
    sleep 1; i=$((i+1))
  done
  return 1
}
wait_for_port() { # port seconds
  local p="$1" max="${2:-60}" i=0
  while [ $i -lt "$max" ]; do
    (echo >"/dev/tcp/127.0.0.1/$p") 2>/dev/null && return 0
    sleep 1; i=$((i+1))
  done
  return 1
}

[ -f "$DAR" ] || die "missing $DAR — the Daml package must be built into the image"

# 1 ── sandbox
log "starting canton sandbox (ledger on $LEDGER_PORT)"
rm -f /tmp/canton-port.txt
daml sandbox --dar "$DAR" --port-file /tmp/canton-port.txt >/tmp/sandbox.log 2>&1 &
wait_for_log /tmp/sandbox.log "sandbox is ready" 120 \
  || die "sandbox never became ready: $(tail -3 /tmp/sandbox.log)"

# 2 ── bootstrap parties + first hold
log "bootstrapping parties and the opening held payment"
daml script --dar "$DAR" --script-name ListParties:run \
  --ledger-host 127.0.0.1 --ledger-port "$LEDGER_PORT" >/tmp/bootstrap.log 2>&1 \
  || die "bootstrap failed: $(tail -3 /tmp/bootstrap.log)"
grep -q "held_cid=" /tmp/bootstrap.log \
  || die "bootstrap produced no held contract — judges would see an empty page"
log "bootstrap ok: $(grep -oE 'held_cid=[a-f0-9]{10}' /tmp/bootstrap.log | head -1)"

# 3 ── json api
log "starting json-api (Canton Ledger API on $JSON_PORT)"
daml json-api --ledger-host 127.0.0.1 --ledger-port "$LEDGER_PORT" \
  --address 0.0.0.0 --http-port "$JSON_PORT" >/tmp/jsonapi.log 2>&1 &
wait_for_log /tmp/jsonapi.log "Started server" 90 \
  || die "json-api never started: $(tail -3 /tmp/jsonapi.log)"

# 4 ── roles UI (the public surface)
log "starting roles UI on $PORT"
PROVENANCE_UI_PORT="$PORT" PROVENANCE_API="http://127.0.0.1:$JSON_PORT" \
  python3 ui/server.py >/tmp/ui.log 2>&1 &
wait_for_port "$PORT" 45 || die "UI never bound port $PORT: $(tail -3 /tmp/ui.log)"

# 5 ── prove it actually serves before declaring success
log "verifying the demo answers before declaring ready"
for i in $(seq 1 30); do
  if curl -fsS --max-time 5 "http://127.0.0.1:$PORT/api/state" \
       | grep -q '"strangerVisibleHolds": *0'; then
    log "READY — public demo on port $PORT"
    break
  fi
  [ "$i" = 30 ] && die "UI is up but /api/state never returned a clean ledger state"
  sleep 2
done

log "stack up. ledger=$LEDGER_PORT json=$JSON_PORT ui=$PORT"
# Park so the container stays alive; the UI is the served surface.
while true; do sleep 3600; done
