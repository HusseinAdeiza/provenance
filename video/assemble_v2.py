#!/usr/bin/env python3
"""assemble_v2.py — build Provenance_DEMO_v2.mp4 in the sample's style.

Structure (see SCRIPT_V2.md): persona reconstruction in designed motion-graphics
frames (labelled on screen as a reconstruction — no fabricated live-action), then
the REAL product capture for the demo act, then proof close.

Discipline:
- visuals are sized to MEASURED VO durations, never the reverse
- narration is natural pace (Abeo, rate +0%), never sped up
- loudness normalised to ~-16 LUFS (the sample measured ~-18 dB mean; ours was
  -22.6, too quiet)
- every still gets a slow Ken Burns push so nothing looks like a slideshow
"""
import subprocess, os, json, re

FF = "/root/.hermes/tools/ffmpeg-9.0.1-linux-x64/bin/ffmpeg"
HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
W, H, FPS = 1920, 1080, 30

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"FAILED: {cmd[:120]}\n{r.stderr[-600:]}")
    return r

def dur(path):
    o = subprocess.run([FF, "-i", path], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", o)
    return int(m.group(1))*3600 + int(m.group(2))*60 + float(m.group(3))

# ── measured VO durations ──────────────────────────────────────────────────
vo = {f"b{i}": dur(f"vo2/b{i}.mp3") for i in range(1, 8)}
for k, v in vo.items():
    print(f"  {k}: {v:.2f}s")

GAP = 0.8      # breath between beats
LEAD = 0.8     # lead-in before b1
TAIL = 1.6     # hold on close card after b7

# segment video durations = VO + trailing gap (last gets TAIL)
seg = {
    "b1": vo["b1"] + GAP,
    "b2": vo["b2"] + GAP,
    "b3": vo["b3"] + GAP,
    "b4": vo["b4"] + GAP,
    "b5": vo["b5"] + GAP,
    "b6": vo["b6"] + GAP,
    "b7": vo["b7"] + TAIL,
}
total = LEAD + sum(seg.values())
print(f"  total video: {total:.1f}s")

os.makedirs("v2", exist_ok=True)

# ── Ken Burns still segment ────────────────────────────────────────────────
def still_seg(png, out, d, zoom_to=1.14):
    """Slow push-in on a designed frame."""
    frames = int(d * FPS)
    # scale up big so the zoom is smooth, then zoompan pushes in
    vf = (f"scale=3840:2160:flags=lanczos,"
          f"zoompan=z='min(1.0+({zoom_to}-1.0)*on/{frames}, {zoom_to})':"
          f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS}")
    run(f'{FF} -hide_banner -loglevel error -y -loop 1 -i "{png}" -t {d:.3f} '
        f'-vf "{vf}" -c:v libx264 -preset veryfast -crf 17 -pix_fmt yuv420p '
        f'-r {FPS} "{out}"')

# ── product capture segment (trim + normalise, NO artificial zoom) ─────────
def clip_seg(src, out, start, d):
    run(f'{FF} -hide_banner -loglevel error -y -ss {start:.2f} -t {d:.3f} -i "{src}" '
        f'-vf "scale={W}:{H}:flags=lanczos,fps={FPS}" '
        f'-c:v libx264 -preset veryfast -crf 17 -pix_fmt yuv420p -an "{out}"')

print("building segments…")
# B1 persona
still_seg("cards2/b1_persona.png", "v2/s1.mp4", LEAD + seg["b1"] - LEAD, 1.12)
# wait: s1 must include the LEAD (b1 starts after LEAD). Build s1 = LEAD+vo1+gap.
# rebuild with lead baked in:
still_seg("cards2/b1_persona.png", "v2/s1.mp4", LEAD + seg["b1"], 1.12)
# B2 notification artefact
still_seg("cards2/b2_notification.png", "v2/s2.mp4", seg["b2"], 1.10)
# B3 wrong move
still_seg("cards2/b3_wrongmove.png", "v2/s3.mp4", seg["b3"], 1.10)
# B4 quote (first ~47%) then pivot (rest)
q = seg["b4"] * 0.47
still_seg("cards2/b4_quote.png", "v2/s4a.mp4", q, 1.08)
still_seg("cards2/b4b_pivot.png", "v2/s4b.mp4", seg["b4"] - q, 1.12)
# B5 product take A (fabrication → rejection).
# MEASURED on the re-recorded take A: clean UI from t=10s (held card, no reason
# field), cursor+click ~34s, red REJECTED line visible t=37→58s (~21s hold).
# Clip starts at 16.0s so the click lands at segment-rel 18s and the rejection
# at 21s — exactly under the VO "watch what happens…" / "the platform refuses"
# (b5 VO is 28.8s; those words fall at ~19-22s). Verified, not guessed.
clip_seg("/tmp/prov_v2_A.mp4", "v2/s5.mp4", 16.0, seg["b5"])

# B6 product take B (release + trail).
# MEASURED on take B: held card 10-21s, GREEN RELEASED card 22-31s, audit-trail
# rows from 32s. Start at 21 so the released card (rel 1s) lands on the VO "a
# cause enters the record only when both sides sign it" (~0-4s) and the trail
# (rel ~11s) lands on "every step writes an audit trail" (~6.5-12s). The held
# card is already shown at length in take A, so we don't spend b6 time on it.
# Usman second-interview card carries "one agency owner we interviewed…" (last
# ~9.5s of the 24.4s beat).
b6_clip = seg["b6"] * 0.62
clip_seg("/tmp/prov_v2_B.mp4", "v2/s6a.mp4", 21.0, b6_clip)
still_seg("cards2/b6_usman.png", "v2/s6b.mp4", seg["b6"] - b6_clip, 1.10)
# B7 close
still_seg("cards2/b7_close.png", "v2/s7.mp4", seg["b7"], 1.10)

print("  segments built")
for f in sorted(os.listdir("v2")):
    if f.endswith(".mp4"):
        print(f"    {f}: {dur('v2/'+f):.2f}s")
