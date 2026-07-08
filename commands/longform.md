---
description: Generate a horizontal 16:9 long-form YouTube video from a timestamped script (MS Paint stickman style)
argument-hint: paste your timestamped script (or leave blank and paste it next)
---
You are producing a **LONG-FORM, horizontal 16:9** video.

Use the `youtube-generator` skill and follow it exactly, with:
- ORIENTATION = horizontal, ASPECT_RATIO = 16:9
- image-prompt orientation phrase = "horizontal 16:9 wide"
- render with `python build_video.py 16:9` (outputs 1920×1080)

The user's script (with timestamps) is below. If it is empty, ask the user to paste their timestamped script, then run the whole pipeline autonomously.

$ARGUMENTS
