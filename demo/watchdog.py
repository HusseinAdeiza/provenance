#!/usr/bin/env python3
"""watchdog.py — keeps the public demo alive through judging.

Checks every 2 minutes: tunnel process, canton sandbox, json-api, UI server,
and the public URL itself. Restarts whatever died (full stack rebuild if the
sandbox went down, since the ledger is in-memory). Appends a log line on every
action so the uptime history is auditable — no silent revivals.

Run under cron or as a background process:  python3 demo/watchdog.py --once
"""
import json, os, subprocess, sys, time, urllib.request, urllib.error

TUNNEL_URL_FILE = "/tmp/tunnel_public_url.txt"
LOG = "/root/provenance/demo/watchdog.log"
CHECK_INTERVAL = 120

def log(msg):
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    with open(LOG, "a") as f:
        f.write(line + "\n")

def port_up(port):
    r = subprocess.run(["bash", "-c", f"ss -ltn | grep -q ':{port} '"], capture_output=True)
    return r.returncode == 0

def http_ok(url, timeout=30):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "prov-watchdog"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status == 200
    except Exception:
        return False

def tunnel_url():
    try:
        return open(TUNNEL_URL_FILE).read().strip()
    except FileNotFoundError:
        return None

def tunnel_alive():
    r = subprocess.run(["bash", "-c", "pgrep -f 'cloudflared tunnel' >/dev/null"], capture_output=True)
    return r.returncode == 0

def start(cmd, logfile, env=None):
    e = dict(os.environ)
    e["PATH"] = os.path.expanduser("~/.daml/bin") + ":" + e["PATH"]
    if env: e.update(env)
    with open(logfile, "a") as f:
        p = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, env=e,
                             cwd="/root/provenance", start_new_session=True)
    log(f"started: {' '.join(cmd[:4])}… pid={p.pid}")
    return p

def wait_port(port, seconds=60):
    for _ in range(seconds):
        if port_up(port): return True
        time.sleep(1)
    return False

def wait_log(path, needle, seconds=60):
    for _ in range(seconds):
        try:
            if needle in open(path).read(): return True
        except FileNotFoundError:
            pass
        time.sleep(1)
    return False

def rebuild_stack():
    """Full restart: sandbox (fresh ledger) -> bootstrap -> json-api -> UI."""
    log("rebuilding full stack (sandbox was down)")
    for port in (8090, 7575, 6865):
        subprocess.run(["bash", "-c",
            f"PID=$(ss -ltnp 2>/dev/null | grep ':{port} ' | grep -oE 'pid=[0-9]+' | head -1 | cut -d= -f2); [ -n \"$PID\" ] && kill $PID"],
            capture_output=True)
    time.sleep(3)
    try: os.remove("/tmp/canton-port.txt")
    except FileNotFoundError: pass
    start(["daml", "sandbox", "--dar", ".daml/dist/provenance-0.1.0.dar",
           "--port-file", "/tmp/canton-port.txt"], "/tmp/sb_wd.log")
    if not wait_log("/tmp/sb_wd.log", "sandbox is ready", 90):
        log("ABORT rebuild: sandbox never came ready"); return False
    port = open("/tmp/canton-port.txt").read().strip()
    subprocess.run(["daml", "script", "--dar", ".daml/dist/provenance-0.1.0.dar",
                    "--script-name", "ListParties:run", "--ledger-host", "127.0.0.1",
                    "--ledger-port", port], capture_output=True,
                   env={**os.environ, "PATH": os.path.expanduser("~/.daml/bin")+":"+os.environ["PATH"]},
                   cwd="/root/provenance")
    start(["daml", "json-api", "--ledger-host", "127.0.0.1", "--ledger-port", port,
           "--address", "127.0.0.1", "--http-port", "7575"], "/tmp/ja_wd.log")
    if not wait_log("/tmp/ja_wd.log", "Started server", 60):
        log("ABORT rebuild: json-api never started"); return False
    start(["python3", "ui/server.py"], "/tmp/ui_wd.log")
    if not wait_port(8090, 30):
        log("ABORT rebuild: UI never bound"); return False
    log("stack rebuilt; bootstrap hold recreated")
    return True

def check_once():
    fixed = []
    # 1. local stack
    if not port_up(6865):
        if not rebuild_stack(): return fixed
        fixed.append("stack")
    else:
        if not port_up(7575):
            start(["daml", "json-api", "--ledger-host", "127.0.0.1", "--ledger-port", "6865",
                   "--address", "127.0.0.1", "--http-port", "7575"], "/tmp/ja_wd.log")
            wait_port(7575, 45); fixed.append("json-api")
        if not port_up(8090):
            start(["python3", "ui/server.py"], "/tmp/ui_wd.log")
            wait_port(8090, 30); fixed.append("ui")
    # 2. tunnel
    if not tunnel_alive():
        p = start(["cloudflared", "tunnel", "--url", "http://127.0.0.1:8090", "--no-autoupdate"],
                  "/tmp/tunnel_wd.log")
        # new quick-tunnel = new hostname; parse and persist it
        url = None
        for _ in range(30):
            time.sleep(2)
            try:
                m = [l for l in open("/tmp/tunnel_wd.log") if "trycloudflare.com" in l]
                if m:
                    import re
                    found = re.search(r"https://[a-z0-9-]+\.trycloudflare\.com", m[-1])
                    if found: url = found.group(0); break
            except FileNotFoundError:
                pass
        if url:
            open(TUNNEL_URL_FILE, "w").write(url + "\n")
            log(f"TUNNEL RESTARTED — NEW URL {url} (submission link must be updated!)")
            fixed.append("tunnel-new-url")
        else:
            log("tunnel restart failed to yield a URL")
            fixed.append("tunnel-failed")
    # 3. end-to-end public check
    url = tunnel_url()
    if url and not http_ok(url + "/api/state", 45):
        log(f"public URL {url} not answering /api/state — local stack will be checked next cycle")
        fixed.append("public-degraded")
    return fixed

if __name__ == "__main__":
    once = "--once" in sys.argv
    while True:
        fixed = check_once()
        if fixed:
            log(f"fixed: {fixed}")
        if once:
            print("watchdog single pass done:", fixed or "all healthy")
            break
        time.sleep(CHECK_INTERVAL)
