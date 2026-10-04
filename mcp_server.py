#!/usr/bin/env python3
"""Provenance MCP server — raw JSON-RPC over stdio, no SDK.

Exposes the hold lifecycle as standard agent tools. The point (and the pitch
upgrade): an AI agent drives the SAME ledger path a human uses through the UI,
and the ledger's guardrails apply to the agent exactly as they apply to the
human — a fabricated cause from an agent is rejected by the platform, not by
us.

Tools:
  provenance_roles()                  -> the three party ids on the ledger
  provenance_query(role)              -> everything that role can see
  provenance_create_hold(amount, currency, reference)
                                      -> two-party create (issuer+holder)
  provenance_release(reference, reason)
                                      -> establishes a cause; ledger enforces
                                         non-empty AND both parties
  provenance_dispute(reference, statement)
                                      -> holder contests; records no cause
  provenance_audit_trail(reference?)  -> the observer-readable trail
  provenance_fabricate_cause(reference)
                                      -> deliberately attempts a release with
                                         an invented (empty) cause and returns
                                         the ledger's rejection verbatim.
                                         Demo/eval tool: agents SHOULD fail.

Protocol: MCP 2024-11-05 (initialize, tools/list, tools/call) over stdio,
newline-delimited JSON. Written from scratch per the adopted build strategy
("MCP Server and Client, raw JSON-RPC, no SDK").
"""
import json, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui"))
# reuse the exact JSON-API client the UI server uses — same code path, no shim
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ui.server import ledger, parties, package, query_role  # noqa: E402

SERVER_INFO = {"name": "provenance-mcp", "version": "0.1.0"}
PROTOCOL = "2024-11-05"

TOOLS = [
    {"name": "provenance_roles",
     "description": "List the issuer/holder/auditor party ids on the Canton ledger.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "provenance_query",
     "description": "Everything a given role can see on the ledger. The ledger decides visibility — this server does no filtering.",
     "inputSchema": {"type": "object",
                     "properties": {"role": {"type": "string", "enum": ["Issuer", "Holder", "Auditor"]}},
                     "required": ["role"]}},
    {"name": "provenance_create_hold",
     "description": "Create a held payment (two-party: issuer and holder must both authorise). A held payment has NO cause field — there is nothing to fabricate into.",
     "inputSchema": {"type": "object",
                     "properties": {"amount": {"type": "string"}, "currency": {"type": "string"},
                                    "reference": {"type": "string"}},
                     "required": ["amount", "currency", "reference"]}},
    {"name": "provenance_release",
     "description": "Release a held payment with an ESTABLISHED cause. The ledger rejects an empty cause and requires both parties to act.",
     "inputSchema": {"type": "object",
                     "properties": {"reference": {"type": "string"}, "reason": {"type": "string"}},
                     "required": ["reference", "reason"]}},
    {"name": "provenance_dispute",
     "description": "Holder disputes a hold. Records the holder's statement; establishes NO cause.",
     "inputSchema": {"type": "object",
                     "properties": {"reference": {"type": "string"}, "statement": {"type": "string"}},
                     "required": ["reference", "statement"]}},
    {"name": "provenance_audit_trail",
     "description": "The observer-readable audit trail: every transition and every established cause.",
     "inputSchema": {"type": "object",
                     "properties": {"reference": {"type": "string"}}}},
    {"name": "provenance_fabricate_cause",
     "description": "Deliberately attempt to release with a fabricated (empty) cause and return the ledger's rejection verbatim. Agents SHOULD fail at this — the failure is the product.",
     "inputSchema": {"type": "object",
                     "properties": {"reference": {"type": "string"}},
                     "required": ["reference"]}},
]


def _find_by_reference(reference, template):
    """Locate a live contract by its rail-side reference, as the issuer sees it."""
    ids = parties(); pkg = package()
    st, res = ledger("POST", "/v1/query",
                     {"templateIds": [f"{pkg}:Provenance:{template}"]}, [ids["Issuer"]])
    for c in (res.get("result") or []):
        if c["payload"].get("reference") == reference:
            return c
    return None


