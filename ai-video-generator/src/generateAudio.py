import os
import time
import json
import http.client

conn = http.client.HTTPSConnection("gen.pollinations.ai")

headers = {
    "Authorization": "Bearer " + os.getenv("POLLINATIONS_API_KEY"),
    "Content-Type": "application/json",
    "Accept": "audio/mpeg"
}


def generate_voice(
    voiceOverText,
    sceneNumber,
    folderName,
    voice_name="WeK8ylKjTV2trMlayizC",
    max_retries=3
):

    folder_path = os.path.join("data", folderName)
    os.makedirs(folder_path, exist_ok=True)

    final_audio_path = os.path.join(folder_path, f"Scene{sceneNumber}.mp3")

    payload = json.dumps({
        # "model": "openai-audio",
        "input": voiceOverText,
        "voice": voice_name,
        "response_format": "mp3",
        "speed": 0.9,
        "instruct": "Speak naturally in Hindi with a warm storytelling tone"
    })

    for attempt in range(1, max_retries + 1):
        try:
            conn.request("POST", "/v1/audio/speech", payload, headers)
            res = conn.getresponse()

            content_type = res.getheader("Content-Type")

            if res.status != 200:
                error_msg = res.read().decode()
                raise Exception(f"HTTP {res.status}: {error_msg}")

            if "audio" not in content_type:
                error_msg = res.read().decode()
                raise Exception(f"Invalid response: {error_msg}")

            audio_data = res.read()

            with open(final_audio_path, "wb") as f:
                f.write(audio_data)

            if verify_audio(final_audio_path):
                print(f"✅ Scene {sceneNumber} saved: {final_audio_path}")
                return final_audio_path
            else:
                print("⚠️ Invalid audio, retrying...")

        except Exception as e:
            print(f"⚠️ Attempt {attempt} failed: {e}")
            time.sleep(2)

    print(f"❌ Failed to generate audio for Scene {sceneNumber}")
    return None


def verify_audio(audio_path):
    return os.path.exists(audio_path) and os.path.getsize(audio_path) > 2000