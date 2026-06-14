import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("MISTRAL_API_KEY")

def extract_job_details(job_description):
    try:
        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistral-small-latest",
                "messages": [
                    {
                        "role": "user",
                        "content": f"""
You are a job description analyser for Indian tech companies.
Extract details and return ONLY a JSON object, no markdown, no backticks:

{{
    "company": "company name or Unknown",
    "role": "job role/title",
    "skills": "comma separated skills",
    "ctc": "CTC/salary or Not mentioned",
    "location": "location or Not mentioned"
}}

Job Description:
{job_description[:2000]}
"""
                    }
                ]
            }
        )
        text = response.json()['choices'][0]['message']['content'].strip()
        text = text.replace('```json', '').replace('```', '').strip()
        data = json.loads(text)
        return data

    except Exception as e:
        print("AI extractor error:", e)
        return {
            "company": "",
            "role": "",
            "skills": "",
            "ctc": "",
            "location": ""
        }