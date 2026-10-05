# Provenance

**When a payment is frozen, Provenance makes it impossible to invent a reason
for the freeze — and lets an auditor check what happened without seeing private
details.**

Product site: https://husseinadeiza.github.io/provenance-site/
Built for HackCanton (Track 1: RWA & Business Workflows). Delivery window Oct 4–9, 2026.

---

## What this is, in plain words

Someone's money gets held by a payment system. The system says *"frozen"* but
not *"why."* So people guess — and a wrong guess means chasing the wrong fix
while the money stays stuck. Some tools try to be helpful and **make up** a
reason. A made-up reason is worse than no reason, because people act on it.

Provenance runs the same "held payment" on **Canton**, a ledger for finance. On
Canton, the rule "don't invent a cause" isn't a promise our code makes — it's
something the **ledger itself enforces**. Try to release a held payment with a
fake or empty reason, and the ledger refuses the transaction. It's not our
server saying no; it's the platform.

Three roles:
- **Issuer** — the side that pays out.
- **Holder** — the person whose money is held.
- **Auditor** — watches everything to check it was handled right, but can't
  change anything and never sees what they shouldn't.

---

## What the demo proves — and what it does not

This matters, so it's up front rather than buried.

**What it really does:** it runs a genuine Canton ledger (the local sandbox from
the official Daml SDK) and real Daml contracts. Every rejection you see is a
real response from that ledger — not a mocked message, not a hard-coded "error."
You can run it yourself (`./demo/run_stack.sh`) and press the red button.

**What it is not (yet):** the three-pane screen runs on **one machine**, where a
single small server talks to the ledger three times — once wearing each role's
identity — to show what that role is allowed to see. It is a clear demonstration
of the *rules*, but it is **not** three separate people on three separate wallets
and devices. A production version would have each party sign from their own
Canton wallet. The **rule being demonstrated is identical either way** — the
ledger requires both parties' authorisation no matter who submits — and that
rule is what we test. We say this plainly so nobody mistakes a rules demo for a
deployed multi-user app.

Also: this runs on a **local sandbox, not a public network.** Canton's DevNet
needs a sponsoring validator, a VPN and a 2–4 week approval, which does not fit
this deadline. The hackathon rules explicitly accept a local deployment for
judging. Moving the same contract to DevNet later is a configuration change, not
a rebuild.

---

## The core rule, and why Canton is the only place it holds

On a normal website or a public blockchain, "we won't invent a cause" is just
something the app *says* — and an app can be changed, bypassed, or lied with.

On Canton it's baked into the contract:

- A **held payment has no "reason" field at all.** There's nowhere to put a fake
  reason. You can't fill in a box that doesn't exist.
- A reason can only be added when the payment is **released** or **returned**,
  and then it **must be real** — an empty reason makes the ledger reject the
  transaction.
- **Both the issuer and the holder must act together** to release. One of them
  alone — even with a perfectly good reason — is rejected. (We found this the
  hard way; see the honest note in BUILD_LOG D4.)
- The **auditor** can read the whole history but can't change it, and a total
  stranger sees **nothing.** So you can prove a hold was handled correctly
  without exposing private payment details — something a public blockchain
  can't do (everything there is world-readable) and a normal API can't enforce
  (it trusts whatever the server decides to show).
- Every step that establishes a reason also writes an **audit entry**. A
  *dispute* writes an entry with **no reason** — because a dispute proves
  nothing was established, and the record says exactly that.

---

## Run it yourself

```bash
./demo/run_stack.sh
```

Needs: the Daml SDK (`curl -sSL https://get.daml.com | sh`) and Python 3.
No accounts, no tokens, no cost — it all runs on your machine.

One command runs every check:

```bash
./proof.sh      # contract tests + live checks + AI screen + agent evals
```

---

## What the checks show

| # | What we try | What the ledger does |
|---|---|---|
| 1 | Create a hold with both parties | **accepted** |
| 2 | Create a hold with only the issuer | **rejected** — the holder must agree too |
| 3 | Release with an empty (fake) reason | **rejected** — this is the whole point |
| 4 | Release with a good reason, but issuer alone | **rejected** — a reason needs both parties |
| 5 | Release with a real reason, both parties | **accepted** — reason is now on the record |
| 6 | A stranger looks at the ledger | **sees nothing** |
| 7 | The auditor looks | **sees the release and its reason** |
| 8 | The auditor tries to change something | **rejected** — auditors only watch |
| 9 | The auditor reads the audit trail | **sees every step and reason** |
| 10 | A stranger reads the audit trail | **sees nothing** |
| 11 | The released payment carries its reason | **verified** |

Latest run on a local Canton sandbox (Daml SDK 2.10.6): **all 11 checks pass.**
Contract tests: **5/5 green**, including one that specifically proves the issuer
can't release alone.

---

## The AI helper (and why it can't lie either)

There's an optional AI layer that answers questions about a held payment — but
it is **not trusted to behave.** It only ever sees the facts the ledger holds,
and every answer it writes is checked before anyone sees it. If the AI says a
reason that the ledger never established, the answer is **thrown away** and
replaced with the plain, factual text. The screen even shows "this was filtered."

It also works with **no AI at all** — if there's no model key, every card still
renders from the ledger facts alone. An app that dies without an API key is a
toy; this isn't one.

`python3 ai.py` runs the 13 checks on this filtering, with no key and no internet.

---

## An AI agent gets the same treatment

`mcp_server.py` exposes the same hold workflow as standard tools an AI agent can
call (MCP, written from scratch). The point: **the ledger's rules apply to an AI
agent exactly as they apply to a person.** The agent-eval (`eval_mcp.py`, 7/7
pass) drives a real agent connection and confirms that when an agent tries to
invent a cause, the ledger rejects it just the same.

---

## Files

```
daml-src/Provenance.daml    the contracts: held → release/return/dispute + audit entry
daml-src/AuthProbe.daml     the test that caught the issuer-alone bug
daml-src/ListParties.daml   sets up the three parties and the first hold
demo/live_demo.py           the 11 checks, run against the live ledger
demo/run_stack.sh           one command to start everything and run the demo
ui/server.py                the three-pane screen (does no filtering — the ledger decides)
ui/index.html               the issuer / holder / auditor views
ai.py                       the AI helper + the filter that stops it inventing causes
mcp_server.py               the AI-agent interface (MCP)
eval_mcp.py                 proves an agent can't invent a cause either
proof.sh                    one command: every check, in order
BUILD_LOG.md                every decision, dated — including the bug we found and fixed
```

---

## Honest disclosure (per the hackathon rules)

**A pre-window research probe.** On Oct 3, before this season's build, I wrote a
single experimental Daml contract to see whether Canton could enforce an
empty-reason rule. It's in `/root/canton_probe/holdwatch-probe`. It never solved
multi-party signing and was never deployed. The hackathon FAQ allows pre-existing
code **if disclosed**, and judges score only in-window work — so: **everything
in this repository is in-window work** (Oct 4–9). The git history timestamps
every commit inside the window.

**Where the idea came from.** The "explain holds, never invent causes" idea comes
from HoldWatch, my PayPal AI Hackathon entry (public on Devpost). Provenance is
not a copy of its code — it's the same honesty rule, moved from "our server
promises it" to "the ledger enforces it."

MIT licensed. Not affiliated with Digital Asset or the Canton Network.
