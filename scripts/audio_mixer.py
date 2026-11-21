#!/usr/bin/env python3
"""
Autonomous Audio Mixer for Chess Video Generator
Mixes raw voiceovers with authentic Chess.com sound effects (move, capture, check, mate, castle, start)
at exact move timestamps using FFmpeg, maintaining broadcast speech clarity and professional loudness.
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
SOUNDS_DIR = SKILL_ROOT / "assets" / "sounds"
if not SOUNDS_DIR.exists():
    SOUNDS_DIR = SKILL_ROOT / "assets" / "sfx"

def get_sfx_path(event_name: str) -> str:
    """Finds the authentic Chess.com audio file for a given event."""
    candidates = [
        SOUNDS_DIR / f"{event_name}.wav",
        SOUNDS_DIR / f"{event_name}.mp3",
        SOUNDS_DIR / f"sfx_{event_name}.wav",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    
    # Fallback to move-self if specific not found
    fallback = SOUNDS_DIR / "move-self.wav"
    return str(fallback) if fallback.exists() else ""

def generate_sfx_events_from_timeline(timeline: list) -> list:
    """
    Parses a chess match timeline and extracts the exact audio events and delays.
    Returns list of (timestamp_seconds, sfx_filepath, volume_multiplier).
    """
    events = []
    
    # Opening game start chime
    start_sfx = get_sfx_path("game-start")
    if start_sfx:
        events.append((0.4, start_sfx, 0.65))

    for item in timeline:
        if "move" not in item:
            continue
        
        move_info = item["move"]
        t_start = item.get("t_start", 0.0)
        dur = move_info.get("dur", 0.35)
        # Transient hits when piece touches down
        touchdown_t = round(t_start + dur * 0.85, 2)
        
        piece = move_info.get("piece", "P")
        badge = item.get("badge", {})
        badge_move = badge.get("move", "")
        badge_cat = badge.get("cat", "").upper()
        badge_desc = badge.get("desc", "").lower()
        
        # 1. Checkmate / Game End
        if "#" in badge_move or "MATE" in badge_cat or "checkmate" in badge_desc or "resigns" in badge_desc:
            sfx = get_sfx_path("game-end")
            vol = 0.95
        # 2. Check
        elif "+" in badge_move or "CHECK" in badge_cat or "check" in badge_desc:
            sfx = get_sfx_path("move-check")
            vol = 1.0
        # 3. Capture
        elif "x" in badge_move or "take" in badge_desc or "capture" in badge_desc or "sac" in badge_desc:
            sfx = get_sfx_path("capture")
            vol = 0.90
        # 4. Castle
        elif "O-O" in badge_move or "castle" in badge_desc:
            sfx = get_sfx_path("castle")
            vol = 0.85
        # 5. Normal move (distinguish self vs opponent by piece case: upper is White, lower is Black)
        elif piece.isupper():
            sfx = get_sfx_path("move-opponent")
            vol = 0.80
        else:
            sfx = get_sfx_path("move-self")
            vol = 0.80

        if sfx:
            events.append((touchdown_t, sfx, vol))

    # Concluding win chime if not already placed
    last_item = timeline[-1] if timeline else {}
    last_t = last_item.get("t_end", 45.0)
    if not any(e[1].endswith("game-end.wav") or e[1].endswith("game-end.mp3") for e in events):
        end_sfx = get_sfx_path("game-end")
        if end_sfx:
            events.append((max(0.5, last_t - 2.0), end_sfx, 0.9))

    return events

def mix_voiceover_with_sfx(voiceover_path: str, timeline: list, output_wav: str = "final_audio.wav") -> str:
    """
    Mixes voiceover audio with timed chess sound effects using FFmpeg.
    Uses amix normalize=0 and broadcast loudnorm filter (I=-14, LRA=7, TP=-1.5).
    """
    if not os.path.exists(voiceover_path):
        raise FileNotFoundError(f"Voiceover file not found: {voiceover_path}")

    events = generate_sfx_events_from_timeline(timeline)
    if not events:
        print("[AudioMixer] No move events generated, copying voiceover directly.")
        shutil.copy(voiceover_path, output_wav)
        return output_wav

    # Resolve ffmpeg binary
    ffmpeg_bin = shutil.which("ffmpeg")
    if not ffmpeg_bin:
        # Check current dir or parent
        for local_cand in ["./ffmpeg", "/Users/apple/Desktop/chess v/ffmpeg"]:
            if os.path.exists(local_cand) and os.access(local_cand, os.X_OK):
                ffmpeg_bin = local_cand
                break
    
    if not ffmpeg_bin:
        print("[AudioMixer] ⚠️ ffmpeg binary not found in PATH. Using source audio.")
        shutil.copy(voiceover_path, output_wav)
        return output_wav

    cmd = [ffmpeg_bin, "-y", "-i", voiceover_path]
    for _, path, _ in events:
        cmd.extend(["-i", path])

    filter_parts = []
    # Input 0: voiceover
    filter_parts.append("[0:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[v0]")

    for i, (delay, _, vol) in enumerate(events):
        delay_ms = int(delay * 1000)
        filter_parts.append(
            f"[{i+1}:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,adelay={delay_ms}|{delay_ms},volume={vol}[sfx{i}]"
        )

    inputs_str = "[v0]" + "".join(f"[sfx{i}]" for i in range(len(events)))
    num_inputs = len(events) + 1
    # amix normalize=0 ensures voiceover volume NEVER ducks or drops under sound effects
    filter_parts.append(
        f"{inputs_str}amix=inputs={num_inputs}:duration=first:normalize=0,loudnorm=I=-14:LRA=7:TP=-1.5[out]"
    )

    filter_graph = ";".join(filter_parts)
    cmd.extend(["-filter_complex", filter_graph, "-map", "[out]", "-ar", "48000", output_wav])

    print(f"[AudioMixer] 🎵 Mixing {os.path.basename(voiceover_path)} with {len(events)} authentic Chess.com SFX...")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        print(f"[AudioMixer] ⚠️ FFmpeg mixing notice: {res.stderr.decode()[-400:]}")
        shutil.copy(voiceover_path, output_wav)
        return output_wav

    print(f"[AudioMixer] ✅ Master broadcast audio mixed cleanly: {output_wav}")
    return output_wav

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 audio_mixer.py <voiceover.mp3> <config.json> [output.wav]")
        sys.exit(1)
    
    vo = sys.argv[1]
    cfg = sys.argv[2]
    out = sys.argv[3] if len(sys.argv) > 3 else "final_audio.wav"
    
    with open(cfg, "r", encoding="utf-8") as f:
        cdata = json.load(f)
    
    mix_voiceover_with_sfx(vo, cdata.get("timeline", []), out)
