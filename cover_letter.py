from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def generate_cover_letter(resume_text: str, job_description: str, company_name: str = "the company") -> str:
    """Generate a personalized cover letter"""
    
    prompt = f"""
    Write a professional cover letter for this candidate applying to {company_name}.
    
    CANDIDATE RESUME:
    {resume_text[:2000]}
    
    JOB DESCRIPTION:
    {job_description[:1500]}
    
    Instructions:
    - 3 paragraphs: intro, why I'm a fit, closing
    - Reference specific skills from BOTH the resume AND job description
    - Sound human, not robotic
    - Professional but not stiff
    - End with clear call to action
    - Max 250 words
    
    Write the cover letter directly. No subject line. Start with "Dear Hiring Manager,"
    """
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a professional career coach who writes compelling cover letters."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,  # Higher temp = more creative writing
        max_tokens=600
    )
    
    return response.choices[0].message.content.strip()