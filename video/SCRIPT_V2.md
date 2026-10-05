# Provenance — demo video v2 script (sample-style)

Reference: canton_sample.mp4 (studied) — cinematic dark grade, persona name card
("Maya. 23."), one accent colour, HUD-style data overlays, ~2:00, live-action +
motion graphics hybrid.

Our honest adaptation: NO live-action (cannot film a person; AI faces would be
fabrication). Persona reconstruction in motion graphics, labelled on screen.
Product act = real capture, slower + sharper + zoomed callouts.

VOICE: Abeo (en-NG-AbeoNeural), rate +0% — natural pace, NO speeding.
LOUDNESS target: mean ≈ -18 dB (match sample), max ≈ -1 dB.

---

## B1 — PERSONA CARD (motion graphics, ~12s VO)

Visual: near-black. Name card animates in, sample style:
  "Nuhu." large white sans
  "Freelance 3D artist · Okene, Nigeria" smaller, dim
  one amber accent line. Bottom corner: "reconstruction from a real interview"
  (No age — the interview record doesn't state one; invent it and the card
  becomes the fabrication the product refuses.)

VO: "Nuhu is a freelance 3D artist in Okene, Nigeria. He finished a three-week
milestone on Upwork, and withdrew eight hundred and fifty dollars. It usually
clears in four hours."

## B2 — THE SILENCE (notification artefact + timeline, ~28s VO)

Visual: the literal notification rendered as an artefact card (like the sample's
HUD): "Your withdrawal is pending review. This process can take up to 2-3
business days. No further action is required from you at this time."
Then a timeline bar: hours pass → "Day 3" → "Day 5" → "Day 9". Counter of
support round-trips: "38 hours for an automated reply · 5 days for a human".

VO: "By five in the evening, nothing. The app said: your withdrawal is pending
review. No further action is required from you at this time. That was all. No
reason. No link. No next step. He checked his email for a compliance request.
There was nothing. He asked support. Thirty-eight hours later, a bot replied.
Five days later, a human did."

## B3 — THE WRONG MOVE (~18s VO)

Visual: the split — "$850" divides into "$400 + $450", then a red stamp:
"ACCOUNT FLAGGED · TIMELINE RESET". The 9-day bar restarts and stretches.

VO: "On Friday, out of panic, Nuhu cancelled the withdrawal and split it in two,
hoping smaller amounts would pass. It did the opposite. Cancelling an in-flight
review looks like account takeover. The clock reset. Nine days without his
money. A thirty-thousand-naira rent penalty. And one sentence he keeps
repeating:"

## B4 — THE QUOTE + PIVOT (~14s VO)

Visual: black screen, serif italic quote (the only serif moment):
  "You are sitting in a dark room. You don't know whether to keep quiet
   or start panicking."
Then the pivot line animates: "What if the system couldn't invent a reason?"

VO: quote is on screen silent for ~3s (let it land), then:
"What if a payment system could not invent a reason — not because it promised,
but because the ledger refused?"

## B5 — THE PRODUCT + THE MOMENT (real capture, ~30s VO)

Visual: real roles UI. Slow cursor. Zoom-in crop on the ledger log when the red
REJECTED line lands (like the sample's gauge dominating frame). Callout labels:
"no reason field exists" → held card; "BOTH parties must sign" → release.

VO: "This is Provenance, on Canton. Three roles, one ledger: the payer, the
person waiting for the money, and an auditor who watches everything and can
touch nothing. A held payment has no reason field at all. There is nowhere to
put a lie. Watch what happens when I try to release this hold with an empty,
invented cause. The platform refuses. That rejection did not come from our app.
It came from the ledger itself."

## B6 — HONEST PATH + PRIVACY (real capture, ~20s VO)

Visual: honest release (both parties) → green "cause established" + audit trail
row appears. Then pan to auditor pane, then the stranger line "0 contracts".
Usman flash card: "$2,400 · 14 days · 6 contractors · 'one cold word: PENDING'"

VO: "A cause enters the record only when both sides sign it — one signature
alone is rejected too. Every step writes an audit trail the auditor can read
without seeing private details. A stranger sees nothing. This is not a toy
problem. One agency owner we interviewed paid her team from personal savings
during a fourteen-day silence — and paid them twice when the batch finally
cleared."

## B7 — PROOF + CLOSE (~12s VO)

Visual: close card, numbers animate up (seek-safe): 11 live checks · 5 contract
tests · 13 AI-screen checks · 7 agent evals. Repo + site URLs.

VO: "Every number we claim is test output, and the page refuses to build if any
check fails. Provenance. The honesty rule the ledger refuses to break."

---

## Timing discipline
- Generate ALL VO first, measure, THEN size visuals to measured audio.
- No beat's VO is sped up. If total exceeds ~2:20, trim WORDS, never rate.
- Silence gaps ≥0.6s between beats for breath.
