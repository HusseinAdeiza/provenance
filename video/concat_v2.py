#!/usr/bin/env python3
"""concat_v2.py — join segments, build the VO track with real gaps, normalise, mux."""
import subprocess, os, re

FF = "/root/.hermes/tools/ffmpeg-9.0.1-linux-x64/bin/ffmpeg"
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode != 0: raise RuntimeError(f"FAILED {cmd[:100]}\n{r.stderr[-500:]}")
    return r

def dur(p):
    o = subprocess.run([FF,"-i",p],capture_output=True,text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", o)
    return int(m.group(1))*3600+int(m.group(2))*60+float(m.group(3))

# ── concat video segments in order ───────────────────────────────────────
order = ["s1","s2","s3","s4a","s4b","s5","s6a","s6b","s7"]
with open("v2/list.txt","w") as f:
    for s in order: f.write(f"file '{s}.mp4'\n")
run(f'{FF} -hide_banner -loglevel error -y -f concat -safe 0 -i v2/list.txt '
    f'-c copy v2/video_only.mp4')
vid_dur = dur("v2/video_only.mp4")
print(f"video: {vid_dur:.2f}s")

# ── VO track: each beat offset to its segment start + small lead-in ───────
# segment video durations (measured) -> cumulative starts
seg_dur = {s: dur(f"v2/{s}.mp4") for s in order}
LEAD = 0.8
starts, t = {}, LEAD
# map beat -> which segment(s) carry it
beat_seg = {"b1":["s1"],"b2":["s2"],"b3":["s3"],"b4":["s4a","s4b"],
            "b5":["s5"],"b6":["s6a","s6b"],"b7":["s7"]}
for beat, segs in beat_seg.items():
    starts[beat] = t
    t += sum(seg_dur[s] for s in segs)
print("beat starts:", {k: round(v,2) for k,v in starts.items()})

inputs, filt, n = "", "", 0
for beat in ["b1","b2","b3","b4","b5","b6","b7"]:
    ms = int(starts[beat]*1000)
    inputs += f' -i vo2/{beat}.mp3'
    filt += f"[{n}:a]adelay={ms}|{ms}[a{n}];"
    n += 1
mix = "".join(f"[a{i}]" for i in range(n))
filt += f"{mix}amix=inputs={n}:duration=longest:normalize=0,aresample=48000[vomix]"
run(f'{FF} -hide_banner -loglevel error -y {inputs} -filter_complex "{filt}" '
    f'-map "[vomix]" -c:a pcm_s16le v2/vo_mix.wav')
print(f"vo mix: {dur('v2/vo_mix.wav'):.2f}s")

# ── normalise loudness to ~-16 LUFS (sample measured louder than our v1) ──
run(f'{FF} -hide_banner -loglevel error -y -i v2/vo_mix.wav '
    f'-af loudnorm=I=-16:TP=-1.5:LRA=11 -c:a pcm_s16le v2/vo_norm.wav')

# ── mux video + normalised VO, cap to video length ───────────────────────
run(f'{FF} -hide_banner -loglevel error -y -i v2/video_only.mp4 -i v2/vo_norm.wav '
    f'-c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart '
    f'out/Provenance_DEMO_v2.mp4')

# ── QC ────────────────────────────────────────────────────────────────────
print("\n═══ final ═══")
o = subprocess.run([FF,"-i","out/Provenance_DEMO_v2.mp4"],capture_output=True,text=True).stderr
for ln in o.splitlines():
    if "Duration" in ln or "Stream" in ln: print(" ", ln.strip())
v = subprocess.run([FF,"-hide_banner","-i","out/Provenance_DEMO_v2.mp4",
                    "-af","volumedetect","-f","null","-"],capture_output=True,text=True).stderr
for ln in v.splitlines():
    if "mean_volume" in ln or "max_volume" in ln: print(" ", ln.strip())
print("  size:", os.path.getsize("out/Provenance_DEMO_v2.mp4")//1024, "KB")
