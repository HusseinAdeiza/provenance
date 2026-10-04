#!/usr/bin/env bash
# assemble.sh — build Provenance_DEMO.mp4 from the verified take + VO + cards.
# Beat windows verified by vision on real frames (see BUILD_LOG): REJECTED line
# visible ~52s, ACCEPTED + audit trail ~68s in /tmp/prov_take.mp4.
# Rule: each video slot >= its measured VO (b1 10.1 b2 14.5 b3 9.4 b4 13.9
# b5 11.7 b6 13.1 b7 8.8); if VO overruns, tpad holds the last frame.
set -euo pipefail
cd "$(dirname "$0")"
FF=/root/.hermes/tools/ffmpeg-9.0.1-linux-x64/bin/ffmpeg
TAKE=/tmp/prov_take.mp4
[ -f "$TAKE" ] || { echo "no take at $TAKE — run take.sh first"; exit 1; }
mkdir -p beats out

# ── video beats from the take (absolute windows, verified) ────────────────
#        beat  start  dur
cut() { $FF -hide_banner -loglevel error -y -ss "$2" -t "$3" -i "$TAKE" -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p -an "beats/$1.mp4"; }

$FF -hide_banner -loglevel error -y -loop 1 -t 11 -i cards/title.png -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p beats/b1.mp4
cut b2  6 18          # pane sweep across issuer/holder/auditor
cut b3 24 12          # hover the held card's "no reason field" line
cut b4 38 24          # fabrication click -> red REJECTED, cursor traces the log
cut b5 62 12          # honest release -> green cause established
cut b6 74 11          # auditor trail rows + stranger 0-contracts line
$FF -hide_banner -loglevel error -y -loop 1 -t 10 -i cards/close.png -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p beats/b7.mp4

# ── pad each beat so video >= VO (+0.4s breath), never cut a word ─────────
python3 - <<'PY'
import subprocess, re, os
FF="/root/.hermes/tools/ffmpeg-9.0.1-linux-x64/bin/ffmpeg"
def dur(p):
    o=subprocess.run([FF,"-i",p],capture_output=True,text=True).stderr
    m=re.search(r"Duration: (\d+):(\d+):([\d.]+)",o)
    if not m: raise SystemExit(f"no duration for {p}: {o[-200:]}")
    return int(m.group(1))*3600+int(m.group(2))*60+float(m.group(3))
for i in range(1,8):
    b=f"beats/b{i}.mp4"; a=f"vo/b{i}.ogg"
    vs, as_ = dur(b), dur(a)
    need = max(0.0, as_ + 0.4 - vs)
    if need > 0.05:
        subprocess.run([FF,"-hide_banner","-loglevel","error","-y","-i",b,
                        "-vf",f"tpad=stop_mode=clone:stop_duration={need}",
                        "-c:v","libx264","-preset","veryfast","-crf","18",
                        "-pix_fmt","yuv420p",b+".tmp.mp4"],check=True)
        os.replace(b+".tmp.mp4", b)
        print(f"  b{i}: padded +{need:.2f}s (video {vs:.2f} < audio {as_:.2f})")
    else:
        print(f"  b{i}: fits (video {vs:.2f} >= audio {as_:.2f})")
PY

# ── concat video ───────────────────────────────────────────────────────────
: > beats/list.txt
for i in 1 2 3 4 5 6 7; do echo "file 'b$i.mp4'" >> beats/list.txt; done
$FF -hide_banner -loglevel error -y -f concat -safe 0 -i beats/list.txt -c copy out/video_only.mp4

# ── audio: VO beats back-to-back, aligned to each video beat's start ──────
# compute per-beat start offsets from the padded durations
python3 - <<'PY' > beats/audiomap.txt
import subprocess, re
FF="/root/.hermes/tools/ffmpeg-9.0.1-linux-x64/bin/ffmpeg"
def dur(p):
    o=subprocess.run([FF,"-i",p],capture_output=True,text=True).stderr
    m=re.search(r"Duration: (\d+):(\d+):([\d.]+)",o)
    h,mi,s=int(m.group(1)),int(m.group(2)),float(m.group(3))
    return h*3600+mi*60+s
t=0.0
for i in range(1,8):
    print(f"{i} {t:.3f}")
    t+=dur(f"beats/b{i}.mp4")
print(f"total {t:.3f}")
PY
cat beats/audiomap.txt

# build the mixed track with adelay per beat (0.2s in-beat offset for breath)
FILTERS=""; INPUTS=""; N=0
while read -r idx off; do
  [ "$idx" = "total" ] && continue
  INPUTS="$INPUTS -i vo/b$idx.ogg"
  ms=$(python3 -c "print(int(($off+0.2)*1000))")
  FILTERS="$FILTERS[$N:a]adelay=$ms|$ms[a$N];"
  N=$((N+1))
done < beats/audiomap.txt
MIXIN=""
for k in $(seq 0 $((N-1))); do MIXIN="$MIXIN[a$k]"; done
FILTERS="${FILTERS}${MIXIN}amix=inputs=$N:duration=longest:normalize=0[aout]"
$FF -hide_banner -loglevel error -y $INPUTS -filter_complex "$FILTERS" -map "[aout]" -c:a aac -b:a 160k beats/vo_mix.m4a

# ── mux ────────────────────────────────────────────────────────────────────
$FF -hide_banner -loglevel error -y -i out/video_only.mp4 -i beats/vo_mix.m4a \
  -c:v copy -c:a aac -b:a 160k -shortest -movflags +faststart out/Provenance_DEMO.mp4

$FF -i out/Provenance_DEMO.mp4 2>&1 | grep -E "Duration|Stream"
ls -la out/Provenance_DEMO.mp4
