# AI-Powered Resume Extractor

## Project Description
This project extracts structured information from resume text using Python and Google Gemini AI. It validates the extracted information using Pydantic and generates JSON output.

## Features
- Accepts resume text dynamically from the user.
- Uses Google Gemini AI to extract resume details.
- Extracts name, email, skills, and experience.
- Uses few-shot examples in the prompt.
- Validates output using a Pydantic model.
- Saves the result to `resume_output.json`.

## Technologies Used
- Python
- Google Gemini API
- Pydantic
- python-dotenv

## How to Run

1. Install the required packages:
   `pip install -r requirements.txt`

2. Create a `.env` file and add your Gemini API key:
   `GEMINI_API_KEY=your_api_key_here`

3. Run the program:
   `python main.py`

4. Enter resume text and type `END` on a new line when finished.

## Output
The extracted and validated resume information is saved as JSON in `resume_output.json`.

## Security
Keep your API key private. Do not upload the `.env` file to GitHub.