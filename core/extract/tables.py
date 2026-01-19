"""
Table extraction from PDFs using camelot-py or pdfplumber.
"""
from typing import List, Dict, Any, Optional

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    pdfplumber = None


def extract_tables_from_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Extract tables from PDF using pdfplumber.
    
    Args:
        pdf_path: Path to the PDF file
    
    Returns:
        List of tables, each with page number and table data
    """
    if not PDFPLUMBER_AVAILABLE:
        return [{
            "page": 1,
            "table_index": 0,
            "error": "pdfplumber not installed",
            "data": [],
            "text": "[Table extraction not available: Install pdfplumber]"
        }]
    
    tables = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                page_tables = page.extract_tables()
                
                for table_idx, table in enumerate(page_tables):
                    if table and len(table) > 0:
                        # Convert table to structured format
                        table_data = {
                            "page": page_num,
                            "table_index": table_idx,
                            "rows": len(table),
                            "columns": len(table[0]) if table else 0,
                            "data": table,
                            # Convert to markdown-like format for embedding
                            "text": _table_to_text(table)
                        }
                        tables.append(table_data)
    except Exception as e:
        # Return error info
        tables.append({
            "page": 1,
            "table_index": 0,
            "error": str(e),
            "data": [],
            "text": f"[Table extraction error: {str(e)}]"
        })
    
    return tables


def _table_to_text(table: List[List[str]]) -> str:
    """
    Convert table data to text format for embedding.
    """
    if not table:
        return ""
    
    lines = []
    for row in table:
        # Filter out None values and join with tabs
        clean_row = [str(cell) if cell else "" for cell in row]
        lines.append(" | ".join(clean_row))
    
    return "\n".join(lines)
