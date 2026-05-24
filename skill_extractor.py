import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()  # Load .env file

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def extract_skills_from_resume(resume_text: str) -> dict:
    """Use AI to extract structured info from resume"""
    
    prompt = f"""
    Analyze this resume and extract information in JSON format.
    
    Resume Text:
    {resume_text}
    
    Return ONLY valid JSON (no markdown, no explanation) with this exact structure:
    {{
        "name": "candidate name",
        "email": "email if found",
        "skills": ["skill1", "skill2", "skill3"],
        "experience_years": 2,
        "education": "degree and college",
        "job_titles": ["previous job titles"],
        "summary": "2 sentence professional summary of this person"
    }}
    """
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # Free Groq model
        messages=[
            {
                "role": "system",
                "content": "You are a resume parser. Always respond with valid JSON only. No markdown."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1,  # Low temp = more consistent output
        max_tokens=1000
    )
    
    result_text = response.choices[0].message.content.strip()
    
    # Parse JSON response
    try:
        result = json.loads(result_text)
    except json.JSONDecodeError:
        # If JSON is broken, extract what we can
        result = {
            "name": "Unknown",
            "skills": [],
            "experience_years": 0,
            "summary": result_text
        }
    
    return result

# Test it
if __name__ == "__main__":
    sample_resume = """
    John Doe | john@email.com
    Software Engineer with 2 years experience in Python, Machine Learning
    Skills: Python, TensorFlow, SQL, Docker, AWS
    Education: B.Tech CSE, IIT Delhi, 2023
    """
    
    result = extract_skills_from_resume(sample_resume)
    print(json.dumps(result, indent=2))
    print("✅ Skill extractor working!")