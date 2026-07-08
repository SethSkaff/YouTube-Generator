# YouTube Generator — script → finished video (Claude Code plugin)

Turn a **timestamped script** into a finished MS Paint stickman explainer video, fully autonomously:

- `/longform <script>` → horizontal **16:9** YouTube video (1920×1080)
- `/shortform <script>` → vertical **9:16** Short / Reel / TikTok (1080×1920)

Both do the same pipeline; the command just sets the aspect ratio.

## How it works
1. **Agents write the scene prompts** — 3 background agents each take a chunk of timestamps and write one short scene description per timestamp.
2. **Images via ChatGPT web** — 5 parallel ChatGPT tabs (driven by the Claude-in-Chrome extension) generate one image per timestamp in the crude stickman style, auto-downloaded to `script_images/`.
3. **A vision agent QAs** every frame (blank / off-style / misspelled / duplicate) and regenerates any it flags.
4. **ffmpeg assembles** the images to their timestamps and muxes your audio → `output/final_video_with_audio.mp4` (plus a silent visuals-only version and a `thumbnail.png`).

## Install (as a plugin)
```
/plugin marketplace add SethSkaff/YouTube-Generator
/plugin install youtube-generator@youtube-generator
```
Then in any folder that has your narration **audio file**:
```
/longform   <paste your timestamped script>
/shortform  <paste your timestamped script>
```

### Manual install (copy the skill + commands)
```
git clone https://github.com/SethSkaff/YouTube-Generator
```
Copy `commands/*` into `~/.claude/commands/` and `skills/script-to-video/` into `~/.claude/skills/`.

## Prerequisites
- Chrome open, **logged into ChatGPT**, with the Claude (Claude-in-Chrome) extension installed.
- One-time Chrome settings (persist in your profile): **"Ask where to save each file" OFF**, and **automatic multiple downloads allowed for chatgpt.com**.
- Python available (the skill will `pip install imageio-ffmpeg` if ffmpeg is missing).
- Run Claude with `--dangerously-skip-permissions` (or allowlist Bash / the Chrome MCP) so the long run isn't interrupted by approvals.

## Notes
- It's a long unattended run (~30–60 min for a full long-form script); it self-recovers from tab freezes and duplicate grabs.
- Uses your ChatGPT web session for images — no paid image API.
- `.gitignore` keeps generated images, audio, and output out of git.

The generation logic lives in the `script-to-video` skill; `/longform` and `/shortform` are thin wrappers that pass the orientation/aspect ratio.
