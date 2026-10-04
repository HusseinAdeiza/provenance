#!/usr/bin/env bash
# proof.sh — run every check and emit machine-readable proof.json.
# The site's build gate reads THIS file, so the published numbers are the same
# ones the evals just produced. No number is typed by hand anywhere.
set -uo pipefail
cd "$(dirname "$0")"
export PATH="$HOME/.daml/bin:$PATH"

echo "── daml test ──────────────────────────────────"
TEST_OUT=$(daml test 2>&1)
echo "$TEST_OUT" | grep -E ": ok|failed"
TESTS_OK=$(echo "$TEST_OUT" | grep -cE ": ok")
TESTS_FAIL=$(echo "$TEST_OUT" | grep -cE ": failed|FAIL")

echo "── AI screen self-test ────────────────────────"
AI_OUT=$(python3 ai.py 2>&1); echo "$AI_OUT" | tail -1
AI_PASS=$(echo "$AI_OUT" | grep -c "^PASS")
AI_FAIL=$(echo "$AI_OUT" | grep -c "^FAIL")

echo "── MCP agent eval ─────────────────────────────"
MCP_OUT=$(python3 eval_mcp.py 2>&1); echo "$MCP_OUT" | tail -1
MCP_PASS=$(echo "$MCP_OUT" | grep -c "^PASS")
MCP_FAIL=$(echo "$MCP_OUT" | grep -c "^FAIL")

echo "── live demo (needs running stack) ────────────"
if curl -s --max-time 5 -o /dev/null http://127.0.0.1:7575/livez -X POST -H 'Content-Type: application/json' -d '{}'; then
  DEMO_OUT=$(python3 demo/live_demo.py 2>&1); echo "$DEMO_OUT" | tail -1
  DEMO_PASS=$(echo "$DEMO_OUT" | grep -c "^PASS")
  DEMO_FAIL=$(echo "$DEMO_OUT" | grep -c "^FAIL")
  LIVE=true
else
  echo "  ledger not running — live checks recorded as 0/unrun"
  DEMO_PASS=0; DEMO_FAIL=0; LIVE=false
fi

cat > proof.json <<EOF
{
  "generatedAt": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "damlTests": {"ok": $TESTS_OK, "failed": $TESTS_FAIL},
  "aiScreen":  {"pass": $AI_PASS, "fail": $AI_FAIL},
  "mcpEval":   {"pass": $MCP_PASS, "fail": $MCP_FAIL},
  "liveDemo":  {"pass": $DEMO_PASS, "fail": $DEMO_FAIL, "ran": $LIVE}
}
EOF
echo "── wrote proof.json ──"
cat proof.json
# gate: nothing may have failed
[ "$TESTS_FAIL" = 0 ] && [ "$AI_FAIL" = 0 ] && [ "$MCP_FAIL" = 0 ] && [ "$DEMO_FAIL" = 0 ] || { echo "PROOF FAILED"; exit 1; }
echo "all green"
