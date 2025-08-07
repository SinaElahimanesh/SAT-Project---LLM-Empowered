import os
import random
from api.bot.gpt import openai_req_with_history
from api.bot.gpt_recommendations import create_recommendations


PROMPT_PATH = 'api/bot/Prompts/simple_fsm_full.md'
EXERCISES_DIR = 'api/bot/RAG/Exercises'


def load_system_prompt():
    with open(PROMPT_PATH, 'r', encoding='utf-8') as f:
        return f.read()


def get_random_exercises(count=5):
    """Get random exercises from the exercises directory"""
    try:
        exercise_files = [f for f in os.listdir(EXERCISES_DIR) if f.startswith('exercise') and f.endswith('.txt')]

        selected_files = random.sample(exercise_files, min(count, len(exercise_files)))

        exercises = []
        for file_name in selected_files:
            file_path = os.path.join(EXERCISES_DIR, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    exercises.append(f"تمرین {file_name.replace('exercise', '').replace('.txt', '')}: {content}")
            except Exception as e:
                print(f"Error reading {file_name}: {e}")
                continue

        return "\n\n".join(exercises)
    except Exception as e:
        print(f"Error getting random exercises: {e}")
        return "تمرین‌های نمونه در دسترس نیستند."


def simple_bot_response(history, user_message):
    """
    Accepts a list of previous messages (history) and a new user message.
    Returns: (response, recommendations, updated_history)
    """
    random_exercises = get_random_exercises(5)

    system_prompt = load_system_prompt()
    formatted_system_prompt = system_prompt.format(random_exercises=random_exercises)

    messages = [{"role": "system", "content": formatted_system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    response = openai_req_with_history(messages, temperature=0.1)
    updated_history = (history or []) + [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": response}
    ]
    recommendations = create_recommendations(response, memory="")
    return response, recommendations, updated_history
