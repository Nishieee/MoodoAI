import streamlit as st
import requests

# Define emojis for moods
mood_emojis = {
    "😄": "Feeling Great",
    "😊": "Feeling Good",
    "😐": "Feeling Okay",
    "😔": "Feeling Low",
    "😢": "Feeling Bad"
}

API_URL = "http://127.0.0.1:8000/api/get-mood-response"  # Replace with your actual API URL
music_API_URL = "http://127.0.0.1:8000/api/create-mood-music" 

# Initialize session state
if "selected_mood" not in st.session_state:
    st.session_state.selected_mood = None
if "ai_response" not in st.session_state:
    st.session_state.ai_response = None
if "track_url" not in st.session_state:
    st.session_state.track_url = None

def mood_selection_page(username: str):
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 20px;">
            <h2 style="color: #4CAF50;">🌈 How are you feeling today?</h2>
            <p style="font-size: 16px;">Tap on an emoji that best describes your mood.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Display emoji buttons
    cols = st.columns(len(mood_emojis))  # Create columns for emoji buttons

    for idx, (emoji, label) in enumerate(mood_emojis.items()):
        with cols[idx]:
            if st.button(emoji, key=emoji):
                st.session_state.selected_mood = emoji  # Store selected mood in session state
                st.session_state.ai_response = None  # Reset AI response when mood changes
                st.session_state.track_url = None  # Reset track URL when mood changes

    # If a mood is selected, fetch AI response
    if st.session_state.selected_mood:
        selected_mood = st.session_state.selected_mood
        st.markdown(f"### You selected: {mood_emojis[selected_mood]} {selected_mood}")

        if not st.session_state.ai_response:  # Fetch AI response only if not already fetched
            payload = {"username": username, "emoji": selected_mood}
            try:
                response = requests.post(API_URL, json=payload)
                if response.status_code == 200:
                    st.session_state.ai_response = response.json().get("response", "No response generated.")
                else:
                    st.error(f"Failed to fetch a response. Server returned: {response.status_code}")
            except Exception as e:
                st.error(f"An error occurred while fetching mood response: {str(e)}")

        # Display AI response
        if st.session_state.ai_response:
            st.markdown(
                f"""
                <div style="background-color: #f9f9f9; border-left: 4px solid #4CAF50; padding: 50px; margin: 30px 0; color: #333; font-size: 16px; font-family: Arial, sans-serif; border-radius: 5px; text-align: left;">
                    {st.session_state.ai_response}
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Generate music button
        if st.button("🎵 Generate Music", key="generate_music"):
            if not st.session_state.track_url:  # Only call API if track URL isn't already fetched
                try:
                    st.write("Generating music... Please wait.")
                    music_response = requests.post(music_API_URL, json={"username": username, "emoji": selected_mood})

                    if music_response.status_code == 200:
                        music_data = music_response.json()
                        st.session_state.track_url = music_data.get("track_url", "#")
                    else:
                        error_message = music_response.json().get("detail", "Unknown error occurred.")
                        st.error(f"Failed to generate music: {error_message}")
                except Exception as e:
                    st.error(f"An error occurred while generating music: {str(e)}")

        # Display track URL if available
        if st.session_state.track_url:
            st.markdown(
                f"""
                <div style="text-align: center; margin-top: 20px;">
                    <h3 style="color: #4CAF50;">Your personalized music track is ready! 🎶</h3>
                    <a href="{st.session_state.track_url}" target="_blank" style="text-decoration: none;">
                        <button style="background-color: #4CAF50; color: white; border: none; padding: 10px 20px; font-size: 16px; border-radius: 5px; cursor: pointer;">
                            Listen to Track 🎧
                        </button>
                    </a>
                </div>
                """,
                unsafe_allow_html=True,
            )