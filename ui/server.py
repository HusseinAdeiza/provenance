#!/usr/bin/env python3
"""Provenance roles UI — three panes, one ledger, zero dependencies.

Serves a single page showing what the Issuer, the Holder and the Auditor can
each SEE and DO, queried live from the Canton JSON API with that role's own
party token. The point of the UI is disclosure: the same ledger, three
different worlds — and a fabrication attempt rejected on screen, in real time,
by the platform rather than by this server.

Run the stack first (./demo/run_stack.sh). Then:  python3 ui/server.py
"""
import json, base64, http.server, socketserver, urllib.request, urllib.error, os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ai as ai_layer

API = os.environ.get("PROVENANCE_API", "http://127.0.0.1:7575")
PORT = int(os.environ.get("PROVENANCE_UI_PORT", "8090"))
LEDGER_ID = "sandbox"
APP_ID = "provenance-ui"

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- ledger glue

def jwt(act):
    p = {"https://daml.com/ledger-api": {
        "ledgerId": LEDGER_ID, "applicationId": APP_ID, "actAs": act}}
    def b64(d): return base64.urlsafe_b64encode(json.dumps(d).encode()).rstrip(b"=").decode()
    return f"{b64({'alg':'HS256','typ':'JWT'})}.{b64(p)}.sig"

def ledger(method, path, body, act):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{API}{path}", data=data, method=method,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {jwt(act)}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try: return e.code, json.loads(e.read())
        except Exception: return e.code, {"errors": [str(e)]}

_state: dict = {"parties": None, "pkg": None}

def parties():
    if _state["parties"]: return _state["parties"]
    st, res = ledger("GET", "/v1/parties", None, ["bootstrap"])
    ids = {p["identifier"].split("::")[0]: p["identifier"] for p in res.get("result", [])}
    need = ("Issuer", "Holder", "Auditor")
    if not all(r in ids for r in need):
        raise RuntimeError("parties not allocated — run ListParties:run first")
    _state["parties"] = ids
    return ids

def package():
    if _state["pkg"]: return _state["pkg"]
    ids = parties()
    st, res = ledger("GET", "/v1/packages", None, [ids["Issuer"]])
    for pkg in res.get("result", []):
        st2, r2 = ledger("POST", "/v1/query",
                         {"templateIds": [f"{pkg}:Provenance:HeldPayment"]}, [ids["Issuer"]])
        # bootstrap hold exists from ListParties:run — non-empty result = right package
        if st2 == 200 and (r2.get("result") or []):
            _state["pkg"] = pkg
            return pkg
    raise RuntimeError("Provenance package not found on the ledger")

def query_role(role):
    """Everything this role can see — the ledger decides, not us."""
    ids = parties(); pkg = package()
    out = []
    for tmpl in ("HeldPayment", "ReleasedPayment", "ReturnedPayment", "DisputedHold", "AuditEntry"):
        st, res = ledger("POST", "/v1/query",
                         {"templateIds": [f"{pkg}:Provenance:{tmpl}"]}, [ids[role]])
        for c in (res.get("result") or []):
            out.append({"template": tmpl, "contractId": c["contractId"], "payload": c["payload"]})
    return out

def act(body, role):
    """Perform an action AS a role. Rejections come back verbatim from the ledger."""
    ids = parties()
    act_as = [ids[role]]
    # Choices that ESTABLISH A CAUSE are multi-controller (issuer AND holder):
    # the ledger requires both in actAs. Create is likewise two-party. Dispute
    # stays single-controller (holder alone) — a payee contests unilaterally —
    # and the auditor "try to act" button must stay auditor-only so it fails.
    DUAL_CHOICES = {"Release", "Return", "ResolveDispute"}
    if body.get("action") == "create" or body.get("choice") in DUAL_CHOICES:
        if role in ("Issuer", "Holder"):
            act_as = [ids["Issuer"], ids["Holder"]]
    path = "/v1/create" if body.get("action") == "create" else "/v1/exercise"
    pkg = package()
    payload: dict = {"templateId": f"{pkg}:Provenance:{body['template']}"}
    if body.get("action") == "create":
        # the server fills in the role parties; the browser only supplies
        # amount/currency/reference — no party handling in the UI
        p = dict(body["payload"])
        p["issuer"] = ids["Issuer"]; p["holder"] = ids["Holder"]; p["auditor"] = ids["Auditor"]
        payload["payload"] = p
    else:
        payload["contractId"] = body["contractId"]
        payload["choice"] = body["choice"]
        payload["argument"] = body.get("argument", {})
    st, res = ledger("POST", path, payload, act_as)
    err = None
    if st >= 400:
        errs = res.get("errors") or [json.dumps(res)[:300]]
        err = errs[0] if errs else str(res)[:300]
    return {"status": st, "ok": st < 400, "error": err,
            "contractId": (res.get("result") or {}).get("contractId") if st < 400 else None}

# ---------------------------------------------------------------- http server

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            with open(os.path.join(HERE, "index.html"), "rb") as f:
                self._send(200, f.read(), "text/html; charset=utf-8")
        elif self.path == "/api/state":
            try:
                ids = parties()
                views = {r: query_role(r) for r in ("Issuer", "Holder", "Auditor")}
                stranger = None
                st, res = ledger("POST", "/v1/query",
                                 {"templateIds": [f"{package()}:Provenance:HeldPayment"]},
                                 ["Stranger::provenance-ui"])
                stranger = len(res.get("result") or [])
                self._send(200, {"parties": {k: v[:24] + "…" for k, v in ids.items()},
                                 "views": views, "strangerVisibleHolds": stranger,
                                 "aiEnabled": ai_layer.enabled()})
            except Exception as e:
                self._send(500, {"error": str(e)})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n)) if n else {}
        if self.path == "/api/act":
            try:
                self._send(200, act(body, body["role"]))
            except Exception as e:
                self._send(500, {"error": str(e)})
        elif self.path == "/api/ask":
            # AI follow-up: answers from contract state ONLY, screened so a
            # fabricated cause is discarded. The template+payload come from the
            # client's current view of the ledger — the AI never invents facts.
            try:
                tmpl = body["template"]; payload = body["payload"]; q = body["question"]
                self._send(200, ai_layer.ask(tmpl, payload, q))
            except KeyError as e:
                self._send(400, {"error": f"missing field {e}"})
            except Exception as e:
                self._send(500, {"error": str(e)})
        else:
            self._send(404, {"error": "not found"})

class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

if __name__ == "__main__":
    with Server(("0.0.0.0", PORT), Handler) as httpd:
        print(f"Provenance roles UI on http://127.0.0.1:{PORT}  (ledger: {API})")
        httpd.serve_forever()
