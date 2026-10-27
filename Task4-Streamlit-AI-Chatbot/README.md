
# Interactive AI Chatbot with Streamlit

A web-based AI chatbot built using Python, Streamlit, LangChain, and Google Gemini. It supports conversational interaction and maintains chat history during the current session.

## Features

- Interactive Streamlit chat interface
- Google Gemini AI integration
- Streaming response generation
- Conversation history using Streamlit session state
- Clear Chat button
- Environment-variable configuration for API key security

## Technologies Used

- Python
- Streamlit
- LangChain
- Google Gemini API
- Python Dotenv

## Project Structure

```text
Task4-Streamlit-AI-Chatbot/
├── main.py
├── requirements.txt
├── .gitignore
├── .env
└── README.md
```

Note: The `.env` file contains the API key and must not be uploaded to GitHub.

## Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/divyanagasai2006/datheon-ai-json-extractor.git
```

### 2. Navigate to the project folder

```bash
cd datheon-ai-json-extractor/Task4-Streamlit-AI-Chatbot
```

### 3. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Configure the API key

Create a `.env` file in this folder and add:

```text
GOOGLE_API_KEY=your_gemini_api_key
```

Replace the placeholder with your own Gemini API key. Never share or commit the key.

### 6. Run the application

```bash
python -m streamlit run main.py
```

Open the local URL displayed in the terminal, usually `http://localhost:8501`.

## Conversation Memory

The chatbot uses Streamlit session state to retain messages during the active app session. Clearing the chat resets the displayed conversation.

## Author

Divya Chinnimalli
