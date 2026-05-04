import subprocess
from sendTelegramNotification import send_telegram
# from dotenv import load_dotenv
# load_dotenv()

print("🚀 STARTING PIPELINE")

def run_once():
    try:
        
        send_telegram("🚀 GitHub pipeline started")
        
        print("👉 Step 1: Generating video")
        
        # 1. Generate video
        result = subprocess.run(
            ["python", "run.py"],
            cwd="ai-video-generator",
            check=True,
        )

        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        
        if result.returncode != 0:
            raise Exception("Generation failed")

        print("👉 Step 2: Uploading video")

        # 2. Upload video
        result2 = subprocess.run(
            ["python","-m", "src.watch_and_upload",],
            cwd="ai-video-uploader",
            check=True
        )
        print("STDOUT:", result2.stdout)
        print("STDERR:", result2.stderr)

        if result2.returncode != 0:
            raise Exception("Upload failed")

        print("Uploaded Properly")
        send_telegram("✅ Video uploaded successfully!")

    except Exception as e:
        send_telegram(f"❌ PIPELINE FAILED\n\n{str(e)[:1000]}")

if __name__ == "__main__":
    run_once()
