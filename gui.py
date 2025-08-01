#!/usr/bin/env python3
"""
GUI Module for Batch OCR Tool
Provides a user interface for selecting images, processing them, and saving results.
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
from typing import List, Optional, Callable
from tkinterdnd2 import DND_FILES, TkinterDnD
import threading
from batch_ocr import BatchOCR
import config
from PIL import ImageGrab, Image
import io
import tempfile

class OCRApplication:
    """Main application class for the OCR GUI"""

    def __init__(self):
        """Initialize the application"""
        self.root = TkinterDnD.Tk()
        self.root.title("Batch Image OCR Tool")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)

        self.selected_files: List[str] = []
        self.output_path: Optional[str] = None

        # Bind paste event
        self.root.bind('<Control-v>', self._paste_image)
        self.root.bind('<Command-v>', self._paste_image) # For macOS

        # Load configuration
        self._load_config()

        # Try to initialize OCR processor with saved Tesseract path
        self.ocr_processor = BatchOCR(tesseract_cmd=self.tesseract_path)

        self._create_widgets()
        self._create_layout()

        # Check Tesseract availability on startup
        if not self.ocr_processor.tesseract_available:
            self._show_tesseract_warning()

    def _load_config(self):
        """Load configuration from file"""
        # Load Tesseract path
        self.tesseract_path = config.get_config_value("tesseract_path")

        # Load last output directory
        last_output_dir = config.get_config_value("last_output_dir")
        if last_output_dir and os.path.exists(last_output_dir):
            self.last_output_dir = last_output_dir
        else:
            self.last_output_dir = os.path.expanduser("~")

        # Load last input directory
        last_input_dir = config.get_config_value("last_input_dir")
        if last_input_dir and os.path.exists(last_input_dir):
            self.last_input_dir = last_input_dir
        else:
            self.last_input_dir = os.path.expanduser("~")

    def _create_widgets(self):
        """Create all the widgets for the application"""
        # File selection frame
        self.file_frame = ttk.LabelFrame(self.root, text="Image Selection")
        self.file_list = tk.Listbox(self.file_frame, selectmode=tk.EXTENDED, height=10)
        self.file_scroll = ttk.Scrollbar(self.file_frame, orient=tk.VERTICAL, command=self.file_list.yview)
        self.file_list.configure(yscrollcommand=self.file_scroll.set)

        # Enable drag and drop for the file list
        self.file_list.drop_target_register(DND_FILES)
        self.file_list.dnd_bind('<<Drop>>', self._drop_files)

        # Buttons for file operations
        self.btn_frame = ttk.Frame(self.file_frame)
        self.add_btn = ttk.Button(self.btn_frame, text="Add Files", command=self._add_files)
        self.add_folder_btn = ttk.Button(self.btn_frame, text="Add Folder", command=self._add_folder)
        self.paste_btn = ttk.Button(self.btn_frame, text="Paste Image", command=self._paste_image)
        self.clear_btn = ttk.Button(self.btn_frame, text="Clear Selection", command=self._clear_selection)

        # Output selection
        self.output_frame = ttk.LabelFrame(self.root, text="Output Options")
        self.output_path_var = tk.StringVar()
        self.output_path_var.set("No output file selected")
        self.output_label = ttk.Label(self.output_frame, textvariable=self.output_path_var, wraplength=500)
        self.output_btn = ttk.Button(self.output_frame, text="Select Output File", command=self._select_output)

        self.display_output_var = tk.BooleanVar(value=False)
        self.display_output_checkbox = ttk.Checkbutton(self.output_frame, text="Display Output in GUI", variable=self.display_output_var, command=self._toggle_output_mode)

        # OCR Output Display Area
        self.ocr_output_frame = ttk.LabelFrame(self.root, text="OCR Output")
        self.ocr_output_text = tk.Text(self.ocr_output_frame, wrap=tk.WORD, height=10, state=tk.DISABLED)
        self.ocr_output_scroll = ttk.Scrollbar(self.ocr_output_frame, orient=tk.VERTICAL, command=self.ocr_output_text.yview)
        self.ocr_output_text.config(yscrollcommand=self.ocr_output_scroll.set)

        # Tesseract configuration
        self.tesseract_frame = ttk.LabelFrame(self.root, text="Tesseract OCR Configuration")
        self.tesseract_path_var = tk.StringVar()

        # Display the current Tesseract path
        if self.tesseract_path:
            self.tesseract_path_var.set(f"Using Tesseract at: {self.tesseract_path}")
        else:
            self.tesseract_path_var.set("Using default Tesseract installation")

        self.tesseract_label = ttk.Label(self.tesseract_frame, textvariable=self.tesseract_path_var, wraplength=500)
        self.tesseract_btn = ttk.Button(self.tesseract_frame, text="Set Tesseract Path", command=self._set_tesseract_path)

        # Progress indicators
        self.progress_frame = ttk.LabelFrame(self.root, text="Progress")
        self.progress_var = tk.StringVar()
        self.progress_var.set("Ready")
        self.progress_label = ttk.Label(self.progress_frame, textvariable=self.progress_var)
        self.progress_bar = ttk.Progressbar(self.progress_frame, orient=tk.HORIZONTAL, mode='determinate')

        # Process button
        self.process_btn = ttk.Button(self.root, text="Process Images", command=self._process_images)

    def _create_layout(self):
        """Arrange widgets in the layout"""
        # File selection area
        self.file_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.file_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Button area
        self.btn_frame.pack(fill=tk.X, padx=5, pady=5)
        self.add_btn.pack(side=tk.LEFT, padx=5)
        self.add_folder_btn.pack(side=tk.LEFT, padx=5)
        self.paste_btn.pack(side=tk.LEFT, padx=5)
        self.clear_btn.pack(side=tk.RIGHT, padx=5)

        # Output selection area
        self.output_frame.pack(fill=tk.X, padx=10, pady=10)
        self.output_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        self.output_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.display_output_checkbox.pack(side=tk.RIGHT, padx=5, pady=5)

        # Tesseract configuration area
        self.tesseract_frame.pack(fill=tk.X, padx=10, pady=10)
        self.tesseract_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        self.tesseract_btn.pack(side=tk.RIGHT, padx=5, pady=5)

        # Progress area
        self.progress_frame.pack(fill=tk.X, padx=10, pady=10)
        self.progress_label.pack(fill=tk.X, padx=5, pady=2)
        self.progress_bar.pack(fill=tk.X, padx=5, pady=5)

        # Process button
        self.process_btn.pack(pady=20)

        # OCR Output Display Area Layout
        self.ocr_output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.ocr_output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.ocr_output_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

    def _add_files(self):
        """Add individual files to the selection"""
        files = filedialog.askopenfilenames(
            title="Select Images",
            initialdir=self.last_input_dir,
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff *.tif *.gif"),
                ("All files", "*.*")
            ]
        )

        if files:
            # Save the last directory used
            last_dir = os.path.dirname(files[0])
            self.last_input_dir = last_dir
            config.update_config("last_input_dir", last_dir)

            for file in files:
                if file not in self.selected_files:
                    self.selected_files.append(file)
                    self.file_list.insert(tk.END, os.path.basename(file))

    def _add_folder(self):
        """Add all image files from a folder"""
        folder = filedialog.askdirectory(
            title="Select Folder Containing Images",
            initialdir=self.last_input_dir
        )

        if folder:
            # Save the last directory used
            self.last_input_dir = folder
            config.update_config("last_input_dir", folder)

            image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.gif')
            for root, _, files in os.walk(folder):
                for file in files:
                    if file.lower().endswith(image_extensions):
                        full_path = os.path.join(root, file)
                        if full_path not in self.selected_files:
                            self.selected_files.append(full_path)
                            self.file_list.insert(tk.END, file)

    def _clear_selection(self):
        """Clear the current file selection"""
        self.selected_files = []
        self.file_list.delete(0, tk.END)

    def _paste_image(self, event=None):
        """Paste image from clipboard and add to selected files"""
        try:
            # Attempt to get image from clipboard
            img = ImageGrab.grabclipboard()

            if img:
                # Save the image to a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                    img_path = temp_file.name
                    img.save(img_path)

                if img_path not in self.selected_files:
                    self.selected_files.append(img_path)
                    self.file_list.insert(tk.END, os.path.basename(img_path))
                    messagebox.showinfo("Image Pasted", f"Pasted image added: {os.path.basename(img_path)}")
            else:
                messagebox.showinfo("No Image", "No image found in clipboard.")
        except Exception as e:
            messagebox.showerror("Paste Error", f"Failed to paste image: {e}")

    def _toggle_output_mode(self):
        """Toggle between saving to file and displaying in GUI"""
        if self.display_output_var.get():
            self.output_btn.config(state=tk.DISABLED)
            self.output_path_var.set("Output will be displayed in GUI")
            self.output_path = None # Clear output path if displaying in GUI
        else:
            self.output_btn.config(state=tk.NORMAL)
            self.output_path_var.set("No output file selected")

    def _select_output(self):
        """Select the output JSON file"""
        file = filedialog.asksaveasfilename(
            title="Save OCR Results",
            initialdir=self.last_output_dir,
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.* ")]
        )

        if file:
            self.output_path = file
            self.output_path_var.set(file)
            # If a file is selected, uncheck the display in GUI option
            self.display_output_var.set(False)
            self._toggle_output_mode()

            # Save the last output directory
            last_dir = os.path.dirname(file)
            self.last_output_dir = last_dir
            config.update_config("last_output_dir", last_dir)

    def _drop_files(self, event):
        """Handle files dropped onto the listbox"""
        # TkinterDnD returns a string of paths, potentially with spaces
        # It's safer to parse it as a list of paths
        file_paths = self.root.tk.splitlist(event.data)
        
        for file_path in file_paths:
            # Check if it's a directory
            if os.path.isdir(file_path):
                self._add_folder_from_path(file_path)
            else:
                # Check if it's an image file
                image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.gif')
                if file_path.lower().endswith(image_extensions):
                    if file_path not in self.selected_files:
                        self.selected_files.append(file_path)
                        self.file_list.insert(tk.END, os.path.basename(file_path))
                else:
                    messagebox.showwarning(
                        "Unsupported File Type",
                        f"Skipping non-image file: {os.path.basename(file_path)}"
                    )
        
        # Update last input directory if files were added
        if file_paths:
            first_path = file_paths[0]
            if os.path.isfile(first_path):
                last_dir = os.path.dirname(first_path)
            else:
                last_dir = first_path # It's a directory
            self.last_input_dir = last_dir
            config.update_config("last_input_dir", last_dir)

    def _add_folder_from_path(self, folder_path):
        """Helper to add files from a folder path (used by drag and drop)"""
        image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.gif')
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(image_extensions):
                    full_path = os.path.join(root, file)
                    if full_path not in self.selected_files:
                        self.selected_files.append(full_path)
                        self.file_list.insert(tk.END, os.path.basename(full_path))

    def _update_progress(self, current: int, total: int, filename: str):
        """Update the progress indicators"""
        progress_pct = int((current / total) * 100)
        self.progress_bar['value'] = progress_pct
        self.progress_var.set(f"Processing {current+1}/{total}: {filename}")
        self.root.update_idletasks()

    def _process_images(self):
        """Process the selected images"""
        if not self.selected_files:
            messagebox.showwarning("No Images", "Please select at least one image to process.")
            return

        if not self.output_path and not self.display_output_var.get():
            messagebox.showwarning("No Output", "Please select an output file location or choose to display in GUI.")
            return

        # Disable UI during processing
        self._set_ui_state(False)

        # Start processing in a separate thread
        thread = threading.Thread(target=self._run_processing)
        thread.daemon = True
        thread.start()

    def _run_processing(self):
        """Run the OCR processing in a background thread"""
        try:
            results = self.ocr_processor.process_batch(
                self.selected_files,
                callback=self._update_progress
            )

            if self.display_output_var.get():
                # Display in GUI
                formatted_results = {os.path.basename(k): v for k, v in results.items()}
                output_text = json.dumps(formatted_results, indent=4, ensure_ascii=False)
                self.root.after(0, lambda: self._display_ocr_output(output_text))
                self.root.after(0, lambda: self._processing_complete(True, display_in_gui=True))
            else:
                # Save to file
                success = self.ocr_processor.save_to_json(results, self.output_path)
                self.root.after(0, lambda: self._processing_complete(success, display_in_gui=False))

        except Exception as e:
            self.root.after(0, lambda: self._processing_error(str(e)))

    def _display_ocr_output(self, text: str):
        """Display OCR output in the text widget"""
        self.ocr_output_text.config(state=tk.NORMAL)
        self.ocr_output_text.delete(1.0, tk.END)
        self.ocr_output_text.insert(tk.END, text)
        self.ocr_output_text.config(state=tk.DISABLED)

    def _processing_complete(self, success: bool, display_in_gui: bool = False):
        """Handle completion of processing"""
        self._set_ui_state(True)

        if success:
            self.progress_var.set("Processing complete!")
            if display_in_gui:
                messagebox.showinfo(
                    "Processing Complete",
                    f"Text extracted from {len(self.selected_files)} images and displayed in the GUI."
                )
            else:
                messagebox.showinfo(
                    "Processing Complete",
                    f"Text extracted from {len(self.selected_files)} images and saved to {self.output_path}"
                )
        else:
            self.progress_var.set("Error saving results")
            if not display_in_gui:
                messagebox.showerror(
                    "Save Error",
                    f"Failed to save results to {self.output_path}"
                )
            else:
                messagebox.showerror(
                    "Processing Error",
                    "Failed to process images or display results."
                )

    def _processing_error(self, error_msg: str):
        """Handle processing errors"""
        self._set_ui_state(True)
        self.progress_var.set("Error during processing")
        messagebox.showerror("Processing Error", f"An error occurred: {error_msg}")

    def _set_ui_state(self, enabled: bool):
        """Enable or disable UI elements during processing"""
        state = tk.NORMAL if enabled else tk.DISABLED
        self.add_btn['state'] = state
        self.add_folder_btn['state'] = state
        self.paste_btn['state'] = state
        self.clear_btn['state'] = state
        self.output_btn['state'] = state
        self.display_output_checkbox['state'] = state
        self.tesseract_btn['state'] = state
        self.process_btn['state'] = state

    def _set_tesseract_path(self):
        """Set the path to the Tesseract executable"""
        file = filedialog.askopenfilename(
            title="Select Tesseract Executable",
            filetypes=[
                ("Executable files", "*.exe"),
                ("All files", "*.*")
            ]
        )

        if file:
            self.tesseract_path = file
            self.tesseract_path_var.set(f"Using Tesseract at: {file}")

            # Reinitialize the OCR processor with the new path
            self.ocr_processor = BatchOCR(tesseract_cmd=file)

            # Check if it worked
            if self.ocr_processor.tesseract_available:
                # Save the configuration
                config.update_config("tesseract_path", file)

                messagebox.showinfo(
                    "Tesseract Configured",
                    "Tesseract OCR has been successfully configured and saved for future use."
                )
            else:
                messagebox.showerror(
                    "Configuration Error",
                    "The selected file does not appear to be a valid Tesseract executable."
                )

    def _show_tesseract_warning(self):
        """Show a warning about Tesseract not being installed"""
        result = messagebox.askquestion(
            "Tesseract Not Found",
            "Tesseract OCR is not installed or not in your PATH. "
            "This application requires Tesseract OCR to function.\n\n"
            "Would you like to see installation instructions?",
            icon='warning'
        )

        if result == 'yes':
            instructions = (
                "Tesseract OCR Installation Instructions:\n\n"
                "1. Windows:\n"
                "   - Download the installer from: https://github.com/UB-Mannheim/tesseract/wiki\n"
                "   - Run the installer and follow the instructions\n"
                "   - Make sure to add Tesseract to your PATH during installation\n"
                "   - Or use the 'Set Tesseract Path' button to locate the executable\n\n"
                "2. macOS:\n"
                "   - Install using Homebrew: brew install tesseract\n\n"
                "3. Linux:\n"
                "   - Install using apt: sudo apt install tesseract-ocr\n\n"
                "After installation, restart this application."
            )
            messagebox.showinfo("Installation Instructions", instructions)

    def run(self):
        """Run the application main loop"""
        self.root.mainloop()
