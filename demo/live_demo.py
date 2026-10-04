#!/usr/bin/env python3
"""Provenance live demo — the five judge-facing moments, over the JSON API.

Prereqs (both running):
  daml sandbox --dar .daml/dist/provenance-0.1.0.dar --port-file /tmp/canton-port.txt
  daml json-api --ledger-host 127.0.0.1 --ledger-port 6865 --address 127.0.0.1 --http-port 7575
  daml script --dar ... --script-name ListParties:run --ledger-host 127.0.0.1 --ledger-port 6865

Prints PASS/FAIL per demo and exits non-zero on any failure.
"""
import json, base64, sys, urllib.request, urllib.error

API = "http://127.0.0.1:7575"
LEDGER_ID = "sandbox"
APP_ID = "provenance-ui"

def jwt(act):
    p = {"https://daml.com/ledger-api": {"ledgerId": LEDGER_ID, "applicationId": APP_ID, "actAs": act}}
    def b64(d): return base64.urlsafe_b64encode(json.dumps(d).encode()).rstrip(b"=").decode()
    return f"{b64({'alg':'HS256','typ':'JWT'})}.{b64(p)}.sig"

def call(method, path, body, act):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{API}{path}", data=data, method=method,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {jwt(act)}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try: return e.code, json.loads(e.read())
        except Exception: return e.code, {}

def parties():
    st, res = call("GET", "/v1/parties", None, ["x"])
    ids = {p["identifier"].split("::")[0]: p["identifier"] for p in res.get("result", [])}
    for role in ("Issuer", "Holder", "Auditor"):
        if role not in ids:
            sys.exit(f"party {role} not allocated — run ListParties:run against the ledger first")
    return ids

def create_hold(ids):
    """Two-party create over the JSON API: actAs carries BOTH signatories in one
    request. This is the flow the Oct-3 probe could not express in a script
    harness ("missing authorization from 'Holder'"); over /v1/create it works,
    and the ledger — not application code — enforces both signatures."""
    st, res = call("POST", "/v1/create", {
        "templateId": tid,
        "payload": {
            "issuer": ids["Issuer"], "holder": ids["Holder"], "auditor": ids["Auditor"],
            "amount": "4200.0", "currency": "USD",
            "heldAt": "2026-10-04T12:00:00Z", "reference": "PAY-4200",
        }}, [ids["Issuer"], ids["Holder"]])
    if st not in (200, 201):
        sys.exit(f"two-party create failed: HTTP {st} {str(res)[:200]}")
    return st, res

def find_package(ids):
    """Find the package id that actually carries our templates. A 200 with an
    empty result means 'no such contract visible', NOT 'right package' — the
    first version of this accepted the first 200 and picked a stdlib package,
    so create then failed with 'Cannot resolve template ID'."""
    st, res = call("GET", "/v1/packages", None, [ids["Issuer"]])
    for pkg in res.get("result", []):
        st2, r2 = call("POST", "/v1/query", {"templateIds": [f"{pkg}:Provenance:HeldPayment"]}, [ids["Issuer"]])
        if st2 == 200 and (r2.get("result") or []):
            return pkg
    sys.exit("no HeldPayment visible on the ledger — bootstrap script not run?")

results = []
def check(name, ok, detail=""):
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}")

def main():
    ids = parties()
    pkg = find_package(ids)
    tid = f"{pkg}:Provenance:HeldPayment"

    # 0. two-party create over the JSON API — the flow the probe could not express
    st, r = call("POST", "/v1/create", {
        "templateId": tid,
        "payload": {
            "issuer": ids["Issuer"], "holder": ids["Holder"], "auditor": ids["Auditor"],
            "amount": "4200.0", "currency": "USD",
            "heldAt": "2026-10-04T12:00:00Z", "reference": "PAY-4200",
        }}, [ids["Issuer"], ids["Holder"]])
    cid = (r.get("result") or {}).get("contractId")
    check("two-party create (actAs both signatories)", st in (200, 201) and cid,
          f"HTTP {st}, cid={str(cid)[:16]}…")
    if not cid:
        sys.exit(1)
    pay = (r.get("result") or {}).get("payload", {})
    check("hold carries amount+currency from create", pay.get("amount") == "4200.0",
          f"{pay.get('reference')} {pay.get('amount')} {pay.get('currency')}")

    # 0b. one-party create must FAIL — the ledger demands both signatures
    st1, _ = call("POST", "/v1/create", {
        "templateId": tid,
        "payload": {
            "issuer": ids["Issuer"], "holder": ids["Holder"], "auditor": ids["Auditor"],
            "amount": "10.0", "currency": "USD",
            "heldAt": "2026-10-04T12:00:00Z", "reference": "PAY-SOLO",
        }}, [ids["Issuer"]])
    check("create with only issuer signature rejected", st1 >= 400, f"HTTP {st1}")

    # 1. THE demo: fabricating a cause is rejected by the ledger
    st, r = call("POST", "/v1/exercise",
                 {"templateId": tid, "contractId": cid, "choice": "Release",
                  "argument": {"reason": ""}}, [ids["Issuer"]])
    check("release with empty (fabricated) reason rejected", st == 400, f"HTTP {st}")

    # 2. honest release succeeds
    st, r = call("POST", "/v1/exercise",
                 {"templateId": tid, "contractId": cid, "choice": "Release",
                  "argument": {"reason": "Address mismatch confirmed by both parties"}},
                 [ids["Issuer"]])
    check("release with established reason succeeds", st == 200, f"HTTP {st}")

    # 3. privacy: non-party sees nothing
    st, r = call("POST", "/v1/query",
                 {"templateIds": [tid]}, ["Stranger"])
    check("stranger sees zero contracts", st == 200 and len(r.get("result") or []) == 0,
          f"HTTP {st}, n={len(r.get('result') or [])}")

    # 4. auditor observes the trail without being a signatory
    st, r = call("POST", "/v1/query",
                 {"templateIds": [f"{pkg}:Provenance:ReleasedPayment"]}, [ids["Auditor"]])
    n = len(r.get("result") or [])
    reason = (r.get("result") or [{}])[0].get("payload", {}).get("reason", "-")
    check("auditor sees released contract + cause", st == 200 and n >= 1,
          f"n={n}, reason='{reason[:40]}'")

    # 5. auditor cannot act
    st, r = call("POST", "/v1/exercise",
                 {"templateId": tid, "contractId": cid,
                  "choice": "Return", "argument": {"reason": "x"}}, [ids["Auditor"]])
    check("auditor cannot exercise (non-controller)", st >= 400, f"HTTP {st}")

    print()
    if all(results):
        print(f"ALL {len(results)} CHECKS PASSED")
    else:
        print(f"{results.count(False)} of {len(results)} FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
