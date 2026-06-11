# YouTube Script → Video — Project Template

Copy this whole folder for each new video project, then:

1. Drop your **narration audio file** (.m4a/.mp3/.wav) into the copied folder.
2. Open Chrome: logged into ChatGPT, with the Claude extension installed.
3. In the folder, launch: `claude --dangerously-skip-permissions` (accept the one-time "trust this folder").
4. Paste your **YouTube script (with timestamps)** as your first message, then walk away.
5. Return to:
   - `output/final_video_with_audio.mp4` — finished video
   - `output/slideshow_visuals_silent.mp4` — silent visuals (to layer in Clipchamp)
   - `thumbnail.png`

## What's in here
- `CLAUDE.md` — the autonomous workflow (auto-loaded by Claude; runs everything, asks nothing).
- `build_video.py` — assembles the images into a timed MP4; auto-detects the audio.
- `.claude/settings.json` — pre-approves the tools so you're not clicking "allow".

Generated images land in `script_images/` (created automatically during the run).

Notes: it's a long unattended run (~30–60 min for a full script). Requires ChatGPT login + Chrome's "ask where to save" OFF and automatic downloads allowed for chatgpt.com (these persist in your Chrome profile once set).
