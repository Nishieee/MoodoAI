# MoodoAI: Mood Journaling App

MoodoAI is a mood journaling application that allows users to track their emotions, reflect on their feelings, and receive supportive, dynamic responses. The project utilizes **Streamlit** for the frontend, **FastAPI** for the backend, and integrates **OpenAI GPT-3.5** for generating mood-specific responses.

---

## Project Structure

```plaintext
MOODOAI/
├── .github/                     # GitHub-specific files (e.g., workflows)
├── fast_api/                    # Backend folder
│   ├── __pycache__/             # Cached files
│   ├── __init__.py              # Backend package initializer
│   ├── .env                     # Backend environment variables
│   ├── Dockerfile               # Backend Dockerfile
│   ├── main.py                  # FastAPI entry point
│   └── requirements.txt         # Backend dependencies
├── Streamlit/                   # Frontend folder
│   ├── __pycache__/             # Cached files
│   ├── __init__.py              # Frontend package initializer
│   ├── app.py                   # Main Streamlit app
│   ├── login_page.py            # Login page implementation
│   ├── signup_page.py           # Signup page implementation
│   ├── motivate_page.py         # Mood selection and AI response
│   ├── journal_entry_page.py    # Journal entry page
│   ├── past_entries.py          # View past journal entries
│   ├── welcome_page.py          # Welcome page implementation
│   ├── hriday_journal_entries.txt  # Mock journal data
│   ├── Dockerfile               # Frontend Dockerfile
│   ├── docker-compose.yml       # Docker Compose configuration
│   └── requirements.txt         # Frontend dependencies
├── .env                         # Project-level environment variables
└── README.md                    # Project documentation
```

---

## Features

### Frontend (Streamlit)
1. **Welcome Page**: Provides an overview of the app and its features.
2. **Login and Signup**: Secure user authentication with username-password flow.
3. **Mood Selection**: Allows users to select their current mood using emojis and receive AI-generated responses.
4. **Journal Entry**: Enables users to reflect and add entries about their day.
5. **Past Entries**: Allows users to view and review previously saved journal entries.

### Backend (FastAPI)
1. **User Management**: Handles signup, login, and password hashing.
2. **Mood Responses**: Accepts user moods, generates personalized responses using OpenAI, and stores them in the database.
3. **Journal Data**: Manages storing and retrieving journal entries.
4. **Database Integration**: Uses Snowflake for storing user data, mood responses, and timestamps.

---

## Setup and Installation

### Prerequisites
- Python 3.8 or higher
- Docker (optional, for containerized deployment)
- An OpenAI API key
- Snowflake account and credentials

### Steps

#### 1. Clone the Repository
```bash
git clone https://github.com/your-username/moodoai.git
cd moodoai
```

#### 2. Set Up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Dependencies
Install dependencies for both backend and frontend:
```bash
pip install -r fast_api/requirements.txt
pip install -r Streamlit/requirements.txt
```

#### 4. Configure Environment Variables
Create `.env` files in both the `fast_api` and `Streamlit` directories.

- **FastAPI `.env`**:
  ```plaintext
  SNOWFLAKE_USER=<your-snowflake-username>
  SNOWFLAKE_PASSWORD=<your-snowflake-password>
  SNOWFLAKE_ACCOUNT=<your-snowflake-account-id>
  SNOWFLAKE_DATABASE=nosu
  SNOWFLAKE_SCHEMA=PUBLIC
  SNOWFLAKE_WAREHOUSE=COMPUTE_WH
  OPENAI_API_KEY=<your-openai-api-key>
  ```

- **Streamlit `.env`**:
  ```plaintext
  FASTAPI_URL=http://127.0.0.1:8000
  ```

#### 5. Run the Backend (FastAPI)
Navigate to the `fast_api` folder and run the FastAPI server:
```bash
uvicorn main:app --reload
```

#### 6. Run the Frontend (Streamlit)
Navigate to the `Streamlit` folder and start the Streamlit app:
```bash
streamlit run app.py
```

---

## Usage
1. Open the Streamlit app in your browser.
2. Sign up or log in to your account.
3. Select your current mood from the emojis on the **Motivate Page**.
4. View the personalized AI response.
5. Add journal entries or view past entries as needed.

---

## Deployment

### Using Docker
1. Build the Docker images for both frontend and backend:
   ```bash
   docker-compose build
   ```

2. Start the services:
   ```bash
   docker-compose up
   ```

3. Access the app at `http://localhost:8501`.

---

## Technologies Used
- **Frontend**: Streamlit
- **Backend**: FastAPI
- **Database**: Snowflake
- **AI**: OpenAI GPT-3.5
- **Authentication**: Passlib (BCrypt for password hashing)

---

## Contributing
If you'd like to contribute, please fork the repository and submit a pull request.

---

## License
This project is licensed under the MIT License.
```

