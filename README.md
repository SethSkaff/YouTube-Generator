# YouTube Generator

A portable agent skill that turns a **timestamped script** into a finished MS Paint stickman explainer video — images are generated via ChatGPT web, then assembled to their timestamps with your narration audio by ffmpeg. The runtime artifact is plain Markdown (`SKILL.md`), so it can run in any harness that supports skill-style instructions and browser control.

- `/longform` → horizontal **16:9** YouTube video (1920×1080)
- `/shortform` → vertical **9:16** Short / Reel / TikTok (1080×1920)

## Installation

### Skills CLI

Install with the cross-agent skills CLI:

```bash
npx skills add SethSkaff/YouTube-Generator
```

Update an existing install:

```bash
npx skills update youtube-generator
```

To install into every supported agent harness:

```bash
npx skills add SethSkaff/YouTube-Generator --agent '*'
```

### Claude Code plugin

```
/plugin marketplace add SethSkaff/YouTube-Generator
/plugin install youtube-generator@youtube-generator
```

The skill is then invoked as `/youtube-generator:youtube-generator`, and the aspect-ratio commands as `/youtube-generator:longform` and `/youtube-generator:shortform`.

### Manual

The runtime artifact is `SKILL.md`. Install it wherever your harness expects skill directories:

```bash
git clone https://github.com/SethSkaff/YouTube-Generator.git /path/to/your/skills/youtube-generator
```

Or copy `SKILL.md` into an existing skill folder.

## Usage

In a folder that contains your narration **audio file**, invoke the skill and paste your timestamped script:

```
/longform

(0:00) Everyone in politics wants to be on the right side of history.
(0:04) That phrase gets thrown around constantly...
```

```
/shortform

(0:00) ...
```

In a harness without the slash commands, invoke the `youtube-generator` skill directly and say "longform" (16:9) or "shortform" (9:16). Then walk away — it runs the whole pipeline and drops the finished video in `output/`.

## Prerequisites

- Chrome open, **logged into ChatGPT**, with the Claude (Claude-in-Chrome) extension installed.
- One-time Chrome settings (they persist in your profile): **"Ask where to save each file" OFF**, and **automatic multiple downloads allowed for chatgpt.com**.
- Python 3 (the skill runs `pip install imageio-ffmpeg` if ffmpeg is missing).
- Run your agent with permissions relaxed (e.g. Claude Code's `--dangerously-skip-permissions`, or an allowlist) so the long run isn't interrupted by approvals.

## How it works

1. **Background agents write the scene prompts** — one short scene description per timestamp.
2. **Images via ChatGPT web** — five parallel ChatGPT tabs (driven by the Claude-in-Chrome extension) generate one image per timestamp in the crude stickman style, auto-downloaded to `script_images/`.
3. **A vision agent QAs** every frame and regenerates anything blank / off-style / misspelled / duplicate.
4. **ffmpeg assembles** the images to their timestamps and muxes your audio → `output/final_video_with_audio.mp4` (plus a silent visuals-only version and a `thumbnail.png`).

It's a long unattended run (~30–60 min for a full long-form script); it self-recovers from tab freezes and duplicate grabs. Uses your ChatGPT web session for images — no paid image API.

## Version history

- **1.0.0** — Initial release. Packaged as a portable `SKILL.md` with `/longform` (16:9) and `/shortform` (9:16), plus Skills CLI and Claude Code plugin installs.

## License

MIT — see [LICENSE](LICENSE).
