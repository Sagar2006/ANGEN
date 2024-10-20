import tkinter as tk
from PIL import ImageGrab, ImageTk
import pytesseract
import re
import google.generativeai as genai
import sys
import os
from tkinter import messagebox
from dotenv import load_dotenv
import anthropic
import openai
from collections import Counter

load_dotenv()

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'D:\Tesseract-OCR\tesseract.exe'

class ScreenCaptureQA:
    def __init__(self):
        # Configure API keys
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.claude_key = os.getenv("ANTHROPIC_API_KEY")
        
        # Initialize AI models
        self.initialize_ai_models()
        
        self.root = tk.Tk()
        self.root.title("Multi-AI Screen Capture QA Tool")
        
        # GUI setup remains the same
        self.setup_gui()
        
        self.capture_window = None
        self.start_x = None
        self.start_y = None
        self.current_rect = None

    def initialize_ai_models(self):
        try:
            # Initialize Gemini
            genai.configure(api_key=self.gemini_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
            
            # Initialize Claude
            self.claude_client = anthropic.Anthropic(api_key=self.claude_key)
            
            # Initialize ChatGPT
            self.openai_client = openai.OpenAI(api_key=self.openai_key)
            
            print("All AI models initialized successfully!")
        except Exception as e:
            print(f"Error initializing AI models: {str(e)}")
            messagebox.showerror("Error", "Failed to initialize one or more AI models. Please check your API keys.")
            sys.exit(1)

    def get_gemini_answer(self, text, question_type):
        try:
            prompt = self.construct_prompt(text, question_type)
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Gemini Error: {str(e)}"

    def get_claude_answer(self, text, question_type):
        try:
            prompt = self.construct_prompt(text, question_type)
            response = self.claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            return f"Claude Error: {str(e)}"

    def get_chatgpt_answer(self, text, question_type):
        try:
            prompt = self.construct_prompt(text, question_type)
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"ChatGPT Error: {str(e)}"

    def construct_prompt(self, text, question_type):
        if question_type == "MCQ":
            return f"""
            Analyze this multiple choice question and provide:
            1. The correct answer (just the letter/number of the correct option)
            2. Brief explanation
            
            Question text:
            {text}
            """
        else:
            return f"""
            Analyze this question and provide:
            1. A clear, concise answer
            2. Brief explanation
            
            Question text:
            {text}
            """

    def get_consensus_answer(self, text, question_type):
        # Get answers from all models
        answers = {
            "Gemini": self.get_gemini_answer(text, question_type),
            "Claude": self.get_claude_answer(text, question_type),
            "ChatGPT": self.get_chatgpt_answer(text, question_type)
        }
        
        if question_type == "MCQ":
            # Extract just the answer choice (A, B, C, D) from each response
            mcq_choices = {}
            for model, response in answers.items():
                choice = self.extract_mcq_choice(response)
                if choice:
                    mcq_choices[model] = choice
            
            # Get the most common answer
            if mcq_choices:
                consensus = Counter(mcq_choices.values()).most_common(1)[0][0]
            else:
                consensus = "Unable to determine consensus"
        else:
            # For long-form answers, return all responses
            consensus = "\n\n".join([f"{model}:\n{answer}" for model, answer in answers.items()])
        
        return consensus, answers

    def extract_mcq_choice(self, response):
        # Extract single letter/number answer from response
        match = re.search(r'\b[A-D1-4]\b', response)
        return match.group(0) if match else None

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
            
            # Get consensus answer
            consensus, all_answers = self.get_consensus_answer(text, question_type)
            
            # Display results
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Question Type: {question_type}\n\n")
            self.result_text.insert(tk.END, f"Question: {question}\n\n")
            self.result_text.insert(tk.END, f"Consensus Answer: {consensus}\n\n")
            self.result_text.insert(tk.END, "Individual Model Responses:\n")
            for model, answer in all_answers.items():
                self.result_text.insert(tk.END, f"\n{model}:\n{answer}\n")
            
            self.update_status("Processing complete!")
            
        except Exception as e:
            self.update_status(f"Error processing image: {str(e)}")

    # Rest of the existing methods remain the same...

if __name__ == "__main__":
    try:
        app = ScreenCaptureQA()
        app.run()
    except Exception as e:
        print(f"Application error: {str(e)}")