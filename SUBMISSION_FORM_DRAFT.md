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
The repository demonstrates the workflow mechanics, not a commercial pricing model. On a local Canton stack, the build is passing 8/8 live demo checks and 3/3 Daml unit tests, and the public repo is available at github.com/HusseinAdeiza/provenance. The demonstrated behaviors are: a fabricated empty cause is rejected by the ledger with FAILED_PRECONDITION, a one-signature create is rejected because both parties are required, a stranger querying the ledger sees zero contracts, an auditor sees the established cause without being able to act, and a three-pane UI shows exactly what the ledger discloses to issuer, holder, and auditor because the server does no extra filtering.

**Pilot plan**
Step 1 is DevNet deployment, moving the current local demo to shared infrastructure so it can be accessed outside the founder's laptop environment. Step 2 is one agency pilot with a real agency from the target ICP. Step 3 is using the auditor seat as the expansion wedge, because the auditor view is the compliance and verification surface, it can be shown to counterparties without exposing private terms, and it creates a natural path from internal ops use to external verification use.

**Team / existing code**
The repo includes an in-window implementation and also a pre-window research probe disclosed in the README; that probe is included for honesty, but judges should evaluate the in-window work only. The current submission is based on the in-window Canton build, live demo, and tests.

**Status / what remains**
Provenance is a working proof that a payment hold can be modeled so the ledger enforces the difference between a held payment, an established cause, and an invented explanation. The current build proves the contract mechanics, privacy boundaries, and role separation, but it does not yet prove market adoption, pricing, or scale. Not yet in the repo are production deployment, the AI follow-up layer, validated user interviews, business model finalization, and measured pilot outcomes.

---

## Oct 8 pre-paste checklist

- [ ] Re-run `./demo/run_stack.sh` — confirm 8/8 still PASS
- [ ] Re-run `daml test` — confirm 3/3 green
- [ ] If AI layer shipped: move it out of "what remains", add one line to "Current proof"
- [ ] If DevNet shipped: rewrite pilot Step 1 as done, adjust "Current proof" ("local" → DevNet)
- [ ] Interviews done? Add count + one quote (real ones only) to ICP or Problem
- [ ] git log confirms all commits in-window; probe disclosure intact in README
