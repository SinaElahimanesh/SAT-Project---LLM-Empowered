from api.bot.gpt import openai_req_with_history
from api.bot.gpt_recommendations import create_recommendations

# Use the new comprehensive FSM prompt for the simple bot
PROMPT_PATH = 'api/bot/Prompts/simple_fsm_full.md'

def load_system_prompt():
    with open(PROMPT_PATH, 'r', encoding='utf-8') as f:
        return f.read()

SYSTEM_PROMPT = load_system_prompt()

def simple_bot_response(history, user_message):
    """
    Accepts a list of previous messages (history) and a new user message.
    Returns: (response, recommendations, updated_history)
    """
    # Build the messages list for the LLM: system prompt, then history, then new user message
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    # Call the LLM with the full message history
    response = openai_req_with_history(messages, temperature=0.1)
    # Add the assistant's response to the history
    updated_history = (history or []) + [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": response}
    ]
    recommendations = create_recommendations(response, memory="")
    return response, recommendations, updated_history 