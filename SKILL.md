# Chenxin Cinematic Reels — Universal Production Skill

## Purpose
Create reusable **60–90 second cinematic 3D-look vertical medical education videos** for 宸新復健科. This Skill does **not** contain a fixed disease topic. The user supplies a topic, sources, target audience and goal for every new episode. Read `README.md`, `docs/style-bible.md`, `docs/character-bible.md`, `docs/quality-checklist.md` and `templates/project.blank.json` before producing a video.

## Capability boundary
This repository generates storyboards, shot prompts, voice/subtitle plans and **assembles supplied media using FFmpeg**. It does **not** itself create photorealistic 3D footage or natural character locomotion. Real walking, hand gestures, dialogue and camera tracking require continuous video clips produced by an external video model or video editing software. Do not mislabel static image pans as native 3D motion.

## Fixed format and brand
- 9:16 vertical, target 1080×1920, 30 fps, H.264 MP4 with AAC audio
- Runtime 60–90 seconds, default 72–75 seconds
- Traditional Chinese subtitles and natural Taiwanese Mandarin male narration (user-recorded or licensed synthetic)
- Brand: 宸新復健科
- End with accurate takeaways and neutral educational CTA

## Doctor identity
Use the supplied physician photo **only when reference media is present and authorized**. Young East Asian man with short neat black hair, warm expression, white coat, pale blue shirt, navy striped tie, dark trousers. Face should resemble the actual physician while slightly stylized in believable 3D. Preserve consistent face, wardrobe and age across every shot. No alien guide.

## Cinematic language
A physician guides a visitor through an oversized, anatomically informed miniature-body environment. Show purposeful **walking, turning, pointing, speaking**, interacting with the guest. Track with moving camera, use dolly and macro close-ups, warm rim lighting, physical depth of field. 2–4 second shots for Reels pacing, with occasional breathing room. Do not bake Chinese text into AI video clips: composite subtitles after generation.

## Narrative progression
1. Hook (0–10s): relevant curiosity / misconception, with caveats.
2. Transition (10–25s): enter the giant anatomical environment.
3. Main mechanism (25–55s): 2–3 grounded explanations demonstrated visually.
4. Clinical reasoning (55–70s): avoid overclaiming, show diagnostic context.
5. Takeaway / CTA (70–80s or adjusted runtime): summarize, brand.

## Required process
1. Read the user-provided material and preserve uncertainty, not invent evidence.
2. Build 6–12 timed shots with narration, subtitles, actions and camera movement.
3. Create `projects/<topic-slug>/project.json` based on `templates/project.blank.json`.
4. Produce per-shot prompts with `python tools/reels.py prompts <project.json>`.
5. Obtain rights-cleared **continuous motion** video clips and narration.
6. Set `media` and `voice` paths for each shot and validate the project.
7. Render with `python tools/reels.py render <project.json> --out <output.mp4>`.
8. Review captions, synchronization, identity continuity, body mechanics and medical accuracy before publication.

## Medical safeguards
- Explain *可能*, *不一定*, *部分情況* as clinically indicated.
- Do not fabricate research, treatment effects or diagnostic certainty.
- No false cures, comparison of staged before/after outcomes or pressure to buy.
- Keep patient materials out without explicit consent.
- Clinician must review every anatomical rendering and health claim.
- Review medical advertising compliance before posting in Taiwan.

## Deliverables
Per topic: source notes, `project.json`, storyboard, prompt sheet, narration, captions, media manifest, render output, QC result. Clearly state which requested portions are finished and which depend on an external model.

## Tools
Python 3.10+, FFmpeg/FFprobe, Pillow. Optional edge-tts with online access and appropriate terms. Never commit keys or clinical private data. Existing style references are not an implied license to redistribute third-party videos.
