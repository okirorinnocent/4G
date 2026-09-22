import re
import streamlit as st
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

st.set_page_config(page_title="WhatsApp ChatterBot App", layout="centered")

st.title("WhatsApp Chatbot Trainer & Interface")


# --- Text Cleaning Helper Functions ---
def remove_chat_metadata(content):
    """Removes timestamps and user metadata from WhatsApp chat export string[cite: 1]."""
    # Pattern: 14/08/2025, 9:19 at night - monicaiyb:[cite: 1]
    pattern = r"\d+/\d+/\d+,\s\d+:\d+(?:\s(?:am|pm|at\s(?:night|morning|afternoon|noon)))?\s-\s[^:]+:\s"
    cleaned_corpus = re.sub(pattern, "", content)
    return tuple(cleaned_corpus.split("\n"))


def remove_non_message_text(export_text_lines):
    """Filters out non-message content and media notifications[cite: 1]."""
    messages = export_text_lines[1:-1]
    filter_out_msgs = ("<Media omitted>",)
    return tuple((msg.strip() for msg in messages if msg.strip() not in filter_out_msgs))


def full_clean(
    messages,
    lowercase=True,
    remove_url=True,
    remove_whitespace=True,
    remove_empty=True,
):
    """Applies general text cleaning routines[cite: 1]."""
    cleaned = []
    for msg in messages:
        text = msg
        if lowercase:
            text = text.lower()
        if remove_url:
            text = re.sub(r"http\S+|www\.\S+", "", text)
        if remove_whitespace:
            text = " ".join(text.split())
        if remove_empty and not text:
            continue
        cleaned.append(text)
    return cleaned


def prepare_for_chatbot(raw_chat_text):
    """Pipeline to prepare raw WhatsApp text for ChatterBot training[cite: 1]."""
    message_corpus = remove_chat_metadata(raw_chat_text)
    cleaned_corpus = remove_non_message_text(message_corpus)
    final_corpus = full_clean(
        cleaned_corpus,
        lowercase=True,
        remove_url=True,
        remove_whitespace=True,
        remove_empty=True,
    )
    return final_corpus


# --- Streamlit Session State Management ---
if "chatbot" not in st.session_state:
    st.session_state.chatbot = ChatBot("WhatsAppBot")

if "trained" not in st.session_state:
    st.session_state.trained = False

if "messages" not in st.session_state:
    st.session_state.messages = []


# --- Sidebar: Dataset Upload & Training ---
st.sidebar.header("1. Upload & Train Model")
uploaded_file = st.sidebar.file_uploader(
    "Upload chat.txt export", type=["txt"])

if uploaded_file is not None:
    raw_text = uploaded_file.read().decode("utf-8")
    cleaned_messages = prepare_for_chatbot(raw_text)

    st.sidebar.subheader("Dataset Statistics")
    st.sidebar.write(f"**Total messages:** {len(cleaned_messages)}")

    if cleaned_messages:
        total_words = sum(len(msg.split()) for msg in cleaned_messages)
        avg_words = total_words / len(cleaned_messages)
        st.sidebar.write(f"**Total words:** {total_words}")
        st.sidebar.write(f"**Average words per message:** {avg_words:.2f}")

    if st.sidebar.button("Train Chatbot"):
        with st.spinner("Training ChatterBot..."):
            trainer = ListTrainer(st.session_state.chatbot)
            trainer.train(list(cleaned_messages))
            st.session_state.trained = True
        st.sidebar.success("Training complete!")


# --- Main Interface: Chat Section ---
st.header("2. Chat with the Bot")

# Display previous conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Chat Input
if prompt := st.chat_input("Type your message..."):
    # Add user message to display
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        if not st.session_state.trained:
            response_text = "The chatbot hasn't been trained yet. Please upload a chat file and click 'Train Chatbot' first."
        else:
            bot_response = st.session_state.chatbot.get_response(prompt)
            response_text = str(bot_response)

        st.markdown(response_text)
        st.session_state.messages.append(
            {"role": "assistant", "content": response_text}
        )
