import os
import streamlit as st
from google import genai
from google.genai import types

# --- Page Configuration ---
st.set_page_config(
    page_title="OKIROR AI — Intelligent Assistant",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- Custom Styling (Fixed Text Contrast) ---
st.markdown("""
<style>
    /* Main app background */
    .stApp {
        background: #0e1117;
        color: #f3f4f6;
    }

    /* Target headers */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-family: 'Inter', -apple-system, sans-serif;
    }

    /* Force all chat message text to be crisp light text */
    div[data-testid="stChatMessage"] {
        background-color: #1e293b !important;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        border: 1px solid #334155 !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }

    div[data-testid="stChatMessage"] * {
        color: #f8fafc !important;
    }

    /* Sidebar text colors */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b;
    }

    section[data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }

    /* Text area and input field formatting */
    textarea, input {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border: 1px solid #475569 !important;
    }

    /* Metric card text fix */
    div[data-testid="stMetricValue"] {
        color: #38bdf8 !important;
        font-weight: 600;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
    }

    /* Subtitles and captions */
    .stCaption {
        color: #94a3b8 !important;
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
    st.title("✨ OKIROR'S AI")
    st.caption("Next-Gen Intelligent Workspace Companion")
with col2:
    st.metric(label="Model", value="Gemini 3.6 Flash")

st.divider()

# --- Sidebar Controls ---
with st.sidebar:
    st.markdown("### Control Panel")
    st.markdown("Customize assistant parameters and conversation state.")

    system_instruction = st.text_area(
        "Persona & Instructions",
        value="You are OKIROR'S AI, a high-level AI assistant. Provide concise, modern, accurate, and professional answers.",
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
if prompt := st.chat_input("Ask OKIROR'S AI anything..."):
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
