import os
import json
import re
import traceback
import fitz  # PyMuPDF for PDF
import cohere
from dotenv import load_dotenv
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
import time
import tempfile

load_dotenv()

API_KEY = os.getenv("COHERE_API_KEY")
if not API_KEY:
    raise RuntimeError("COHERE_API_KEY not set in environment variables or .env file.")
co = cohere.Client(API_KEY)


def build_prompt(resume_text: str) -> str:
    return f"""
You are an expert resume data extraction system. Your sole output MUST be a single, valid JSON object. 
Extract the following information from the provided resume text.

The JSON object must have these top-level keys:
1.  "Full Name": The full name of the person. If not found, use JSON null (not the string "null").
2.  "Email": The primary email address. If not found, use JSON null.
3.  "Phone Number": The primary phone number. If not found, use JSON null.
4.  "Work Experience": An array of objects. Each object represents a distinct work experience.

For each object in the "Work Experience" array, provide these keys:
    a.  "Company Name": (string) The name of the company. If not found, use the string "N/A".
    b.  "Customer Name": (string) The client/customer name. If internal or not mentioned, use "N/A".
    c.  "Role": (string) The job title/role. If not found, use "N/A".
    d.  "Duration": (string) The period worked (e.g., 'Jan 2020 - Dec 2022'). If not found, use "N/A".
    e.  "Skills/Technologies": (array of strings) Key skills/technologies for this role. If none found, use an empty array []. All strings in this array MUST be in double quotes.
    f.  "Industry/Domain": (string) Industry sector. If not found, use "N/A".
    g.  "Location": (string) Geographical region (e.g., "North America", "Remote"). If not found, use "N/A".

IMPORTANT JSON Structure Rules:
- The entire output MUST be a single JSON object. Do NOT include any explanatory text, markdown formatting (like \\`json), or anything else before or after the JSON object.
- ALL string values, including keys and all textual data, MUST be enclosed in double quotes.
- If a specific Work Experience entry is badly garbled, incomplete, or cannot be reliably extracted to fit the defined structure, OMIT that entire entry from the 'Work Experience' array. Ensure the 'Work Experience' array itself remains valid JSON (e.g., [] if all entries are omitted, or [{{...valid_entry...}}]).
- Ensure no unquoted words or characters appear directly within arrays or objects outside of quoted strings.
- Between the closing brace }} of one work experience object and the comma , and opening brace {{ of the next (or the final closing bracket ]] of the array), there must be absolutely no other text or characters.

Example structure:
{{
  "Full Name": "Jane Doe",
  "Email": "jane.doe@example.com",
  "Phone Number": "123-456-7890",
  "Work Experience": [
    {{
      "Company Name": "Tech Solutions Inc.",
      "Customer Name": "Client X",
      "Role": "Software Engineer",
      "Duration": "Jan 2020 - Present",
      "Skills/Technologies": ["Java", "Spring Boot", "AWS"],
      "Industry/Domain": "Technology",
      "Location": "North America"
    }},
    {{
      "Company Name": "Old Company LLC",
      "Customer Name": "N/A",
      "Role": "Junior Developer",
      "Duration": "May 2018 - Dec 2019",
      "Skills/Technologies": [],
      "Industry/Domain": "N/A",
      "Location": "Remote"
    }}
  ]
}}
If the input text does not appear to be a resume, or no information can be extracted:
{{
  "Full Name": null,
  "Email": null,
  "Phone Number": null,
  "Work Experience": []
}}

Resume Text:
---
{resume_text}
---
End of Resume Text. Output JSON object:
"""

def clean_json_string(json_str: str) -> str:
    json_str = json_str.strip()
    match = re.search(r"\{.*\}", json_str, re.DOTALL)
    if match:
        json_str = match.group(0)
    json_str = re.sub(r",\s*([}\]])", r"\1", json_str)
    json_str = re.sub(r"([\{\[])\s*,", r"\1", json_str)
    json_str = re.sub(r",\s*,", ",", json_str)
    json_str = re.sub(r"\[\s*,", "[", json_str)
    json_str = re.sub(r",\s*\]", "]", json_str)
    json_str = re.sub(r"\{\s*,", "{", json_str)
    json_str = re.sub(r",\s*\}", "}", json_str)
    return json_str

def extract_resume_data(resume_text: str):
    if not resume_text.strip():
        return {
            "full_name": None,
            "email": None,
            "phone_number": None,
            "work_experience": []
        }

    prompt = build_prompt(resume_text)
    response = co.generate(
        model="command-r-plus",
        prompt=prompt,
        temperature=0.2
    )

    raw_output = response.generations[0].text
    json_str = clean_json_string(raw_output)

    try:
        parsed = json.loads(json_str)
    except Exception as e:
        print("Raw Cohere output:\n", raw_output)
        print("JSON parsing failed, retrying with chunked extraction...")
        # Fallback: Use chunked extraction if JSON is incomplete or invalid
        return extract_resume_data_chunked(resume_text)

    work_exp = parsed.get("Work Experience", [])
    mapped_work_exp = []
    if isinstance(work_exp, list):
        for exp in work_exp:
            if isinstance(exp, dict):
                mapped_work_exp.append({
                    "company_name": exp.get("Company Name", "N/A"),
                    "customer_name": exp.get("Customer Name", "N/A"),
                    "role": exp.get("Role", "N/A"),
                    "duration": exp.get("Duration", "N/A"),
                    "skills_technologies": [s for s in exp.get("Skills/Technologies", []) if isinstance(s, str) and s.strip()],
                    "industry_domain": exp.get("Industry/Domain", "N/A"),
                    "location": exp.get("Location", "N/A")
                })

    return {
        "full_name": parsed.get("Full Name"),
        "email": parsed.get("Email"),
        "phone_number": parsed.get("Phone Number"),
        "work_experience": mapped_work_exp
    }

