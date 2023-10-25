import openai
import streamlit as st
from audiorecorder import audiorecorder
from voice.tts import GalaxyTutorial
from voice.stt import NaverSTT

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

openai.api_key = st.secrets["OPENAI_API_KEY"]

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    # Initialize with a system prompt
    st.session_state.messages = [{"role": "system", "content": "너는 어르신을 상대하는 챗봇이야. 지루하지 않게 대화를 계속 이어나가줘."}]

for message in st.session_state.messages:
    if message["role"] != "system":  # Skip the system messages
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Sidebar
with st.sidebar:
    st.title("🔧 설정")
    
    # Start recording
    audio = audiorecorder("🎙️ Click to record", "🛑 Click to stop recording")
    
    prompt = None

    # Check if audio is recorded
    if len(audio) > 0:
        # To save audio to a file, use pydub export method:
        audio.export("audio.wav", format="wav")

        # Transcribe the audio
        stt = NaverSTT()
        transcribed_text = stt.transcribe("audio.wav")

        # Use the transcribed text as a prompt
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

    # Convert the assistant's response to audio
    tutorial = GalaxyTutorial()
    audio_data = tutorial.generate_audio(full_response)  # Convert the text response to audio
    st.audio(audio_data, format='audio/wav')  # Play the audio in Streamlit
