from dotenv import load_dotenv 
load_dotenv()

import json
import requests
import streamlit as st
import os
import re
import google.generativeai as genai
from PIL import Image
from streamlit_lottie import st_lottie
import speech_recognition as sr

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash-exp")

def get_gemini_response(input_text, image):
    if input_text:
        response = model.generate_content([input_text, image])
    else:
        response = model.generate_content([image])
    return response.text

# Load Lottie animations from local JSON files
def load_lottiefile(filepath: str):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.warning(f"⚠️ File not found: {filepath}")
        return None

# Page config
st.set_page_config(page_title="GEN Vision AI Assistant")

# ✅ Styling with multicolor borders
st.markdown("""
    <style>
[data-testid="stApp"] {
    background-color: #ffffff;
    padding: 2rem;
    border-radius: 12px;
}

.stTextInput > div {
    padding: 3px;
    border: 4px solid transparent;
    border-radius: 12px;
    background-image: linear-gradient(white, white), 
                      linear-gradient(90deg, red, orange, yellow, green, cyan, blue, violet);
    background-origin: border-box;
    background-clip: padding-box, border-box;
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
}

.stTextInput input {
    height: 60px;
    font-size: 18px;
    padding: 10px;
    border: none !important;
    outline: none !important;
    width: 100%;
    background-color: white;
    border-radius: 8px;
}

div.stFileUploader > div:first-child {
    padding: 3px;
    border: 4px solid transparent;
    border-radius: 12px;
    background-image: linear-gradient(white, white), 
                      linear-gradient(90deg, red, orange, yellow, green, cyan, blue, violet);
    background-origin: border-box;
    background-clip: padding-box, border-box;
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
}

div.stFileUploader > div div {
    background-color: #gray;
    color: black;
    border-radius: 8px;
    padding: 0.5em 1em;
    font-weight: bold;
}

div.stFileUploader > div div:hover {
    background-color: gray;
}

div.stButton > button:first-child {
    background-color:#3CE37C;
    color: white;
    border-radius: 8px;
    padding: 0.5em 1em;
    font-weight: bold;
}

div.stButton > button:first-child:hover {
    background-color: #E501FF;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# Load animations
lottie_coding = load_lottiefile("coding.json")
lottie_spinner = load_lottiefile("spinner.json")
lottie_balloon = load_lottiefile("balloon.json")
lottie_voice = load_lottiefile("voice_command.json")  # Voice command animation

# App title and subtitle
st.title("GEN Vision AI Assistant")
st.subheader("See the better future with GEN-Vision")

# Show intro animation
if lottie_coding:
    st_lottie(lottie_coding, speed=0.5, loop=True, height=250, key="coding_lottie")

# Session state setup
if "submitted" not in st.session_state:
    st.session_state.submitted = False

def submit_on_enter():
    st.session_state.submitted = True

# 🎙️ Voice input function with animation
def get_voice_input():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    # Show voice command animation
    anim_placeholder = st.empty()
    if lottie_voice:
        with anim_placeholder.container():
            st_lottie(lottie_voice, speed=2, loop=True, height=100,width=150, key="voice_animation")

    with mic as source:
        st.info("Listening for voice input... 🎙️")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    # Stop animation
    anim_placeholder.empty()

    try:
        st.info("Processing voice input...")
        text = recognizer.recognize_google(audio)
        st.success(f"Voice input received: {text}")
        return text
    except sr.UnknownValueError:
        st.error("Sorry, I couldn't understand that.")
        return None
    except sr.RequestError:
        st.error("Could not request results from Google Speech Recognition service.")
        return None

# Input prompt
input_text = st.text_input("Input prompt:", key="input", on_change=submit_on_enter)

# File uploader
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
image = ""
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded image", use_column_width=True)

# Buttons
manual_submit = st.button("Submit")
voice_command = st.button("Use Voice Command")

# Handle voice input
voice_input_text = None
if voice_command:
    voice_input_text = get_voice_input()

# Generate response
if voice_input_text or st.session_state.submitted or manual_submit:
    st.session_state.submitted = False

    if voice_input_text:
        input_text = voice_input_text

    placeholder = st.empty()
    with placeholder.container():
        if lottie_spinner:
            st_lottie(lottie_spinner, speed=0.5, loop=True, height=200, key="loading_spinner")
            st.markdown("<h5 style='text-align: center;'>Ideas Catching Fire... 🚀🚀</h5>", unsafe_allow_html=True)
        else:
            st.info("Generating response...")

    raw_response = get_gemini_response(input_text, image)
    cleaned_response = re.sub(r'</div>\s*$', '', raw_response.strip(), flags=re.IGNORECASE)

    placeholder.empty()

    if lottie_balloon:
        st_lottie(lottie_balloon, speed=1.5, loop=False, height=100, width=100, key="balloon_animation_success")

    st.markdown("### The Response is 🔥: ")
    st.markdown(
        f"""
        <div style="background-color: #6EF5FC; padding: 15px; border-radius: 10px; font-size: 16px;">
            {cleaned_response}
        </div>
        """,
        unsafe_allow_html=True
    )
