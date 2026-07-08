---
name: youtube-generator
version: 1.0.0
description: |
  Turn a timestamped script into a finished MS Paint stickman explainer video.
  Background agents pre-write one scene prompt per timestamp, images are generated
  via ChatGPT web (Claude-in-Chrome), a vision agent QAs them, and ffmpeg assembles
  a timestamp-synced video with the narration audio. Use for "make a video from
  this script"; /longform gives horizontal 16:9 (YouTube), /shortform gives vertical
  9:16 (Shorts/Reels/TikTok).
compatibility: >
  Needs an agent harness with browser automation (the Claude-in-Chrome extension),
  a shell, and Python 3. Built for Claude Code; other harnesses can run it if they
  expose equivalent browser + shell tools.
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Task
---

# YouTube Generator — script → finished video

Turn the user's timestamped script into a finished video. For EVERY timestamp, generate one image that visually explains the narration at that moment, then assemble all images into a video synced to the audio file in the current folder.

**Orientation.** If invoked by `/longform` use horizontal 16:9 ("horizontal 16:9 wide", render `16:9`, 1920×1080). If invoked by `/shortform` use vertical 9:16 ("vertical 9:16 tall", render `9:16`, 1080×1920). If the user's request says "short"/"vertical"/"reel"/"tiktok" use 9:16; otherwise default to horizontal 16:9.

## Operating rules
- Run autonomously. Don't pause for confirmation, cost, or "should I proceed". The only thing you may ask for is the script itself if it wasn't provided. Then execute every phase and stop with a one-line summary.
- The audio is whatever audio file (.m4a/.mp3/.wav/…) is already in the current folder. Generate images through **ChatGPT web** via the Claude-in-Chrome MCP (not paid image APIs).
- If a step fails, self-recover (retry / regenerate / simplify) and keep going.
- Prerequisites in the user's Chrome profile: logged into ChatGPT; "Ask where to save each file" OFF; automatic multiple downloads allowed for chatgpt.com. If a download silently fails to land on disk, re-pull rather than stalling.

## Style (every image)
Childish MS Paint doodle, plain white background, thick uneven wobbly black outlines drawn badly on purpose, stick figures (round heads, dot eyes, line bodies), flat colors only, no shading/3D/gradients, lots of empty white space, amateur funny "bad" look, occasional red arrows/question marks. Text must be SHORT and spelled correctly. Never realistic/anime/Disney/vector/polished. **Never depict real identifiable people** — use generic stick figures + generic labels.

Per-image prompt = this prefix + the scene (insert the orientation phrase):
`Create an image, <ORIENTATION PHRASE>. A childish MS Paint doodle on a plain white background, thick uneven wobbly black outlines drawn badly on purpose, stick figures with round heads and dot eyes and simple line bodies, flat colors only, no shading, no 3D, lots of empty white space, amateur funny noob style. Any text short and spelled correctly. Scene: <SCENE>`

## Phase 1 — Pre-write scene prompts (3 background agents)
Parse every timestamp. Split into 3 contiguous ranges; spawn 3 background general-purpose agents (one per range). Each writes one short SCENE per timestamp to `prompts_A.txt`/`B`/`C`, format `M:SS :: <scene>`, following the style + no-real-people rules. Start Phase 2 on the earliest timestamps yourself while they run.

## Phase 2 — Generate images (ChatGPT web, 5 parallel tabs)
Connect: `list_connected_browsers` → `select_browser` (auto-pick if one). Create exactly **5 tabs** (a 6th causes renderer freezes). Output to `script_images/`, filenames `MMSS_M-SS.png` (e.g. `0555_5-55.png`).

