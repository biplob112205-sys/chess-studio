# ♚ Chess Video Generator — Antigravity Skill

An autonomous, production-ready Antigravity skill and Python rendering engine for generating viral, studio-quality vertical (9:16, 1080x1920) chess short-form videos (YouTube Shorts, Instagram Reels, TikTok) directly from a voiceover audio file and chess move sequence.

---

## 🌟 Features

- **Word-by-Word Kinetic Subtitles**: Strictly synchronized with audio speech; active word highlighted with smooth pill container.
- **Authentic Chess.com Sound Effects**: Piece landing clicks, captures, checks, castling, and game-end chords aligned to exact move touchdowns.
- **Broadcast-Grade Visuals**:
  - Two-tone complementary typography header (White + Amber Gold) with soft drop shadow.
  - Matte Dark Charcoal `#24221E` background (no tacky AI gradients or textures).
  - Chess.com Green (`#739552`) and Buff (`#EBECD0`) board with subtle square highlights.
  - Tactical arrows (checks, forks, sacrifices) rendered cleanly **on top of pieces**.
  - Player HUD cards with Elo ratings and clocks.
- **Self-Contained & Privacy-Safe**: Zero personal data, no hardcoded API keys or external account secrets.

---

## 📁 Repository Structure

```
chess-video-generator/
├── SKILL.md                 # Antigravity skill definition & instructions
├── requirements.txt         # Python dependencies (Pillow, python-chess, etc.)
├── assets/
│   ├── pieces/              # 12 Wikipedia vector-grade chess pieces (wP.png - bK.png)
│   ├── sounds/              # Full official Chess.com audio library (12 .wav & .mp3 files)
│   ├── sfx/                 # Move, capture, check, mate, castle, and start SFX
│   ├── icons/               # Move evaluation badges (Brilliant, Great, Blunder, etc.)
│   └── avatars/             # Neutral default player and bot avatars
├── scripts/
│   ├── engine.py            # High-performance PIL + FFmpeg 1080x1920 renderer
│   ├── audio_mixer.py       # Automated SFX mixing & broadcast loudness normalization
│   └── run.py               # Turnkey CLI runner
├── templates/
│   ├── scholars_mate.json   # Match timeline: Scholar's Mate Counter
│   ├── italian_destroy.json # Match timeline: Italian Game Counter-Attack
│   └── template_blank.json  # Blank template for custom games
├── .gitignore               # Strict privacy & media ignore rules
└── README.md                # Documentation
```

---

## 🚀 How to Use on Any Computer

### Option A: Use as an Antigravity Skill
1. Copy or clone this folder into your Antigravity skills directory:
   - macOS / Linux: `~/.gemini/antigravity/skills/chess-video-generator`
   - Or keep it directly inside your project workspace.
2. In Antigravity chat, simply provide your voiceover audio file and say:
   > *"Make a chess short video from this voiceover and PGN"*
3. Antigravity will automatically read `SKILL.md`, configure the timeline, and render the complete master video!

### Option B: Run Standalone via Terminal
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Place your voiceover in 'Voiceovers/' directory and run:
python3 scripts/run.py --voice "Voiceovers/my_audio.mp3" --config "templates/italian_destroy.json" --output "Export videos/chess_short.mp4"
```

---

## 🔒 Privacy & Safety Guarantee

This skill repository is completely clean and decoupled from personal data:
- No API keys, credentials, or client secrets.
- No personal user portraits (bundled with neutral vector chess avatar).
- No personal voiceover files or rendered videos included.
