# ANGEN

ANGEN is a desktop utility designed to streamline the process of extracting and answering questions from on-screen images using Google's Gemini API. With a simple and interactive GUI powered by Tkinter, users can select any area of their screen containing a question, and ANGEN will automatically extract the text, send it to Gemini for processing, and return the answer right in the application window.

> **Disclaimer:**  
> This tool is described as a "cheating tool" for students to quickly extract and answer questions from their screen. Please use responsibly and in accordance with your local laws, academic policies, and ethical guidelines.

---

## Features

- **Easy to Use GUI:**  
  Launch the app and interact with a friendly Tkinter dialogue box.

- **Screen Region Selection:**  
  Click a button to activate a selection tool that lets you draw a rectangle around the question on your screen.

- **Automatic OCR:**  
  Instantly extracts the text from the selected screen region.

- **Gemini API Integration:**  
  Sends the extracted text to the Gemini API, which processes the question and returns an answer.

- **Instant Answers:**  
  The answer appears in the application window, saving you time and effort.

---

## How It Works

1. **Start the Application:**  
   Run ANGEN to open the main Tkinter window.

2. **Begin Selection:**  
   Click the "Start" button to bring up the selection screen.

3. **Select Question Area:**  
   Use your mouse to select the region of your screen containing the question.

4. **Text Extraction:**  
   The app uses OCR to extract the question text from your selection.

5. **Get Answer:**  
   The extracted text is sent to Gemini via API, and the answer is retrieved and displayed.

---

## Installation

1. **Clone the Repository**
    ```bash
    git clone https://github.com/Sagar2006/ANGEN.git
    cd ANGEN
    ```

2. **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```
    *Dependencies may include `tkinter`, `pillow`, `pytesseract`, `requests` or `httpx` for API calls, etc.*

3. **Configure Gemini API**
    - Obtain a Gemini API key from Google.
    - Set the API key in your environment variables or in a configuration file as required by the app.

---

## Usage

```bash
python main.py
```

- Follow the on-screen instructions.
- Select the area on your screen with the question.
- Wait for the answer to appear in the app window.

---

## Screenshots

*(Add screenshots here to show the workflow)*

---

## Contributing

Contributions are welcome! Please open issues or pull requests for bugs, feature requests, or improvements.

---

## License

This project is for educational purposes only.  
See [LICENSE](LICENSE) for more details.

---

## Disclaimer

ANGEN is intended for demonstration and research purposes. Use of this tool for academic dishonesty or violating ethical standards is not condoned by the author.
