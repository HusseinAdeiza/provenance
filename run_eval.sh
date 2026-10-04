#!/usr/bin/env bash
# Provenance — one command, every proof.
# Runs: daml build -> daml test -> live demo (ledger) -> AI screen self-test -> MCP eval
# Every number quoted in README/pitch comes from THIS output, never typed by hand.
set -uo pipefail
cd "$(dirname "$0")"
export PATH="$HOME/.daml/bin:$PATH"

echo "════ 1/5  daml build ════════"
daml build 2>&1 | tail -1

echo "════ 2/5  daml test (contract invariants) ════════"
daml test 2>&1 | grep -E ": ok|failed"

echo "════ 3/5  live demo (against the running stack) ════════"
if ! curl -s --max-time 5 -o /dev/null http://127.0.0.1:7575/livez -X POST -H 'Content-Type: application/json' -d '{}'; then
  echo "  ledger not running — start it with: ./demo/run_stack.sh"
  echo "  skipping (this is the only skippable section)"
else
  python3 demo/live_demo.py
fi

echo "════ 4/5  AI screening self-test ════════"
python3 ai.py

echo "════ 5/5  MCP eval (agent guardrails) ════════"
python3 eval_mcp.py
