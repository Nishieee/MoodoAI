from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import snowflake.connector
from passlib.context import CryptContext
import os
from fastapi import Form
import logging
from datetime import datetime
import openai
import logging
from datetime import datetime
from fastapi import HTTPException, APIRouter
from openai import ChatCompletion
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import asyncio
import os
import aiohttp
import aiofiles
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# FastAPI app
app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for security in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Snowflake connection details from .env
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")

def get_snowflake_connection():
    return snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA,
        warehouse=SNOWFLAKE_WAREHOUSE
    )

class SignupModel(BaseModel):
    username: str
    password: str

class LoginModel(BaseModel):
    username: str
    password: str

# Request schema for mood response
class MoodRequest(BaseModel):
    username: str
    emoji: str

# Define the data model for the request
class JournalEntry(BaseModel):
    username: str
    prompt: str
    journal_entry: str

# Define the data model for the update request
class UpdateJournalEntry(BaseModel):
    id: int
    updated_entry: str

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

@app.post("/signup")
async def signup(username: str, password: str):
    conn = get_snowflake_connection()
    try:
        cursor = conn.cursor()
        # Check if username already exists
        cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username already taken")

        # Insert the new user
        hashed_password = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, hashed_password),
        )
        conn.commit()
        return {"message": "User signed up successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@app.post("/login")
async def login(username: str, password: str):
    conn = get_snowflake_connection()
    try:
        cursor = conn.cursor()
        # Check if the user exists
        cursor.execute("SELECT password_hash FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=401, detail="Invalid username or password")

        # Verify the password
        stored_password_hash = result[0]
        if not verify_password(password, stored_password_hash):
            raise HTTPException(status_code=401, detail="Invalid username or password")

        return {"message": "Login successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
        

prompts = {
    "MAKE SURE TO TALK LIKE A GENZ": {
        "description": "Yo, you’re like the go-to Gen Z bestie—always hyping up your friends when they’re winning, and their ride-or-die support when life’s a mess. You’re chill, sarcastic (in a fun way), and totally warm when it counts, like the perfect combo of funny and understanding. Think of this as texting a friend: Keep it casual, relatable, and always on point with a little humor or sass sprinkled in. Structure your replies in 3 short, vibe-y paragraphs that sound like a real convo. The goal? Make them feel seen, heard, and 100% supported.",
     "instructions":{
    "😄": "Be their biggest cheerleader! Gas them up like it’s the win of the century. Acknowledge their joy with excitement and hype. Toss in a funny line, quirky story, or bold one-liner to keep the vibe fun and positive. End by encouraging them to fully enjoy the moment with something like, 'You earned this, enjoy every second!'",
    "😊": "Keep it sweet and calm. Recognize their good vibes and encourage them to soak it in like sunshine. Share a light, uplifting piece of wisdom about finding joy in small moments. End with a positive reminder like, 'Your energy’s contagious, don’t stop spreading it!'",
    "😐": "Normalize their neutral mood and let them know it’s totally valid to feel 'meh.' Reassure them with something like, 'It’s totally cool to just be. Life’s about balance, no stress.' Drop a thoughtful quote or perspective on embracing calm and stillness. Suggest a mindful activity such as, 'Maybe go for a walk or vibe out to your fave playlist?'",
    "😔": "Be their emotional anchor by validating their struggles with something like, 'I get it, this sucks, and it’s okay to feel that way.' Share a comforting thought or quote about resilience to remind them they’re strong. Gently suggest a low-effort self-care action, like, 'Try watching a feel-good show or texting someone who gets you.'",
    "😢": "Acknowledge their pain with empathy and say something like, 'This is heavy, and it’s okay to not be okay right now.' Share a tender, hopeful thought about healing, but don’t rush them to feel better. Suggest something soothing, like journaling or just taking a moment to breathe. End with a heartfelt reminder, 'You’re not alone, I’ve got you.'"
}
    }
}


# Updated endpoint
@app.post("/api/get-mood-response")
async def get_mood_response(request: MoodRequest):
    try:
        logging.info(f"Received mood request: {request}")

        # Step 1: Connect to Snowflake
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        logging.info("Database connection established.")

        # Step 2: Capture timestamp
        timestamp = datetime.utcnow()
        logging.info(f"Timestamp captured: {timestamp}")

        # Select the appropriate prompt
        prompt = prompts.get(request.emoji, "Yo, you’re like the go-to Gen Z bestie—always hyping up your friends when they’re winning, and their ride-or-die support when life’s a mess. You’re chill, sarcastic (in a fun way), and totally warm when it counts, like the perfect combo of funny and understanding. Think of this as texting a friend: Keep it casual, relatable, and always on point with a little humor or sass sprinkled in. Structure your replies in 3 short, vibe-y paragraphs that sound like a real convo. The goal? Make them feel seen, heard, and 100% supported.do add some enojis like 4 emojis in the respose.")

        # Step 3: Generate response using OpenAI
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": "Please share something meaningful for my current mood."}
                ],
                max_tokens=150,
                temperature=0.7
            )
            ai_response = response['choices'][0]['message']['content']
            logging.info("AI response generated successfully.")
        except Exception as openai_error:
            logging.error(f"OpenAI error: {openai_error}")
            raise HTTPException(status_code=500, detail=f"Failed to generate AI response: {openai_error}")

        # Step 4: Save mood and AI response into the database
        try:
            cursor.execute(
                "INSERT INTO mood_ratings (username, mood, timestamp, ai_response) VALUES (%s, %s, %s, %s)",
                (request.username, request.emoji, timestamp, ai_response)
            )
            conn.commit()
            logging.info("Mood data and AI response saved to the database.")
        except Exception as db_error:
            logging.error(f"Database error: {db_error}")
            raise HTTPException(status_code=500, detail=f"Failed to save data to the database: {db_error}")

        # Step 5: Return the AI response
        return {"response": ai_response}

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

    finally:
        # Ensure the database connection is closed
        try:
            conn.close()
            logging.info("Database connection closed.")
        except Exception as close_error:
            logging.error(f"Error closing the database connection: {close_error}")

BACKEND_V1_API_URL = "https://public-api.beatoven.ai/api/v1"
BACKEND_API_HEADER_KEY = os.getenv("BEATOVEN_API_KEY", "KdsWws5m8xM7Oop2Om-BbQ")

async def create_track(request_data):
    """
    Creates a track on Beatoven.ai using the provided metadata.
    """
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{BACKEND_V1_API_URL}/tracks",
                json=request_data,
                headers={"Authorization": f"Bearer {BACKEND_API_HEADER_KEY}"}
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_message = await response.text()
                    raise HTTPException(status_code=response.status, detail=f"Create track failed: {error_message}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error during create_track: {e}")

async def compose_track(request_data, track_id):
    """
    Composes a track on Beatoven.ai using the provided track ID.
    """
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{BACKEND_V1_API_URL}/tracks/compose/{track_id}",
                json=request_data,
                headers={"Authorization": f"Bearer {BACKEND_API_HEADER_KEY}"}
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_message = await response.text()
                    raise HTTPException(status_code=response.status, detail=f"Compose track failed: {error_message}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error during compose_track: {e}")

async def watch_task_status(task_id, interval=10):
    """
    Watches the status of a Beatoven.ai composition task until completion.
    """
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(
                    f"{BACKEND_V1_API_URL}/tasks/{task_id}",
                    headers={"Authorization": f"Bearer {BACKEND_API_HEADER_KEY}"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("status") == "composed":
                            return data
                        elif data.get("status") == "failed":
                            raise HTTPException(status_code=500, detail="Composition task failed.")
                        else:
                            await asyncio.sleep(interval)
                    else:
                        error_message = await response.text()
                        raise HTTPException(status_code=response.status, detail=f"Task status failed: {error_message}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Unexpected error during task monitoring: {e}")



@app.post("/api/create-mood-music")
async def create_mood_music(request: MoodRequest):
    """
    Endpoint to generate music based on the user's mood.
    """
    try:
        logging.info(f"Received music generation request: {request}")

        # Step 1: Map moods to music prompts
        music_prompts = {
            "😄": "Create an upbeat, energetic, and celebratory music track.",
            "😊": "Generate a calm, relaxing, and happy instrumental.",
            "😐": "Compose a neutral, ambient, and balanced piece.",
            "😔": "Create a soft, reflective, and comforting soundscape.",
            "😢": "Compose a slow, soothing, and melancholic melody.",
        }
        mood_prompt = music_prompts.get(request.emoji, "Compose a balanced and neutral music track.")
        track_meta = {"prompt": {"text": mood_prompt}}

        track_url = None
        try:
            # Step 2: Create and compose track using Beatoven.ai
            create_res = await create_track(track_meta)
            track_id = create_res["tracks"][0]
            compose_res = await compose_track({"format": "mp3", "looping": False}, track_id)
            task_id = compose_res["task_id"]
            status_res = await watch_task_status(task_id)
            track_url = status_res["meta"]["track_url"]
            logging.info(f"Music track composed successfully: {track_url}")
        except Exception as e:
            logging.error(f"Error during music generation: {e}")
            raise HTTPException(status_code=500, detail="Music generation failed.")

        # Step 3: Save the mood, AI response, and track URL into the database
        timestamp = datetime.utcnow()
        conn = get_snowflake_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO tracks_generated (username, track_url, timestamp)
                VALUES (%s, %s, %s)
                """,
                (request.username, track_url, timestamp)
            )
            conn.commit()
            logging.info("Mood data, AI response, and track URL saved to the database.")
        except Exception as db_error:
            logging.error(f"Database error: {db_error}")
            raise HTTPException(status_code=500, detail="Failed to save data to the database.")
        finally:
            conn.close()

        # Step 4: Return the track URL
        return {"track_url": track_url}

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

# Endpoint to save a journal entry
@app.post("/save-journal-entry/")
async def save_journal_entry(entry: JournalEntry):
    try:
        # Validate input data
        if not entry.username or not entry.prompt or not entry.journal_entry:
            raise HTTPException(status_code=400, detail="All fields are required.")

        # Connect to Snowflake
        conn = get_snowflake_connection()
        cursor = conn.cursor()

        # Current timestamp
        timestamp = datetime.now()

        # Insert query
        insert_query = """
        INSERT INTO journall_entries (username, timestamp, prompt, journal_entry)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (entry.username, timestamp, entry.prompt, entry.journal_entry))
        conn.commit()

        # Close the connection
        cursor.close()
        conn.close()

        return {"message": "Journal entry saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    
# Endpoint to retrieve journal entries for a user
@app.get("/get-journal-entries/{username}")
async def get_journal_entries(username: str):
    try:
        # Connect to Snowflake
        conn = get_snowflake_connection()
        cursor = conn.cursor()

        # Query to fetch all journal entries for the user
        query = """
        SELECT id, timestamp, prompt, journal_entry
        FROM journall_entries
        WHERE username = %s
        ORDER BY timestamp DESC
        """
        cursor.execute(query, (username,))
        rows = cursor.fetchall()

        # Close the connection
        cursor.close()
        conn.close()

        # Return the results
        if not rows:
            return {"message": "No journal entries found for this user."}

        entries = [
            {
                "id": row[0],
                "timestamp": row[1],
                "prompt": row[2],
                "journal_entry": row[3],
            }
            for row in rows
        ]
        return {"entries": entries}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    

@app.get("/get-journal-entries/{username}")
async def get_journal_entries(username: str):
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()

        # Your SQL query and logic
        query = """
        SELECT id, timestamp, prompt, journal_entry
        FROM journall_entries
        WHERE username = %s
        ORDER BY timestamp DESC
        """
        cursor.execute(query, (username,))
        rows = cursor.fetchall()

        # Close the connection
        cursor.close()
        conn.close()

        if not rows:
            return {"message": "No journal entries found for this user."}

        entries = [
            {"id": row[0], "timestamp": row[1], "prompt": row[2], "journal_entry": row[3]}
            for row in rows
        ]
        return {"entries": entries}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    
@app.put("/update-journal-entry/")
async def update_journal_entry(entry: UpdateJournalEntry):
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()

        # Log the payload
        print("Payload received:", entry.dict())

        # Update the journal entry
        query = "UPDATE journall_entries SET journal_entry = %s WHERE id = %s"
        cursor.execute(query, (entry.updated_entry, entry.id))
        conn.commit()

        # Check if the update was successful
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="No entry found with the provided ID.")

        # Close the connection
        cursor.close()
        conn.close()
        return {"message": "Journal entry updated successfully"}

    except Exception as e:
        print("Error occurred:", str(e))
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")




