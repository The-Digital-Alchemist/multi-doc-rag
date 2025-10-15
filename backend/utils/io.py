"""
Input/Output utilities for file handling and text extraction.

This module provides functionality for saving uploaded files and extracting
text content from various document formats including TXT, PDF, and DOCX files.
"""

import os
import uuid
from pathlib import Path
from pypdf import PdfReader
import docx


def save_upload(file_obj, dest_dir: str) -> str:
    """
    Save an uploaded file to the specified directory with a unique filename.
    
    This function generates a unique filename using UUID to prevent conflicts
    and saves the uploaded file to the specified destination directory.
    
    Args:
        file_obj: FastAPI UploadFile object containing the uploaded file
        dest_dir (str): Destination directory path where the file should be saved
        
    Returns:
        str: Full path to the saved file
        
    Note:
        The original filename extension is preserved for proper file type detection.
    """
    # Extract file extension and generate unique filename
    ext = Path(file_obj.filename).suffix.lower()
    fid = f"{uuid.uuid4().hex}{ext}"    
    fullpath = Path(dest_dir) / fid
    fpath = str(fullpath)
    
    # Write file content to disk
    with open(fpath, "wb") as f:
        f.write(file_obj.file.read())
    
    return fpath


def read_text_from_path(path: str) -> str:
    """
    Extract text content from a file based on its extension.
    
    This function supports multiple file formats and extracts plain text
    content for processing by the RAG system. It handles encoding issues
    gracefully and returns clean text content.
    
    Args:
        path (str): Path to the file to extract text from
        
    Returns:
        str: Extracted text content from the file
        
    Raises:
        ValueError: If the file type is not supported
        FileNotFoundError: If the file doesn't exist
        Exception: If text extraction fails for supported formats
        
    Supported formats:
        - .txt: Plain text files
        - .pdf: PDF documents
        - .docx: Microsoft Word documents
    """
    ext = Path(path).suffix.lower()
    
    # Extract text from plain text files
    if ext == ".txt":
        with open(path, "r", encoding="UTF-8", errors="ignore") as f:
            return f.read()

    # Extract text from PDF files
    elif ext == ".pdf":
        chunks = []
        reader = PdfReader(path)

        # Extract text from each page
        for page in reader.pages:
            t = page.extract_text() or ""
            chunks.append(t)
        return "\n".join(chunks).strip()

    # Extract text from Word documents
    elif ext == ".docx":
        chunks = []
        doc = docx.Document(path)

        # Extract text from each paragraph
        for p in doc.paragraphs:
            t = p.text or ""
            chunks.append(t)
        return "\n".join(chunks).strip()
 
    else:
        raise ValueError("Unsupported file type")