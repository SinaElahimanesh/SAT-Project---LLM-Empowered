import openai
from openai import OpenAI

client = OpenAI(
    # This is the default and can be omitted
    api_key=''
)

def openai_req_generator(system_prompt, user_prompt, json_output=False, temperature=0.01):
    if json_output:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="gpt-4o",
            # model="gpt-4o-mini",
            response_format={"type": "json_object"},
            temperature=temperature,
        )
    else:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="gpt-4o",
            # model="chatgpt-4o-latest",
            temperature=temperature,
        )
    return chat_completion.choices[0].message.content