import streamlit as st
from datetime import datetime
import requests

def journal_entry_page(username):
    st.title(f"📖 Journal for {username}")

    # Sidebar with prompts
    st.sidebar.title("Journal Prompts")
    st.sidebar.write("Use these prompts to inspire your writing:")
    prompts = [
        "What are you grateful for today?",
        "What challenges did you face today, and how did you overcome them?",
        "Describe a moment that made you smile today.",
        "What did you learn about yourself today?",
        "What are your goals for tomorrow?",
    ]
    for prompt in prompts:
        st.sidebar.markdown(f"- {prompt}")

    # Journal entry form
    st.header("Write Your Journal Entry")
    selected_prompt = st.selectbox("Choose a prompt:", prompts)
    journal_entry = st.text_area("Write your thoughts:", height=200)

 
   

    # Save button logic
    if st.button("Save Entry"):
        if journal_entry.strip():
            payload = {
                "username": username,
                "prompt": selected_prompt,
                "journal_entry": journal_entry
            }
            try:
                response = requests.post("http://127.0.0.1:8000/save-journal-entry/", json=payload)
                if response.status_code == 200:
                    st.success("Your journal entry has been saved!")
                else:
                    st.error(f"Error: {response.json().get('detail')}")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("Please write something before saving.")

