/**
 * record_provenance.mjs — records the Provenance demo against the LIVE local
 * stack (http://127.0.0.1:8090) with a real headed browser on Xvfb, captured
 * by ffmpeg x11grab running alongside (sharp text, per the capture skill).
 *
 * RECORDER GUARD: refuses to record unless the UI is the corrected build —
 * the HoldWatch lesson: a stale product on camera is worse than no video.
 */
import { chromium } from 'playwright'

const URL = process.env.URL || 'http://127.0.0.1:8090/'
const W = 1920, H = 1080
const sleep = ms => new Promise(r => setTimeout(r, ms))

const browser = await chromium.launch({
  headless: false,
  executablePath: process.env.CHROME || undefined,
  args: ['--no-sandbox', '--window-size=1920,1080', '--start-maximized',
         '--force-device-scale-factor=1', '--hide-scrollbars']
})
const ctx = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: 1 })
const page = await ctx.newPage()

page.on('dialog', async d => {
  // the honest-release prompt: supply the established cause
  await d.accept('Address mismatch verified by both parties')
})

await page.goto(URL, { waitUntil: 'networkidle' })
await sleep(1500)

// ── GUARD ────────────────────────────────────────────────────────────────
const state = await page.evaluate(async () => {
  const t = document.body.innerText
  const st = await (await fetch('/api/state')).json()
  return {
    correctTitle: t.includes('one ledger, three worlds'),
    noReasonField: t.includes('no reason field'),
    rolesLoaded: !!(st.views && st.views.Issuer && st.views.Holder && st.views.Auditor),
    strangerZero: st.strangerVisibleHolds === 0,
    hasHeld: st.views.Issuer.some(c => c.template === 'HeldPayment'),
  }
})
console.log('guard:', JSON.stringify(state))
// NOTE: the audit trail is NOT required pre-take — on a fresh ledger it is
// empty until beat B5 performs the release on camera. Requiring it made the
// recorder refuse every clean stack. What MUST hold: correct UI build, roles
// loaded, stranger sees zero, and at least one live hold to act on.
if (!state.correctTitle || !state.noReasonField || !state.rolesLoaded ||
    !state.strangerZero || !state.hasHeld) {
  console.error('ABORT: live UI failed the pre-recording guard.')
  await browser.close(); process.exit(1)
}

// marker file so the ffmpeg wrapper knows the take is live
import { writeFileSync } from 'fs'
writeFileSync('/tmp/prov_rec_ready', String(Date.now()))

// ── beats ────────────────────────────────────────────────────────────────
// B2: sweep the three panes — dwell sized to the MEASURED VO (14.50s)
await sleep(2000)                                  // settle on the loaded panes
await page.mouse.move(300, 480, { steps: 14 }); await sleep(2600)
await page.mouse.move(950, 480, { steps: 14 }); await sleep(2600)
await page.mouse.move(1600, 480, { steps: 14 }); await sleep(3600)
await page.mouse.move(950, 620, { steps: 12 }); await sleep(4400)

// B3: hover the held card's cause-absent line in the issuer pane
const heldCard = page.locator('#v-issuer .card.held').first()
await heldCard.scrollIntoViewIfNeeded()
const causeLine = heldCard.locator('.cause').first()
const cb = await causeLine.boundingBox()
await page.mouse.move(cb.x + cb.width / 2, cb.y + cb.height / 2, { steps: 12 })
await sleep(10000)                                 // VO b3 = 9.41s

// B4: THE MOMENT — fabricate a cause
const fab = page.locator('#btn-fabricate')
const fb = await fab.boundingBox()
await page.mouse.move(fb.x + fb.width / 2, fb.y + fb.height / 2, { steps: 10 })
await sleep(1000)
await fab.click()
await sleep(3600)                       // let the rejection render — VO b4 = 13.88s
const logEl = page.locator('#ledgerlog')
await logEl.scrollIntoViewIfNeeded()
// scrollIntoViewIfNeeded leaves the log as a bottom sliver — the REJECTED line
// is the whole video, so centre it in frame instead
await page.evaluate(() => document.querySelector('#ledgerlog').scrollIntoView({ block: 'center' }))
await sleep(700)
let lb = await logEl.boundingBox()
await page.mouse.move(lb.x + 400, lb.y + 40, { steps: 10 })   // cursor traces the log
await sleep(4200)
lb = await logEl.boundingBox()
await page.mouse.move(lb.x + 700, lb.y + 62, { steps: 8 })
await sleep(4600)

// B5: honest release (both parties) — VO b5 = 11.72s
await page.evaluate(() => window.scrollTo(0, 0))
await sleep(800)
const rel = page.locator('#btn-release-honest')
const rb = await rel.boundingBox()
await page.mouse.move(rb.x + rb.width / 2, rb.y + rb.height / 2, { steps: 10 })
await sleep(800)
await rel.click()                        // dialog auto-accepts the reason
await sleep(3400)
// dwell on the newly released card with its green established cause, CENTRED
const relCard = page.locator('#v-issuer .card.released').first()
await relCard.evaluate(el => el.scrollIntoView({ block: 'center' }))
await sleep(700)
const rc = await relCard.locator('.cause').first().boundingBox()
await page.mouse.move(rc.x + rc.width / 2, rc.y + rc.height / 2, { steps: 10 })
await sleep(6400)

// B6: auditor trail + stranger line
const trailHead = page.locator('#v-auditor .trail-head').first()
await trailHead.evaluate(el => el.scrollIntoView({ block: 'center' }))
await sleep(600)
let tb = await trailHead.boundingBox()
await page.mouse.move(tb.x + 120, tb.y + 8, { steps: 12 })
await sleep(1600)
const rows = page.locator('#v-auditor .trail-row')
const n = await rows.count()
for (let i = 0; i < Math.min(n, 3); i++) {
  const b = await rows.nth(i).boundingBox()
  await page.mouse.move(b.x + 200, b.y + b.height / 2, { steps: 6 })
  await sleep(900)
}
const stranger = page.locator('.stranger')
await stranger.evaluate(el => el.scrollIntoView({ block: 'center' }))
await sleep(500)
const sb = await stranger.boundingBox()
await page.mouse.move(sb.x + 200, sb.y + sb.height / 2, { steps: 10 })
await sleep(4200)

// hold final frame for the close card crossfade
await sleep(2000)

writeFileSync('/tmp/prov_rec_done', String(Date.now()))
console.log('take complete')
await ctx.close()
await browser.close()
