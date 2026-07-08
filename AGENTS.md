# AGENTS.md

Guidance for AI coding agents (Claude Code, Codex, Warp, etc.) working in this repository.

## What this repo is

A portable agent skill that turns a timestamped script into a finished video. The runtime artifact is `SKILL.md`: YAML frontmatter (metadata + allowed tools) followed by the numbered workflow. There is no separate build step to run in this repo — the skill itself drives a browser (ChatGPT web via the Claude-in-Chrome extension), spawns helper agents, and writes + runs a small Python/ffmpeg script (embedded in `SKILL.md`, Phase 4) inside the user's project folder.

## Key files

- `SKILL.md` — the skill itself. YAML frontmatter (`name`, `version`, `description`, `compatibility`, `allowed-tools`) followed by the phase-by-phase workflow. The ffmpeg assembly script lives in Phase 4. **This is the source of truth.**
- `README.md` — for humans: installation, usage, prerequisites, how it works.
- `commands/longform.md`, `commands/shortform.md` — Claude Code convenience commands that invoke the skill with an aspect ratio (16:9 vs 9:16).
- `.claude-plugin/plugin.json` — Claude Code plugin manifest.
- `.claude-plugin/marketplace.json` — single-repo marketplace entry so `/plugin marketplace add SethSkaff/YouTube-Generator` works.

## The maintenance contract

`SKILL.md` and `README.md` must stay in sync. When you change behavior:

- **Workflow / phases:** if you change what a phase does (browser mechanics, the render command, orientation handling), reflect it in the README's "How it works" and usage sections in the same change.
- **Render script:** `build_video.py` exists only as the code block embedded in `SKILL.md` Phase 4 — that is the single copy. Change render behavior there.
- **Version:** bump `version` in both `SKILL.md` frontmatter and `.claude-plugin/plugin.json` together. (`marketplace.json` intentionally omits a version so `plugin.json` stays the package source of truth.)
- **Compatibility:** keep install/usage language harness-neutral where possible, but be honest about the hard requirements — a browser-automation tool (Claude-in-Chrome), a shell, and Python 3. Unlike a pure-text skill, this one cannot run in a harness with no browser control.

## Editing SKILL.md

- Preserve valid YAML frontmatter (formatting and indentation).
- The workflow below the frontmatter is the product. Edit it like a careful instruction document, not code.
