
import os
import streamlit as st
from dotenv import load_dotenv
from google import genai

load_dotenv()

# Set up Gemini API client
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key = None

st.set_page_config(
    page_title="Chatbot with Memory",
    page_icon="💬",
    layout="centered"
)

st.title("💬 Chatbot with Memory")
st.caption("I'll remember what we discuss in this chat!")

# Create the conversation memory
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# Create the Gemini client
if api_key:
    client = genai.Client(api_key=api_key)
else:
    client = None
    st.warning("Please configure your GEMINI_API_KEY.")

# Display previous messages
for message in st.session_state.conversation:
    role = "user" if message["role"] == "user" else "assistant"

    with st.chat_message(role):
        st.markdown(message["parts"][0]["text"])

# Clear conversation button
if st.button("🗑️ Clear conversation"):
    st.session_state.conversation = []
    st.rerun()

# Get new user input
user_message = st.chat_input("Type your message...")

if user_message and client:
    # Add the user's message to memory
    st.session_state.conversation.append({
        "role": "user",
        "parts": [{"text": user_message}]
    })

    # Display the user's message immediately
    with st.chat_message("user"):
        st.markdown(user_message)

    # Send the entire conversation to Gemini
    try:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=st.session_state.conversation
                )

                reply = response.text or "I couldn't generate a reply."
                st.markdown(reply)

        # Add Gemini's response to memory
        st.session_state.conversation.append({
            "role": "model",
            "parts": [{"text": reply}]
        })

    except Exception as e:
        # Remove the failed user message so history stays valid
        st.session_state.conversation.pop()
        st.error(f"Something went wrong: {e}")
