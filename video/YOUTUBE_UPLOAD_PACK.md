# YouTube upload pack — Provenance demo

Video file: `/root/provenance/video/out/Provenance_DEMO_share.mp4`
(2.6 MB · 99.6s · 1920×1080 · H.264/AAC — under every platform limit)
Channel: @web3alphatester

---

## Title (pick one — all under 100 chars)

1. `Provenance — a Canton ledger that refuses an invented cause`
2. `Watch a ledger reject a fabricated reason (Canton / Daml)`
3. `Payment holds where "we won't invent a cause" is enforced by the ledger`

Recommended: **#2** — it names the single most memorable moment, and "watch X
refuse Y" is a curiosity gap that earns the click without overclaiming.

## Description (paste verbatim)

```
Provenance puts payment holds on Canton, where "we will not invent a cause" is
a contract invariant — not a promise a server keeps.

When a payment rail freezes your money it tells you THAT, never WHY. Tools that
"explain" holds invent causes their data never established, and a confident
wrong answer sends someone to the wrong remedy. Provenance refuses to: a held
payment has no reason field to fabricate into, and a made-up cause is a
rejected transaction.

In this demo (real clicks against a live local Canton stack — no simulation, no
mock ledger):
• 0:29  A held payment carries no reason field — there is nothing to invent into
• 0:41  THE MOMENT — I ask the ledger to release with an invented (empty) cause
        and the platform itself refuses: FAILED_PRECONDITION, AssertionFailed
• 1:05  An honest release (both parties) records the established cause and
        writes the on-ledger audit trail
• 1:17  The auditor reads the whole trail without signing; a stranger sees nothing

(The one-signature rejection — a valid cause from the issuer alone is also
refused — is proven in the eval suite and pinned by test_issuer_cannot_release_alone,
rather than shown on camera.)

Every number quoted is eval output, not a claim:
  11 live demo checks · 5 contract tests · 13 AI-screen checks · 7 MCP agent evals
  all passing, all reproducible with ./proof.sh

The AI layer answers from contract state only and is re-screened: any answer
asserting a cause the ledger didn't establish is discarded. Agents get no
exemption — the MCP server is driven by a real client in the eval, and an
agent's fabricated cause is rejected exactly like a human's.

Source (MIT): https://github.com/HusseinAdeiza/provenance
Product site:  https://husseinadeiza.github.io/provenance-site/

Built for HackCanton Season 4 (Track 1 — RWA & Business Workflows) on a local
Canton sandbox, SDK 2.10.6. Not affiliated with Digital Asset or Canton Network.
A pre-window research probe is disclosed in the README; all implementation is
in-window.

Timestamps
0:00  The problem: frozen money, no stated cause
0:11  One ledger, three worlds (issuer / holder / auditor)
0:29  A held payment has no reason field
0:41  THE MOMENT — the ledger rejects a fabricated cause
1:05  An honest, dual-signed release writes the audit trail
1:17  Auditor reads the trail; stranger sees nothing
1:31  Proof: every figure is eval output
```

## Tags

```
Canton Network, Daml, smart contracts, blockchain privacy, HackCanton, RWA,
payment holds, PayPal hold, webhook, ledger, multi-party, zero knowledge,
developer demo, AI agent, MCP, fintech
```

## Thumbnail

Use `video/cards/close.png` (has the wordmark + 11/11·5/5·7/7 stats) OR the
fabrication-rejection frame at 0:44 of the video (the red REJECTED log line is
the strongest hook). 1280×720 for YouTube — I can render a dedicated one.

## AI disclosure (YouTube's synthetic-media prompt)

Select based on the actual wording of the categories shown. This video is a
**real screen recording of a real working system** — the ledger responses are
genuine. The narration is TTS. If the prompt asks specifically about
"realistic-looking scenes that didn't happen" or "altered footage of real
events," the honest answer is **No** — nothing is depicted that did not occur.
If it asks "was AI used to generate any part," the narration is synthetic voice,
so answer per the exact category shown (read the on-screen wording before
selecting — the categories are specific, per the video skill).

---

## After upload

1. Send me the watch URL — I'll verify visibility via oEmbed and add it to the
   Devpost/hackathon submission's video field and the README.
2. If YouTube holds it for a content check, that's normal for a fresh upload;
   visibility flips once it clears.
