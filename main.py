
import os
import json
from typing import Optional

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, ValidationError

# Load API key from .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "Gemini API key not found. Check your .env file."
    )

client = genai.Client(api_key=api_key)


# Define the expected JSON structure
class ResumeAnalysis(BaseModel):
    name: str
    email: Optional[str] = None
    skills: list[str]
    experience: Optional[str] = None


# Reusable parameterized prompt template
def create_resume_prompt(resume_text: str) -> str:
    return f"""
You are a resume information extraction assistant.

Extract information from the resume text below.

Rules:
- Extract only information present in the resume.
- Do not invent details.
- Return null for missing optional fields.
- Return the requested JSON structure.

Resume text:
{resume_text}
"""


# Sample resume text for testing
resume_text = """
Name: Divya
Email: divya@example.com
Skills: Python, Excel, Linux
Experience: Beginner Python project
"""

# Create the prompt using the resume text
prompt = create_resume_prompt(resume_text)

try:
    # Ask Gemini to extract the information as JSON
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": ResumeAnalysis,
        },
    )

    # Validate the returned JSON with Pydantic
    result = ResumeAnalysis.model_validate_json(response.text)

    # Print formatted JSON output
    print("Resume extracted and validated successfully!")
    print(json.dumps(result.model_dump(), indent=4))

except ValidationError as error:
    print("The extracted data did not pass validation.")
    print(error)

except Exception as error:
    print("Something went wrong while calling Gemini.")
    print(f"{type(error).__name__}: {error}")
