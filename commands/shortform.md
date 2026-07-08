---
description: Generate a vertical 9:16 short-form video (Shorts / Reels / TikTok) from a timestamped script (MS Paint stickman style)
argument-hint: paste your timestamped script (or leave blank and paste it next)
---
You are producing a **SHORT-FORM, vertical 9:16** video.

Use the `script-to-video` skill and follow it exactly, with these parameters:
- ORIENTATION = vertical
- ASPECT_RATIO = 9:16
- image-prompt orientation phrase = "vertical 9:16 tall"
- video render command = `python build_video.py 9:16` (outputs 1080×1920)

The user's script (with timestamps) is below. If it is empty, ask the user to paste their timestamped script, then run the whole pipeline autonomously.

$ARGUMENTS
