---
name: chess-video-generator
description: Generate viral, studio-quality vertical (9:16, 1080x1920) chess short-form videos (YouTube Shorts, Instagram Reels, TikTok) from a voiceover audio file. Automatically synchronizes board moves, pieces, dynamic word-by-word kinetic captions with keyword color highlights, authentic Chess.com sound effects (move, capture, check, mate), floating player match cards intro, and coach victory dialogue outro. Use whenever the user asks to "make a chess video", "create a chess reel/short", "turn voiceover into chess video", "generate chess short", "render chess game", or provides a chess audio/match to animate.
---

# Chess Video Generator

Automated pipeline for transforming chess voiceover audio into high-retention vertical (9:16, 1080×1920) social media videos (YouTube Shorts, Instagram Reels, TikTok).

## 📁 Standard Project Structure

When using this skill in any workspace, organize files into these clean dedicated directories:

```
workspace/
├── Voiceovers/                  # 🎙️ User puts voiceover audio files (.mp3, .wav) here
├── Export videos/               # 🎬 Finished 1080x1920 MP4 videos are exported here
├── chess-video-generator/       # 🧠 Self-contained skill engine
│   ├── SKILL.md
│   ├── assets/
│   │   ├── pieces/              # Sharpened Wikipedia chess piece PNGs
│   │   ├── sfx/                 # Authentic Chess.com move, capture, check, mate SFX
│   │   ├── icons/               # Brilliant, great, best, blunder move evaluation badges
│   │   └── avatars/             # User avatar & opponent avatars
│   ├── scripts/
│   │   ├── engine.py            # High-performance PIL + FFmpeg renderer
│   │   └── run.py               # One-click CLI runner
│   └── templates/
│       └── scholars_mate.json   # Move timeline & match config
```

---

## 🚀 Quick Start (One Command)

To generate a completed video from a voiceover file:

```bash
# Place your audio file in 'Voiceovers/' and run:
python3 chess-video-generator/scripts/run.py

# Or specify a custom voiceover file:
python3 chess-video-generator/scripts/run.py --voice "Voiceovers/my_voiceover.mp3" --output "Export videos/my_video.mp4"
```

The script automatically:
1. Picks up the voiceover from `Voiceovers/`.
2. Mixes authentic Chess.com move click, capture, and check sound effects at the exact move timings.
3. Renders the board, pieces, centered header pill, and word-by-word kinetic captions.
4. Saves the finished master MP4 directly into `Export videos/`.

---

## 🎨 Visual Design Guidelines (Strict Non-AI Aesthetic)

To guarantee high engagement, clean aesthetics, and avoid cheap "AI look":

1. **Background**:
   - **NO** crumpled paper texture.
   - **NO** neon glows, aggressive gradients, or blue/purple artificial lighting.
   - Use a clean **Solid Matte Warm Dark Charcoal (`#24221e` / `rgb(36, 34, 30)`)** background.

2. **Top Header**:
   - Centered horizontally (`cx = 540`, `y = 105`).
   - Sleek rounded dark pill container with warm amber border (`#FACC15`) and glowing indicator dot.
   - Large bold sans text: `HOW TO BEAT SCHOLAR'S MATE`.

3. **Word-by-Word Kinetic Captions (Strict Audio Sync)**:
   - Centered above the board (`base_y = 245`).
   - **Word-for-Word Accuracy**: Every subtitle word must match the exact spoken audio from the voiceover.
   - **Sequential Appearance**: Words that have NOT yet been spoken must remain **invisible** (`if t < w_start: continue`). Never show the entire sentence or line all at once before words are spoken.
   - **Active Word Pill Container**: The word currently being spoken (`w_start <= t <= w_end`) is highlighted with a natural, clean rounded dark pill container (`fill=(52, 48, 42), outline=(250, 204, 21), width=2`).
   - **Persistence**: Once spoken, words remain visible, solid, and clear on their line until the phrase ends.
   - Keyword Color Highlights:
     - 🟡 **Gold (`#FACC15`)**: Piece names, key squares, and critical moves (`Queen`, `Knight`, `e4`, `Nc6`, `d4`, `d5`, `Qh4`).
     - 🔴 **Red (`#F87171` / `#EF4444`)**: Threats, danger, and checks (`f7`, `cheap win`, `threat`, `check`, `fork`).
     - 🔵 **Cyan (`#38BDF8`)**: Tactical strikes & brilliant moves (`return the favor`, `run home`, `Knight e4!!`).
     - 🟢 **Green (`#4ADE80`)**: Defense & Checkmate (`covers`, `blocks`, `mate!`).

4. **Chess Board & Pieces**:
   - Authentic Chess.com board squares: Buff (`#ebecd0`) and Green (`#739552`).
   - Move highlights: Soft Pale Yellow (`#f5f682`) on light squares, Olive Yellow-Green (`#baca44`) on dark squares.
   - **NO black circle shadows or muddy brown trails** behind moving pieces. Pure flat 2D cubic-eased glide (`1 - (1-p)^3`).
   - Pieces are micro-sharpened (UnsharpMask radius 1.2, percent 140) for crystal 1080p rendering.

