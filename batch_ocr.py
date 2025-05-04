#!/usr/bin/env python3
"""
OCR Processing Module
Handles the extraction of text from images using Tesseract OCR.
"""

import os
import json
import sys
import platform
from PIL import Image
import pytesseract
from typing import List, Dict, Union, Optional

class BatchOCR:
    """Class for handling batch OCR processing of images"""

    def __init__(self, tesseract_cmd: Optional[str] = None):
        """
        Initialize the BatchOCR processor

        Args:
            tesseract_cmd: Path to tesseract executable (optional)
        """
        # Set default Tesseract path based on OS if not provided
        if not tesseract_cmd:
            if platform.system() == 'Windows':
                # Common installation paths on Windows
                possible_paths = [
                    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                ]
                for path in possible_paths:
                    if os.path.exists(path):
                        tesseract_cmd = path
                        break

        # Set the Tesseract command path if provided or found
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

        # Check if Tesseract is available
        try:
            pytesseract.get_tesseract_version()
            self.tesseract_available = True
        except Exception:
            self.tesseract_available = False

    def process_image(self, image_path: str) -> str:
        """
        Process a single image and extract text

        Args:
            image_path: Path to the image file

        Returns:
            Extracted text from the image
        """
        if not self.tesseract_available:
            error_msg = (
                "Tesseract OCR is not installed or not in your PATH. "
                "Please install Tesseract OCR and make sure it's in your PATH, "
                "or provide the path to the executable when initializing BatchOCR. "
                "See README file for installation instructions."
            )
            raise RuntimeError(error_msg)

        try:
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img)
            return text.strip()
        except Exception as e:
            print(f"Error processing {image_path}: {str(e)}")
            return ""

    def process_batch(self, image_paths: List[str], callback=None) -> Dict[str, str]:
        """
        Process multiple images and extract text

        Args:
            image_paths: List of paths to image files
            callback: Optional callback function to report progress

        Returns:
            Dictionary mapping image paths to extracted text
        """
        results = {}
        total = len(image_paths)

        for i, path in enumerate(image_paths):
            if callback:
                callback(i, total, os.path.basename(path))

            text = self.process_image(path)
            results[path] = text

        return results

    def save_to_json(self, results: Dict[str, str], output_path: str) -> bool:
        """
        Save OCR results to a JSON file

        Args:
            results: Dictionary of OCR results
            output_path: Path to save the JSON file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert to a more readable format with just filenames as keys
            formatted_results = {os.path.basename(k): v for k, v in results.items()}

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(formatted_results, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving results to {output_path}: {str(e)}")
            return False
