---
name: script-to-video
description: Turn a timestamped script into a finished MS Paint stickman explainer video. AI agents pre-write one scene prompt per timestamp, images are generated via ChatGPT web (Claude-in-Chrome), a vision agent QAs them, and ffmpeg assembles a timestamp-synced video with the narration audio. Invoked by /longform (horizontal 16:9) and /shortform (vertical 9:16); those commands pass ORIENTATION, ASPECT_RATIO, and the image-prompt orientation phrase.
---

# Script → Finished Video

Turn the user's timestamped script into a finished video. For EVERY timestamp, generate one image that visually explains the narration at that moment, then assemble all images into a video synced to the audio file in the current folder.

**Orientation:** the invoking command passes `ORIENTATION`, `ASPECT_RATIO`, and an image-prompt orientation phrase. `/longform` → horizontal, 16:9, "horizontal 16:9 wide", render `python build_video.py 16:9`. `/shortform` → vertical, 9:16, "vertical 9:16 tall", render `python build_video.py 9:16`. If the skill is used directly with no command, default to horizontal 16:9.

## Operating rules
- Run autonomously. Don't pause for confirmation, cost, or "should I proceed". The only thing you may ask is for the script itself if it wasn't provided. Then execute every phase to completion and stop with a one-line summary.
- The audio is whatever audio file (.m4a/.mp3/.wav/…) is already in the current folder. Generate images through **ChatGPT web** via the Claude-in-Chrome MCP (not paid image APIs).
- If a step fails, self-recover (retry / regenerate / simplify) and keep going.
- Prerequisites that must already be true in the user's Chrome profile: logged into ChatGPT; "Ask where to save each file" is OFF; automatic multiple downloads allowed for chatgpt.com. If a download silently fails to land on disk, assume those reset; re-pull rather than stalling.

## Style (every image)
Childish MS Paint doodle, plain white background, thick uneven wobbly black outlines drawn badly on purpose, stick figures (round heads, dot eyes, line bodies), flat colors only, no shading/3D/gradients, lots of empty white space, amateur funny "bad" look, occasional red arrows/question marks. Text must be SHORT and spelled correctly. Never realistic/anime/Disney/vector/polished. **Never depict real identifiable people** — use generic stick figures + generic labels.

Per-image prompt = this prefix + the scene (insert the orientation phrase from the command):
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
Copy `build_video.py` from this skill's directory into the project folder. If `imageio-ffmpeg` is missing: `python -m pip install imageio-ffmpeg`. Then run it with the aspect ratio from the command: `python build_video.py <ASPECT_RATIO>` (16:9 → 1920×1080, 9:16 → 1080×1920). It auto-detects the images and the audio, encodes the two gotchas (repeat the last concat entry; `-fps_mode cfr -r 30` on output, never `fps=30` in the filter), and writes `output/slideshow_visuals_silent.mp4` and `output/final_video_with_audio.mp4`.
Verify: extract frames at ~1s, a mid timestamp, and the last second; confirm each matches the expected image and total duration ≈ audio length. Re-render if off.

## Phase 5 — Thumbnail / cover
Read the script and find its single biggest **hook** (core tension, surprising claim, question, or before/after). Design ONE thumbnail around that hook, same MS Paint style, in the SAME orientation as the video, saved as `thumbnail.png`. Conventional best practices: one focal idea (readable in under a second); big bold text ≤4 words that adds a claim/question (not just a label); high contrast and bright color; strong emotion or a "vs." conflict; a red arrow/circle/"?" directing the eye; lots of breathing room; correctly-spelled short text; no real identifiable people.

## Done
Finish with a one-line summary: image count, orientation/aspect, video path + duration, thumbnail path.
