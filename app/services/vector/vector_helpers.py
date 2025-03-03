import io
import json
import os
from typing import List, BinaryIO, Tuple, Dict, Any

import PyPDF2
import mammoth
import pandas as pd

from app.models.vector import DocumentChunk, DocumentType


def convert_to_dict(obj):
    """Recursively convert custom objects to dictionaries"""
    if isinstance(obj, dict):
        return {k: convert_to_dict(v) for k, v in obj.items()}
    elif hasattr(obj, '__dict__'):
        return convert_to_dict(obj.__dict__)
    elif hasattr(obj, 'items'):
        return {k: convert_to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_dict(item) for item in obj]
    else:
        return obj


def get_document_type(filename: str) -> str:
    """Determine document type from filename."""
    ext = os.path.splitext(filename)[1].lower().lstrip('.')

    if ext == 'pdf':
        return DocumentType.PDF.value
    elif ext in ['doc', 'docx']:
        return DocumentType.DOCX.value
    elif ext in ['xls', 'xlsx', 'xlsm']:
        return DocumentType.XLSX.value
    elif ext == 'csv':
        return DocumentType.CSV.value
    elif ext == 'txt':
        return DocumentType.TXT.value
    elif ext in ['htm', 'html']:
        return DocumentType.HTML.value
    elif ext in ['ppt', 'pptx']:
        return DocumentType.PPTX.value
    elif ext == 'md':
        return DocumentType.MD.value
    elif ext == 'json':
        return DocumentType.JSON.value
    else:
        return DocumentType.OTHER.value


async def extract_text(
        file_content: bytes,
        document_type: str,
        filename: str
) -> Tuple[str, Dict[str, Any]]:
    """
    Extract text from different document types.
    Returns tuple of (text_content, metadata).
    """
    file_stream = io.BytesIO(file_content)

    if document_type == DocumentType.PDF.value:
        return extract_from_pdf(file_stream)

    elif document_type == DocumentType.DOCX.value:
        return extract_from_docx(file_stream)

    elif document_type == DocumentType.XLSX.value:
        return extract_from_excel(file_stream)

    elif document_type == DocumentType.CSV.value:
        return extract_from_csv(file_stream)

    elif document_type == DocumentType.TXT.value:
        text = file_content.decode('utf-8', errors='replace')
        return text, {"line_count": text.count('\n') + 1}

    elif document_type == DocumentType.JSON.value:
        try:
            json_data = json.loads(file_content)
            text = json.dumps(json_data, indent=2)
            return text, {
                "json_keys": list(json_data.keys()) if isinstance(json_data, dict) else [],
                "structure": "object" if isinstance(json_data, dict) else "array"
            }
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON file")

    elif document_type == DocumentType.HTML.value:
        from html.parser import HTMLParser

        class HTMLTextExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.text = []

            def handle_data(self, data):
                self.text.append(data.strip())

        parser = HTMLTextExtractor()
        parser.feed(file_content.decode('utf-8', errors='replace'))
        text = " ".join(parser.text)
        return text, {"html_size": len(file_content)}

    else:
        try:
            text = file_content.decode('utf-8', errors='replace')
            return text, {"size": len(text)}
        except UnicodeDecodeError:
            return f"Binary file: {filename}", {"binary": True}


def extract_from_pdf(file_stream: BinaryIO) -> Tuple[str, Dict[str, Any]]:
    """Extract text from PDF files."""
    try:
        reader = PyPDF2.PdfReader(file_stream)
        text_content = ""
        for page_num in range(len(reader.pages)):
            text_content += reader.pages[page_num].extract_text() + "\n\n"

        metadata = {
            "page_count": len(reader.pages),
            "pdf_info": reader.metadata or {}
        }

        return text_content, metadata

    except Exception as e:
        raise ValueError(f"Failed to process PDF: {str(e)}")


def extract_from_docx(file_stream: BinaryIO) -> Tuple[str, Dict[str, Any]]:
    """Extract text from DOCX files."""
    try:
        # Reset stream position to beginning
        file_stream.seek(0)

        result = mammoth.extract_raw_text(file_stream)
        text_content = result.value

        metadata = {
            "paragraph_count": text_content.count('\n') + 1,
            "section_count": 1,  # Default without detailed inspection
            "has_tables": False,  # Without inspection, we can't determine this accurately
            "table_count": 0  # Without inspection, we can't determine this accurately
        }

        return text_content, metadata

    except Exception as e:
        raise ValueError(f"Failed to process DOCX: {str(e)}")


def extract_from_excel(file_stream: BinaryIO) -> Tuple[str, Dict[str, Any]]:
    """Extract text from Excel files."""
    try:
        xls = pd.ExcelFile(file_stream)
        sheet_names = xls.sheet_names

        text_content = ""
        sheet_data = {}

        for sheet in sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet)

            # Track shape and columns for metadata
            sheet_data[sheet] = {
                "rows": df.shape[0],
                "columns": df.shape[1],
                "column_names": df.columns.tolist()
            }

            # Convert dataframe to string
            text_content += f"Sheet: {sheet}\n"
            text_content += df.to_string(index=False) + "\n\n"

        metadata = {
            "sheet_count": len(sheet_names),
            "sheet_names": sheet_names,
            "sheets": sheet_data
        }

        return text_content, metadata

    except Exception as e:
        raise ValueError(f"Failed to process Excel file: {str(e)}")


def extract_from_csv(file_stream: BinaryIO) -> Tuple[str, Dict[str, Any]]:
    """Extract text from CSV files."""
    try:
        df = pd.read_csv(file_stream)

        text_content = df.to_string(index=False)

        metadata = {
            "row_count": df.shape[0],
            "column_count": df.shape[1],
            "column_names": df.columns.tolist()
        }

        return text_content, metadata

    except Exception as e:
        # Try with different encoding if the first attempt fails
        try:
            file_stream.seek(0)
            df = pd.read_csv(file_stream, encoding='latin1')

            text_content = df.to_string(index=False)

            metadata = {
                "row_count": df.shape[0],
                "column_count": df.shape[1],
                "column_names": df.columns.tolist(),
                "encoding": "latin1"
            }

            return text_content, metadata

        except Exception as nested_e:
            raise ValueError(
                f"Failed to process CSV file: {str(e)}, also tried with latin1 encoding: {str(nested_e)}")


def split_text(text: str, document_id: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[DocumentChunk]:
    """
    Split text into overlapping chunks for embedding.
    """
    chunks = []

    # Skip empty text
    if not text.strip():
        # Create at least one chunk even for empty documents
        return [DocumentChunk(
            document_id=document_id,
            chunk_index=0,
            content="[Empty document]",
            chunk_metadata={"empty": True}
        )]

    # Use simple character-based chunking
    text_length = len(text)
    start = 0
    chunk_index = 0

    while start < text_length:
        # Calculate end position for this chunk
        end = min(start + chunk_size, text_length)

        # Extract chunk text
        chunk_text = text[start:end]

        # Create chunk object
        chunk = DocumentChunk(
            document_id=document_id,
            chunk_index=chunk_index,
            content=chunk_text,
            chunk_metadata={
                "start_char": start,
                "end_char": end,
                "char_length": end - start
            }
        )

        chunks.append(chunk)

        # Move start position for next chunk, accounting for overlap
        start = start + chunk_size - chunk_overlap

        # Avoid creating zero-length chunks at the end
        if start >= text_length:
            break

        chunk_index += 1

    return chunks
