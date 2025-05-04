#!/usr/bin/env python3
"""
Batch Image OCR Tool
A GUI application for extracting text from multiple images and saving to JSON.
"""

import sys
from gui import OCRApplication

def main():
    """Main entry point for the application"""
    app = OCRApplication()
    app.run()

if __name__ == "__main__":
    main()
