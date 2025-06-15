import io
import re
import spacy
import fitz  # PyMuPDF
import csv
from keybert import KeyBERT
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
from docx import Document

kw_model = KeyBERT(model='all-MiniLM-L6-v2')
resume_ner = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")
embed_model = SentenceTransformer('all-MiniLM-L6-v2')
nlp = spacy.load("en_core_web_sm")
name_pipe = pipeline("ner", grouped_entities=True)

# Define all possible section heading variants
EXPERIENCE_HEADINGS = {
    "EXPERIENCE", "EXPERIENCES", "WORK EXPERIENCE", "WORK", "WORK HISTORY",
    "PROFESSIONAL EXPERIENCE", "EMPLOYMENT", "EMPLOYMENT HISTORY", "CAREER HISTORY"
}
EDUCATION_HEADINGS = {
    "EDUCATION", "EDUCATIONAL QUALIFICATION", "ACADEMICS", "ACADEMIC BACKGROUND", "EDUCATIONAL BACKGROUND", "QUALIFICATIONS"
}
SKILLS_HEADINGS = {
    "SKILLS", "TECHNICAL SKILLS", "TECHNICAL EXPERTISE", "SKILL SET", "CORE COMPETENCIES", "AREAS OF EXPERTISE"
}
PROJECTS_HEADINGS = {
    "PROJECTS", "PERSONAL PROJECTS", "ACADEMIC PROJECTS", "PROJECT EXPERIENCE", "PROJECT WORK"
}
CERTIFICATIONS_HEADINGS = {
    "CERTIFICATIONS", "CERTIFICATION", "LICENSES", "LICENSE", "PROFESSIONAL CERTIFICATIONS"
}
ACHIEVEMENTS_HEADINGS = {
    "ACHIEVEMENTS", "AWARDS", "HONORS", "HONOURS", "RECOGNITION", "ACCOMPLISHMENTS"
}
OBJECTIVE_HEADINGS = {
    "OBJECTIVE", "CAREER OBJECTIVE", "PROFESSIONAL OBJECTIVE", "SUMMARY", "PROFILE SUMMARY", "PROFESSIONAL SUMMARY"
}

# Combine for extraction and all possible headings
EXTRACT_SECTIONS = (
    EDUCATION_HEADINGS |
    SKILLS_HEADINGS |
    EXPERIENCE_HEADINGS
)
ALL_SECTION_HEADINGS = (
    EXTRACT_SECTIONS |
    PROJECTS_HEADINGS |
    CERTIFICATIONS_HEADINGS |
    ACHIEVEMENTS_HEADINGS |
    OBJECTIVE_HEADINGS
)

def load_tech_keywords(csv_path):
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)  # skip header
        return set(row[0].strip().lower() for row in reader if row)

# Load tech keywords once at module level
TECH_KEYWORDS = load_tech_keywords("app/skills.csv")

