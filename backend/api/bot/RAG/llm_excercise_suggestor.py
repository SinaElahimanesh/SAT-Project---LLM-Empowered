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


def get_exercise_content(exercise_tuples: List[Tuple[int, float]]) -> List[str]:
    """
    Get the content of exercises from their numbers and similarity scores.
    
    Args:
        exercise_tuples: List of tuples containing (exercise_number, similarity_score)
        
    Returns:
        List of exercise contents as strings
    """
    exercise_contents = []
    
    for exercise_num, _ in exercise_tuples:
        file_path = f'backend/api/bot/RAG/Exercises/exercise{exercise_num}.txt'
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                exercise_contents.append(content)
        except FileNotFoundError:
            print(f"Exercise file {file_path} not found")
            continue
            
    return exercise_contents, [exercise_num for exercise_num, _ in exercise_tuples]

def suggest_exercises(done_exercises: List[str], user_memory: str, user_stage: str) -> List[dict]:
    # Filter out exercises that have been done
    available_exercises = [
        exercise for exercise in exercises 
        if exercise["Exercise Number"] not in done_exercises
    ]
    system_prompt = system_prompt.format(memory=user_memory, stage=user_stage, exc=available_exercises)

    excs_nums = openai_req_generator(system_prompt=system_prompt).split(',')
    return excs_nums



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

# todo: add enum for stage, reranking