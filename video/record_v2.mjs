/**
 * record_v2.mjs — product-act captures for demo v2.
 *
 * Two takes, slower and roomier than v1 (v1 was cramped and the log line was
 * hard to read at speed). Assembly zooms into the log for the callout.
 *
 *   take A (~38s): fabrication click → red REJECTED line, long dwells
 *   take B (~30s): honest release (both parties) → green cause + trail row
 *
 * Same guard discipline as v1: refuse to record unless the live UI is the
 * corrected build and a held contract exists to act on.
 */
import { chromium } from 'playwright'
import { writeFileSync } from 'fs'

const URL = process.env.URL || 'http://127.0.0.1:8090/'
const W = 1920, H = 1080
const sleep = ms => new Promise(r => setTimeout(r, ms))
const TAKE = process.argv[2] || 'A'

const browser = await chromium.launch({
  headless: false,
  executablePath: process.env.CHROME || undefined,
  args: ['--no-sandbox', '--window-size=1920,1080', '--start-maximized',
         '--force-device-scale-factor=1', '--hide-scrollbars']
})
const ctx = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: 1 })
const page = await ctx.newPage()
page.on('dialog', async d => d.accept('Address mismatch verified by both parties'))

await page.goto(URL, { waitUntil: 'networkidle' })
await sleep(1500)

const state = await page.evaluate(async () => {
  const t = document.body.innerText
  const st = await (await fetch('/api/state')).json()
  return {
    correctTitle: t.includes('one ledger, three worlds'),
    noReasonField: t.includes('no reason field'),
    strangerZero: st.strangerVisibleHolds === 0,
    hasHeld: st.views.Issuer.some(c => c.template === 'HeldPayment'),
  }
})
console.log('guard:', JSON.stringify(state))
if (!state.correctTitle || !state.noReasonField || !state.strangerZero || !state.hasHeld) {
  console.error('ABORT: guard failed')
  await browser.close(); process.exit(1)
}

writeFileSync('/tmp/prov_v2_ready_' + TAKE, String(Date.now()))

if (TAKE === 'A') {
  // ── take A: the fabrication moment ────────────────────────────────────
  // Long settle FIRST: the assembled video opens this beat with the VO
  // "This is Provenance... three roles, one ledger" over the pristine UI, and
  // the click must land when the VO says "watch what happens" (~19s into the
  // beat). An 8s hold before the cursor even moves puts the click at ~25s of
  // recording time, so a clip starting at 6s aligns it with the cue.
  await sleep(2500)                                   // page settle
  await sleep(8000)                                   // pristine-UI hold for the VO intro
  // slow approach to the red button
  const fab = page.locator('#btn-fabricate')
  const fb = await fab.boundingBox()
  await page.mouse.move(400, 300, { steps: 20 }); await sleep(800)
  await page.mouse.move(fb.x + fb.width / 2, fb.y + fb.height / 2, { steps: 25 })
  await sleep(1800)                                   // hover beat
  await fab.click()
  await sleep(2800)                                   // rejection lands
  // Bring the log to CENTRE and HOLD it there for the whole payoff. Earlier
  // this beat scrolled back to top at the end, so the red REJECTED line — the
  // single most important frame in the video — was on screen for only ~4s and
  // then gone. Now it dominates the frame for ~20s so assembly can place it
  // exactly under the VO "the platform refuses."
  await page.evaluate(() => document.querySelector('#ledgerlog').scrollIntoView({ block: 'center' }))
  await sleep(1000)
  let lb = await page.locator('#ledgerlog').boundingBox()
  await page.mouse.move(lb.x + 380, lb.y + 40, { steps: 18 })
  await sleep(6000)
  await page.mouse.move(lb.x + 900, lb.y + 62, { steps: 20 })
  await sleep(6000)
  await page.mouse.move(lb.x + 640, lb.y + 50, { steps: 14 })
  await sleep(6000)
  // (no scroll back to top — hold the rejection as the beat's final image)
} else {
  // ── take B: honest release + trail ────────────────────────────────────
  await sleep(2000)
  const rel = page.locator('#btn-release-honest')
  const rb = await rel.boundingBox()
  await page.mouse.move(400, 300, { steps: 18 }); await sleep(600)
  await page.mouse.move(rb.x + rb.width / 2, rb.y + rb.height / 2, { steps: 22 })
  await sleep(1600)
  await rel.click()                                   // dialog auto-accepts
  await sleep(2800)
  // dwell on the released card + its green cause line
  const relCard = page.locator('#v-issuer .card.released').first()
  await relCard.evaluate(el => el.scrollIntoView({ block: 'center' }))
  await sleep(900)
  const rc = await relCard.locator('.cause').first().boundingBox()
  await page.mouse.move(rc.x + rc.width / 2, rc.y + rc.height / 2, { steps: 20 })
  await sleep(4200)
  // pan to the auditor pane's trail
  const th = page.locator('#v-auditor .trail-head').first()
  await th.evaluate(el => el.scrollIntoView({ block: 'center' }))
  await sleep(800)
  let tb = await th.boundingBox()
  await page.mouse.move(tb.x + 140, tb.y + 8, { steps: 18 })
  await sleep(3000)
  const rows = page.locator('#v-auditor .trail-row')
  const n = Math.min(await rows.count(), 3)
  for (let i = 0; i < n; i++) {
    const b = await rows.nth(i).boundingBox()
    await page.mouse.move(b.x + 220, b.y + b.height / 2, { steps: 10 })
    await sleep(1400)
  }
  // end on the stranger line
  const stranger = page.locator('.stranger')
  await stranger.evaluate(el => el.scrollIntoView({ block: 'center' }))
  await sleep(700)
  const sb = await stranger.boundingBox()
  await page.mouse.move(sb.x + 220, sb.y + sb.height / 2, { steps: 16 })
  await sleep(4000)
}

await sleep(1500)
writeFileSync('/tmp/prov_v2_done_' + TAKE, String(Date.now()))
console.log('take ' + TAKE + ' complete')
await ctx.close()
await browser.close()
