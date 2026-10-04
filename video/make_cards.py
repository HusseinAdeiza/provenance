#!/usr/bin/env python3
"""Title and close cards for the Provenance demo — same dark palette as the UI,
drawn in code (no AI text generation, per the video skill: brand text must be
verified glyphs)."""
from PIL import Image, ImageDraw, ImageFont
import glob

W, H = 1920, 1080
BG = (10, 26, 32)
PANEL = (15, 35, 43)
INK = (232, 244, 242)
DIM = (157, 184, 189)
TEAL = (42, 200, 160)
AMBER = (232, 179, 75)

def font(sz, bold=False):
    pats = [
        f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-%s.ttf" % ("Bold" if bold else "Regular"),
    ]
    for p in pats:
        g = glob.glob(p)
        if g: return ImageFont.truetype(g[0], sz)
    return ImageFont.load_default()

def center(d, y, text, f, fill):
    w = d.textlength(text, font=f)
    d.text(((W - w) / 2, y), text, font=f, fill=fill)

# ── title card ────────────────────────────────────────────────────────────
im = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(im)
d.rectangle([0, 0, W, 6], fill=TEAL)
center(d, 360, "PROVENANCE", font(96, True), INK)
center(d, 490, "payment holds where the honesty rule is", font(40), DIM)
center(d, 545, "enforced by the ledger", font(40, True), TEAL)
center(d, 680, "Canton · Daml · HackCanton S4", font(28), DIM)
im.save("cards/title.png")

# ── close card ────────────────────────────────────────────────────────────
im = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(im)
d.rectangle([0, H - 6, W, H], fill=TEAL)
center(d, 300, "PROVENANCE", font(76, True), INK)
center(d, 420, "the honesty rule the ledger refuses to break", font(38), TEAL)
# stat row
stats = [("11/11", "live checks"), ("5/5", "contract tests"), ("7/7", "MCP agent evals")]
xs = [W // 6, W // 2, 5 * W // 6]
for (n, lbl), x in zip(stats, xs):
    d.rounded_rectangle([x - 170, 560, x + 170, 700], radius=14, fill=PANEL)
    nw = d.textlength(n, font=font(56, True))
    d.text((x - nw / 2, 580), n, font=font(56, True), fill=AMBER)
    lw = d.textlength(lbl, font=font(24))
    d.text((x - lw / 2, 652), lbl, font=font(24), fill=DIM)
center(d, 780, "github.com/HusseinAdeiza/provenance", font(30), DIM)
im.save("cards/close.png")
print("cards/title.png + cards/close.png written")
