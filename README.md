# Provenance

**Payment holds where "we will not invent a cause" is enforced by the ledger —
not promised by a server.**

Built for HackCanton Season 4 (Track 1: RWA & Business Workflows). Delivery
window Oct 4–9, 2026.

## The problem

When a payment rail freezes funds, it tells you *that* — never *why*. The
payee guesses remedies (chasing a fraud review when the cause was an address
mismatch), tools that "explain" holds invent causes their data never
established, and auditors can only verify compliance by being shown private
payment records in full.

## The Canton answer

On a public chain or behind an API, *"we will not invent a cause"* is a policy:
application code that can be bypassed. On Canton it is a **contract invariant**:

- `HeldPayment` **has no reason field at all.** There is nothing to fabricate
  into while a payment is held.
- A cause enters the record only through `Release`/`Return`, where the reason
  is **required, non-empty, and asserted** — an empty cause is a failed
  transaction (`FAILED_PRECONDITION` from the ledger itself).
- Both parties sign the transition: `signatory issuer, holder` means the
  resolved contract **cannot exist** without both authorisations.
- The `auditor` is an **observer**: sees every state and established cause,
  signs nothing, and cannot act — and a non-party sees **nothing**.
  Auditability and privacy in the same transaction, which no public ledger
  can express.
- Every cause-establishing transition writes an `AuditEntry` on-ledger:
  `RELEASED`/`RETURNED`/`RESOLVED` carry the established cause; `DISPUTED`
  carries `detail = None` — a dispute NEVER establishes a cause, and the
  trail shows that too. This is Track 1's create → status → fulfill →
  **audit** workflow, with the audit step as a first-class contract.

## Layout

```
daml-src/Provenance.daml    the lifecycle: HeldPayment → Release/Return/Dispute
daml-src/AuthProbe.daml     authoritative authorisation probe (ide-ledger)
daml-src/ListParties.daml   idempotent bootstrap: parties + two-party create
demo/live_demo.py           the judge-facing demo (8 checks over the JSON API)
demo/run_stack.sh           build → test → sandbox → bootstrap → json-api → demo
```

## Run it

```bash
./demo/run_stack.sh
```

Requirements: Daml SDK 2.x (`curl -sSL https://get.daml.com | sh`), Python 3.
No tokens, no gas, no external accounts — everything runs locally.

## The demo, in one table

| # | Action | Ledger response |
|---|---|---|
| 1 | Two-party create (`actAs: [issuer, holder]`) | **200** — hold exists |
| 2 | Create with only the issuer's signature | **400 rejected** — holder's authorisation is missing |
| 3 | `Release` with an empty (fabricated) reason, both parties acting | **400 rejected** — the honesty invariant |
| 4 | `Release` with a VALID reason but the **issuer acting alone** | **400 rejected** — a cause needs both parties, not just a reason |
| 5 | `Release` with an established reason, both parties acting | **200** — cause now part of the record |
| 6 | Stranger queries active contracts | **0 results** — disclosure is a contract property |
| 7 | Auditor queries | **sees the released contract and its cause** |
| 8 | Auditor tries to exercise a choice | **rejected** — observers cannot act |
| 9 | Auditor reads the audit trail | **RELEASED entries with established causes** — every cause-establishing transition writes an `AuditEntry` the observer can read |
| 10 | Stranger queries the trail | **0 results** — the audit record is disclosed like everything else |

Latest run (local Canton sandbox, SDK 2.10.6):

```
PASS  two-party create (actAs both signatories)  HTTP 200
PASS  hold carries amount+currency from create  PAY-4200 4200.0 USD
PASS  create with only issuer signature rejected  HTTP 400
PASS  release with empty (fabricated) reason rejected  HTTP 400
PASS  issuer-alone release rejected even with a valid reason  HTTP 400
PASS  release with established reason succeeds HTTP 200
PASS  stranger sees zero contracts              HTTP 200, n=0
PASS  auditor sees released contract + cause  n=1
PASS  auditor cannot exercise (non-controller) HTTP 404
PASS  auditor reads the audit trail (RELEASED entries)  2 entries, 2 RELEASED
PASS  stranger sees no audit trail  HTTP 200
ALL 11 CHECKS PASSED
```

`daml test`: all green — including `test_hold_cannot_carry_a_reason` (fabrication
attempt fails at the assertion), `test_issuer_cannot_release_alone` (regression:
a valid cause with one signature is still rejected) and
`test_auditor_sees_without_signing`.

## Disclosure (existing code, per hackathon FAQ)

A research probe — one Daml template modelling a held payment with an
enforced-empty reason — was built on Oct 3, 2026, while evaluating Canton, and
lives in `/root/canton_probe/holdwatch-probe`. It never solved multi-party
authorisation and was never deployed. **Everything in this repository is
in-window work** (Oct 4–9, 2026): the multi-contract lifecycle, the two-party
JSON-API create, the bootstrap, the demo harness, the UI and the AI layer.
Git history timestamps every commit inside the delivery window.

The product thesis (explain holds, never invent causes) comes from HoldWatch,
our PayPal AI Hackathon entry — public at
devpost.com/software/holdwatch-paypal-payout-holds-explained. Provenance is
not a port of its code; it is the same honesty rule moved from application
policy into ledger law.

## The AI follow-up layer (ai.py)

A language model (Gemini when `GEMINI_API_KEY` is set) answers questions about
a contract **strictly from its ledger state** — and is not trusted to obey:

- every generated answer is re-screened before display; if it asserts a cause
  for a cause-absent contract (`HeldPayment`/`DisputedHold`), the answer is
  **discarded** and a deterministic fallback shown instead, with the UI
  labelling exactly what happened
- two screening tiers: strong cause terms ("fraud", "flagged for compliance")
  flag unconditionally — even smuggled behind an honest-sounding denial
  prefix — while weak connectives ("because") flag only when the text is not
  itself a denial of a cause
- no key set → the layer reports itself disabled and everything renders from
  contract state alone. The product does not die without an API key.

`python3 ai.py` runs the screening self-test (13 checks) with no key and no
network: the screen's job is the product claim, so it is tested like one.

## Known limitations

- Local Canton sandbox; DevNet deployment is the next milestone (in-window).
- The JSON API uses unsigned dev tokens; DevNet requires proper party
  provisioning through its onboarding flow.
- `Release`/`Return`/`ResolveDispute` are multi-controller (`controller issuer,
  holder`) — both parties must act for a cause to enter the record. This was
  NOT the original design: the first version used a single controller and
  claimed the created contract's signatories enforced dual authorisation. An
  authoritative `daml script` test proved that claim FALSE (the issuer could
  release alone — consuming the jointly-signed hold implicitly authorises the
  counterparty for the archive). Fixed the same evening; the regression test
  `test_issuer_cannot_release_alone` pins it, and demo check 4 exercises it
  live. Recorded here because the honest history is part of the evidence.

MIT licensed. Not affiliated with Digital Asset or the Canton Network.