def _result(obj):
    return {"content": [{"type": "text", "text": json.dumps(obj, indent=2, default=str)}]}


def call_tool(name, args):
    ids = parties(); pkg = package()
    tid_held = f"{pkg}:Provenance:HeldPayment"

    if name == "provenance_roles":
        return _result(ids)

    if name == "provenance_query":
        return _result({"role": args["role"], "contracts": query_role(args["role"])})

    if name == "provenance_create_hold":
        st, res = ledger("POST", "/v1/create", {
            "templateId": tid_held,
            "payload": {"issuer": ids["Issuer"], "holder": ids["Holder"],
                        "auditor": ids["Auditor"],
                        "amount": str(args["amount"]), "currency": args["currency"],
                        "heldAt": "2026-10-04T12:00:00Z", "reference": args["reference"]},
        }, [ids["Issuer"], ids["Holder"]])
        ok = st < 400
        return _result({"created": ok, "http": st,
                        "contractId": (res.get("result") or {}).get("contractId"),
                        "error": None if ok else (res.get("errors") or [None])[0]})

    if name in ("provenance_release", "provenance_fabricate_cause"):
        held = _find_by_reference(args["reference"], "HeldPayment")
        if not held:
            return _result({"ok": False, "error": f"no held payment with reference {args['reference']}"})
        reason = "" if name == "provenance_fabricate_cause" else args["reason"]
        st, res = ledger("POST", "/v1/exercise", {
            "templateId": tid_held, "contractId": held["contractId"],
            "choice": "Release", "argument": {"reason": reason},
        }, [ids["Issuer"], ids["Holder"]])
        ok = st < 400
        return _result({"ok": ok, "http": st,
                        "ledger_says": None if ok else (res.get("errors") or [None])[0]})

    if name == "provenance_dispute":
        held = _find_by_reference(args["reference"], "HeldPayment")
        if not held:
            return _result({"ok": False, "error": f"no held payment with reference {args['reference']}"})
        st, res = ledger("POST", "/v1/exercise", {
            "templateId": tid_held, "contractId": held["contractId"],
            "choice": "Dispute", "argument": {"statement": args["statement"]},
        }, [ids["Holder"]])
        ok = st < 400
        return _result({"ok": ok, "http": st,
                        "error": None if ok else (res.get("errors") or [None])[0]})

    if name == "provenance_audit_trail":
        st, res = ledger("POST", "/v1/query",
                         {"templateIds": [f"{pkg}:Provenance:AuditEntry"]}, [ids["Auditor"]])
        entries = [c["payload"] for c in (res.get("result") or [])]
        if args.get("reference"):
            entries = [e for e in entries if e.get("reference") == args["reference"]]
        return _result({"entries": entries, "count": len(entries)})

    return {"isError": True, "content": [{"type": "text", "text": f"unknown tool {name}"}]}


def handle(msg):
    m = msg.get("method")
    mid = msg.get("id")
    if m == "initialize":
        return {"jsonrpc": "2.0", "id": mid, "result": {
            "protocolVersion": PROTOCOL, "capabilities": {"tools": {}},
            "serverInfo": SERVER_INFO}}
    if m == "notifications/initialized":
        return None
    if m == "tools/list":
        return {"jsonrpc": "2.0", "id": mid, "result": {"tools": TOOLS}}
    if m == "tools/call":
        p = msg.get("params", {})
        try:
            r = call_tool(p.get("name"), p.get("arguments") or {})
        except Exception as e:
            r = {"isError": True, "content": [{"type": "text", "text": f"{type(e).__name__}: {e}"}]}
        return {"jsonrpc": "2.0", "id": mid, "result": r}
    if mid is not None:
        return {"jsonrpc": "2.0", "id": mid,
                "error": {"code": -32601, "message": f"method not found: {m}"}}
    return None


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = handle(msg)
        if resp is not None:
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
