
import os
import json
from typing import Optional

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, ValidationError, Field


# 1. Load API key securely from .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "Gemini API key not found. Check your .env file."
    )

client = genai.Client(api_key=api_key)


# 2. Define the expected JSON structure
class ResumeAnalysis(BaseModel):
    name: str = Field(description="Full name of the person")
    email: Optional[str] = Field(
        default=None,
        description="Email address, if available"
    )
    skills: list[str] = Field(
        description="Skills explicitly mentioned in the resume"
    )
    experience: Optional[str] = Field(
        default=None,
        description="Experience or projects, if available"
    )


# 3. Reusable parameterized prompt template
def create_resume_prompt(resume_text: str) -> str:
        return f"""
You are a resume information extraction assistant.

Extract only information present in the resume.
Never invent details.
Use an empty list if no skills are mentioned.
Use null for missing optional fields.
If the name is missing, use "Not provided".

Example 1:
Resume:
Name: Ravi Kumar
Email: ravi@example.com
Skills: Python, SQL
Experience: Data analysis internship

Expected JSON:
{{
    "name": "Ravi Kumar",
    "email": "ravi@example.com",
    "skills": ["Python", "SQL"],
    "experience": "Data analysis internship"
}}

Example 2:
Resume:
Name: Anu
Skills: Java

Expected JSON:
{{
    "name": "Anu",
    "email": null,
    "skills": ["Java"],
    "experience": null
}}

Now extract information from this resume:
{resume_text}
"""

# 4. Get resume text from the user
def get_resume_text() -> str:
    print("\n=== Resume Information Extractor ===")
    print("Paste your resume text below.")
    print("When finished, type END on a new line.\n")

    lines = []

    while True:
        line = input()

        if line.strip().upper() == "END":
            break

        lines.append(line)

    resume_text = "\n".join(lines).strip()

    if not resume_text:
        raise ValueError("Resume text cannot be empty.")

    return resume_text


# 5. Extract and validate resume information
def analyze_resume(resume_text: str) -> ResumeAnalysis:
    prompt = create_resume_prompt(resume_text)

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": ResumeAnalysis,
        },
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    # Validate the generated JSON using Pydantic
    result = ResumeAnalysis.model_validate_json(response.text)

    return result


# 6. Main program
def main():
    try:
        resume_text = get_resume_text()

        print("\nAnalyzing resume... Please wait.\n")

        result = analyze_resume(resume_text)

        print("Resume extracted and validated successfully!")
        print("\nStructured JSON Output:\n")

        print(
            json.dumps(
                result.model_dump(),
                indent=4,
                ensure_ascii=False
            )
        )

        # Save the extracted result to a JSON file
        with open(
            "resume_output.json",
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                result.model_dump(),
                file,
                indent=4,
                ensure_ascii=False
            )

        print("\nOutput saved to resume_output.json")

    except ValueError as error:
        print(f"Input or configuration error: {error}")

    except ValidationError as error:
        print("The extracted data did not pass validation.")
        print(error)

    except Exception as error:
        print("Something went wrong.")
        print(f"{type(error).__name__}: {error}")


if __name__ == "__main__":
    main()
