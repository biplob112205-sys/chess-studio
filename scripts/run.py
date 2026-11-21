#!/usr/bin/env python3
"""
Turnkey Runner for Chess Video Generator
Scans 'Voiceovers/' directory or accepts explicit audio input,
synchronizes chess moves, mixes sound effects, and renders master 1080x1920 MP4 to 'Export videos/'.
"""

import os, sys, argparse, json, subprocess
import engine

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(SCRIPT_DIR)
TEMPLATES_DIR = os.path.join(SKILL_ROOT, "templates")

def main():
    parser = argparse.ArgumentParser(description="Autonomous Chess Short-Form Video Generator")
    parser.add_argument("--voice", "-v", help="Path to voiceover audio file (.mp3 / .wav)")
    parser.add_argument("--config", "-c", help="Path to match config JSON (default: templates/scholars_mate.json)")
    parser.add_argument("--output", "-o", help="Output MP4 destination (default: 'Export videos/chess_short.mp4')")
    parser.add_argument("--title", "-t", help="Video Title (default: from config or 'HOW TO BEAT SCHOLAR\'S MATE')")
    args = parser.parse_args()

    # 1. Resolve Voiceover file
    voice_file = args.voice
    if not voice_file:
        voiceover_dir = "Voiceovers"
        if os.path.exists(voiceover_dir):
            audio_files = [
                os.path.join(voiceover_dir, f) for f in os.listdir(voiceover_dir)
                if f.lower().endswith(('.mp3', '.wav', '.m4a'))
            ]
            if audio_files:
                # Pick most recent
                audio_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
                voice_file = audio_files[0]
                print(f"🎙️ Auto-detected voiceover in Voiceovers/: {voice_file}")

    if not voice_file:
        # Fallback to local final_audio.wav if present
        if os.path.exists("final_audio.wav"):
            voice_file = "final_audio.wav"
            print(f"🎙️ Using existing mixed audio: {voice_file}")
        else:
            print("❌ Error: No voiceover file specified or found in 'Voiceovers/' directory.")
            sys.exit(1)

    # 2. Resolve Config & Timeline
    config_file = args.config or os.path.join(TEMPLATES_DIR, "scholars_mate.json")
    if not os.path.exists(config_file):
        print(f"❌ Error: Config file not found: {config_file}")
        sys.exit(1)

    with open(config_file) as f:
        config = json.load(f)

    title = args.title or config.get("title", "HOW TO BEAT SCHOLAR'S MATE")
    timeline = config.get("timeline", [])

    # 3. Resolve Phrases / Kinetic Subtitles
    phrases = engine.PHRASES

    # 4. Resolve Output Path
    out_dir = "Export videos"
    os.makedirs(out_dir, exist_ok=True)
    output_mp4 = args.output or os.path.join(out_dir, "scholars_mate_punish.mp4")

    # 5. Automatically mix authentic Chess.com sound effects with voiceover
    mixed_audio_file = os.path.join(out_dir, "master_audio_mixed.wav")
    try:
        from audio_mixer import mix_voiceover_with_sfx
        print("🎵 Synchronizing and mixing authentic Chess.com sound effects...")
        voice_file = mix_voiceover_with_sfx(voice_file, timeline, mixed_audio_file)
    except Exception as e:
        print(f"⚠️ Audio mixer notice: {e}. Proceeding with base audio.")

    # 6. Execute Render
    print("🚀 Initializing Chess Video Generator...")
    engine.render_chess_short(
        audio_file=voice_file,
        timeline=timeline,
        phrases=phrases,
        title=title,
        output_mp4=output_mp4
    )

    # Duplicate to root if run from workspace
    if os.path.dirname(output_mp4) != "":
        basename = os.path.basename(output_mp4)
        try:
            shutil.copyfile(output_mp4, basename)
            print(f"📁 Backup also saved in current folder: {basename}")
        except Exception:
            pass

if __name__ == "__main__":
    main()
