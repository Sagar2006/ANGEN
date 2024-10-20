import tkinter as tk
from PIL import ImageGrab, ImageTk
import pytesseract
import re
import google.generativeai as genai
import sys
import os
from tkinter import messagebox
from dotenv import load_dotenv

load_dotenv()

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'D:\Tesseract-OCR\tesseract.exe'

class ScreenCaptureQA:
    def __init__(self, api_key):
        # Configure Gemini API
        genai.configure(api_key=api_key)
        try:
            # Initialize Gemini model
            self.model = genai.GenerativeModel('gemini-pro')
            print("Gemini API initialized successfully!")
        except Exception as e:
            print(f"Error initializing Gemini API: {str(e)}")
            messagebox.showerror("Error", "Failed to initialize Gemini API. Please check your API key.")
            sys.exit(1)

        self.root = tk.Tk()
        self.root.title("Screen Capture QA with Gemini")
        
        # Make it topmost
        self.root.attributes('-topmost', True)
        
        # Configure grid weight
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(3, weight=1)
        
        # Create a status label
        self.status_label = tk.Label(self.root, text="Press 'Capture' to start", pady=10)
        self.status_label.grid(row=0, column=0, sticky='ew')
        
        # Create capture button
        self.capture_btn = tk.Button(self.root, text="Capture", command=self.start_capture)
        self.capture_btn.grid(row=1, column=0, pady=5)
        
        # Create result text widget with scrollbar
        self.result_frame = tk.Frame(self.root)
        self.result_frame.grid(row=3, column=0, sticky='nsew', padx=10, pady=10)
        
        self.scrollbar = tk.Scrollbar(self.result_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.result_text = tk.Text(self.result_frame, height=20, width=60, yscrollcommand=self.scrollbar.set)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.scrollbar.config(command=self.result_text.yview)
        
        self.capture_window = None
        self.start_x = None
        self.start_y = None
        self.current_rect = None

    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.update()

    def start_capture(self):
        self.root.iconify()
        self.capture_window = tk.Toplevel()
        self.capture_window.attributes('-fullscreen', True, '-alpha', 0.3)
        self.capture_window.attributes('-topmost', True)
        
        self.canvas = tk.Canvas(self.capture_window, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
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
        lines = [text]
        question = next((line for line in lines if '?' in line), lines[0] if lines else "No question detected")
        
        return "MCQ" if is_mcq else "Long Answer", question

    def generate_answer_with_gemini(self, text, question_type):
        try:
            # Construct prompt based on question type
            if question_type == "MCQ":
                prompt = f"""
                Analyze this multiple choice question and provide:
                1. The correct answer
                
                Question text:
                {text}
                """
            else:
                prompt = f"""
                Analyze this question as an mcq also and provide:
                1. The correct answer
                
                Question text:
                {text}
                """
            
            # Generate response using Gemini
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Error generating answer: {str(e)}"

    def process_image(self, image):
        self.update_status("Processing image...")
        try:
            # Extract text using OCR
            text = pytesseract.image_to_string(image)
            if not text.strip():
                self.update_status("No text detected in the image")
                return
            
            # Detect question type
            question_type, question = self.detect_question_type(text)
            
            # Generate answer using Gemini
            answer = self.generate_answer_with_gemini(text, question_type)
            
            # Display results
            self.result_text.delete(1.0, tk.END)
            # self.result_text.insert(tk.END, f"Extracted Text:\n{text}\n\n")
            self.result_text.insert(tk.END, f"Question Type: {question_type}\n\n")
            self.result_text.insert(tk.END, f"Question: {question}\n\n")
            self.result_text.insert(tk.END, f"Answer from Gemini:\n{answer}\n")
            
            self.update_status("Processing complete!")
            
        except Exception as e:
            self.update_status(f"Error processing image: {str(e)}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    # Replace with your Gemini API key
    GEMINI_API_KEY = os.getenv("api_key")
    
    try:
        app = ScreenCaptureQA(GEMINI_API_KEY)
        app.run()
    except Exception as e:
        print(f"Application error: {str(e)}")