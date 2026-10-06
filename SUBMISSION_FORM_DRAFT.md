# Track 1 Submission — FORM DRAFT (do not paste until Oct 8–9)

Status: mentor-compressed form answers, verified against repo at 8854d59 on
2026-10-04. UPDATE BEFORE PASTING: "What remains" (AI layer / DevNet may be
done by then) and re-run demo/live_demo.py + daml test the night of Oct 8.

---

**Problem**
When a payment is held, the rail tells the operator that it is frozen but not why. That gap is where the real damage happens. In four interviews with people who experienced a silent hold (a Payoneer/Upwork freelancer, a Flutterwave/Wise agency lead, a Paystack/Stripe engineer, an Upwork cross-border contractor), every one said the delay was secondary — the absence of a stated reason is what forced a costly guess. They saw messages like "pending review… no further action is required," "PENDING COMPLIANCE CLEARANCE," and a production webhook returning `reason: null`, then acted blind: one split a payout and reset the review clock, one paid staff from personal savings and double-paid when the batch cleared, one auto-retried a failed transfer and got every API key revoked, one opened parallel tickets and lost their queue position. Support round-trips ran 18 hours to 5 days. A wrong guess was worse than waiting, and nobody could tell a routine delay from an active blocker.

**ICP**
The primary ICP is an operations lead at a small agency that bills overseas clients and pays a roster of freelancers through PayPal, Wise, Flutterwave or Payoneer. This is the person pulled into every "my money is missing" issue, who sees a status like ONHOLD or "pending compliance clearance," and who has to know what is established, what is not, and what to do next — usually within minutes, facing the people waiting on the money. The persona we use is Amina: a 5–50 person agency ops lead sitting between the payer, the payee, and the rail. She is not invented — she is modelled on a real interviewee (Usman Hasiya, an Abuja agency MD) whose $2,400 batch to six contractors sat at "PENDING COMPLIANCE CLEARANCE" for 14 days while she had to answer to all six. In her words: *"The worst thing about managing a team is having to say 'I don't know where the money is' when the dashboard just writes one cold word: PENDING."*

**Use case / workflow**
Provenance models the hold lifecycle on Canton as a ledger-enforced contract flow: an issuer and holder co-create a held payment, the contract has no reason field that can be fabricated later, a release with an established cause records that cause, a fabricated or empty cause is rejected by the ledger, a dispute path records the holder's words without pretending a cause has been established, and an auditor can observe the established record without being able to act while a stranger sees nothing.

**Validation**
Four interviews with people who experienced a silent hold (Oct 2026): a freelancer (Payoneer/Upwork, $850, 9 days), an agency payout lead (Flutterwave/Wise, $2,400 batch, 14 days), a payments-API engineer (Paystack/Stripe, $4,200, 6 days), and a cross-border contractor (Upwork/Payoneer, $1,650, 8 days). Every one confirmed the same pattern: the hold itself was secondary — the absence of a stated reason was the damage. Each then made a costly guess that reset a clock or triggered a lock: splitting a payout (account flagged, timeline reset), paying staff from personal savings (double-paid when the batch cleared), auto-retrying a failed transfer (all API keys revoked), opening parallel tickets (queue position reset). Support round-trips ran 18 hours to 5 days. The engineer's case is the technical proof of the thesis: a production webhook returned `{"status":"reversed","reason":null}` while the docs promised descriptive errors — in his words, *"you are expected to debug silence."* That `null` is exactly the field Provenance refuses to fabricate. A representative quote from the freelancer: *"When an app says 'no action required' while holding your money, you are sitting in a dark room. You don't know whether to keep quiet or start panicking."* Full interview record, verbatim quotes and an honest statement of the sample's limits are in VALIDATION.md. (Four interviews establish the pattern and the design; they do not size a market — the ~5,000 beachhead figure remains an order-of-magnitude derivation, not a sourced TAM.)

**Why Canton**
Canton fits because this product depends on two things that are hard to express as a normal app-layer promise: a ledger-enforced invariant and observer disclosure with privacy. In Provenance, "do not invent a cause" is enforced by the contract structure and ledger behavior, not by UI validation or a backend policy, and the auditor can verify the record without gaining control over it. Signatories can act, observers can see the established record, strangers see nothing. This is the product's technical center.

