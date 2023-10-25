import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()

class NaverSTT:
    def __init__(self, client_id=None, client_secret=None, lang="Kor"):
        self.base_url = "https://naveropenapi.apigw.ntruss.com/recog/v1/stt?lang="
        self.lang = lang
        
        self.client_id = client_id or os.getenv("client_id") or None
        self.client_secret = client_secret or os.getenv("client_secret") or None

    def get_headers(self):
        return {
            "Content-Type": "application/octet-stream",
            "X-NCP-APIGW-API-KEY-ID": self.client_id,
            "X-NCP-APIGW-API-KEY": self.client_secret,
        }

    def transcribe(self, file_path):
        with open(file_path, "rb") as data:
            response = requests.post(self.base_url + self.lang, data=data, headers=self.get_headers())
            rescode = response.status_code

            if rescode == 200:
                return response.text
            else:
                return "Error : " + response.text

if __name__ == "__main__":
    # Usage
    client_id = "your_client_id"
    client_secret = "your_secret"
    file_path = "your/path/to/voice.mp3"

    stt = NaverSTT(client_id, client_secret)
    result = stt.transcribe(file_path)
    print(result)