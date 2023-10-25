import openai
import streamlit as st
from audiorecorder import audiorecorder
from voice.tts import GalaxyTutorial  # Not used in this code snippet
from voice.stt import NaverSTT

st.title("디지털 문화센터에 오신 것을 환영합니다")

openai.api_key = st.secrets["OPENAI_API_KEY"]

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Start recording
audio = audiorecorder("Click to record", "Click to stop recording")

prompt = None

# Check if audio is recorded
if len(audio) > 0:
    # To save audio to a file, use pydub export method:
    audio.export("audio.wav", format="wav")

    # Transcribe the audio
    stt = NaverSTT()
    transcribed_text = stt.transcribe("audio.wav")

    # Use the transcribed text as a prompt (I'm assuming you are trying to slice the result to get meaningful content)
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
