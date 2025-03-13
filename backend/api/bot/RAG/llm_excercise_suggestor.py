import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from typing import List, Tuple
import glob
import re
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load exercises from JSON file
with open('backend/api/bot/RAG/exercises_mapping.json', 'r', encoding='utf-8') as f:
    exercises = json.load(f)


def get_exercise_content(ids):
    exercise_contents = []
    
    for exercise_num in ids:
        file_path = f'backend/api/bot/RAG/Exercises/exercise{exercise_num}.txt'
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                exercise_contents.append(content)
        except FileNotFoundError:
            print(f"Exercise file {file_path} not found")
            continue
            
    return exercise_contents

def suggest_exercises(done_exercises: List[str], user_memory: str, user_stage: str):
    # Filter out exercises that have been done
    available_exercises = [
        exercise for exercise in exercises 
        if exercise["Exercise Number"] not in done_exercises
    ]
    
    # First get 3 potential exercises using the initial prompt
    with open('backend/api/bot/RAG/prompt.md', 'r', encoding='utf-8') as f:
        system_prompt = f.read()
    
    system_prompt = system_prompt.format(
        memory=user_memory, 
        stage=user_stage, 
        exc=available_exercises, 
        done_before=','.join(done_exercises) if done_exercises else "None"
    )

    potential_excs_nums = openai_req_generator(system_prompt=system_prompt).split(',')
    potential_excs_nums = [exc_num.strip() for exc_num in potential_excs_nums]
    
    # Get the content and metadata for these potential exercises
    exercises_contents = get_exercise_content(potential_excs_nums)
    
    # Get metadata for the potential exercises
    potential_exercises_metadata = [
        exercise for exercise in exercises
        if exercise["Exercise Number"] in potential_excs_nums
    ]
    
    # Use the exercise decider to choose the best exercise
    with open('backend/api/bot/RAG/exercise_decider.md', 'r', encoding='utf-8') as f:
        decider_prompt = f.read()
    
    # Format a structured prompt with all the data needed for decision
    exercise_data = []
    for i, exc_num in enumerate(potential_excs_nums):
        metadata = next((e for e in potential_exercises_metadata if e["Exercise Number"] == exc_num), {})
        exercise_data.append({
            "Number": exc_num,
            "Content": exercises_contents[i] if i < len(exercises_contents) else "Content not available",
            "Task": metadata.get("Task", ""),
            "Stage": metadata.get("Stage", ""),
            "Circumstance": metadata.get("Circumstance", ""),
            "Benefits": metadata.get("Benefits", ""),
            "Why": metadata.get("Why", "")
        })
    
    decision_prompt  = decider_prompt.format(
        memory=user_memory, 
        stage=user_stage, 
        exc=exercise_data, 
        done_before=','.join(done_exercises) if done_exercises else "None"
    )
    
    # Get the final chosen exercise number
    chosen_exc_num = openai_req_generator(system_prompt=decision_prompt).strip()
    
    # Get the content for the chosen exercise
    chosen_exc_content = get_exercise_content([chosen_exc_num])
    
    return chosen_exc_content



load_dotenv()

client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
)

def openai_req_generator(system_prompt):
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt}
        ],
        model="gpt-4o",
        temperature=0.05,
    )
    return chat_completion.choices[0].message.content


# todo change 2 --> 2a, 2b

