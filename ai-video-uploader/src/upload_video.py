import json
from googleapiclient.http import MediaFileUpload
from .auth import get_youtube_client


def upload_to_youtube(video_path: str, script_path: str) -> str:
    youtube = get_youtube_client()

    with open(script_path, "r", encoding="utf-8") as f:
        script = json.load(f)

    title = script.get(
        "title",
        "99% लोग इस GK Quiz में फेल हो जाते हैं 🤯 | क्या आप पास हो सकते हैं?"
    )

    description = script.get(
        "description",
        (
            "🔥 GK Quiz Challenge 🔥\n\n"
            "इन सवालों को बिना गूगल किए हल करने की कोशिश करो 👀\n"
            "हर सवाल के लिए सिर्फ 5 सेकंड ⏱️\n\n"
            "👇 COMMENT में बताओ आपने कितने सही किए?\n\n"
            "#GKQuiz #QuizChallenge #HindiQuiz #GeneralKnowledge "
            "#BrainTest #Shorts #QuizShorts"
        )
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title[:100],          
                "description": description,
                "categoryId": "27",            
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False,
            },
        },
        media_body=MediaFileUpload(
            video_path,
            resumable=True,
            chunksize=-1
        ),
    )

    response = request.execute()
    return response["id"]