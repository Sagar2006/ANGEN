import tkinter as tk
from PIL import ImageGrab, ImageTk
import pytesseract
import re
from transformers import pipeline
import torch
import sys
import os

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'D:\Tesseract-OCR\tesseract.exe'

class ScreenCaptureQA:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Screen Capture QA")
        
        # Make it topmost
        self.root.attributes('-topmost', True)
        
        # Create a status label
        self.status_label = tk.Label(self.root, text="Press 'Capture' to start", pady=10)
        self.status_label.pack()
        
        # Create capture button
        self.capture_btn = tk.Button(self.root, text="Capture", command=self.start_capture)
        self.capture_btn.pack(pady=5)
        
        # Create result text widget
        self.result_text = tk.Text(self.root, height=20, width=50)
        self.result_text.pack(padx=10, pady=10)
        
        # Initialize QA pipeline
        try:
            self.qa_pipeline = pipeline("question-answering")
            self.update_status("System ready!")
        except Exception as e:
            self.update_status(f"Error initializing QA pipeline: {str(e)}")
            self.qa_pipeline = None
            
        self.capture_window = None
        self.start_x = None
        self.start_y = None
        self.current_rect = None

    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.update()

    def start_capture(self):
        self.root.iconify()  # Minimize main window
        self.capture_window = tk.Toplevel()
        self.capture_window.attributes('-fullscreen', True, '-alpha', 0.3)
        self.capture_window.attributes('-topmost', True)
        
        # Configure canvas
        self.canvas = tk.Canvas(self.capture_window, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind events
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.capture_window.bind("<Escape>", lambda e: self.cancel_capture())

    def cancel_capture(self):
        if self.capture_window:
            self.capture_window.destroy()
            self.capture_window = None
        self.root.deiconify()

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        
    def on_drag(self, event):
        if self.current_rect:
            self.canvas.delete(self.current_rect)
        self.current_rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y, 
            outline='red', width=2
        )
        
    def on_release(self, event):
        if self.start_x and self.start_y:
            x1 = min(self.start_x, event.x)
            y1 = min(self.start_y, event.y)
            x2 = max(self.start_x, event.x)
            y2 = max(self.start_y, event.y)
            
            self.capture_window.withdraw()
            try:
                screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                self.process_image(screenshot)
            except Exception as e:
                self.update_status(f"Error capturing screenshot: {str(e)}")
            finally:
                self.capture_window.destroy()
                self.capture_window = None
                self.root.deiconify()

    def process_image(self, image):
        self.update_status("Processing image...")
        try:
            # Extract text using OCR
            text = pytesseract.image_to_string(image)
            if not text.strip():
                self.update_status("No text detected in the image")
                return
            
            # Detect question type and extract question
            question_type, question = self.detect_question_type(text)
            
            # Generate answer
            answer = self.generate_answer(question, question_type)
            
            # Display results
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Extracted Text:\n{text}\n\n")
            self.result_text.insert(tk.END, f"Question Type: {question_type}\n")
            self.result_text.insert(tk.END, f"Question: {question}\n")
            self.result_text.insert(tk.END, f"Answer: {answer}\n")
            
            self.update_status("Processing complete!")
            
        except Exception as e:
            self.update_status(f"Error processing image: {str(e)}")
    
    def detect_question_type(self, text):
        mcq_patterns = [
            r'\b[A-D]\)\s',
            r'\b[A-D]\.\s',
            r'\b[1-4]\)\s',
            r'\b[1-4]\.\s'
        ]
        
        is_mcq = any(re.search(pattern, text) for pattern in mcq_patterns)
        
        # Extract the question
        # lines = [line.strip() for line in text.split('\n') if line.strip()]
        # question = next((line for line in lines if '?' in line), lines[0] if lines else "No question detected")

        lines = [text]

        question = next((line for line in lines if '?' in line), lines[0] if lines else "No question detected")
        
        return "MCQ" if is_mcq else "Long Answer", question
    
    def generate_answer(self, question, question_type):
        try:
            if self.qa_pipeline:
                context = "This is a placeholder context. In a real implementation, " \
                         "you would provide relevant context or knowledge base information."
                result = self.qa_pipeline(question=question, context=context)
                return result['answer']
            else:
                return "QA Pipeline not available"
        except Exception as e:
            return f"Error generating answer: {str(e)}"

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ScreenCaptureQA()
    app.run()