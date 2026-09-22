import os
import streamlit as st
from google import genai
from google.genai import types

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Chat Assistant",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Modern AI Assistant")
st.caption("Powered by Google GenAI & Streamlit")

# --- Initialize API Client ---
# Fetches key from Streamlit secrets (or environment variables)
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("🔑 API Key not found. Please add `GEMINI_API_KEY` to your Streamlit secrets or environment variables.")
    st.stop()


@st.cache_resource
def get_genai_client(key: str):
    return genai.Client(api_key=key)


client = get_genai_client(api_key)

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar Controls ---
with st.sidebar:
    st.header("Settings")

    system_instruction = st.text_area(
        "System Instruction",
        value="You are a helpful, precise, and concise AI assistant.",
        help="Guide how the chatbot behaves."
    )

    if st.button("Clear Chat History", type="secondary"):
        st.session_state.messages = []
        st.rerun()

# --- Render Existing Chat Messages ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Handle User Input & Stream Response ---
if prompt := st.chat_input("How can I help you today?"):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response with streaming
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # Format chat history into contents for the API call
            contents = []
            for msg in st.session_state.messages:
                role = "user" if msg["role"] == "user" else "model"
                contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=msg["content"])]
                    )
                )

            # Request response stream from Gemini
            response_stream = client.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
                )
            )

            for chunk in response_stream:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

            # Save assistant response to session
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(
                f"An error occurred while generating a response: {str(e)}")
