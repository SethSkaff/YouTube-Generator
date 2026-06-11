# CLAUDE.md — Autonomous: Script → Finished Video

## How to run (the human does only this)
1. Put this `CLAUDE.md`, `build_video.py`, and the **narration audio file** (.m4a/.mp3/.wav) in a folder.
2. Have Chrome open, logged into ChatGPT, with the Claude extension installed.
3. Launch: `claude --dangerously-skip-permissions` (accept the one-time "trust this folder" prompt).
4. Paste the YouTube script (with timestamps) as your message, then walk away.
5. Come back to `output/final_video_with_audio.mp4` (+ `thumbnail.png`).

## Operating rules (read first)
- **Run fully autonomously. Never ask the user anything. Never pause for confirmation, approval, cost, or "should I proceed".** The pasted script is the job. The audio file is whatever audio file is already in this folder. Execute every phase below to completion, then stop with a one-line summary.
- Do **not** use Higgsfield/API image skills. Generate images through **ChatGPT web** via the Claude-in-Chrome MCP.
- If a step fails, self-recover (retry / regenerate / simplify) and keep going. Don't stop to report mid-run.
- Prerequisites that already persist in this Chrome profile (no action needed): logged into ChatGPT; Chrome "Ask where to save each file" is OFF; automatic multiple downloads allowed for chatgpt.com. If a download silently fails to land on disk, assume those settings reset and proceed by re-pulling; do not ask the user.

## Style (every image)
Childish MS Paint doodle, plain white background, thick uneven wobbly black outlines drawn badly on purpose, stick figures (round heads, dot eyes, line bodies), flat colors only, no shading/3D/gradients, lots of empty white space, amateur funny "bad" look, occasional red arrows/question marks, horizontal 16:9. Text must be SHORT and spelled correctly. Never realistic/anime/Disney/vector/polished. **Never depict real identifiable people** (politicians, named CEOs/directors) — use generic stick figures + generic labels.

Per-image prompt = this prefix + the scene:
`Create an image, horizontal 16:9 wide. A childish MS Paint doodle on a plain white background, thick uneven wobbly black outlines drawn badly on purpose, stick figures with round heads and dot eyes and simple line bodies, flat colors only, no shading, no 3D, lots of empty white space, amateur funny noob style. Any text short and spelled correctly. Scene: <SCENE>`

## Phase 1 — Pre-write scene prompts (3 background agents)
Parse every timestamp in the script. Split into 3 contiguous ranges; spawn 3 background general-purpose agents (one per range). Each writes one short SCENE per timestamp to `prompts_A.txt`/`B`/`C`, format `M:SS :: <scene>`, following the style + no-real-people rules, no boilerplate. Start Phase 2 on the earliest timestamps yourself while they run; use their files for later batches.

## Phase 2 — Generate images (ChatGPT web, 5 parallel tabs)
Connect the browser: `list_connected_browsers` → `select_browser` (auto-pick if one). Create exactly **5 tabs** (a 6th causes renderer freezes). Output to `script_images/`, filenames `MMSS_M-SS.png` (e.g. `0555_5-55.png`).

Per batch of 5 timestamps:
1. `browser_batch` navigate all 5 tabs to `https://chatgpt.com/`; wait 3s.
2. Inject + submit each prompt via JS (works on background tabs): focus `#prompt-textarea`, `document.execCommand('insertText',false,PROMPT)`, then click `[data-testid="send-button"]`. (Do NOT use the computer `type` action — it only hits the foreground tab.)
3. **Wait ~55s** (generation is slow; pulling early grabs a stale/shared image → identical files).
4. Download each in parallel via JS in its tab: take the last `img` whose `src` matches `estuary/content`, `fetch(src,{credentials:'include'})` → blob → anchor `download='MMSS_M-SS.png'` → click. **Guard: only save if `blob.type` starts with `image` AND `blob.size > 50000`** (else it's an error blob — retry). The extension blocks returning base64/cookie/query data, so the browser download is the only path to disk.
5. `mv` the 5 files from the Downloads folder into `script_images/`.
6. Run a global MD5 check over `script_images/`; re-pull any identical-hash files (a tab wasn't finished).

Freeze recovery: if a tab returns `Runtime.evaluate timed out`, close it (`tabs_close_mcp`), recreate a tab, and regenerate that frame fresh. If one specific image keeps freezing on render, regenerate it with a simpler scene (fewer objects).

## Phase 3 — Vision QA (1 background agent)
Spawn a background agent that Reads each PNG in `script_images/` and flags blank/broken, wrong-style, off-topic, misspelled, or duplicate frames to a report. Regenerate anything flagged.

## Phase 4 — Assemble the video
Run `python build_video.py` (it auto-detects the images, auto-detects the audio file in this folder, and renders). If `imageio-ffmpeg` is missing: `python -m pip install imageio-ffmpeg` first.
The script already encodes the two gotchas — repeat the last concat entry, and `-fps_mode cfr -r 30` on the output (never `fps=30` in the filter, which drops the first frame). It outputs `output/slideshow_visuals_silent.mp4` and `output/final_video_with_audio.mp4` at 1920×1080.
Verify: extract frames at ~1s, a mid timestamp, and the last second; confirm each matches the expected image and total duration ≈ audio length. Re-render if off.

## Phase 5 — Thumbnail
First read the script and identify its single biggest **hook** — the core tension, the surprising claim, the question, or the before/after the video is really about. Design ONE thumbnail around that hook in the same MS Paint stickman style and save it as `thumbnail.png`. Derive the concept and text from THIS script's hook every time — never reuse a fixed concept.

Apply conventional YouTube thumbnail best practices:
- **One idea, one focal point.** A viewer should get it in under a second — don't cram multiple scenes or details.
- **Big bold text, ≤4 words.** Short, punchy, readable on a phone. Text should add a question/claim/payoff, not just label the picture.
- **High contrast, bright color.** Make it pop against a white feed — a couple of bold flat colors and thick outlines.
- **Show emotion or conflict.** Strong stick-figure expression, a face, a "vs." standoff, a shocked reaction, or a clear before→after.
- **Direct the eye.** Use a red arrow, a circle, or a big "?" to point at the key element.
- **Leave breathing room.** Lots of empty white space, nothing crammed to the edges, still legible when small.
- Same frame rules: 16:9, correctly-spelled short text, and no real identifiable people.

## Done
Finish with a one-line summary: image count, video path + duration, thumbnail path. Leftover scratch files (`prompts_*.txt`, reports, `concat.txt`) are fine to leave.
