from abc import ABC, abstractmethod
from typing import Dict, Any
from pathlib import Path


class OCRProvider(ABC):
    """
    Pluggable OCR Provider Interface.
    Decouples document image/scanned PDF ingestion from specific engine implementations.
    """

    @abstractmethod
    def extract_text(self, file_path: Path) -> str:
        """Extracts raw text from an image or document."""
        pass

    @abstractmethod
    def extract_structured_data(self, file_path: Path) -> Dict[str, Any]:
        """Extracts key-value or table structured data from a document."""
        pass


class TesseractProvider(OCRProvider):
    """
    Default Open-Source OCR implementation using Tesseract OCR engine.
    """

    def __init__(self, tesseract_cmd: str = "tesseract"):
        self.tesseract_cmd = tesseract_cmd

    def extract_text(self, file_path: Path) -> str:
        try:
            import pytesseract
            from PIL import Image

            pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
            image = Image.open(file_path)
            return pytesseract.image_to_string(image)
        except Exception as e:
            # Fallback stub for dev environments without tesseract binaries
            return f"[OCR Extraction Stub - file: {file_path.name} | Error: {str(e)}]"

    def extract_structured_data(self, file_path: Path) -> Dict[str, Any]:
        raw_text = self.extract_text(file_path)
        return {
            "file_name": file_path.name,
            "raw_text_length": len(raw_text),
            "status": "EXTRACTED_PENDING_CONFIRMATION",
            "extracted_text": raw_text,
        }
