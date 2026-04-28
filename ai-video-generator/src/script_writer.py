import json
import os
from google import genai
import re

LATIN_PATTERN = re.compile(r'[A-Za-z]')

def is_devanagari(text: str) -> bool:
    if not text:
        return True
    
    return not bool(LATIN_PATTERN.search(text))

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
TOPICS_FILE = os.path.join(DATA_DIR, "usedQuizTopics.json")


# ===================== TOPIC MEMORY =====================

def is_hindi_start(text):
    if not text:
        return False
    return not text[0].isascii()

def load_used_topics(file_path=TOPICS_FILE):
    if not os.path.exists(file_path):
        return set()

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return set(data.get("topics", []))


def save_used_topic(topic, file_path=TOPICS_FILE):
    topics = []

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            topics = data.get("topics", [])

    if topic not in topics:
        topics.append(topic)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump({"topics": topics}, f, indent=4, ensure_ascii=False)


# ===================== QUIZ GENERATION =====================

def generate_quiz():
    used_topics = load_used_topics()
    used_topics_text = ", ".join(used_topics) if used_topics else "None"

    prompt = prompt = f"""
You are a VIRAL QUIZ CONTENT CREATOR for YouTube Shorts & Instagram Reels.

Your goal is NOT just to ask questions.
Your goal is to MAXIMIZE RETENTION and COMMENTS.

━━━━━━━━━━━━━━━━━━
LANGUAGE RULES (STRICT):

- Title → ENGLISH (viral, curiosity-based)
- Description → ENGLISH (engaging, CTA heavy)
- ALL questions → PURE HINDI (Devanagari only)
- ALL options → PURE HINDI
- NO English words inside questions/options

━━━━━━━━━━━━━━━━━━
VIRAL STRUCTURE:

- Hook curiosity instantly
- Make user feel “I think I know this… or do I?”
- Encourage self-testing + ego challenge

━━━━━━━━━━━━━━━━━━
QUESTION RULES:

- EXACTLY 5 questions
- Medium difficulty
- Not basic, not too hard
- Answerable in 3–5 seconds
- Slightly tricky / confusing / surprising

❌ Avoid:
- obvious GK
- boring textbook questions

✅ Prefer:
- “Wait… really?” type facts
- commonly misunderstood facts
- tricky comparisons

━━━━━━━━━━━━━━━━━━
TITLE RULES (VERY IMPORTANT):

- English only
- 5–10 words
- MUST feel like a challenge or shock

Examples:
- "99% People Fail This Quiz 😱"
- "Only Smart Minds Can Pass This 🤯"
- "Can You Get 3/5 Right?"

━━━━━━━━━━━━━━━━━━
DESCRIPTION RULES:

- English only
- 2–3 lines
- MUST include:
  - Call to action (comment score)
  - Time pressure (5 seconds)
  - Hashtags (#quiz #gk #shorts)

Example:
"Test your brain in 5 seconds per question ⏳  
Comment your score below 👇  
#gk #quiz #shorts"

━━━━━━━━━━━━━━━━━━
OUTPUT FORMAT (STRICT JSON):

{{
  "quizTopic": "General Knowledge",
  "title": "...",
  "description": "...",
  "questions": [
    {{
      "question": "... (Hindi)",
      "options": {{
        "A": "...",
        "B": "...",
        "C": "...",
        "D": "..."
      }},
      "correctAnswer": "A"
    }}
  ]
}}

ONLY JSON. NO EXTRA TEXT.
"""
    
    MAX_RETRIES = 5

    for attempt in range(MAX_RETRIES):
        response = client.models.generate_content(
            model="models/gemini-flash-latest",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "temperature": 0.3
            }
        )

        result = json.loads(response.text)

        valid = True

        for q in result.get("questions", []):
            if not is_hindi_start(q.get("question", "")):
                valid = False
                break

            for opt in q.get("options", {}).values():
                if not is_hindi_start(opt):
                    valid = False
                    break

        if not valid:
            print("⚠️ Non-Hindi detected, regenerating...")
            continue
        
        return result

    raise Exception("Failed to generate pure Hindi quiz after retries")


# ===================== RUN =====================

if __name__ == "__main__":
    quiz_data = generate_quiz()
    print(json.dumps(quiz_data, indent=4, ensure_ascii=False))
