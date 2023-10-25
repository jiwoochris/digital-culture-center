import os
import contents_generation
import json
from dotenv import load_dotenv
import openai

class OpenAIChat:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key

    def get_response(self, system_message, user_message):
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
        )
        return completion
    
def parse_text(text):
    lines = text.strip().split("\n")
    
    subject = lines[0].split(":")[1].strip()
    mission = lines[1].split(":")[1].strip()

    return {"subject": subject, "mission": mission}

def append_to_jsonl(data, filename="data.jsonl"):
    with open(filename, 'a', encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

    

def get_last_5_messages_from_jsonl(filename):
    messages = []
    with open(filename, 'r', encoding="utf-8") as f:
        for line in reversed(f.readlines()):  # 읽기 시작 위치를 파일의 끝으로 설정
            messages.append(json.loads(line))
            if len(messages) == 5:
                break
    return messages


def run_chat_session(filename="data.jsonl"):
    chat = OpenAIChat()
    system_message = """디지털 기기를 어떻게 사용하는지 잘 모르는 노인에게 챗봇으로 디지털 기기 사용법과 디지털 기기를 이용하여 할 수 있는 다양한 활동에 대해 알려줄 때 어떤 주제로 대화를 하면 좋을지 주제에 대한 부연 설명 없이 주제를 하나 먼저 출력하고, 주제를 일상속에서 실천해볼 수 있는 재미있는 미션을 하나만 출력해줘.
    유저가 제시한 (주제, 미션) 쌍은 이전에 했던 주제, 미션들이야. 웬만하면 겹치지 않게 참고해서 만들어줘.
    포맷은
    주제:ㅁㅁㅁ
    미션:ㅁㅁㅁ
    """

    last_5_messages = get_last_5_messages_from_jsonl(filename)
    user_message_content = last_5_messages[-1] if last_5_messages else {}
    user_message = f"{user_message_content.get('subject', 'Your user message here')} {user_message_content.get('mission', '')}".strip()

    response = chat.get_response(system_message, user_message).choices[0]['message'].content
    print(response)

    parsed_data = parse_text(response)
    append_to_jsonl(parsed_data, filename)

if __name__ == "__main__":
    run_chat_session()
