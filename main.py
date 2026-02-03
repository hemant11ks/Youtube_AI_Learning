# ============================================================
# AI PDF SUMMARIZER USING PYTHON (ChatGPT-5 Mini)
# ============================================================
# This script:
# 1. Reads text from a PDF file
# 2. Sends the text to an AI model
# 3. Gets a summarized version
# 4. Prints the summary
# ============================================================

from pypdf import PdfReader          # Used to read and extract text from PDF files
from dotenv import load_dotenv       # Used to load environment variables from .env file
import os                            # Used to access environment variables
from openai import OpenAI            # OpenAI client to interact with AI models


# -------------------------------
# LOAD ENVIRONMENT VARIABLES
# -------------------------------

# This reads the .env file and loads variables into the system environment
# Example: OPENAI_API_KEY=sk-xxxx
load_dotenv()

# Create OpenAI client using API key from environment
# This avoids hardcoding the API key (security best practice)
# Creates a client to communicate with OpenAI servers
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


# -------------------------------
# FUNCTION: READ PDF FILE
# -------------------------------
def read_pdf(file_path):
    """
    Reads text from a PDF file and returns it as a string.

    Parameters:
    file_path (str): Path to the PDF file

    Returns:
    str: Extracted text from the PDF
    """

    # Create PdfReader object to open the PDF
    reader = PdfReader(file_path)

    # Variable to store all extracted text
    text = ""

    # Loop through each page in the PDF
    for page in reader.pages:
        # Extract text from the page and append to text variable
        text += page.extract_text()

    # Return the full text from the PDF
    return text


# -------------------------------
# FUNCTION: SUMMARIZE TEXT USING AI
# -------------------------------
def summarize_text(text):
    """
    Sends text to the AI model and returns a summarized version.

    Parameters:
    text (str): Input text to summarize

    Returns:
    str: AI-generated summary
    """

    # Limit text size to control cost and avoid token overflow
    # AI models charge per token (large input = higher cost)
    # text is a string

    # Strings are sliced by character index
  
    # Each letter, space, or symbol = 1 character
    text = text[:4000]

    # Send request to OpenAI using Responses API

    #Internal working:
    # Text → tokens
    #Tokens → AI model AI predicts next words # Summary returned
    # “AI doesn’t understand language — it predicts patterns.”
    response = client.responses.create(
        model="gpt-5-mini",  # Lightweight, fast, low-cost model
        input=(
            "Summarize the following text in simple and clear language:\n\n"
            + text
        )
    )

    # Extract and return only the readable text output
    # API response is JSON

# This extracts only the final readable answer
    return response.output_text


# -------------------------------
# MAIN PROGRAM EXECUTION
# -------------------------------

# Step 1: Read text from PDF
pdf_text = read_pdf("sample.pdf")

# Step 2: Validate PDF content
# Prevents summarizing empty content
# Avoids wasting API calls
if not pdf_text.strip():
    raise ValueError("PDF contains no readable text")

# Step 3: Generate AI summary
summary = summarize_text(pdf_text)

# Step 4: Display result
print("\n========== AI GENERATED SUMMARY ==========\n")
print(summary)





