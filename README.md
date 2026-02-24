# Local AI Chatbot 🤖

A lightweight, local-first chatbot application built with Python, Streamlit, and Hugging Face's Flan-T5 model. It runs entirely on your CPU and logs all conversations to Google Sheets.

## Features
- **Local Execution**: No API keys required for the AI, runs 100% locally on your CPU.
- **Instruct-Tuned**: Uses `google/flan-t5-base` for natural instruction following.
- **Short-term Memory**: Remembers the last 3-4 turns of conversation for context-aware replies.
- **Google Sheets Integration**: Automatically logs every message and response to a specified spreadsheet.
- **Simple UI**: Powered by Streamlit for a clean, chat-like experience.

## Setup & Installation

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd local-chatbot
```

### 2. Create and activate a Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Google Sheets Configuration (Required for Logging)
- Create a project on [Google Cloud Console](https://console.cloud.google.com/).
- Enable the **Google Sheets API**.
- Create a **Service Account**, download the JSON key file, and rename it to `service_account.json` in the root of this project.
- Open your Google Sheet and share it with the `client_email` found inside your `service_account.json`.
- The Spreadsheet ID used is: `1zysi4NGU8RQVUbvjcFE1pYAvscoEeXTclJkFEZl7A9M`.

### 5. Run the Application
```bash
streamlit run app.py
```

## How it works
- **Model**: The app uses `AutoModelForSeq2SeqLM` and `AutoTokenizer` from the `transformers` library to load the model on the CPU.
- **Prompting**: Refined instruction-style prompting ensures the bot stays on task and remains helpful.
- **Logging**: The `sheets_service.py` module handles the asynchronous-style logging to Google Sheets without blocking the UI.
- **First Run**: The model files (approx. 990MB) will be downloaded automatically during the initial launch.

## Requirements
- Python 3.8+
- RAM: 8GB+ (Recommended)
- Storage: ~2GB for model and libraries
