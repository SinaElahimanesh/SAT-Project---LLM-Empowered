

from backend.api.bot.gpt import openai_req_generator


def create_recommendations(bot_message):
    suggestions = openai_req_generator(f"""You are tasked with assisting in a dialogue between two parties.
                          Given the message from one side, your goal is to generate three concise and actionable suggestions that the other side
                          could provide in response. Each suggestion should be brief, contextually relevant, and formatted clearly as:
                          suggestion1 / suggestion2 / suggestion3.
                          Ensure that the responses are thoughtful, aligned with the conversation's context, and maintain a neutral tone.
                                       The output language should be in Farsi.
                                       MESSAGE FROM ONE SIDE: {bot_message}""", "")
    suggestions = suggestions.split("/")
    return suggestions