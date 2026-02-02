# ============================================================
# AI MEETING NOTES GENERATOR USING PYTHON
# ============================================================
# What this script does:
# 1. Takes a meeting audio file
# 2. Converts speech to text using AI
# 3. Converts raw text into structured meeting notes
# 4. Segregates notes into sections
# 5. Prints and stores notes cleanly
# ============================================================

# -------------------------------
# IMPORT REQUIRED MODULES
# -------------------------------

from dotenv import load_dotenv       # Loads environment variables securely
import os                            # Access system environment variables
from openai import OpenAI            # OpenAI client for AI models


# -------------------------------
# LOAD ENVIRONMENT VARIABLES
# -------------------------------

# Load variables from .env file into memory
load_dotenv()

# Read API key from environment
API_KEY = os.getenv("OPENAI_API_KEY")

# Stop program if API key is missing
if not API_KEY:
    raise ValueError("OPENAI_API_KEY not found. Please check your .env file.")


# -------------------------------
# INITIALIZE OPENAI CLIENT
# -------------------------------

# Create OpenAI client using API key
client = OpenAI(api_key=API_KEY)


# -------------------------------
# FUNCTION: TRANSCRIBE AUDIO
# -------------------------------

def transcribe_audio(audio_file_path):
    """
    Converts meeting audio into text using AI speech-to-text.

    Args:
        audio_file_path (str): Path to audio file

    Returns:
        str: Transcribed meeting text
    """

    # Open audio file in binary mode
    with open(audio_file_path, "rb") as audio_file:

        # Call OpenAI transcription model
        transcription = client.audio.transcriptions.create(
            file=audio_file,                    # Audio input
            model="gpt-4o-mini-transcribe"      # Fast & accurate transcription model
        )
    # Return only the transcribed text
    return transcription.text


# -------------------------------
# FUNCTION: GENERATE MEETING NOTES
# -------------------------------

def generate_meeting_notes(transcript):
    """
    Converts raw transcript into structured meeting notes.

    Args:
        transcript (str): Transcribed meeting text

    Returns:
        str: Structured meeting notes
    """

    # Limit input size to reduce cost and improve performance
    transcript = transcript[:4000]

    # Prompt instructing AI how to structure output
    prompt = f"""
    You are a professional meeting assistant.

    Convert the following transcript into structured meeting notes
    using EXACTLY the format below:
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

    # Send prompt to AI model
    response = client.responses.create(
        model="gpt-5-mini",     # Lightweight summarization model
        input=prompt
    )

    return response.output_text


# -------------------------------
# FUNCTION: SEGREGATE NOTES
# -------------------------------

def segregate_notes(notes_text):
    """
    Separates AI output into individual sections.

    Args:
        notes_text (str): Full AI-generated notes

    Returns:
        dict: Segregated meeting notes
    """

    sections = {
        "SUMMARY": "",
        "KEY POINTS": "",
        "DECISIONS": "",
        "ACTION ITEMS": ""
    }

    current_section = None

    # Process notes line by line
    for line in notes_text.splitlines():
        line = line.strip()

        # Check if line is a section heading
        if line in sections:
            current_section = line
        elif current_section and line:
            sections[current_section] += line + "\n"

    return sections


# -------------------------------
# FUNCTION: PRINT MEETING NOTES
# -------------------------------

def print_meeting_notes(sections):
    """
    Prints segregated meeting notes neatly.
    """
    print("\n📝 MEETING SUMMARY")
    print(sections["SUMMARY"])

    print("\n📌 KEY POINTS")
    print(sections["KEY POINTS"])

    print("\n✅ DECISIONS")
    print(sections["DECISIONS"])

    print("\n🚀 ACTION ITEMS")
    print(sections["ACTION ITEMS"])


# -------------------------------
# FUNCTION: SAVE NOTES TO FILE
# -------------------------------

def save_notes(sections):
    """
    Saves meeting notes in a clean text file.
    """

    with open("meeting_notes.txt", "w", encoding="utf-8") as file:
        for title, content in sections.items():
            file.write(f"{title}\n")
            file.write("-" * 40 + "\n")
            file.write(content + "\n\n")


# -------------------------------
# MAIN FUNCTION
# -------------------------------

def main():
    """
    Controls the full execution flow.
    """

    print("\n🎙️ AI MEETING NOTES GENERATOR STARTED\n")

    audio_path = "meeting.mp3"

    # Step 1: Transcribe audio
    print("🔊 Transcribing meeting audio...")
    transcript = transcribe_audio(audio_path)

    if not transcript.strip():
        raise ValueError("Transcription failed or audio is empty.")

    print("📝 Transcription completed.\n")
    # Step 2: Generate meeting notes
    print("🤖 Generating structured meeting notes...")
    notes = generate_meeting_notes(transcript)
    # Step 3: Segregate notes
    sections = segregate_notes(notes)
    # Step 4: Print notes
    print_meeting_notes(sections)
    # Step 5: Save notes
    save_notes(sections)

    print("\n✅ Meeting notes saved successfully!\n")

# -------------------------------
# PROGRAM ENTRY POINT
# -------------------------------

# Ensures script runs only when executed directly
if __name__ == "__main__":
    main()
