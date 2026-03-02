from groq import Groq
import os
from dotenv import load_dotenv
import json
import re

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_questions(job_description):

    prompt = f"""
    Generate exactly 5 short technical interview questions 
    based on this job description.

    Return ONLY valid JSON in this format:

    {{
        "questions": [
            "Question 1",
            "Question 2",
            "Question 3",
            "Question 4",
            "Question 5"
        ]
    }}

    Do NOT include markdown.
    Do NOT include explanation.
    Only return JSON.

    Job Description:
    {job_description}
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        content = response.choices[0].message.content.strip()

        # Remove ```json ``` if model adds markdown
        content = re.sub(r"```json|```", "", content).strip()

        parsed = json.loads(content)

        return parsed.get("questions", [])

    except Exception as e:
        print("ERROR parsing questions:", e)
        print("RAW RESPONSE:", content)
        return []
