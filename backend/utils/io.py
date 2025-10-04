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