**Current proof**
Demo video (interview-led, ~2:26 as rendered locally): https://www.youtube.com/watch?v=_dGeWs6aE_o. The repository demonstrates the workflow mechanics, not a commercial pricing model. On a local Canton stack, the build is passing 11 live demo checks, 5 Daml contract tests, 13 AI-screen checks and 7 MCP agent evals — all emitted by `./proof.sh` and re-verified at the site's build gate, so every figure quoted is eval output, not a typed claim. The public repo is at github.com/HusseinAdeiza/provenance and the product site at husseinadeiza.github.io/provenance-site. The demonstrated behaviors are: a fabricated empty cause is rejected by the ledger with FAILED_PRECONDITION; a one-signature release is rejected even with a valid reason, because establishing a cause requires both parties (a regression test pins this — see BUILD_LOG D4, where we caught and fixed an earlier version that let the issuer release alone); every cause-establishing transition writes an on-ledger AuditEntry the observer can read while a stranger sees zero; a screened AI layer answers from contract state only and discards any answer that invents a cause; and an MCP server exposes the lifecycle as agent tools, where an agent's fabricated cause is rejected exactly like a human's. A three-pane UI shows what the ledger discloses to issuer, holder, and auditor because the server does no filtering of its own.

**Pilot plan**
Step 1 is a shared-network deployment. DevNet needs a Super Validator sponsor, VPN credentials and an egress-IP allowlist entry with a 2–4 week approval, so in-window the demo runs on a local Canton sandbox (which the hackathon FAQ explicitly accepts for judging) and the validator application is the first post-window action; moving the same DAR to DevNet is a configuration change, not a rebuild. Step 2 is one agency pilot with a real agency from the target ICP. Step 3 is using the auditor seat as the expansion wedge, because the auditor view is the compliance and verification surface, it can be shown to counterparties without exposing private terms, and it creates a natural path from internal ops use to external verification use.

**Team / existing code**
The repo includes an in-window implementation and also a pre-window research probe disclosed in the README; that probe is included for honesty, but judges should evaluate the in-window work only. The current submission is based on the in-window Canton build, live demo, and tests.

**Status / what remains**
Provenance is a working proof that a payment hold can be modeled so the ledger enforces the difference between a held payment, an established cause, and an invented explanation. The current build proves the contract mechanics, privacy boundaries, role separation, the on-ledger audit trail, the screened AI layer and the agent (MCP) surface, and the problem is validated by four field interviews (see VALIDATION.md) — but it does not yet prove market adoption, pricing, or scale. Not yet in the repo are a shared-network deployment (DevNet requires a Super Validator sponsor, VPN and a 2–4 week approval, so the demo runs on a local sandbox, which the FAQ accepts for judging), business model finalization, and measured pilot outcomes.

---

## Oct 8 pre-paste checklist

- [ ] Re-run `./proof.sh` — confirm 11 demo / 5 daml / 13 ai / 7 mcp, all fail=0
- [ ] Re-run `npm run build` in provenance-site — the gate re-verifies proof.json + live stack
- [x] AI layer shipped — moved out of "what remains", added to "Current proof"
- [x] DevNet: documented as blocked (2–4wk SV approval); pilot Step 1 reworded to local-sandbox + validator application
- [x] Interviews done — 4 real interviews folded into Problem/ICP/Validation; verbatim record in VALIDATION.md (no embellishment, per the integrity note)
- [ ] Upload video to YouTube (@web3alphatester) via video/YOUTUBE_UPLOAD_PACK.md; add URL to video field + README
- [ ] git log confirms all commits in-window; probe disclosure intact in README

## Live Demo Deployment Notes (as of Oct 6 2026 - 10:57 CEST)

**Current live demo URL:** https://secondary-manner-gospel-vids.trycloudflare.com

This URL is powered by a Cloudflare tunnel running on a stable VPS. The tunnel is
monitored by a watchdog script (run via cron every 2 minutes) that will restart
it if there's an outage.

**Critical note:** The tunnel URL may change if the cloudflared process restarts.
The watchdog logs any changes to `/root/provenance/demo/watchdog.log`.

**For permanent deployment:** Render.com Blueprint is pre-configured at
https://dashboard.render.com/blueprint/exs-db29o697lnhs73e5okbg
- Service: provenance-demo (Standard plan, $25/mo, 2GB RAM)
- One-click deploy from HusseinAdeiza/provenance

**Why Render Standard is needed:**
- The Canton JVM alone requires 913MB RAM
- Render's free tier is limited to 512MB  
- Standard plan ($25/month) gives 2GB RAM, sufficient for the demo
