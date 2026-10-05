# Validation — four real interviews (Oct 2026)

Evidence for the problem Provenance solves. Four people who experienced a silent
payment hold, interviewed with the five questions in INTERVIEW_KIT.md.

**Integrity note:** these are the interviewees' own words, recorded as given and
reproduced verbatim below. Nothing has been embellished, smoothed, or rewritten
to sound more convincing — a product whose claim is "we will not invent a
reason" cannot be built on invented evidence. Source doc:
https://docs.google.com/document/d/1XCN_J4xtTMclbsFTS0KqUtgd3VDVupJDOWWGh4CaEOE

---

## The four cases

| Who | Platform | Frozen | Held | The literal message | The costly guess |
|---|---|---|---|---|---|
| Nuhu Qamarudeen Etudaye — freelance 3D visualiser, Okene, Nigeria | Payoneer / Upwork | $850 | 9 days | "Your withdrawal is pending review. This process can take up to 2-3 business days. No further action is required from you at this time." | Cancelled and split the payout ($400 + $450) → flagged for account-takeover velocity, timeline reset |
| Usman Hasiya — MD, design & copy agency, Abuja | Flutterwave / Wise Business | $2,400 (6 contractors) | 14 days | "Payout batch FLW-BATCH-0941 status: PENDING COMPLIANCE CLEARANCE." | Paid 3 contractors from personal savings (₦1,850,000) → batch cleared anyway, everyone paid twice, 3 months recovering it |
| Momoh Salihu — lead backend engineer, Idah | Paystack Transfers API / Stripe Connect | $4,200 | 6 days | `{"status": "reversed", "gateway_response": "Declined by processor", "reason": null}` | 10-minute retry worker → processor anti-fraud tripped, all API keys revoked (HTTP 403) |
| Nawab Hannan — full-stack contractor, Lahore | Upwork / Payoneer → Meezan Bank | $1,650 | 8 days | "Your transaction is being processed. Expected date of arrival: pending clearance." | Opened 3 parallel tickets → flagged as duplicate, merged, queue position reset |

Support round-trips ranged from **18 hours to 5 days** per reply. Direct costs
included a ₦30,000 rent penalty, ₦120,000 in FX spread, $180 in failed-transfer
fees, 6,500 PKR on a bounced auto-lease debit, one senior copywriter resigning
over payroll instability, and 36 hours of emergency reconciliation.

---

## What the four cases establish

**1. The silence is the damage, not the hold.** All four said the delay was
secondary; the absence of a reason is what forced a bad decision. In every case
the platform showed a status word — "Pending", "PENDING COMPLIANCE CLEARANCE",
`reason: null` — and nothing else.

**2. Nobody could tell a routine delay from an active blocker.** Two of them
(Nuhu, Nawab) were explicitly told "no action required" / "being processed"
while the correct action existed and had a deadline attached.

**3. Guessing has a price, and the price compounds.** Every wrong move *reset a
clock or triggered a lock*: split payout → security hold; parallel tickets →
queue reset; retry worker → key revocation; personal-savings bridge → double
payment. Acting on a guess was worse than waiting.

**4. The engineer's payload is the technical version of the thesis.** A production
webhook literally returned `"reason": null` while the docs promised descriptive
error objects. His words: *"you are expected to debug silence."* That `null` is
precisely the field Provenance refuses to fabricate — the contract has no reason
box to put one in until both parties establish one.

---

## Verbatim quotes (with permission)

**Nuhu (freelancer), on the message:**
> "It literally said: 'Your withdrawal is pending review… No further action is
> required from you at this time.' That was all. No red flag, no link to click…
> When an app says 'no action required', you don't know whether to wait and
> starve or run around looking for help."

**Nuhu, on the wrong move:**
> "The moment I did that, the whole account got placed on security hold. A
> support agent told me on day 6 that canceling an in-flight review looks like
> account takeover activity. **If they had simply shown why it was delayed in
> the first place, I would have kept my hands to myself.**"

**Usman (agency lead), on the dashboard:**
> "The worst thing about managing a team is having to say 'I don't know where
> the money is' when the dashboard just writes one cold word: PENDING."

**Usman, on what it cost:**
> "The silence from the platform made me look like an incompetent liar to my own
> staff."

**Momoh (engineer), on the payload:**
> "The webhook delivered a payload with status: reversed and literally
> `reason: null`… The API documentation promises descriptive error objects, but
> in production, you just get null."
>
> "Building on payment APIs means accepting that when things break, the machine
> returns null. You are expected to debug silence."

**Nawab (cross-border contractor), on the behavioural cost:**
> "The silence forces you into irrational behaviour. You start opening tickets
> and calling people who know less than you do, just to feel like you're doing
> something."

---

## How this maps to the product

| What they said | What Provenance does |
|---|---|
| "no action required" while money sat frozen | The contract distinguishes HELD (no reason exists yet) from RELEASED/RETURNED (a reason both sides signed). "No reason" is a state, not a shrug. |
| Guessing reset a clock or locked an account | Nothing to guess from: the ledger shows what is established and what isn't. A dispute records the holder's words without pretending a cause exists. |
| `reason: null` in production | There is no reason field on a held payment. An empty or invented reason is a **rejected transaction**, not a null a developer must interpret. |
| "I don't know where the money is" — said to a team | The audit trail is readable by an observer: every transition, every established cause, no private terms exposed. |
| Nobody could prove how a hold was resolved | Resolution writes an `AuditEntry` with the signed cause — the artefact Usman needed for her team and her clients. |

## Limits of this evidence

Four interviews is a pattern, not a statistically representative sample. All four
are in two corridors (Nigeria, Pakistan) and all four are people reachable
through my network, which biases toward people who were willing to talk. The
findings justify the problem and the design; they do not size a market. The
beachhead estimate (~5,000 agency ops leads in Nigeria) remains a
order-of-magnitude derivation, explicitly not a sourced TAM.
