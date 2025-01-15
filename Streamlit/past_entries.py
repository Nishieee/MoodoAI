import streamlit as st
import requests
from datetime import datetime

def view_past_entries_page(username):
    st.title(f"📚 Past Journal Entries for {username}")

    # Fetch the user's past journal entries
    try:
        response = requests.get(f"http://127.0.0.1:8000/get-journal-entries/{username}")
        if response.status_code == 200:
            data = response.json()
            if "entries" in data:
                entries = data["entries"]

                if not entries:
                    st.info("You don't have any journal entries yet.")
                else:
                    for entry in entries:
                        st.markdown("---")

                        # Entry Header
                        st.markdown(
                            f"""
                            <div style="background-color: #f9f9f9; padding: 10px; border-radius: 5px;">
                                <strong>📅 Date:</strong> {datetime.fromisoformat(entry['timestamp']).strftime('%B %d, %Y, %I:%M %p')}<br>
                                <strong>🖊️ Prompt:</strong> {entry['prompt']}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        # Entry Content
                        st.markdown(
                            f"""
                            <div style="background-color: #fefefe; padding: 15px; border-left: 4px solid #4CAF50; margin-top: 10px; border-radius: 5px;">
                                {entry['journal_entry']}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
        else:
            st.error(f"Failed to fetch journal entries. Status code: {response.status_code}, Message: {response.text}")
    except Exception as e:
        st.error(f"An error occurred: {e}")