Per batch of 5 timestamps:
1. `browser_batch` navigate all 5 tabs to `https://chatgpt.com/`; wait 3s.
2. Inject + submit each prompt via JS (works on background tabs): focus `#prompt-textarea`, `document.execCommand('insertText',false,PROMPT)`, then click `[data-testid="send-button"]`. (Do NOT use the computer `type` action — it only hits the foreground tab.)
3. **Wait ~55s** (pulling early grabs a stale/shared image → identical files).
4. Download each in parallel via JS: take the last `img` whose `src` matches `estuary/content`, `fetch(src,{credentials:'include'})` → blob → anchor `download='MMSS_M-SS.png'` → click. **Guard: only save if `blob.type` starts with `image` AND `blob.size > 50000`** (else it's an error blob — retry). The extension blocks returning base64/cookie/query data, so the browser download is the only path to disk.
5. `mv` the 5 files from the Downloads folder into `script_images/`.
6. Global MD5 check over `script_images/`; re-pull any identical-hash files (a tab wasn't finished).

Freeze recovery: if a tab returns `Runtime.evaluate timed out`, close it (`tabs_close_mcp`), recreate a tab, regenerate that frame; simplify the scene if one image keeps freezing.

## Phase 3 — Vision QA (1 background agent)
Spawn a background agent that Reads each PNG and flags blank/broken, wrong-style, off-topic, misspelled, or duplicate frames to a report. Regenerate anything flagged.

## Phase 4 — Assemble the video
If `imageio-ffmpeg` isn't installed: `python -m pip install imageio-ffmpeg`. Write the script below to `build_video.py` in the project folder, then run it with the chosen aspect ratio — `python build_video.py 16:9` or `python build_video.py 9:16`. It auto-detects the images and the audio and writes `output/slideshow_visuals_silent.mp4` and `output/final_video_with_audio.mp4`.

```python
"""Assemble script_images/*.png into a timed video synced to the audio in this folder.
argv[1] aspect: "16:9" (default, 1920x1080) or "9:16" (1080x1920). Run: python build_video.py 16:9
"""
import os, re, glob, subprocess, sys
import imageio_ffmpeg
ASPECT = (sys.argv[1] if len(sys.argv) > 1 else "16:9").replace(" ", "")
W, H = (1080, 1920) if ASPECT == "9:16" else (1920, 1080)
HERE = os.getcwd(); FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
IMG_DIR = os.path.join(HERE, "script_images"); OUTDIR = os.path.join(HERE, "output")
os.makedirs(OUTDIR, exist_ok=True)
def dur(p):
    r = subprocess.run([FFMPEG,"-i",p], capture_output=True, text=True)
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", r.stderr)
    return int(m[1])*3600+int(m[2])*60+float(m[3]) if m else None
cands = [c for ext in ("*.m4a","*.m4b","*.mp3","*.wav","*.aac","*.flac","*.ogg")
         for c in glob.glob(os.path.join(HERE, ext)) if dur(c)]
if not cands: raise SystemExit("No audio file found in this folder.")
AUDIO = max(cands, key=dur); D = dur(AUDIO)
items = sorted((int(m[1])*60+int(m[2]), os.path.join(IMG_DIR, fn))
               for fn in os.listdir(IMG_DIR) for m in [re.search(r'_(\d+)-(\d+)\.png$', fn)] if m)
if not items: raise SystemExit("No images in script_images/.")
cf = os.path.join(OUTDIR, "concat.txt")
with open(cf, "w", encoding="utf-8") as f:
    for i,(s,p) in enumerate(items):
        end = items[i+1][0] if i+1 < len(items) else D
        f.write(f"file '{p.replace(chr(92),'/')}'\nduration {max(0.1,end-s):.3f}\n")
    f.write(f"file '{items[-1][1].replace(chr(92),'/')}'\n")
VF = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:white,format=yuv420p"
base = ["-y","-f","concat","-safe","0","-i",cf]
cfr = ["-vf",VF,"-fps_mode","cfr","-r","30","-c:v","libx264","-preset","medium","-crf","20"]
subprocess.run([FFMPEG,*base,*cfr, os.path.join(OUTDIR,"slideshow_visuals_silent.mp4")])
subprocess.run([FFMPEG,*base,"-i",AUDIO,*cfr,"-c:a","aac","-b:a","192k",
                "-map","0:v","-map","1:a","-shortest", os.path.join(OUTDIR,"final_video_with_audio.mp4")])
print("done ->", OUTDIR)
```

The two gotchas are already encoded: repeat the last concat entry, and do the frame-rate conversion on the OUTPUT side (`-fps_mode cfr -r 30`) — never `fps=30` in the filter, which drops the first frame.
Verify: extract frames at ~1s, a mid timestamp, and the last second; confirm each matches the expected image and total duration ≈ audio length. Re-render if off.

## Phase 5 — Thumbnail / cover
Read the script and find its single biggest **hook** (core tension, surprising claim, question, or before/after). Design ONE thumbnail around that hook, same MS Paint style, in the SAME orientation as the video, saved as `thumbnail.png`. Best practices: one focal idea readable in under a second; big bold text ≤4 words that adds a claim/question (not just a label); high contrast and bright color; strong emotion or a "vs." conflict; a red arrow/circle/"?" directing the eye; lots of breathing room; correctly-spelled short text; no real identifiable people.

## Done
Finish with a one-line summary: image count, orientation/aspect, video path + duration, thumbnail path.
