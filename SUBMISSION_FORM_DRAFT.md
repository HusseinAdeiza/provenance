# Track 1 Submission — FORM DRAFT (do not paste until Oct 8–9)

Status: mentor-compressed form answers, verified against repo at 8854d59 on
2026-10-04. UPDATE BEFORE PASTING: "What remains" (AI layer / DevNet may be
done by then) and re-run demo/live_demo.py + daml test the night of Oct 8.

---

**Problem**
When a payment is held, the rail usually tells the operator that it is frozen, but not why. That creates a costly gap for the person responsible for payouts: they have to respond immediately, but the available signal is often just a status code. Any explanation becomes a guess unless the rail actually established a reason, and wrong guesses cause delay, support churn, and avoidable mistrust.

**ICP**
The primary ICP is an operations lead at a small digital agency that bills overseas clients and pays a roster of freelancers through PayPal or Wise. This is the person who gets pulled into every "my money is missing" issue, sees payment states like ONHOLD or pending review, and has to know what is established, what is not, and what action to take next. The specific persona we use is Amina: a 5–50 person agency ops lead sitting between the payer, the payee, and the rail.

**Use case / workflow**
Provenance models the hold lifecycle on Canton as a ledger-enforced contract flow: an issuer and holder co-create a held payment, the contract has no reason field that can be fabricated later, a release with an established cause records that cause, a fabricated or empty cause is rejected by the ledger, a dispute path records the holder's words without pretending a cause has been established, and an auditor can observe the established record without being able to act while a stranger sees nothing.

**Why Canton**
Canton fits because this product depends on two things that are hard to express as a normal app-layer promise: a ledger-enforced invariant and observer disclosure with privacy. In Provenance, "do not invent a cause" is enforced by the contract structure and ledger behavior, not by UI validation or a backend policy, and the auditor can verify the record without gaining control over it. Signatories can act, observers can see the established record, strangers see nothing. This is the product's technical center.

**Current proof**
The repository demonstrates the workflow mechanics, not a commercial pricing model. On a local Canton stack, the build is passing 11 live demo checks, 5 Daml contract tests, 13 AI-screen checks and 7 MCP agent evals — all emitted by `./proof.sh` and re-verified at the site's build gate, so every figure quoted is eval output, not a typed claim. The public repo is at github.com/HusseinAdeiza/provenance and the product site at husseinadeiza.github.io/provenance-site. The demonstrated behaviors are: a fabricated empty cause is rejected by the ledger with FAILED_PRECONDITION; a one-signature release is rejected even with a valid reason, because establishing a cause requires both parties (a regression test pins this — see BUILD_LOG D4, where we caught and fixed an earlier version that let the issuer release alone); every cause-establishing transition writes an on-ledger AuditEntry the observer can read while a stranger sees zero; a screened AI layer answers from contract state only and discards any answer that invents a cause; and an MCP server exposes the lifecycle as agent tools, where an agent's fabricated cause is rejected exactly like a human's. A three-pane UI shows what the ledger discloses to issuer, holder, and auditor because the server does no filtering of its own.

**Pilot plan**
Step 1 is a shared-network deployment. DevNet needs a Super Validator sponsor, VPN credentials and an egress-IP allowlist entry with a 2–4 week approval, so in-window the demo runs on a local Canton sandbox (which the hackathon FAQ explicitly accepts for judging) and the validator application is the first post-window action; moving the same DAR to DevNet is a configuration change, not a rebuild. Step 2 is one agency pilot with a real agency from the target ICP. Step 3 is using the auditor seat as the expansion wedge, because the auditor view is the compliance and verification surface, it can be shown to counterparties without exposing private terms, and it creates a natural path from internal ops use to external verification use.

**Team / existing code**
The repo includes an in-window implementation and also a pre-window research probe disclosed in the README; that probe is included for honesty, but judges should evaluate the in-window work only. The current submission is based on the in-window Canton build, live demo, and tests.

**Status / what remains**
Provenance is a working proof that a payment hold can be modeled so the ledger enforces the difference between a held payment, an established cause, and an invented explanation. The current build proves the contract mechanics, privacy boundaries, role separation, the on-ledger audit trail, the screened AI layer and the agent (MCP) surface — but it does not yet prove market adoption, pricing, or scale. Not yet in the repo are a shared-network deployment (DevNet requires a Super Validator sponsor, VPN and a 2–4 week approval, so the demo runs on a local sandbox, which the FAQ accepts for judging), validated user interviews, business model finalization, and measured pilot outcomes.

---

## Oct 8 pre-paste checklist

- [ ] Re-run `./proof.sh` — confirm 11 demo / 5 daml / 13 ai / 7 mcp, all fail=0
- [ ] Re-run `npm run build` in provenance-site — the gate re-verifies proof.json + live stack
- [x] AI layer shipped — moved out of "what remains", added to "Current proof"
- [x] DevNet: documented as blocked (2–4wk SV approval); pilot Step 1 reworded to local-sandbox + validator application
- [ ] Interviews done? Add count + one real quote to ICP or Problem (never invented)
- [ ] Upload video to YouTube (@web3alphatester) via video/YOUTUBE_UPLOAD_PACK.md; add URL to video field + README
- [ ] git log confirms all commits in-window; probe disclosure intact in README