def extract_text_from_pdf_bytes(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    lines = []
    for page in doc:
        blocks = page.get_text("blocks")
        blocks.sort(key=lambda b: (round(b[1]), round(b[0])))
        for b in blocks:
            for line in b[4].split('\n'):
                if line.strip():
                    lines.append(line.strip())
    return "\n".join(lines)


def extract_text_from_docx_bytes(file_bytes):
    doc = Document(io.BytesIO(file_bytes))
    return "\n".join([para.text.strip() for para in doc.paragraphs if para.text.strip()])

def extract_name_and_title(lines):
    name = ""
    title = ""

    # Use transformer NER on the first line to get name
    if lines:
        entities = name_pipe(lines[0])
        for ent in entities:
            if ent['entity_group'] == "PER":
                name = ent['word'].replace('##', '')
                break

        # Try spaCy NER if transformer NER fails
        if not name:
            doc = nlp(lines[0])
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    name = ent.text
                    break

        # Heuristic: Use the first line that looks like a name
        if not name:
            for line in lines[:5]:  # Check first 5 lines
                if (
                    not is_section(line)
                    and not re.search(r"@|\d{3}|\d{10}|https?://|\.com/|linkedin|github|leetcode", line.lower())
                ):
                    words = line.strip().split()
                    # Name is usually 2-4 words, all capitalized, no digits
                    if 1 < len(words) <= 4 and all(w[0].isupper() for w in words) and all(w.isalpha() for w in words):
                        name = line.strip()
                        break

    # Define what's not a title: contact info or section headers
    def is_not_title(line):
        return (
            re.search(r"@|\d{3}|\d{10}|https?://|\.com/|linkedin|github|leetcode", line.lower()) or
            is_section(line)
        )

    # Get first line with >5 words that is not contact or header
    for line in lines[1:]:
        if not is_not_title(line) and len(line.split()) > 5:
            title = line
            break

    return name, title


def extract_links(text):
    return re.findall(r"https?://[^\s]+|www\.[^\s]+|[^\s]+\.com/[^\s]*", text)

def is_section(line):
    return line.strip().upper() in ALL_SECTION_HEADINGS

def parse_resume(file_bytes, filename):
    # Determine file type and extract text
    if filename.lower().endswith(".pdf"):
        text = extract_text_from_pdf_bytes(file_bytes)
    elif filename.lower().endswith(".docx"):
        text = extract_text_from_docx_bytes(file_bytes)
    else:
        raise ValueError("Unsupported file type")
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    resume = {
        "name": "",
        "title": "",
        "contact": {
            "email": "",
            "phone": "",
            "location": "",
            "links": []
        },
        "experience": [],
        "education": [],
        "skills": "",
        "all_links": []
    }

    resume["all_links"] = extract_links(text)
    resume["name"], resume["title"] = extract_name_and_title(lines)
    contact_block = " ".join(lines[:10])
    email_match = re.search(r"[\w\.-]+@[\w\.-]+", contact_block)
    phone_match = re.search(r"\d{10}|\d{3}-\d{3}-\d{4}", contact_block)
    resume["contact"]["email"] = email_match.group(0) if email_match else ""
    resume["contact"]["phone"] = phone_match.group(0) if phone_match else ""
    resume["contact"]["links"] = extract_links(contact_block)
    sections = {key: [] for key in EXTRACT_SECTIONS}
    current = None
    for line in lines:
        upper_line = line.strip().upper()
        if upper_line in ALL_SECTION_HEADINGS:
            current = upper_line
        elif current in sections:
            sections[current].append(line)
    resume["education"] = parse_education(sections["EDUCATION"])
    resume["skills"] = "\n".join(sections["SKILLS"]).strip()
    resume["experience"] = parse_experiences(sections["EXPERIENCES"])
    return resume

def extract_skills_from_text(text, tech_keywords):
    found = set()
    text_lower = text.lower()
    for skill in tech_keywords:
        if skill in text_lower:
            found.add(skill)
    return sorted(found)

def postprocess_resume_skills(extracted_data, tech_keywords):
    # When extracting skills, use the extract_technologies function
    if not extracted_data.get("skills"):
        full_text = extracted_data.get("full_text", "")
        extracted_skills = extract_technologies(full_text, TECH_KEYWORDS)
        extracted_data["skills"] = ", ".join(extracted_skills)
    else:
        full_text = extracted_data.get("full_text", "")
        existing_skills = set(s.strip().lower() for s in extracted_data["skills"].split(",") if s.strip())
        additional_skills = set(extract_technologies(full_text, TECH_KEYWORDS))
        all_skills = existing_skills.union(s.lower() for s in additional_skills)
        extracted_data["skills"] = ", ".join(sorted(s.title() for s in all_skills))
    return extracted_data

def parse_education(lines):
    result = []
    i = 0

    def is_date(s):
        # Checks for year or month-year patterns
        return bool(re.search(r'\d{4}', s)) or re.search(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b', s, re.I)

    while i < len(lines):
        institution = lines[i] if i < len(lines) else ""
        degree = lines[i+1] if i+1 < len(lines) else ""
        date = ""
        extra = ""
        if i+2 < len(lines):
            if is_date(lines[i+2]):
                date = lines[i+2]
            else:
                extra = lines[i+2]
        edu = {
            "institution": institution,
            "degree": degree,
            "date": date
        }
        # Optionally, you can store extra in edu if you want to process it later
        result.append(edu)
        # Move to next block (3 if date or extra present, else 2 or 1)
        i += 3 if i+2 < len(lines) else (2 if i+1 < len(lines) else 1)
    return result

def clean_text(text):
    text = text.lower()
    text = re.sub(r"\bgained (hands-on )?experience\b", "", text)
    text = re.sub(r"\b(used|working with|exposure to|familiar with|experience in)\b", "", text)
    text = re.sub(r"[^\w\s\.\-]", "", text)
    return re.sub(r"\s+", " ", text).strip()

def extract_technologies(text, tech_keywords, top_n=10):
    cleaned = clean_text(text)
    tech_keywords = {k.lower() for k in tech_keywords}
    tech_found = set()

    # 1️⃣ KeyBERT
    keybert_kws = kw_model.extract_keywords(
        cleaned,
        keyphrase_ngram_range=(1, 3),
        stop_words='english',
        use_mmr=True,
        diversity=0.7,
        top_n=top_n
    )
    tech_found.update(k for k, _ in keybert_kws if k in tech_keywords)

    # 2️⃣ NER model — you forgot to assign ner_output
    ner_output = resume_ner(text)
    for ent in ner_output:
        if ent['entity_group'] in ["MISC", "ORG"] and ent['word'].lower() in tech_keywords:
            tech_found.add(ent['word'].lower())

    # 3️⃣ Exact match from cleaned block
    for skill in tech_keywords:
        if re.search(r'\b' + re.escape(skill) + r'\b', cleaned):
            tech_found.add(skill)

    # 4️⃣ Semantic similarity
    block_emb = embed_model.encode(cleaned, convert_to_tensor=True)
    keyword_embs = embed_model.encode(list(tech_keywords), convert_to_tensor=True)
    cos_scores = util.cos_sim(block_emb, keyword_embs)[0]
    for i, score in enumerate(cos_scores):
        if score > 0.85:
            tech_found.add(list(tech_keywords)[i])

    return sorted(t.title() for t in tech_found)

def parse_experiences(lines):
    experiences = []
    i = 0
    n = len(lines)

    def is_date(s):
        return bool(re.search(r'\d{4}', s)) or re.search(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b', s, re.I)

    def flush_block(block):
        if not block:
            return

        customer, role, date, tech_lines = "", "", "", []
        i = 0

        if i < len(block):
            customer = block[i]; i += 1
        if i < len(block):
            role = block[i]; i += 1
        if i < len(block):
            # Check if this line is a date
            if is_date(block[i]):
                date = block[i]
                i += 1
            else:
                # Not a date, treat as extra detail for tech_lines
                tech_lines.append(block[i])
                i += 1
        tech_lines += block[i:]

        tech_text = " ".join(tech_lines)
        tech_set = extract_technologies(tech_text, TECH_KEYWORDS)

        experiences.append({
            "customer": customer,
            "role": role,
            "project_dates": date,
            "technology": sorted(tech_set)
        })


    current_block = []
    while i < n:
        line = lines[i]
        if (
            i + 2 < n and
            not is_section(lines[i]) and
            not is_section(lines[i + 1]) and
            is_date(lines[i + 2])
        ):
            # Found start of a new block
            if current_block:
                flush_block(current_block)
                current_block = []
            current_block = [lines[i], lines[i + 1], lines[i + 2]]
            i += 3
        else:
            current_block.append(line)
            i += 1

    flush_block(current_block)
    return experiences

def parse_projects(lines):
    result = []
    i = 0
    while i < len(lines):
        proj = {"title": "", "date": "", "description": ""}
        if i < len(lines): proj["title"] = lines[i]; i += 1
        if i < len(lines) and re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{4})', lines[i]):
            proj["date"] = lines[i]; i += 1
        desc = []
        while i < len(lines) and not is_section(lines[i]) and not re.match(r'[A-Z].* - .*', lines[i]):
            desc.append(lines[i])
            i += 1
        proj["description"] = " ".join(desc)
        result.append(proj)
    return result

def parse_certifications(lines):
    result = []
    i = 0
    while i < len(lines):
        cert = {"title": lines[i], "details": ""}
        i += 1
        details = []
        while i < len(lines) and not is_section(lines[i]):
            details.append(lines[i])
            i += 1
        cert["details"] = " ".join(details)
        result.append(cert)
    return result

def parse_achievements(lines):
    return [line.lstrip("• ").strip() for line in lines if line]

def process_file(path):
    ext = os.path.splitext(path)[-1].lower()
    if ext == '.pdf':
        text = extract_text_from_pdf(path)
    elif ext == '.docx':
        text = extract_text_from_docx(path)
    else:
        print(f"⚠️ Skipping unsupported file: {path}")
        return None

    return parse_resume(text)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Parse single resume or folder of resumes")
    parser.add_argument("input_path", help="Path to a .pdf/.docx file or a folder")
    parser.add_argument("--skills", default="skills.csv", help="Path to skills.csv")
    args = parser.parse_args()

    TECH_KEYWORDS = load_tech_keywords(args.skills)

    input_path = args.input_path
    if os.path.isdir(input_path):
        # Folder mode
        for fname in os.listdir(input_path):
            full_path = os.path.join(input_path, fname)
            if fname.lower().endswith((".pdf", ".docx")):
                print(f"\n📄 Processing: {fname}")
                result = process_file(full_path)
                if result:
                    print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        # Single file mode
        result = process_file(input_path)
        if result:
            print(json.dumps(result, indent=2, ensure_ascii=False))
