"""Assemble script_images/*.png into a timed video synced to the audio file in this folder.
Self-detecting: finds the images, finds the audio (longest audio file in this folder), renders to output/.
Run: python build_video.py
"""
import os, re, glob, subprocess
import imageio_ffmpeg

HERE   = os.path.dirname(os.path.abspath(__file__))
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
IMG_DIR = os.path.join(HERE, "script_images")
OUTDIR  = os.path.join(HERE, "output")
os.makedirs(OUTDIR, exist_ok=True)

def duration(path):
    p = subprocess.run([FFMPEG, "-i", path], capture_output=True, text=True)
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", p.stderr)
    if not m: return None
    h, mn, s = m.groups()
    return int(h)*3600 + int(mn)*60 + float(s)

# --- find the audio file (longest of any common audio type in this folder)
AUDIO_EXTS = ("*.m4a","*.mp3","*.wav","*.aac","*.m4b","*.flac","*.ogg")
cands = []
for ext in AUDIO_EXTS:
    cands += glob.glob(os.path.join(HERE, ext))
cands = [c for c in cands if duration(c)]
if not cands:
    raise SystemExit("No audio file found in this folder.")
AUDIO = max(cands, key=lambda c: duration(c))
dur = duration(AUDIO)
print(f"Audio: {os.path.basename(AUDIO)}  ({round(dur/60,2)} min)")

# --- collect images + timestamps from filenames like 0000_0-00.png / 1125_11-25.png
items = []
for fn in os.listdir(IMG_DIR):
    m = re.search(r'_(\d+)-(\d+)\.png$', fn)
    if m:
        items.append((int(m.group(1))*60 + int(m.group(2)), os.path.join(IMG_DIR, fn)))
items.sort()
print(f"Images: {len(items)}")
if not items:
    raise SystemExit("No images found in script_images/.")

# --- concat list with per-image durations (last image runs to end of audio; repeat last entry)
concat_path = os.path.join(OUTDIR, "concat.txt")
with open(concat_path, "w", encoding="utf-8") as f:
    for i, (secs, path) in enumerate(items):
        end = items[i+1][0] if i+1 < len(items) else dur
        f.write(f"file '{path.replace(chr(92), '/')}'\n")
        f.write(f"duration {max(0.1, end-secs):.3f}\n")
    f.write(f"file '{items[-1][1].replace(chr(92), '/')}'\n")

VF = ("scale=1920:1080:force_original_aspect_ratio=decrease,"
      "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:white,format=yuv420p")
silent = os.path.join(OUTDIR, "slideshow_visuals_silent.mp4")
final  = os.path.join(OUTDIR, "final_video_with_audio.mp4")

# CFR conversion on the OUTPUT side (-fps_mode cfr -r 30) — NOT fps=30 in the filter (drops first frame)
print("Rendering silent visuals...")
r1 = subprocess.run([FFMPEG,"-y","-f","concat","-safe","0","-i",concat_path,
        "-vf",VF,"-fps_mode","cfr","-r","30","-c:v","libx264","-preset","medium","-crf","20",silent],
        capture_output=True, text=True)
print("  silent ok" if r1.returncode==0 else "  SILENT FAIL\n"+r1.stderr[-1500:])

print("Rendering final video with audio...")
r2 = subprocess.run([FFMPEG,"-y","-f","concat","-safe","0","-i",concat_path,"-i",AUDIO,
        "-vf",VF,"-fps_mode","cfr","-r","30","-c:v","libx264","-preset","medium","-crf","20",
        "-c:a","aac","-b:a","192k","-map","0:v","-map","1:a","-shortest",final],
        capture_output=True, text=True)
print("  final ok" if r2.returncode==0 else "  FINAL FAIL\n"+r2.stderr[-1500:])

for p in (silent, final):
    if os.path.exists(p):
        print(f"  {os.path.basename(p)}: {os.path.getsize(p)//1024} KB")
