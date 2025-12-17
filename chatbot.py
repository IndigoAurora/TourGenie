import streamlit as st
import cohere
from dotenv import load_dotenv
import os
from PIL import Image
import requests
from io import BytesIO
import streamlit.components.v1 as components

# Optional: for cached image fetching (used only if needed later)
@st.cache_data(show_spinner=False)
def fetch_image(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content))

# Load environment variables
load_dotenv()
cohere_api_key = st.secrets["COHERE_API_KEY"]
co = cohere.Client(cohere_api_key)

# Set page config
st.set_page_config(page_title="TourGenie", page_icon="🧭")

# Get screen width
components.html("""
    <script>
        const width = window.innerWidth;
        document.cookie = "screen_width=" + width;
    </script>
""", height=0)
screen_width = int(st.query_params.get("screen_width", [1200])[0])

# Inject custom CSS
st.markdown("""
    <style>
    body {
        background: linear-gradient(to right, #fdfbfb, #ebedee);
    }
    .chat-bubble {
        padding: 12px 18px;
        border-radius: 10px;
        margin: 10px 0;
        font-size: 16px;
    }
    .chat-user {
        background-color: #d1f7d6;
        color: black;
        font-weight: bold;
    }
    .chat-bot {
        background-color: #2e86de;
        color: white;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.15);
        font-family: 'Segoe UI', sans-serif;
    }
    @media only screen and (max-width: 768px) {
        .chat-bubble {
            font-size: 16px !important;
        }
        input, button {
            font-size: 18px !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Title and Welcome
st.title("🧭 TourGenie")
st.subheader("Your intelligent travel guide across India 🇮🇳")
st.markdown("### 🙏 Welcome to TourGenie!")
st.markdown("Ask about destinations, weather, food, culture, or travel tips across India.")

# Clear Chat
if st.button("🧹 Clear Chat"):
    st.session_state.chat_history = [
        {"role": "System", "message": "You are a helpful tourism guide for all regions of India. Reply in a friendly, informative tone."}
    ]
    st.rerun()

# Initialize chat state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "System", "message": "You are a helpful tourism guide for all regions of India. Reply in a friendly, informative tone."}
    ]

# Sidebar chat history
with st.sidebar:
    st.markdown("### 📜 Chat History")
    for msg in st.session_state.chat_history[1:]:
        role = "👤" if msg["role"].lower() == "user" else "🤖"
        st.markdown(f"{role} {msg['message'][:50]}...")

# Quick suggestion handler
def handle_quick_input(text):
    st.session_state.user_input = text

# Quick Suggestions
st.markdown("### 🧠 Quick Suggestions:")
if screen_width < 768:
    suggestions = [
        "Suggest beach destinations in India",
        "What are some beautiful hill stations in India?",
        "List some top historical places to visit in India",
        "Which places in India are best for Instagram-worthy photos?",
        "Tell me about famous cultural festivals in India",
        "Tell me about an underrated tourist destination in India"
    ]
    for text in suggestions:
        if st.button(text):
            handle_quick_input(text)
else:
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🏝️ Beaches"): handle_quick_input("Suggest beach destinations in India")
    with col2:
        if st.button("🏔️ Hill Stations"): handle_quick_input("What are some beautiful hill stations in India?")
    with col3:
        if st.button("🏛️ Historical Places"): handle_quick_input("List some top historical places to visit in India")
    col4, col5, col6 = st.columns(3)
    with col4:
        if st.button("📸 Instagram Spots"): handle_quick_input("Which places in India are best for Instagram-worthy photos?")
    with col5:
        if st.button("🎉 Cultural Festivals"): handle_quick_input("Tell me about famous cultural festivals in India")
    with col6:
        if st.button("🎁 Surprise Me!"): handle_quick_input("Tell me about an underrated tourist destination in India")

# Destination Type Filter
st.markdown("### 🔍 Filter by Type:")
option = st.selectbox("Choose a type of destination:", ["", "Beaches", "Hill Stations", "Heritage Sites", "Wildlife", "Spiritual", "Adventure"])
if option:
    st.session_state.user_input = f"Show me the best {option.lower()} in India"

# User Input
# 💬 Ask your own question
st.markdown("### 💬 Ask your own question:")
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("You:", placeholder="Type your travel question here...")
    submit_button = st.form_submit_button("Send")

if submit_button and user_input:
    st.session_state.chat_history.append({"role": "User", "message": user_input})
    with st.spinner("🤖 TourGenie is typing..."):
        response = co.chat(
            model="command-nightly",
            message=user_input,
            temperature=0.7,
            chat_history=st.session_state.chat_history
        )
        st.session_state.chat_history.append({"role": "Chatbot", "message": response.text})

# Custom Itinerary Button
if st.button("📅 Generate Custom 3-Day Itinerary"):
    st.session_state.user_input = "Plan a 3-day itinerary for a trip to India"


# Chat Display
chat_pairs = st.session_state.chat_history[1:]
paired = []
for i in range(0, len(chat_pairs), 2):
    try:
        user_msg = chat_pairs[i]
        bot_msg = chat_pairs[i + 1]
        paired.append((user_msg, bot_msg))
    except IndexError:
        pass

st.markdown("## 🗨️ Conversation:")
for idx, (user_msg, bot_msg) in enumerate(paired[::-1]):
    st.markdown(f"<div class='chat-bubble chat-user'>🧑 You: {user_msg['message']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='chat-bubble chat-bot'>🤖 TourGenie: {bot_msg['message']}</div>", unsafe_allow_html=True)

    st.markdown("Was this helpful?")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("👍", key=f"like-{idx}")
    with col2:
        st.button("👌", key=f"okay-{idx}")
    with col3:
        st.button("👎", key=f"dislike-{idx}")
