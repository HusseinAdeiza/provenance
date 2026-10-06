# Provenance - Pitch Deck

## Slide 1: Title
**Provenance**
*Payment holds where the ledger refuses an invented cause*
HackCanton Season 4 • Track 1: RWA & Business Workflows
─────────────────────────

## Slide 2: The Problem
**When payment rails freeze funds, they say "ON HOLD" but not WHY.**

This creates dangerous ambiguity where recipients must guess and often make costly mistakes.

**Real impacts from 4 interviews (Oct 2026):**
• Freelancer: $850 held 9 days → split to dodge → account flagged, timeline reset
• Agency: $2,400 held 14 days → paid from savings → double-paid when batch cleared  
• Engineer: $4,200 held 6 days → webhook returned `reason:null` → all API keys revoked
• Contractor: $1,650 held 8 days → opened tickets → lost queue position

**Support round-trips: 18 hours to 5 days**

─────────────────────────
## Slide 3: The Solution

**Provenance = Canton Ledger enforcing honesty**

**Key Features:**
• No "reason" field to fabricate
• Release requires BOTH parties' signatures
• Auditor can verify without seeing private data  
• Stranger sees NOTHING

**Enforced by the ledger, not application code.**

─────────────────────────
## Slide 4: Demo

**Three-pane UI (Issuer / Holder / Auditor)**

**Actions Verified:**
• ✓ Fabricated cause → REJECTED
• ✓ One-signature release → REJECTED  
• ✓ Stranger visibility → 0 contracts
• ✓ Auditor access → Full trail

Live at: https://provenance-demo.onrender.com

─────────────────────────
## Slide 5: Why Canton?

**Traditional apps promise, Canton enforces**

**Advantages:**
• True invariant enforcement (cryptographic)
• Observer privacy with auditability
• Multi-party coordination

**Technical Stack:**
• Daml SDK 2.10.6
• Canton sandbox (local)
• Python 3 + Flask UI
• MCP server for AI agents

─────────────────────────
## Slide 6: Validation

**All systems passing:**
• 11/11 live demo checks ✓
• 5/5 contract tests ✓
• 13/13 AI screen checks ✓
• 7/7 MCP agent checks ✓

**Open Source:**
• MIT License
• https://github.com/HusseinAdeiza/provenance
• YouTube: https://youtu.be/_dGeWs6aE_o

─────────────────────────
## Slide 7: What's Next

**Immediate:**
• Get agency pilot
• Add wallet integration

**Long-term:**
• Production DevNet deployment  
• Marketplace integration
• Compliance automation

─────────────────────────
