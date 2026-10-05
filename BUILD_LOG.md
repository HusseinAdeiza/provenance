# BUILD_LOG — every decision, dated

The adopted build strategy (BUILD_STRATEGY.md, from @suraj_sharma14's thread)
requires documenting every decision. Bug-found-and-fixed entries are the most
valuable: they are proof of testing rather than asserting.

All entries in-window (HackCanton S4 delivery opened Oct 4 for this entrant's
season instance). Pre-window artefact: the Oct-3 research probe, disclosed in
README.

---

## 2026-10-04

**D1 — Chose the hold-lifecycle domain over a fresh RWA idea.**
Rejected: tokenized audit reports (AuditGraph angle). Why: the hold thesis has
a shipped predecessor (HoldWatch, public on Devpost), a live problem story, and
a pre-window Daml probe — three of the six judging criteria already had
evidence. Fresh ideas start at zero.

**D2 — HeldPayment carries NO reason field, instead of `Optional Text`.**
The Oct-3 probe used `reason : Optional Text` with an assertion. Rejected for
the product: an assertion can be argued with; a missing field cannot. "You
cannot fabricate what the contract cannot hold" became the design rule.

**D3 — Dispute stays single-controller (holder alone).**
Considered making everything dual-controller. Rejected: a payee must be able
to contest a hold WITHOUT the payer's agreement — that is the point of a
dispute. Resolution is dual; contest is not. Asymmetry is the design.

**D4 — 🔴 FOUND FALSE CLAIM: issuer could release alone.**
The pitch said "a cause only enters when both parties sign." An authoritative
`daml script` test (AuthProbe, `submitMustFail`) reported "Expected submit to
fail but it succeeded" — Release with actAs=[Issuer] returned 200. Root
cause: consuming the jointly-signed HeldPayment implicitly authorises the
holder for the transaction, so single-controller Release rode on the
counterparty's signature. The claim in README/pitch/brief was false; caught
by testing the claim instead of asserting it.
FIX: Release/Return/ResolveDispute → multi-controller (`controller issuer,
holder`). Controllers must be explicitly in actAs; consumption-authorisation
cannot substitute. Regression test `test_issuer_cannot_release_alone` pins
it; demo check #5 exercises it live over HTTP.

**D5 — Corrected an earlier misdiagnosis in the skill notes.**
"Multi-controller choices can't create/getTime" was WRONG — the original
failure was `createCmd` (Commands-typed) inside a choice body; `create`
(Update) works in any choice. Skill patched so the next build doesn't
inherit the error.

**D6 — AuditEntry wired into every transition (was dead code).**
The template existed but nothing created it — Track 1's audit step was only
implied. Now Release/Return/Resolve write entries with the established
cause; Dispute writes `detail = None` (a dispute NEVER establishes a cause,
and the trail records exactly that). signatory issuer, observer auditor+holder.

**D7 — AI layer: screen, don't trust.**
Gemini answers strictly from contract state; every output re-screened.
Two tiers after the self-test caught a false positive: the honest fallback
("no cause ... because none was established") was being discarded as
fabrication. STRONG cause terms (fraud, flagged-for, under-review, AML)
flag unconditionally — even behind a denial prefix ("no cause established,
but likely flagged for compliance" → discarded). WEAK connectives flag only
without a denial. A denial is not an invention.

**D8 — No GEMINI_API_KEY → deterministic mode, by design.**
Layer reports disabled; everything renders from contract state. Reuses the
HoldWatch lesson: a submission that dies without an API key is a demo.

**D9 — MCP server written from scratch (raw JSON-RPC stdio, no SDK).**
Per the adopted strategy. 7 tools; uses the SAME JSON-API client as the UI —
no demo-only shim. `provenance_fabricate_cause` is deliberately included: an
agent SHOULD fail at it, and the eval asserts the ledger's rejection reaches
the agent verbatim. eval_mcp.py: 7/7 PASS, including "agent fabrication is
rejected by the ledger".

**D10 — One eval entry point (run_eval.sh).**
build → daml test → live demo → AI screen self-test → MCP eval. Every number
in README/pitch is quoted from this output, never typed.

**D11 — Roles UI server does NO filtering.**
Each pane queries the ledger with that role's own token; what renders is
what the ledger discloses. A permissions shim in the server would have made
the privacy demo a lie.

**D12 — Local Canton sandbox, not DevNet (yet).**
SDK 2.10.6 `daml sandbox` + `daml json-api` verified end-to-end (v1 routes,
JWT actAs claims, package-id discovery). DevNet is pilot step 1; rules allow
LocalNet for judging. Stale-process port squatting and package-id churn
documented in the skill after they cost an hour.

---

**D13 — Product site: the build gate reads proof.json, not typed numbers.**
Forked the HoldWatch scaffold (tokens + layout survived review there). The
gate refuses to build unless the live stack answers, stranger visibility is
exactly 0, and proof.json is <24h old with zero failures — so a figure on the
page and a check in the eval suite are the same artifact. First gate run
caught a real inconsistency: damlTestsOk said 8 because `: ok` counted setup +
bootstrap + probe scripts as tests; every other surface says 5. Fixed at the
source (proof.sh counts test_* only). Verified: 127 text elements, 0 contrast
failures; 390/768/1440 clean; vision review found no slop tells.
Repo: github.com/HusseinAdeiza/provenance-site (dist/ committed — Render
builder has no ledger, so the gate runs locally at build time; documented in
render.yaml).

**D14 — DevNet is NOT reachable in-window; LocalNet is the honest answer.**
Researched the actual onboarding path (docs.canton.network): DevNet requires a
Super Validator sponsor, VPN credentials, an egress-IP allowlist entry, and
**2–4 weeks approval** (validator application via canton.foundation). Our
deadline is Oct 9. The hackathon FAQ explicitly accepts DevNet/TestNet/
**LocalNet** for judging, so the demo stands on the local sandbox — which is
also the only environment where the eval gate (proof.sh) can run. Pilot-plan
wording adjusted: DevNet becomes "validator application submitted" rather than
a promised in-window deploy. Claiming a DevNet deployment we do not have would
be exactly the fabrication this product exists to refuse.

**D15 — Plain-language rewrite + the single-machine disclosure goes public.**
User asked for two things: make it understandable to ordinary people (not
rigorous writing), and ship real, no false claims. Acted on both:
- Rewrote every section of the site and the README in plain words: "contract
  invariant / fabricate into" → "a rule the ledger enforces / no reason box to
  fill in"; "multi-controller / signatory / observer" → "both sides must act
  together / signs / watches only"; "re-screened / deterministic" → "we throw
  the answer away / the plain facts". Jargon kept only in repo/test names.
- The honesty gap I'd left implicit is now explicit ON THE PUBLIC SITE: a
  prominent note in the Disclosure section + a dedicated FAQ entry state that
  the demo runs on one machine where a small server queries the ledger three
  times (once per role). It proves the RULES — which are the product — but is
  NOT three people on three wallets. The rule the ledger enforces (both parties
  sign a release, whoever submits) is identical either way. This is the
  disclose-the-limitation move the whole product is built on, applied to the
  product's own marketing.
- Wallet question answered honestly: NOT required — Canton's FAQ accepts
  LocalNet for judging, Track 1 asks for a roles UI (which we have), and a real
  wallet needs the DevNet approval we can't get by Oct 9. Bolted-on fake wallet
  = the exact fabrication the user told us to avoid.

Verified on the LIVE URL (byte-identical md5 vs pushed tip): 131 text elements,
0 contrast failures; full page renders; numbers 11/5/13/7 correct; proof.json
regenerated against the live stack before the gated rebuild.

**D16 — Four real interviews folded in; the site gained an Evidence section.**
Interviews conducted by the user (Oct 2026): freelancer $850/9d (Payoneer/
Upwork), agency lead $2,400/14d (Flutterwave/Wise), payments engineer
$4,200/6d (Paystack/Stripe, webhook returned `"reason": null`), cross-border
contractor $1,650/8d (Upwork/Payoneer). Universal pattern: the hold was
secondary, the silence caused the damage, and every guess made it worse
(split payout → clock reset; personal bridge → double payment; retry loop →
keys revoked; parallel tickets → queue reset).

User asked to "enhance them" if they seemed unreal. Refused, and said why:
polishing real quotes is fabrication, and fabricated validation under a
product whose thesis is "we will not invent a reason" is the single most
damning contradiction available. The messy specifics (₦30,000 rent penalty,
FLW-BATCH-0941, 38-hour chatbot loops) are what make them credible. Quotes
reproduced verbatim everywhere; VALIDATION.md carries the full record plus an
integrity note and the sample's honest limits (4 people, 2 corridors, network-
sourced — pattern not market).

Submission draft: Problem, ICP (Amina now grounded in a named real case), new
Validation section; "validated user interviews" removed from what-remains.
Site: new Evidence section between AI helper and Proof — gate green, 159 text
elements 0 contrast failures, deployed byte-identical.

---

## Open items

- [ ] DevNet deployment (pilot step 1)
- [ ] Site public deploy (Render blueprint — needs user's Render dashboard, or GitHub Pages)
- [ ] 3 user interviews (validation evidence)
- [x] ~~Demo video~~ done: video/out/Provenance_DEMO.mp4, 99.6s, QC'd
- [ ] YouTube upload of the demo video + title/description pack
