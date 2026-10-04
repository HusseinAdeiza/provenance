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

---

## Open items

- [ ] DevNet deployment (pilot step 1)
- [ ] Site public deploy (Render blueprint — needs user's Render dashboard, or GitHub Pages)
- [ ] 3 user interviews (validation evidence)
- [x] ~~Demo video~~ done: video/out/Provenance_DEMO.mp4, 99.6s, QC'd
- [ ] YouTube upload of the demo video + title/description pack
