# BUILD STRATEGY — adopted 2026-10-04

Source: @suraj_sharma14 (x.com/suraj_sharma14/status/2106602713635041542 and
his related threads). User directive: "adopt this strategy to our build — all
the buildings we will be doing."

## The strategy (his words, condensed)

1. Pick one **boring, painful problem people pay to fix**
2. Build an **agent that solves it end to end**
3. Give it **real tools, memory and MCP connectors**
4. **Guardrails: approvals, limits, error handling**
5. **Write evals** so you can prove it works
6. Replace fragile chat loops with **state machines**
7. **Document every decision** — "most people import libraries; builders
   understand what happens underneath"

## Our adaptation (the standing rule for every future build)

Every build gets these seven slots filled or explicitly declined-with-reason:

| Slot | Our standard |
|---|---|
| Boring paid problem | One sentence, with evidence someone pays (interview, forum volume, existing budget line). No "visionary" problems. |
| End-to-end agent | The agent must complete a task a human would do, not assist a demo. If there's no agent, say so — don't dress a tool as one. |
| Tools/MCP | Expose the product's real operations as an MCP server (raw JSON-RPC stdio, no SDK dependency) OR documented tool API. Tools call the SAME code path as the UI — never a demo-only shim. |
| Guardrails | Approvals (human-in-loop for irreversible acts), limits (budgets, rate), error handling (fail closed). The HoldWatch/Provenance screening pattern is the template: never trust the model to obey; screen its output. |
| Evals | A runnable eval file with pass/fail counts (`python3 X.py` → "ALL n PASS"). Golden cases + adversarial cases. Numbers in README/pitch are quoted FROM eval output, never typed. |
| State machine | Deterministic lifecycle, explicit states, no vibes-driven branching. Where a ledger/DB can enforce the machine, prefer that (Provenance: Daml contracts ARE the state machine — the strongest possible version of this rule). |
| Decision log | `BUILD_LOG.md` in every repo: date, decision, alternatives rejected, why. Bug-found-and-fixed entries are the most valuable — they're proof of testing, not asserting. |

## Applied to Provenance (gap analysis, 2026-10-04)

| Slot | Status |
|---|---|
| Boring paid problem | ✅ hold-silence; Amina persona; PayPal forum volume; interviews pending |
| End-to-end agent | ⚠️ partial — the AI answers questions but doesn't ACT. The contract lifecycle + UI is the product; an agent layer (e.g. "resolve this hold: propose cause, collect both signatures, write the audit entry") is the natural next build |
| Tools/MCP | ❌ MISSING — build a Provenance MCP server: `provenance_query(role)`, `provenance_create_hold`, `provenance_release(reason)` (fails per ledger rules), `provenance_audit_trail`. Same JSON-API client the UI uses |
| Guardrails | ✅ strong — two-tier cause screen, fail-closed fallback, dual-controller ledger enforcement |
| Evals | ✅ exists but unnamed — 11-check live demo + 5 daml tests + 13-check ai.py self-test. Package them as one `eval` entry point with a printed summary |
| State machine | ✅✅ the strongest slot — the ledger IS the state machine; transitions are choices; illegal states are unrepresentable (no reason field on HeldPayment) |
| Decision log | ❌ MISSING — the false-claim bug (single→multi controller) is exactly the kind of entry this log exists for. Write BUILD_LOG.md from session history |

Order for the hackathon window (5 days): decision log + eval packaging (fast,
uses existing work) → MCP server (biggest missing slot, ~150 lines JSON-RPC)
→ video → site. The MCP server also upgrades the pitch: "an AI agent can drive
the hold lifecycle through standard tools, and the ledger's guardrails apply to
agents exactly as they apply to humans."