def iter_block_items(parent):
    """Yield paragraphs and tables in document order."""
    for child in parent.element.body.iterchildren():
        if child.tag.endswith('}p'):
            yield Paragraph(child, parent)
        elif child.tag.endswith('}tbl'):
            yield Table(child, parent)

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    content = []
    for block in iter_block_items(doc):
        if isinstance(block, Paragraph):
            text = block.text.strip()
            if text:
                content.append(text)
        elif isinstance(block, Table):
            for row in block.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells)
                if row_text:
                    content.append(row_text)
    return "\n".join(content)

def extract_text_from_file(filepath):
    ext = filepath.lower().split(".")[-1]
    if ext == "pdf":
        doc = fitz.open(filepath)
        return "\n".join(page.get_text() for page in doc)
    elif ext == "docx":
        return extract_text_from_docx(filepath)
    elif ext == "doc":
        print(f"Skipping {filepath}, convert into .docx first.")
        return ""
    else:
        raise ValueError("Unsupported file type: " + ext)

def extract_email_from_lines(lines):
    for line in lines:
        match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', line)
        if match:
            return match.group(0)
    return None

def extract_phone_from_lines(lines):
    for line in lines:
        match = re.search(r'(\+?\d[\d\-\(\) ]{7,}\d)', line)
        if match:
            return match.group(0)
    return None

def parse_resume(file_bytes, filename):
    """
    Accepts file bytes and filename, extracts text, parses resume, and returns structured data.
    """
    ext = filename.lower().split(".")[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        text = extract_text_from_file(tmp_path)
        result = extract_resume_data(text)
        # If all are missing, try extracting from top 5 lines
        if not result.get("full_name") and not result.get("email") and not result.get("phone_number"):
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            if result["email"]:
                result["email"] = extract_email_from_lines(lines)
            if result["phone_number"]:
                result["phone_number"] = extract_phone_from_lines(lines)
        return result
    finally:
        os.remove(tmp_path)
        
def split_experience_sections(resume_text, max_chunks=5):
    """
    Naive splitter: splits resume text into chunks based on 'Experience' or similar keywords.
    You may want to improve this for your specific resume formats.
    """
    # Try to split by common section headers
    sections = re.split(r'\n(?=Experience|Work History|Work Experience|Professional Experience|Employment History|Professional Background)', resume_text, flags=re.IGNORECASE)
    print("Sections found:", sections)
    # Always include the first section (personal info, summary, etc.)
    head = sections[0]
    experiences = sections
    # Further split experiences if too many lines
    chunks = []
    chunk = []
    for exp in experiences:
        chunk.append(exp)
        if len(chunk) >= max_chunks:
            chunks.append('\n'.join(chunk))
            chunk = []
    if chunk:
        chunks.append('\n'.join(chunk))
    # Return head (for personal info) and experience chunks
    return head, chunks

def extract_resume_data_chunked(resume_text: str, chunk_size=5, rate_limit_seconds=5):
    if not resume_text.strip():
        return {
            "full_name": None,
            "email": None,
            "phone_number": None,
            "work_experience": []
        }

    # Split resume into head and experience chunks
    head, exp_chunks = split_experience_sections(resume_text, max_chunks=chunk_size)

    # 1. Extract personal info from the head section
    prompt = build_prompt(head)
    response = co.generate(
        model="command-r-plus",
        prompt=prompt,
        temperature=0.2
    )
    raw_output = response.generations[0].text
    json_str = clean_json_string(raw_output)
    try:
        parsed = json.loads(json_str)
    except Exception as e:
        print("Raw Cohere output (head):\n", raw_output)
        raise ValueError("Failed to parse JSON response from Cohere (head)") from e

    # Get personal info
    full_name = parsed.get("Full Name")
    email = parsed.get("Email")
    phone_number = parsed.get("Phone Number")
    mapped_work_exp = []

    # 2. Extract work experiences from each experience chunk
    for chunk in exp_chunks:
        time.sleep(rate_limit_seconds)  # Respect Cohere rate limit
        prompt = build_prompt(chunk)
        response = co.generate(
            model="command-r-plus",
            prompt=prompt,
            temperature=0.2
        )
        raw_output = response.generations[0].text
        json_str = clean_json_string(raw_output)
        try:
            parsed_chunk = json.loads(json_str)
            print("Parsed chunk:", parsed_chunk)
        except Exception as e:
            print("Raw Cohere output (chunk):\n", raw_output)
            continue  # skip this chunk if it fails

        work_exp = parsed_chunk.get("Work Experience", [])
        if isinstance(work_exp, list):
            for exp in work_exp:
                if isinstance(exp, dict):
                    mapped_work_exp.append({
                        "company_name": exp.get("Company Name", "N/A"),
                        "customer_name": exp.get("Customer Name", "N/A"),
                        "role": exp.get("Role", "N/A"),
                        "duration": exp.get("Duration", "N/A"),
                        "skills_technologies": [s for s in exp.get("Skills/Technologies", []) if isinstance(s, str) and s.strip()],
                        "industry_domain": exp.get("Industry/Domain", "N/A"),
                        "location": exp.get("Location", "N/A")
                    })

    return {
        "full_name": full_name,
        "email": email,
        "phone_number": phone_number,
        "work_experience": mapped_work_exp
    }
