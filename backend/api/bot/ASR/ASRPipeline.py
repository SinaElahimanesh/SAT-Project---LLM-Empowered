from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

def feed_audio_to_ASR_modal(audio_path):
    client = OpenAI(
        api_key=os.getenv('OPENAI_API_KEY'),
    )
    audio_file = open(audio_path, "rb")

    transcription = client.audio.transcriptions.create(
        file=audio_file,
        model="whisper-1",
        response_format="verbose_json",
        timestamp_granularities=["word"]
    )

    return transcription.words

