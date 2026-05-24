from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pdf_parser import extract_text_from_bytes
from skill_extractor import extract_skills_from_resume
from job_matcher import calculate_match_score
from cover_letter import generate_cover_letter
import uvicorn

app = FastAPI(title="AI Resume Analyzer", version="1.0.0")

# Allow Streamlit to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def home():
    return {"message": "AI Resume Analyzer API is running! ✅"}

@app.post("/parse-resume")
async def parse_resume(file: UploadFile = File(...)):
    """Upload PDF → Get structured resume data"""
    pdf_bytes = await file.read()
    
    # Extract text from PDF
    resume_text = extract_text_from_bytes(pdf_bytes)
    
    # Extract skills using AI
    structured_data = extract_skills_from_resume(resume_text)
    structured_data["raw_text"] = resume_text
    
    return {"success": True, "data": structured_data}

@app.post("/match-job")
async def match_job(
    resume_text: str = Form(...),
    job_description: str = Form(...)
):
    """Match resume text against job description"""
    result = calculate_match_score(resume_text, job_description)
    return {"success": True, "data": result}

@app.post("/generate-cover-letter")
async def create_cover_letter(
    resume_text: str = Form(...),
    job_description: str = Form(...),
    company_name: str = Form(default="the company")
):
    """Generate personalized cover letter"""
    letter = generate_cover_letter(resume_text, job_description, company_name)
    return {"success": True, "cover_letter": letter}

@app.post("/full-analysis")
async def full_analysis(
    file: UploadFile = File(...),
    job_description: str = Form(...),
    company_name: str = Form(default="the company")
):
    """All-in-one: Parse + Match + Cover Letter"""
    pdf_bytes = await file.read()
    resume_text = extract_text_from_bytes(pdf_bytes)
    
    # Run all analyses
    skills_data = extract_skills_from_resume(resume_text)
    match_data = calculate_match_score(resume_text, job_description)
    cover_letter = generate_cover_letter(resume_text, job_description, company_name)
    
    return {
        "success": True,
        "resume_data": skills_data,
        "match_analysis": match_data,
        "cover_letter": cover_letter
    }

# Run with: uvicorn main:app --reload
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)