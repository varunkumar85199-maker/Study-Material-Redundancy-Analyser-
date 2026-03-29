"""
pdf_processor.py — PDF, DOCX, TXT files se text extract karta hai.
"""

import pdfplumber
import re


class PDFProcessor:

    def extract_text(self, filepath: str) -> str:
        """File extension check karke sahi extractor use karta hai."""
        ext = filepath.rsplit(".", 1)[-1].lower()

        if ext == "pdf":
            return self._from_pdf(filepath)

        elif ext == "docx":
            return self._from_docx(filepath)

        else:
            return self._from_txt(filepath)

    # ───────────────────────────────────────────────────────────────
    # 1. PDF Text Extract
    # ───────────────────────────────────────────────────────────────
    def _from_pdf(self, path: str) -> str:
        pages = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text.strip())
        return "\n\n".join(pages)

    # ───────────────────────────────────────────────────────────────
    # 2. DOCX Text Extract
    # ───────────────────────────────────────────────────────────────
    def _from_docx(self, path: str) -> str:
        try:
            import docx
            doc = docx.Document(path)
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except ImportError:
            return "[python-docx install karein: pip install python-docx]"

    # ───────────────────────────────────────────────────────────────
    # 3. TXT Text Extract
    # ───────────────────────────────────────────────────────────────
    def _from_txt(self, path: str) -> str:
        with open(path, encoding="utf-8", errors="ignore") as f:
            return f.read()

    # ───────────────────────────────────────────────────────────────
    # Clean & Sentence Split Helpers
    # ───────────────────────────────────────────────────────────────
    def split_into_sentences(self, text: str) -> list[str]:
        """Text ko sentences me todta hai."""
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        return [s.strip() for s in sentences if len(s.strip()) > 20]

    def clean(self, text: str) -> str:
        """Extra whitespace aur garbage characters remove karta hai."""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\x20-\x7E\n]', '', text)
        return text.strip()  
