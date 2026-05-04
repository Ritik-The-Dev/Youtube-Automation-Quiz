from PIL import Image

# ======================================================
# 🔧 Pillow >=10 compatibility fix for MoviePy
# ======================================================
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS


import os
from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    VideoFileClip,
    concatenate_videoclips,
    CompositeAudioClip,
    CompositeVideoClip,
    vfx
)

# ======================================================
# CONFIG
# ======================================================
QUESTION_TOTAL_DURATION = 10        # total duration per question
ANSWER_REVEAL_DURATION = 2          # last seconds show answer image
MIN_TIMER_DURATION = 3              # minimum timer visibility

TIMER_SCALE = 0.35
GREEN_SCREEN_COLOR = [0, 255, 0]
GREEN_TOLERANCE = 80

BG_MUSIC_VOLUME = 0.15
FPS = 24

# ======================================================
# TIMER OVERLAY
# ======================================================
def load_timer_overlay(start_time, scene_height):
    """
    Timer starts after speech ends, stays till scene end,
    and is placed in a safe visible zone below options.
    """
    timer_path = os.path.join("data", "timer.mp4")

    timer = (
        VideoFileClip(timer_path)
        .without_audio()
        .fx(vfx.mask_color, color=GREEN_SCREEN_COLOR, thr=GREEN_TOLERANCE)
        .resize(TIMER_SCALE)
        .set_start(start_time)
        .set_duration(QUESTION_TOTAL_DURATION - start_time)
        .set_position(lambda t: ("center", int(scene_height * 0.72)))
    )

    return timer


# ======================================================
# MAIN VIDEO GENERATOR
# ======================================================
def generate_video(vid, scene_data, folder_path):
    clips = []

    # ---------- Background Music ----------
    bg_music_path = os.path.join("data", "bg_music.mp3")
    if not os.path.exists(bg_music_path):
        raise FileNotFoundError("bg_music.mp3 not found")

    bg_music = AudioFileClip(bg_music_path)

    # ---------- Question Loop ----------
    for i, scene in enumerate(scene_data["questions"]):

        question_img = os.path.join(folder_path, f"quiz_{i}_question.png")
        answer_img   = os.path.join(folder_path, f"quiz_{i}_answer.png")
        mp3_path = os.path.join(folder_path, f"Scene{i}.mp3")
        wav_path = os.path.join(folder_path, f"Scene{i}.wav")

        if os.path.exists(mp3_path):
            audio_path = mp3_path
        elif os.path.exists(wav_path):
            audio_path = wav_path
        else:
            audio_path = None

        if not all(map(os.path.exists, [question_img, answer_img, audio_path])):
            print(f"⚠️ Skipping question {i} (missing files)")
            continue

        # ==================================================
        # CLEAN VOICE AUDIO (NO DISTORTION)
        # ==================================================
        voice = AudioFileClip(audio_path)

        CLEAN_TAIL = 0.25  # aggressively remove noisy tail
        max_voice_duration = QUESTION_TOTAL_DURATION - MIN_TIMER_DURATION
        safe_duration = min(voice.duration, max_voice_duration) - CLEAN_TAIL

        if safe_duration <= 0:
            safe_duration = max_voice_duration

        voice = (
            voice
            .subclip(0, safe_duration)
            .audio_fadeout(0.15)
            .set_duration(safe_duration)
        )

        voice_duration = safe_duration

        # ==================================================
        # QUESTION IMAGE
        # ==================================================
        question_clip = (
            ImageClip(question_img)
            .set_duration(QUESTION_TOTAL_DURATION)
            .set_audio(voice)
        )

        # ==================================================
        # TIMER
        # ==================================================
        timer_clip = load_timer_overlay(
            start_time=voice_duration,
            scene_height=question_clip.h
        )

        # ==================================================
        # ANSWER REVEAL
        # ==================================================
        answer_clip = (
            ImageClip(answer_img)
            .set_start(QUESTION_TOTAL_DURATION - ANSWER_REVEAL_DURATION)
            .set_duration(ANSWER_REVEAL_DURATION)
        )

        # ==================================================
        # FINAL SCENE (LAYER ORDER MATTERS)
        # ==================================================
        final_scene = CompositeVideoClip(
            [
                question_clip,   # base
                timer_clip,      # visible till end
                answer_clip      # top layer
            ],
            size=question_clip.size
        ).set_duration(QUESTION_TOTAL_DURATION)

        clips.append(final_scene)

    if not clips:
        raise RuntimeError("No quiz scenes generated")

    # ==================================================
    # MERGE ALL QUESTIONS
    # ==================================================
    final_video = concatenate_videoclips(clips, method="compose")

    # ==================================================
    # BACKGROUND MUSIC
    # ==================================================
    bg_music = (
        bg_music
        .volumex(BG_MUSIC_VOLUME)
        .audio_loop(duration=final_video.duration)
        .audio_fadein(1)
        .audio_fadeout(1)
    )

    final_audio = CompositeAudioClip([
        final_video.audio,
        bg_music
    ])

    final_video = final_video.set_audio(final_audio)

    # ==================================================
    # EXPORT
    # ==================================================
    output_path = os.path.join(folder_path, f"{vid}_quiz_final.mp4")

    final_video.write_videofile(
        output_path,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        threads=4
    )

    # ==================================================
    # CLEANUP
    # ==================================================
    final_video.close()
    bg_music.close()

    print(f"\n✅ Quiz video generated successfully:\n{output_path}\n")
