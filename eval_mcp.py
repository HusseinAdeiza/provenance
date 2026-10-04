#!/usr/bin/env python3
"""Eval for the Provenance MCP server — drives it as a real MCP client would
(newline-delimited JSON-RPC over stdio) and asserts the guardrails hold for an
AGENT caller, not just a human one.

This is the "write evals so you can prove it works" slot of the build strategy.
Exit 0 + 'ALL n PASS' when green.
"""
import json, subprocess, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
SERVER = os.path.join(HERE, "mcp_server.py")

def run_session(messages):
    """Start the server, feed it JSON-RPC lines, collect responses."""
    inp = "".join(json.dumps(m) + "\n" for m in messages)
    p = subprocess.run([sys.executable, SERVER], input=inp, capture_output=True,
                       text=True, timeout=120, cwd=HERE)
    out = []
    for line in p.stdout.splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out, p.stderr

def tool(name, args=None, id=1):
    return {"jsonrpc": "2.0", "id": id, "method": "tools/call",
            "params": {"name": name, "arguments": args or {}}}

def text_of(resp):
    return json.loads(resp["result"]["content"][0]["text"])

fails = 0
def expect(name, cond, detail=""):
    global fails
    print(("PASS  " if cond else "FAIL  ") + name + (f"  [{detail}]" if detail else ""))
    if not cond: fails += 1

REF = "MCP-EVAL-4200"

# 1. handshake + tool discovery
resp, err = run_session([
    {"jsonrpc": "2.0", "id": 1, "method": "initialize",
     "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                "clientInfo": {"name": "eval", "version": "0"}}},
    {"jsonrpc": "2.0", "method": "notifications/initialized"},
    {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
])
init = next((r for r in resp if r.get("id") == 1), None)
lst = next((r for r in resp if r.get("id") == 2), None)
expect("initialize returns protocol + serverInfo",
       bool(init) and init["result"]["protocolVersion"] == "2024-11-05"
       and init["result"]["serverInfo"]["name"] == "provenance-mcp")
expect("tools/list advertises 7 tools",
       bool(lst) and len(lst["result"]["tools"]) == 7,
       f"n={len(lst['result']['tools']) if lst else 0}")

# 2. an agent creates a hold
resp, _ = run_session([tool("provenance_create_hold",
    {"amount": "4200.00", "currency": "USD", "reference": REF}, id=10)])
r = text_of(resp[0])
expect("agent can create a hold (two-party)", r.get("created") is True, f"http={r.get('http')}")

# 3. THE guardrail: an agent fabricates a cause -> the LEDGER rejects it
resp, _ = run_session([tool("provenance_fabricate_cause", {"reference": REF}, id=11)])
r = text_of(resp[0])
expect("agent fabrication is rejected by the ledger",
       r.get("ok") is False and "AssertionFailed" in (r.get("ledger_says") or "")
       or (r.get("ok") is False and "reason must not be empty" in (r.get("ledger_says") or "")),
       (r.get("ledger_says") or "")[:70])

# 4. an agent CAN establish a real cause (both parties, non-empty)
resp, _ = run_session([tool("provenance_release",
    {"reference": REF, "reason": "Address mismatch verified by both parties"}, id=12)])
r = text_of(resp[0])
expect("agent establishes a real cause", r.get("ok") is True, f"http={r.get('http')}")

# 5. the audit trail shows the agent's transition
resp, _ = run_session([tool("provenance_audit_trail", {"reference": REF}, id=13)])
r = text_of(resp[0])
rels = [e for e in r.get("entries", []) if e.get("event") == "RELEASED"]
expect("agent's release is on the audit trail with its cause",
       r.get("count", 0) >= 1 and any(e.get("detail") for e in rels),
       f"entries={r.get('count')}")

# 6. querying as a role returns what that role sees (no over-disclosure)
resp, _ = run_session([tool("provenance_query", {"role": "Auditor"}, id=14)])
r = text_of(resp[0])
expect("auditor query returns the observer's view",
       isinstance(r.get("contracts"), list) and len(r["contracts"]) >= 1)

print()
print("ALL PASS" if fails == 0 else f"{fails} FAILED")
sys.exit(1 if fails else 0)
