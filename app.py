import os
import streamlit as st
from google import genai
from google.genai import types

# --- Page Configuration ---
st.set_page_config(
    page_title="Aura AI — Intelligent Assistant",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- Custom Styling (CSS Injection) ---
st.markdown("""
<style>
    /* Main app padding & clean background accent */
    .stApp {
        background: linear-gradient(135deg, #0e1117 0%, #161b22 100%);
    }

    /* Target headers */
    h1 {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        font-weight: 700;
        letter-spacing: -0.5px;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Styled metric status cards */
    div[data-testid="stMetricValue"] {
        font-size: 1.1rem !important;
        font-weight: 600;
    }

    /* Glassmorphism sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.7);
        backdrop-filter: blur(12px);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* Custom Chat Container styling */
    div[data-testid="stChatMessage"] {
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    /* Subtle divider */
    hr {
        margin: 1.5rem 0;
        border-color: rgba(255, 255, 255, 0.08);
    }

    /* Polish buttons */
    div.stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        border-color: #38bdf8;
        color: #38bdf8;
    }
</style>
""", unsafe_allow_html=True)

# --- Initialize API Client ---
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error(
        "🔑 API Key missing. Please add `GEMINI_API_KEY` to your Streamlit secrets.")
    st.stop()


@st.cache_resource
def get_genai_client(key: str):
    return genai.Client(api_key=key)


client = get_genai_client(api_key)

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Header Section ---
col1, col2 = st.columns([3, 1])
with col1:
    st.title("✨ Aura AI")
    st.caption("Next-Gen Intelligent Workspace Companion")
with col2:
    st.metric(label="Model", value="Gemini 3.6 Flash")

st.divider()

# --- Sidebar Controls ---
with st.sidebar:
    st.image("https://img.icons8.com/gradient/96/000000/bot.png", width=64)
    st.markdown("### Control Panel")
    st.markdown("Customize assistant parameters and conversation state.")

    system_instruction = st.text_area(
        "Persona & Instructions",
        value="You are Aura, a high-level AI assistant. Provide concise, modern, accurate, and professional answers.",
        help="Defines how the chatbot speaks and formats output.",
        height=120
    )

    st.divider()

    st.markdown("#### Conversation")
    msg_count = len(st.session_state.messages)
    st.caption(f"Active messages in history: **{msg_count}**")

    if st.button("🗑️ Clear Chat History", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.rerun()

# --- Render Chat History ---
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "✨"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- User Input & Response Generation ---
if prompt := st.chat_input("Ask Aura anything..."):
    # Append & display user prompt
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Generate assistant response with streaming
    with st.chat_message("assistant", avatar="✨"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # Format chat history for API payload
            contents = []
            for msg in st.session_state.messages:
                role = "user" if msg["role"] == "user" else "model"
                contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=msg["content"])]
                    )
                )

            # Request streaming response
            response_stream = client.models.generate_content_stream(
                model="gemini-3.6-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction
                )
            )

            for chunk in response_stream:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

            # Save assistant message
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"⚠️ Connection error: {str(e)}")
