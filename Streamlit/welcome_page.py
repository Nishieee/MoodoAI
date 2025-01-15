import streamlit as st
from dotenv import load_dotenv
import os
load_dotenv()

FASTAPI_URL = os.getenv("FASTAPI_URL")


def welcome_page():
    # Render the welcome page content with st.markdown
    st.markdown(
        """
        <div style="text-align: center;">
            <h1 style="color: #4CAF50;">🌈 Welcome to Moodo: Your Mood Journaling Companion</h1>
            <p style="font-size: 18px;">Track your emotions, reflect on your day, and gain insights into your mental well-being!</p>
            <p style="font-size: 16px;">
                Moodo helps you with:<br>
                📖 Recording and categorizing your daily moods<br>
                🌟 Reflecting on your experiences through guided prompts<br>
                📊 Visualizing trends with mood analytics<br>
                🛠️ Building better habits with personalized suggestions<br>
                ✨ Fostering mindfulness and self-awareness<br>
            </p>
            <p style="font-size: 16px; font-weight: bold;">
                Your journey to understanding and nurturing your emotions starts here!
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
