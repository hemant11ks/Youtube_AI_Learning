# ============================================================
# AI MEETING NOTES GENERATOR USING PYTHON
# ============================================================
# Steps:
# 1. Convert meeting audio to text
# 2. Send transcript to AI
# 3. Generate structured meeting notes
# 4. Safely parse AI output
# 5. Print and store notes
# ============================================================


# -------------------------------
# IMPORT REQUIRED MODULES
# -------------------------------

from dotenv import load_dotenv
import os
from openai import OpenAI


# -------------------------------
# LOAD API KEY
# -------------------------------

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env file")

client = OpenAI(api_key=API_KEY)


# -------------------------------
# TRANSCRIBE AUDIO
# -------------------------------

def transcribe_audio(audio_path):
    """
    Converts meeting audio into text using AI.
    """

    with open(audio_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            file=audio_file,
            model="gpt-4o-mini-transcribe"
        )

    return transcription.text


# -------------------------------
# GENERATE MEETING NOTES
# -------------------------------

def generate_meeting_notes(transcript):
    """
    Converts transcript into structured meeting notes.
    """

    transcript = transcript[:4000]  # cost & safety control

    prompt = f"""
You are a professional meeting assistant.

IMPORTANT:
Return output in EXACT format below.
Do not change headings.

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

    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt
    )

    return response.output_text


# -------------------------------
# SAFE SEGREGATION LOGIC
# -------------------------------

def segregate_notes(notes_text):
    """
    Extracts meeting sections safely even if formatting varies.
    """

    sections = {
        "SUMMARY": "",
        "KEY POINTS": "",
        "DECISIONS": "",
        "ACTION ITEMS": ""
    }

    current_section = None

    for line in notes_text.splitlines():
        clean = line.strip().upper()

        if clean.startswith("SUMMARY"):
            current_section = "SUMMARY"
        elif clean.startswith("KEY POINTS"):
            current_section = "KEY POINTS"
        elif clean.startswith("DECISIONS"):
            current_section = "DECISIONS"
        elif clean.startswith("ACTION ITEMS"):
            current_section = "ACTION ITEMS"
        elif current_section and line.strip():
            sections[current_section] += line.strip() + "\n"

    # Fallback safety
    for key in sections:
        if not sections[key].strip():
            sections[key] = "No information detected.\n"

    return sections


# -------------------------------
# PRINT NOTES
# -------------------------------

def print_notes(sections):
    print("\n📝 MEETING SUMMARY")
    print(sections["SUMMARY"])

    print("📌 KEY POINTS")
    print(sections["KEY POINTS"])

    print("✅ DECISIONS")
    print(sections["DECISIONS"])

    print("🚀 ACTION ITEMS")
    print(sections["ACTION ITEMS"])


# -------------------------------
# SAVE NOTES
# -------------------------------

def save_notes(sections):
    with open("meeting_notes.txt", "w", encoding="utf-8") as file:
        for title, content in sections.items():
            file.write(f"{title}\n")
            file.write("-" * 40 + "\n")
            file.write(content + "\n")


# -------------------------------
# MAIN FLOW
# -------------------------------

def main():
    print("\n🎙️ AI MEETING NOTES GENERATOR STARTED\n")

    audio_path = "meeting.mp3"

    print("🔊 Transcribing meeting audio...")
    transcript = transcribe_audio(audio_path)

    if not transcript.strip():
        raise ValueError("Transcription failed or audio empty")

    print("📝 Transcription completed\n")

    print("🤖 Generating structured meeting notes...")
    notes = generate_meeting_notes(transcript)

    sections = segregate_notes(notes)

    print_notes(sections)

    save_notes(sections)

    print("\n✅ Meeting notes saved successfully!")


# -------------------------------
# ENTRY POINT
# -------------------------------

if __name__ == "__main__":
    main()
