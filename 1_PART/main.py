# Importing necessary modules

from pypdf import PdfReader
from dotenv import load_dotenv
import os
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def read_pdf(file_path):
    """Reads a PDF file and extracts its text content."""

    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() 
    return text

def summarize_text(text):
    text = text[:4000]

    response = client.responses.create(
        model="gpt-5-mini",
        input=("Summarize the following text in simple and clear language:\n\n" + text)
    )

    return response.output_text


# Main Execution Flow:

pdf_text = read_pdf("Hemant_Resume_DPJ.pdf")

if not pdf_text.strip():
    ValueError("The PDF file is empty or could not be read.")   

summary = summarize_text(pdf_text)

print("Summary of the PDF content:")
print(summary) 
