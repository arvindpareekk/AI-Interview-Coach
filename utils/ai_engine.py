from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("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"))

def generate_questions(role):
    
    prompt = f"""
    Generate 5 interview questions for the role of {role}.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert interviewer."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content