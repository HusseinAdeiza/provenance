#!/usr/bin/env python3
"""frames_v2.py — designed motion-graphics frames for demo v2 (sample style).

Dark cinematic ground, one amber accent, big white sans, serif italic only for
the quote. Every text element is drawn from the interview record — verbatim.
No invented details (the persona card carries no age because none was stated).
"""
from PIL import Image, ImageDraw, ImageFont
import glob, os

W, H = 1920, 1080
BG = (8, 10, 13)          # near-black, slightly cool like the sample grade
INK = (244, 242, 237)
DIM = (154, 150, 140)
DIMMER = (110, 106, 98)
AMBER = (240, 169, 59)
RED = (255, 107, 107)
GREEN = (95, 211, 164)

def font(sz, kind="sans", bold=False):
    if kind == "serif":
        pats = ["/usr/share/fonts/truetype/dejavu/DejaVuSerif%s.ttf" % ("-Bold" if bold else ""),
                "/usr/share/fonts/truetype/liberation/LiberationSerif-%s.ttf" % ("Bold" if bold else "Regular")]
    elif kind == "mono":
        pats = ["/usr/share/fonts/truetype/dejavu/DejaVuSansMono%s.ttf" % ("-Bold" if bold else ""),
                "/usr/share/fonts/truetype/liberation/LiberationMono-%s.ttf" % ("Bold" if bold else "Regular")]
    else:
        pats = ["/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else ""),
                "/usr/share/fonts/truetype/liberation/LiberationSans-%s.ttf" % ("Bold" if bold else "Regular")]
    for p in pats:
        g = glob.glob(p)
        if g: return ImageFont.truetype(g[0], sz)
    return ImageFont.load_default()

def base():
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    # subtle vignette via corner darkening (cheap, cinematic)
    return im, d

def save(im, name):
    os.makedirs("cards2", exist_ok=True)
    im.save(f"cards2/{name}.png")
    print(f"  {name}.png")

def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

# ── B1: persona name card (sample's "Maya. 23." pattern, no invented age) ──
im, d = base()
d.rectangle([0, 0, W, 5], fill=AMBER)
f_big = font(150, bold=True)
d.text((160, 330), "Nuhu.", font=f_big, fill=INK)
f_sub = font(44)
d.text((166, 520), "Freelance 3D artist  ·  Okene, Nigeria", font=f_sub, fill=DIM)
f_small = font(30)
d.text((166, 600), "$850 withdrawn from Upwork  ·  usually clears in 4 hours", font=f_small, fill=DIMMER)
# reconstruction label — honest staging disclosure
f_lab = font(24, "mono")
d.text((166, 980), "RECONSTRUCTION FROM A REAL INTERVIEW · OCT 2026", font=f_lab, fill=DIMMER)
save(im, "b1_persona")

# ── B2: the notification artefact + timeline ──────────────────────────────
im, d = base()
f_head = font(34, "mono")
d.text((160, 90), "THE NOTIFICATION — VERBATIM", font=f_head, fill=AMBER)
# artefact card
card = [160, 160, 1760, 560]
d.rounded_rectangle(card, radius=14, fill=(16, 18, 22), outline=(45, 48, 56), width=2)
d.rectangle([card[0], card[1], card[0]+8, card[3]], fill=AMBER)
f_quote = font(52, "serif")
lines = wrap(d, "“Your withdrawal is pending review. This process can take up to 2-3 business days. No further action is required from you at this time.”", f_quote, 1440)
y = 220
for ln in lines:
    d.text((230, y), ln, font=f_quote, fill=INK)
    y += 74
f_attrib = font(30, "mono")
d.text((230, y+20), "— Payoneer, on an $850 payout", font=f_attrib, fill=DIM)
# timeline
f_t = font(30, "mono")
d.text((160, 650), "WHAT FOLLOWED", font=f_t, fill=DIM)
bar_y = 730
d.rounded_rectangle([160, bar_y, 1760, bar_y+26], radius=13, fill=(30, 33, 40))
d.rounded_rectangle([160, bar_y, 1760, bar_y+26], radius=13, outline=(60, 64, 74), width=1)
marks = [(0.0, "0h", "cleared? no"), (38/216, "38h", "automated reply"), (120/216, "5 days", "a human replies"), (1.0, "9 days", "money finally moves")]
for frac, lab, sub in marks:
    x = int(160 + frac * 1600)
    d.ellipse([x-9, bar_y+4, x+9, bar_y+22], fill=AMBER)
    d.text((x-40, bar_y-52), lab, font=font(28, "mono", True), fill=INK)
    d.text((x-90, bar_y+44), sub, font=font(24), fill=DIMMER)
d.text((160, 880), "no reason given at any point", font=font(36, bold=True), fill=RED)
save(im, "b2_notification")

