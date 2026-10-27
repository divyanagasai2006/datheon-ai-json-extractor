
import os
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv()

st.set_page_config(
    page_title="Divya's AI Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 AI Chatbot")
st.caption("Powered by Google Gemini · Built with Streamlit")

with st.sidebar:
    st.header("⚙️ Settings")
    st.write("Your AI assistant remembers messages during this session.")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("Model: Gemini Flash Lite")
    st.caption("Conversation history is stored in this browser session.")

if "messages" not in st.session_state:
    st.session_state.messages = []

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error(
        "Gemini API key not found. Please add GOOGLE_API_KEY "
        "to your .env file in this project folder."
    )
    st.stop()

@st.cache_resource
def create_model():
    return ChatGoogleGenerativeAI(
        model="gemini-flash-lite-latest",
        google_api_key=api_key,
        temperature=0.7,
        streaming=True,
    )

try:
    model = create_model()
except Exception as error:
    st.error(f"Could not initialize the AI model: {error}")
    st.stop()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask me anything...")

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    chat_history = [
        SystemMessage(
            content=(
                "You are a helpful AI assistant. "
                "Give clear, accurate answers in simple language. "
                "Remember and use the conversation history."
            )
        )
    ]

    for message in st.session_state.messages[:-1]:
        if message["role"] == "user":
            chat_history.append(
                HumanMessage(content=message["content"])
            )
        else:
            chat_history.append(
                AIMessage(content=message["content"])
            )

    chat_history.append(HumanMessage(content=prompt))

    with st.chat_message("assistant"):
        response_area = st.empty()
        full_response = ""

        try:
            for chunk in model.stream(chat_history):
                content = chunk.content

                if isinstance(content, str):
                    full_response += content
                elif isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "text":
                            full_response += item.get("text", "")

                response_area.markdown(full_response + "▌")

            response_area.markdown(full_response)

            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )

        except Exception as error:
            st.error(
                "Something went wrong while generating the response. "
                "Check your API key and internet connection, then try again."
            )
            st.caption(f"Error details: {error}")
            st.session_state.messages.pop()