5. **Player Profiles & Ratings (Strict Layout Rules)**:
   - **User Identity**: The user is always **`Biplob`** with an authentic rating > 1000 (e.g. `1620`).
   - **Opponent Identity**: Always use realistic human usernames (e.g. `Alex_Miller`, `David_Ross`) with rating > 1000 (e.g. `1580`).
   - **No Text Collisions**: Name and Elo rating must be drawn **side-by-side on a single line** with measured text bounding boxes (`Alex_Miller (1580)` and `Biplob (1620)`), never stacked vertically where they can collide or overlap.

6. **Realistic Arrows & Skewer/Pin Animations (Chess.com Broadcast Grade)**:
   - **Layering Order**: Arrows, attack paths, and skewer lines MUST ALWAYS be rendered **on top of pieces** (drawn after piece sprites). Never draw arrows underneath pieces.
   - **Selective Tactical Usage**: Do NOT draw arrows on standard/trivial opening moves (like `1. e4 e5`). Reserve arrows exclusively for critical tactical moments: checks, sacrifices, forks, skewers, and mate attacks.
   - **Precise Timing (No Premature Arrows)**: Never display an arrow while a piece is still flying in mid-air. An arrow MUST only start shooting **after** the moving piece has landed on its destination square (`arrow_start = t_start + move['dur'] + 0.15s`) or exactly when the voiceover mentions the tactic.
   - **Realistic Shooting Dynamic**: Instead of a flat static fade, arrows shoot forward smoothly from origin to destination using cubic ease-out (`1 - (1-p)^3`) over ~0.28s. The arrowhead emerges dynamically as it nears the target.
   - **Authentic Chevron Geometry**: Signature Chess.com chevron arrowhead (head length 40px, width 44px, chevron recess 75%, rounded shaft start) with a soft dark drop shadow (`offset: +2, +3`, alpha ~0.38) that makes the arrow float cleanly with 3D depth.
   - **Skewer / Pin-Out Visualization**: When a piece skewers or pins (e.g. Bishop checking King through to Queen):
     - Primary attack arrow strikes the King with check.
     - Piercing continuation ray shoots through the King directly to the Queen behind it, capped with an arrowhead and target evaluation reticle on the pinned Queen.
   - **Color Coding**: Red (`#F87171`) for opponent threats/bait, Warm Gold (`#FACC15`) for checks & tactics, Emerald Green (`#4ADE80`) for winning conversions and underpromotions.

7. **Audio Mixing & Loudness Standards**:
   - In FFmpeg `amix`, ALWAYS set `normalize=0`. Default normalization divides voiceover volume by the number of audio inputs, making speech too quiet.
   - Follow with `loudnorm=I=-14:LRA=7:TP=-1.5` so voiceover remains broadcast-rich, loud, and crystal-clear with authentic Chess.com SFX (move, capture, check, mate) without volume drops.

8. **Special Animations**:
   - **Brilliant Move (`8... Ne4!!`)**: Expanding cyan shockwave ripple (`radius 50 -> 120`), pop-in `!!` badge, cyan glowing tactical card.
   - **Match Intro (0.0s - 3.8s)**: Chess.com match cards (opponent Silver Division, player Gold Division with user avatar) + center floating `VS` pill.
   - **Victory Outro**: Chess.com Coach "You Won!" dialog box, trophy, stats row (Great, Best, Excellent), and big green "Game Review" button.

---

## 📹 Video Quality & Encoding Standards

To prevent YouTube Shorts or Instagram Reels from compressing the video into low-bitrate blocky mush:

```python
ffmpeg_cmd = [
    "./ffmpeg", "-y",
    "-f", "rawvideo",
    "-vcodec", "rawvideo",
    "-s", "1080x1920",
    "-pix_fmt", "rgb24",
    "-r", "30",
    "-i", "-",
    "-i", audio_file,
    "-c:v", "libx264",
    "-preset", "medium",
    "-crf", "15",              # Visually lossless master
    "-b:v", "14M",             # 14 Mbps high target bitrate
    "-maxrate", "20M",
    "-bufsize", "28M",
    "-color_primaries", "bt709",
    "-color_trc", "bt709",
    "-colorspace", "bt709",
    "-pix_fmt", "yuv420p",
    "-movflags", "+faststart", # Instant playback on YouTube / mobile
    "-c:a", "aac",
    "-b:a", "256k",
    "-ar", "48000",
    "-shortest",
    output_mp4
]
```

---

## 📂 Bundled Assets

- `assets/pieces/`: Complete 12-piece Wikipedia PNG set.
- `assets/sfx/`: Authentic Chess.com move, capture, check, mate, and game-end audio tracks.
- `assets/icons/`: Official evaluation icons (Brilliant, Great, Best, Excellent, Mistake, Blunder).
- `assets/avatars/`: High-resolution user profile picture and opponent avatar.