# ── B3: the wrong move ────────────────────────────────────────────────────
im, d = base()
d.text((160, 110), "THE WRONG MOVE", font=font(34, "mono"), fill=AMBER)
f_amt = font(120, bold=True)
d.text((300, 240), "$850", font=f_amt, fill=INK)
d.line([(560, 330), (760, 250)], fill=DIMMER, width=4)
d.line([(560, 330), (760, 420)], fill=DIMMER, width=4)
d.text((800, 190), "$400", font=font(84, bold=True), fill=DIM)
d.text((800, 370), "$450", font=font(84, bold=True), fill=DIM)
d.text((800, 500), "“smaller amounts will pass”", font=font(34, "serif"), fill=DIMMER)
# red stamp
stamp = [300, 620, 1620, 800]
d.rounded_rectangle(stamp, radius=10, fill=(40, 16, 16), outline=RED, width=4)
f_stamp = font(56, bold=True)
d.text((350, 665), "ACCOUNT FLAGGED · REVIEW CLOCK RESET", font=f_stamp, fill=RED)
d.text((160, 870), "cancelling an in-flight review reads as account takeover", font=font(34), fill=DIM)
d.text((160, 930), "9 days frozen · ₦30,000 rent penalty · $35 in fees", font=font(34, bold=True), fill=INK)
save(im, "b3_wrongmove")

# ── B4: the quote (serif, alone, sample's quietest moment) ────────────────
im, d = base()
f_q = font(64, "serif")
qt = "“You are sitting in a dark room. You don’t know whether to keep quiet — or start panicking.”"
lines = wrap(d, qt, f_q, 1500)
y = (H - len(lines)*90) // 2 - 60
for ln in lines:
    w = d.textlength(ln, font=f_q)
    d.text(((W-w)/2, y), ln, font=f_q, fill=INK)
    y += 90
f_att = font(30, "mono")
att = "— NUHU, ON DAY FIVE"
w = d.textlength(att, font=f_att)
d.text(((W-w)/2, y+30), att, font=f_att, fill=DIM)
save(im, "b4_quote")

# ── B4b: the pivot ────────────────────────────────────────────────────────
im, d = base()
d.rectangle([0, 0, W, 5], fill=AMBER)
f_p = font(76, bold=True)
l1 = "What if the system could not"
l2 = "invent a reason?"
w1, w2 = d.textlength(l1, font=f_p), d.textlength(l2, font=f_p)
d.text(((W-w1)/2, 360), l1, font=f_p, fill=INK)
d.text(((W-w2)/2, 460), l2, font=f_p, fill=AMBER)
f_s = font(40, "serif")
l3 = "Not because it promised. Because the ledger refused."
w3 = d.textlength(l3, font=f_s)
d.text(((W-w3)/2, 640), l3, font=f_s, fill=DIM)
save(im, "b4b_pivot")

# ── B6b: Usman flash card (second interview, mid-video proof of scale) ────
im, d = base()
d.text((160, 110), "IT IS NOT ONLY FREELANCERS", font=font(34, "mono"), fill=AMBER)
f_u = font(64, bold=True)
d.text((160, 220), "An agency owner. $2,400 for 6 contractors.", font=f_u, fill=INK)
d.text((160, 310), "14 days at “PENDING COMPLIANCE CLEARANCE”.", font=font(64, bold=True), fill=INK)
d.text((160, 440), "She paid three of them from personal savings.", font=font(44), fill=DIM)
d.text((160, 510), "The batch cleared anyway. They were paid twice.", font=font(44), fill=DIM)
d.text((160, 580), "Three months to recover the money. One resignation.", font=font(44), fill=DIM)
f_uq = font(46, "serif")
qlines = wrap(d, "“The worst thing about managing a team is having to say ‘I don’t know where the money is’ when the dashboard just writes one cold word: PENDING.”", f_uq, 1500)
y = 700
for ln in qlines:
    d.text((200, y), ln, font=f_uq, fill=INK)
    y += 66
d.text((200, y+10), "— USMAN, AGENCY MD, ABUJA · REAL INTERVIEW", font=font(26, "mono"), fill=DIMMER)
save(im, "b6_usman")

# ── B7: close card ────────────────────────────────────────────────────────
im, d = base()
d.rectangle([0, H-6, W, H], fill=AMBER)
f_c = font(96, bold=True)
t = "PROVENANCE"
d.text(((W-d.textlength(t, font=f_c))/2, 240), t, font=f_c, fill=INK)
f_tag = font(44, "serif")
t2 = "the honesty rule the ledger refuses to break"
d.text(((W-d.textlength(t2, font=f_tag))/2, 380), t2, font=f_tag, fill=AMBER)
stats = [("11", "live checks"), ("5", "contract tests"), ("13", "AI-screen checks"), ("7", "agent evals")]
xs = [W//8 + i*(W//4) for i in range(4)]
for (n, lbl), x in zip(stats, xs):
    d.rounded_rectangle([x-150, 540, x+150, 720], radius=14, fill=(16, 18, 22), outline=(45,48,56), width=2)
    f_n = font(72, bold=True)
    d.text((x-d.textlength(n, font=f_n)/2, 565), n, font=f_n, fill=GREEN)
    f_l = font(24)
    d.text((x-d.textlength(lbl, font=f_l)/2, 668), lbl, font=f_l, fill=DIM)
f_r = font(32, "mono")
for i, u in enumerate(["github.com/HusseinAdeiza/provenance", "husseinadeiza.github.io/provenance-site"]):
    d.text(((W-d.textlength(u, font=f_r))/2, 800+i*52), u, font=f_r, fill=DIM)
save(im, "b7_close")
print("all frames written")
