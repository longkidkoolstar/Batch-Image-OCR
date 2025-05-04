# Batch Image OCR Tool

A Python application with a graphical user interface for extracting text from multiple images and saving the results to a JSON file.

## Features

- Select individual image files or entire folders for batch processing
- Extract text from images using Tesseract OCR
- Save extracted text to a JSON file
- User-friendly GUI with progress tracking

## Requirements

- Python 3.6 or higher
- Tesseract OCR installed on your system
- Python packages listed in `requirements.txt`

## Installation

1. Install Tesseract OCR:

   **Windows:**
   - Download the installer from [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
   - Run the installer and follow the instructions
   - **Important:** During installation, check the option "Add to PATH" to make Tesseract available system-wide
   - Default installation path is usually `C:\Program Files\Tesseract-OCR\`
   - After installation, you may need to restart your computer for PATH changes to take effect

   **macOS:**
   - Install using Homebrew: `brew install tesseract`

   **Linux:**
   - Install using apt: `sudo apt install tesseract-ocr`

2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python main.py
   ```

2. Use the "Add Files" button to select individual image files or "Add Folder" to add all images from a directory.

3. Select an output JSON file location using the "Select Output File" button.

4. Click "Process Images" to start the OCR process.

5. Once processing is complete, the extracted text will be saved to the specified JSON file.

## Output Format

The output JSON file will have the following structure:

```json
{
    "image1.jpg": "Extracted text from image1",
    "image2.png": "Extracted text from image2",
    ...
}
```

## Troubleshooting

### Tesseract Not Found Error

If you see an error like "tesseract is not installed or it's not in your PATH", try these solutions:

1. **Check Tesseract Installation:**
   - Verify that Tesseract is properly installed
   - For Windows, make sure it was added to your PATH during installation
   - Try restarting your computer after installation

2. **Specify Tesseract Path in the Application:**
   - Use the "Set Tesseract Path" button in the application
   - Navigate to your Tesseract installation directory and select the `tesseract.exe` file
   - Common locations:
     - Windows: `C:\Program Files\Tesseract-OCR\tesseract.exe`
     - Windows (32-bit): `C:\Program Files (x86)\Tesseract-OCR\tesseract.exe`

3. **Verify Tesseract Works:**
   - Open a command prompt/terminal and type: `tesseract --version`
   - If this command works, Tesseract is properly installed and in your PATH
   - If not, you need to add the Tesseract installation directory to your PATH or reinstall with the PATH option enabled

## License

MIT
