# Provenance — demo video script (Explainer Cut)

Target: ~85s, 1920x1080, real clicks against the live local stack
(http://127.0.0.1:8090), narration over capture, hard cuts, no motion-graphics
padding. Every on-screen claim verified against repo @ audit-trail commit
(11/11 demo checks, 5 daml tests green).

RECORDER GUARD (preconditions, abort if false — per the HoldWatch lesson):
- page contains "one ledger, three worlds" (correct UI build)
- page contains "no reason field" (corrected hold copy)
- ledger reachable: /api/state returns views for all three roles
- stranger count == 0

## Beats

B1 (0:00–0:12) TITLE CARD (rendered card, dark palette matching UI)
  VO: "When a payment rail freezes your money, it tells you that — never why.
  So people guess. And the wrong guess keeps the money frozen longer."
  On screen: Provenance wordmark + "payment holds where the honesty rule is
  enforced by the ledger"

B2 (0:12–0:24) LIVE UI — three panes
  VO: "Provenance puts the hold on Canton. Three roles, one ledger: the issuer,
  the holder, and an auditor who observes without signing. Each pane shows
  exactly what the ledger discloses to that party — the server filters nothing."
  Action: cursor sweeps the three panes; hovers the held card's
  "cause: — none established" line.

B3 (0:24–0:36) ZOOM: held card
  VO: "A held payment has no reason field at all. There is nothing to invent
  into — the absence of a cause is the contract's structure, not our promise."
  Action: cursor points at the amber cause-absent line.

B4 (0:36–0:52) THE MOMENT — fabrication rejected
  VO: "Watch. I ask the ledger to release this hold with an invented cause.
  The platform itself refuses — not our server. Failed precondition, with the
  contract's own assertion, verbatim."
  Action: click "☠ Fabricate a cause (empty reason)" → ledger log fills with
  red "✗ REJECTED HTTP 400 · FAILED_PRECONDITION … AssertionFailed:
  reason must not be empty at release". Cursor traces the log line.

B5 (0:52–1:04) honest release, both parties
  VO: "A cause enters the record only when both parties sign it. One signature
  with a valid reason is still rejected — that was a real bug we caught in
  testing, and the ledger now refuses it too."
  Action: click "✓ Release with established cause (both parties)…", enter
  "Address mismatch verified by both parties", confirm → card moves to
  ReleasedPayment with green "cause established".

B6 (1:04–1:18) privacy + audit trail
  VO: "The auditor reads the whole trail — every transition, every established
  cause, disputes recorded without one — while a stranger on the same ledger
  sees nothing. Auditable and private, in the same transaction."
  Action: cursor moves to auditor pane's "Audit trail (observer record)" rows;
  then to the stranger line "0 contracts (sees none of it)".

B7 (1:18–1:28) CLOSE card
  VO: "Eleven live checks, five contract tests, all passing. Provenance — the
  honesty rule the ledger refuses to break."
  On screen: 11/11 checks · 5/5 tests · github.com/HusseinAdeiza/provenance

## Numbers audit (every figure in the VO)
- "eleven live checks" — demo/live_demo.py output: ALL 11 CHECKS PASSED (2026-10-04)
- "five contract tests" — daml test: 5 test_* named tests ok (setup + 2 probes
  excluded from the spoken count)
- "one signature with a valid reason is still rejected" — demo check #5 +
  test_issuer_cannot_release_alone
- No claim about DevNet/mainnet (local stack, and the video says Canton
  generally — B7 card shows the repo, README states local sandbox)
