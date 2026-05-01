import os
import json
from src.script_writer import generate_quiz , save_used_topic
from src.generateImage import generate_quiz_images
from src.generateAudio import generate_voice
from src.generateVideo import generate_video

def run():
    scene_data = generate_quiz()
   
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(BASE_DIR, "data", "File_To_Upload")
    os.makedirs(folder_path, exist_ok=True)
    
    scriptPath = os.path.join(folder_path, "Script.json")
    with open(scriptPath, 'w', encoding="utf-8") as f:
            json.dump(scene_data, f, ensure_ascii=False, indent=4)
    
    print("Scene generated successfully")
    allQuestions = ""
    for i in range(len(scene_data['questions'])):
        voice = scene_data['questions'][i]['question']
        allQuestions += scene_data['questions'][i]['question']
        allQuestions += " \n "
        generate_quiz_images(
            question=scene_data['questions'][i]['question'],
            options=scene_data['questions'][i]['options'],
            correct_answer=scene_data['questions'][i]['correctAnswer'],
            output_prefix = f"quiz_{i}"
        )  
        generate_voice(voice, i, "File_To_Upload")  
    
    generate_video("File_To_Upload", scene_data, folder_path)
    save_used_topic(allQuestions)

if __name__ == "__main__":
    run()
