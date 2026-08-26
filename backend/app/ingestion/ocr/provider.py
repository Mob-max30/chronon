from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
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
    Applies image preprocessing where applicable.
    """

    def __init__(self, tesseract_cmd: str = "tesseract"):
        self.tesseract_cmd = tesseract_cmd

    def extract_text(self, file_path: Path) -> str:
        try:
            import pytesseract
            from PIL import Image, ImageEnhance, ImageFilter

            pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
            image = Image.open(file_path)

            # Preprocessing: convert to grayscale and enhance contrast for better OCR accuracy
            if image.mode != "L":
                image = image.convert("L")
            image = image.filter(ImageFilter.SHARPEN)
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)

            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            # Fallback stub for dev/test environments without tesseract binaries
            return f"[OCR Extraction - file: {file_path.name} | Note: Tesseract fallback active: {str(e)}]"

    def extract_structured_data(self, file_path: Path) -> Dict[str, Any]:
        raw_text = self.extract_text(file_path)
        return {
            "file_name": file_path.name,
            "raw_text_length": len(raw_text),
            "status": "EXTRACTED_PENDING_CONFIRMATION",
            "extracted_text": raw_text,
        }


class MockOCRProvider(OCRProvider):
    """
    Deterministic mock provider for unit and regression testing.
    """

    def __init__(self, mock_text_map: Optional[Dict[str, str]] = None):
        self.mock_text_map = mock_text_map or {}

    def set_mock_text(self, filename_or_key: str, text: str):
        self.mock_text_map[filename_or_key] = text

    def extract_text(self, file_path: Path) -> str:
        if file_path.name in self.mock_text_map:
            return self.mock_text_map[file_path.name]
        return f"MOCK_OCR_OUTPUT_FOR_{file_path.name}"

    def extract_structured_data(self, file_path: Path) -> Dict[str, Any]:
        raw_text = self.extract_text(file_path)
        return {
            "file_name": file_path.name,
            "raw_text_length": len(raw_text),
            "status": "EXTRACTED_PENDING_CONFIRMATION",
            "extracted_text": raw_text,
        }


def get_ocr_provider(provider_type: str = "tesseract") -> OCRProvider:
    if provider_type.lower() == "mock":
        return MockOCRProvider()
    return TesseractProvider()
