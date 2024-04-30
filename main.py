import os
import dotenv

from markdown_utils import to_markdown
from pathlib import Path
import hashlib
import google.generativeai as genai
from langchain_community.document_loaders import PyPDFLoader
import PyPDF2
from typing import BinaryIO

dotenv.load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=api_key)

# Set up the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 8192,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
]

system_instruction = "Act as an intelligent search assistant tool. Speak in a direct, operational tone focused on efficiently understanding queries and providing relevant search results and information. \nWhen fetching results, prioritize authoritative and recently updated sources over outdated or questionable information. Evaluate result quality and provide concise summaries highlighting the most relevant portions.\nIf no high-quality results are available for the specified query, transparently explain the lack of information and suggest alternative avenues like modifying the search terms or consulting other references. Use clear language and get quickly to the point. The goal is productive information retrieval, not meandering discussion."

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    generation_config=generation_config,
    system_instruction=system_instruction,
    safety_settings=safety_settings,
)

uploaded_files = []


def upload_if_needed(pathname: str) -> list[str]:
    path = Path(pathname)
    hash_id = hashlib.sha256(path.read_bytes()).hexdigest()
    try:
        existing_file = genai.get_file(name=hash_id)
        return [existing_file]
    except:
        pass
    uploaded_files.append(genai.upload_file(path=path, display_name=hash_id))
    return [uploaded_files[-1]]


def extract_pdf_pages_old(pathname: str) -> list[str]:
    parts = []
    with open(pathname, "rb") as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            parts.append(f"--- PAGE {page_num + 1} ---")
            parts.append(page.extract_text())
    return parts


def extract_pdf_pages(pdf_file: BinaryIO) -> list[str]:
    parts = []
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        parts.append(f"--- PAGE {page_num + 1} ---")
        parts.append(page.extract_text())
    return parts


def model_calling(prompt):
    response = model.generate_content(prompt)
    to_markdown(response.text)
    return response.text


# for uploaded_file in uploaded_files:
#     genai.delete_file(name=uploaded_file.name)
