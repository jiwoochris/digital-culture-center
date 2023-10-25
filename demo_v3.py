import openai
import streamlit as st
from audiorecorder import audiorecorder
from voice.tts import GalaxyTutorial
from voice.stt import NaverSTT

from contents_generation import run_chat_session

import json

def get_last_line(filename):
    last_line = None
    with open(filename, 'r') as file:
        for line in file:
            last_line = line
    if last_line:
        return json.loads(last_line)
    return None

from googletrans import Translator

def translate_korean_to_english(text):
    translator = Translator()
    result = translator.translate(text, src='ko', dest='en')
    return result.text


# Styling
st.markdown("""
<style>
    .reportview-container {
        background-color: #f4f4f4;
    }
    .chat-message.user {
        background-color: #FFDDC1;
    }
    .chat-message.assistant {
        background-color: #C1FFD7;
    }
    .sidebar .block-container {
        background-color: #FFF5E1;
    }
</style>
""", unsafe_allow_html=True)

st.title("디지털 문화센터")

st.markdown("안녕하세요 디지털 문화센터에 오신 것을 환영합니다. 왼쪽의 공간에서 원하시는 수업을 눌러주세요. 잡담을 원하시면 바로 입력해주세요. 녹음 버튼을 누르면 음성으로도 대화할 수 있습니다.")

openai.api_key = st.secrets["OPENAI_API_KEY"]

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "너는 어르신을 상대하는 챗봇이야. 지루하지 않게 대화를 계속 이어나가줘."}]

# Sidebar
with st.sidebar:
    st.title("🔧 설정")
    
    # Add buttons for different activities
    if st.button("디지털 교육"):

        with st.spinner("디지털 교육 콘텐츠를 만드는 중입니다...💫"):
            run_chat_session()

            last_data = get_last_line("data.jsonl")
            if last_data:
                subject = last_data.get("subject", None)
                mission = last_data.get("mission", None)

        st.session_state.messages = [{"role": "system", "content": f"목적: 디지털기기를 잘 모르는 노인에게 주제에 대화하면서 주제에 대해서 잘 이해할 수 있도록 알기 쉬운 예시를 들고 최대한 쉽게 대화를 진행하는 챗봇처럼 사용자에게 답변을 듣고 다음 답변 생성하기\n주제: {subject}\n미션: {mission}\n조건1: 대화 내용을 생성하는 것이 아니라 사용자에게 묻고 답하는 방식으로 답변\n조건2: 첫 대화는 먼저 사용자에게 주제에 대한 질문을 하면서 시작하기\nEx)  오늘은 \"주제\" 에 대해서 같이 대화해볼거에요. \"주제\" 에 대해서 들어보신 적이 있나요?\n조건3: 대화 마지막에 미션을 제시하므로 사용자가 배운 내용에 대한 실습을 할 수 있도록 하기"},{"role": "assistant", "content": f"디지털 교육을 시작합니다. 오늘 배워볼 주제는 \"{subject}\" 입니다!!"}]
        st.experimental_rerun()

    if st.button("Ai로 그림그리기"):
        st.session_state.messages = [{"role": "system", "content": "Ai 그림 그리기"},{"role": "assistant", "content": f"Ai 그림 그리기 놀이를 시작합니다. 원하는 그림 주제를 말해주세요."}]
        st.experimental_rerun()

    if st.button("간식만들기"):
        st.session_state.messages = [{"role": "system", "content": "너는 사용자가 식재료를 말하면 그 식재료들로 어떤 음식을 만들 수 있는지 알려주고 레시피를 알려주는 챗봇이야. 제공된 재료 이외에 다른 재료는 쓸 수 없어. 사용자에게 어떤 식재료를 가지고 있는지 먼저 질문한 후에 사용자의 답변에 따라서 원하는 음식을 만드는 방법을 단계별로 차근차근 이해하기 쉽게 알려줘. "},{"role": "assistant", "content": f"요리 교실을 시작할게요. 집에 있는 재료를 말씀해주시면 그에 맞는 레시피를 만들어드릴게요!!"}]
        st.experimental_rerun()
    
    if st.button("무엇이든 알려드릴게요"):
        st.session_state.messages = [{"role": "system", "content": "너는 친절하게 알려주는 챗봇이야. 천천히 말해줘."},{"role": "assistant", "content": f"무엇이든 물어보세요!!"}]
        st.experimental_rerun()

    # Start recording
    audio = audiorecorder("🎙️ Click to record", "🛑 Click to stop recording")

# Display messages
for message in st.session_state.messages:
    if message["role"] != "system":  # Skip the system messages
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


    
prompt = None

# Check if audio is recorded
if len(audio) > 0:
    audio.export("audio.wav", format="wav")
    stt = NaverSTT()
    transcribed_text = stt.transcribe("audio.wav")
    prompt = transcribed_text[9:-2]

# Always show the chat input field, regardless of recording
typed_input = st.chat_input("What is up?")
if typed_input:
    prompt = typed_input

# Process the prompt
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if "Ai 그림 그리기" in st.session_state.messages[0]["content"]:

        translated_prompt = translate_korean_to_english(prompt) + ", high quality drawing"
        print(translated_prompt)

        with st.spinner("Ai가 그림을 그리는 중입니다...💫"):
            response = openai.Image.create(
            prompt=translated_prompt,
            n=1,
            size="512x512",
            )
            
            image_url = response['data'][0]['url']

            print(image_url)

            st.image(image_url, caption='Generated by OpenAI')

    else:
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for response in openai.ChatCompletion.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            ):
                full_response += response.choices[0].delta.get("content", "")
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

        # Convert the assistant's response to audio
        tutorial = GalaxyTutorial()
        audio_data = tutorial.generate_audio(full_response)
        st.audio(audio_data, format='audio/wav')
