# ============================================================
# AI MEETING NOTES GENERATOR USING PYTHON
# ============================================================

# -------------------------------
# IMPORT REQUIRED MODULES
# -------------------------------

from dotenv import load_dotenv   # Loads environment variables from .env file
import os                        # Used to access system environment variables
from openai import OpenAI        # Official OpenAI SDK


# -------------------------------
# LOAD API KEY SECURELY
# -------------------------------

load_dotenv()  # Reads .env file and loads variables into system

# Fetch API key from environment variables
API_KEY = os.getenv("OPENAI_API_KEY")

# Safety check to ensure API key exists
if not API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env file")

# Create OpenAI client object
client = OpenAI(api_key=API_KEY)


# -------------------------------
# STEP 1 — TRANSCRIBE AUDIO
# -------------------------------

def transcribe_audio(audio_path):
    """
    Converts meeting audio into text using AI speech recognition.
    """

    # Open audio file in binary read mode
    with open(audio_path, "rb") as audio_file:

        # Call OpenAI speech-to-text model
        transcription = client.audio.transcriptions.create(
            file=audio_file,                 # Audio file input
            model="gpt-4o-mini-transcribe"   # Speech recognition model
        )

    # Return transcribed text
    return transcription.text


# -------------------------------
# STEP 2 — GENERATE AI NOTES
# -------------------------------

def generate_meeting_notes(transcript):
    """
    Sends transcript to AI and generates structured meeting notes.
    """

    # Limit transcript length (cost + token safety)
    transcript = transcript[:4000]

    # Prompt engineering for structured output
    prompt = f"""
You are a professional meeting assistant.

IMPORTANT:
Return output in EXACT format below.

SUMMARY:
- 

KEY POINTS:
- 

DECISIONS:
- 

ACTION ITEMS:
- 

Transcript:
{transcript}
"""

    # Send prompt to GPT model
    response = client.responses.create(
        model="gpt-5-mini",  # Fast & affordable model
        input=prompt
    )

    # Return generated meeting notes text
    return response.output_text


# -------------------------------
# STEP 3 — SAFE PARSING
# -------------------------------

def segregate_notes(notes_text):
    """
    Extract sections safely even if formatting slightly changes.
    """

    # Dictionary to store sections
    sections = {
        "SUMMARY": "",
        "KEY POINTS": "",
        "DECISIONS": "",
        "ACTION ITEMS": ""
    }

    current_section = None

    # Loop through each line of AI output
    for line in notes_text.splitlines():
        clean = line.strip().upper()

        # Detect headings
        if clean.startswith("SUMMARY"):
            current_section = "SUMMARY"
        elif clean.startswith("KEY POINTS"):
            current_section = "KEY POINTS"
        elif clean.startswith("DECISIONS"):
            current_section = "DECISIONS"
        elif clean.startswith("ACTION ITEMS"):
            current_section = "ACTION ITEMS"

        # Append content to detected section
        elif current_section and line.strip():
            sections[current_section] += line.strip() + "\n"

    # Fallback safety if section empty
    for key in sections:
        if not sections[key].strip():
            sections[key] = "No information detected.\n"

    return sections


# -------------------------------
# STEP 4 — SAVE NOTES TO FILE
# -------------------------------

def save_notes(sections):
    """Save meeting notes to text file."""

     # sections is a dictionary like:
    # {
    #   "SUMMARY": "text...",
    #   "KEY POINTS": "text...",
    #   "DECISIONS": "text...",
    #   "ACTION ITEMS": "text..."
    # }
    
    # Loop through dictionary key-value pairs
    # title   → dictionary KEY   (e.g., SUMMARY)
    # content → dictionary VALUE (actual notes text)

    with open("meeting_notes.txt", "w", encoding="utf-8") as file:
        for title, content in sections.items():
            file.write(f"{title}\n")
            file.write("-" * 40 + "\n")
            file.write(content + "\n")


# -------------------------------
# MAIN PROGRAM FLOW
# -------------------------------

def main():
    print("🎙️ AI Meeting Notes Generator Started")

    audio_path = "meeting.mp3"

    print("Transcribing audio...")
    transcript = transcribe_audio(audio_path)

    print("Generating AI notes...")
    notes = generate_meeting_notes(transcript)

    sections = segregate_notes(notes)

    save_notes(sections)

    print("✅ Meeting notes saved successfully!")


# Entry point of program
if __name__ == "__main__":
    main()

