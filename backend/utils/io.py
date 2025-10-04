import os
import uuid
from pathlib import Path
from pypdf import PdfReader
import docx



def save_upload(file_obj, dest_dir: str) -> str:

    ext = Path(file_obj.filename).suffix.lower()
    fid = f"{uuid.uuid4().hex}{ext}"    
    fullpath = Path(dest_dir) / fid
    fpath = str(fullpath)
    with open(fpath, "wb") as f:
        f.write(file_obj.file.read())
    
    return fpath


def read_text_from_path(path: str) -> str:
    
    ext = Path(path).suffix.lower()
    # Extracting text from a txt file
    if ext == ".txt":
        with open(path, "r", encoding="UTF-8", errors="ignore") as f:
            return f.read()

    elif ext == ".pdf":
        # Extracting text from a pdf file
        chunks = []
        reader = PdfReader(path)

        for page in reader.pages:
            t = page.extract_text() or ""
            chunks.append(t)
        return "\n".join(chunks).strip()

    elif ext == ".docx":
        # Extracting text from a docx file
        chunks = []
        doc = docx.Document(path)

        for p in doc.paragraphs:
            t = p.text or ""
            chunks.append(t)
        return "\n".join(chunks).strip()
 

    else:
        raise ValueError("Unsupported file type")