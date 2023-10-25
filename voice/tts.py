from elevenlabs import generate, play, set_api_key
import os
from dotenv import load_dotenv

class GalaxyTutorial:
    def __init__(self):
        load_dotenv()
        apikey_id = os.getenv("elevenlabs") or None
        if not apikey_id:
            raise ValueError("API key not found!")
        set_api_key(apikey_id)

    def generate_audio(self, text="할머니! 갤럭시 사용법을 알려드릴게요!!", voice="Freya", model="eleven_multilingual_v2"):
        audio = generate(text=text, voice=voice, model=model)
        return audio

    def play_audio(self, audio):
        play(audio)

if __name__ == "__main__":
    tutorial = GalaxyTutorial()
    audio_data = tutorial.generate_audio()
    tutorial.play_audio(audio_data)
