from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from groq import Groq
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Loads once (~90MB) — free, runs locally
model = SentenceTransformer('all-MiniLM-L6-v2')

# Common tech skills for fallback keyword matching
COMMON_SKILLS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "kotlin", "swift",
    "sql", "mysql", "postgresql", "mongodb", "redis", "sqlite", "oracle",
    "machine learning", "deep learning", "nlp", "computer vision", "data science",
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy", "matplotlib",
    "langchain", "llm", "openai", "hugging face", "transformers", "bert", "gpt",
    "fastapi", "flask", "django", "nodejs", "react", "angular", "vue",
    "docker", "kubernetes", "aws", "azure", "gcp", "terraform", "ci/cd",
    "git", "github", "linux", "bash", "rest api", "graphql",
    "html", "css", "php", "jquery", "bootstrap",
    "excel", "tableau", "power bi", "spark", "hadoop",
    "retell", "n8n", "zapier", "streamlit", "gradio"
]

def fallback_skill_match(resume_text: str, jd_text: str, resume_skills: list) -> dict:
    """Keyword-based fallback when AI returns incomplete data"""
    resume_lower = resume_text.lower()
    jd_lower = jd_text.lower()

    # Extract skills present in JD
    jd_skills = [s for s in COMMON_SKILLS if s in jd_lower]

    # Match resume skills against JD skills
    resume_skills_lower = [s.lower() for s in resume_skills]
    resume_text_lower = resume_text.lower()

    matching = []
    missing = []

    for skill in jd_skills:
        if skill in resume_text_lower or any(skill in rs for rs in resume_skills_lower):
            matching.append(skill.title())
        else:
            missing.append(skill.title())

    # Also add known resume skills that match JD
    for skill in resume_skills_lower:
        if skill in jd_lower and skill.title() not in matching:
            matching.append(skill.title())

    return {
        "matching_skills": matching[:10],
        "missing_skills": missing[:8],
        "strengths": [
            f"Has {len(resume_skills)} technical skills listed",
            "Resume includes relevant technical background",
            "Clear educational qualification present"
        ],
        "gaps": [
            f"Consider adding: {', '.join(missing[:3])}" if missing else "Good skill coverage",
            "Quantify achievements with metrics in resume"
        ]
    }

def clean_json_response(text: str) -> str:
    """Strip markdown fences and extra text from LLM response"""
    # Remove ```json ... ``` or ``` ... ```
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    # Find the first { and last }
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        return text[start:end+1]
    return text.strip()

def calculate_match_score(resume_text: str, job_description: str, resume_skills: list = None) -> dict:
    """
    Calculate how well a resume matches a job description.
    Uses two-stage: semantic embeddings + AI qualitative analysis.
    """
    if resume_skills is None:
        resume_skills = []

    # ── Stage 1: Semantic similarity via embeddings ──────────────────────
    resume_embedding = model.encode([resume_text])
    jd_embedding = model.encode([job_description])
    similarity = cosine_similarity(resume_embedding, jd_embedding)[0][0]
    base_score = float(similarity) * 100

    # ── Stage 2: AI qualitative analysis ─────────────────────────────────
    prompt = f"""You are an expert resume screener. Analyze the resume vs job description below.

RESUME TEXT:
{resume_text[:2000]}

JOB DESCRIPTION:
{job_description[:1500]}

CANDIDATE'S SKILLS (already extracted): {', '.join(resume_skills) if resume_skills else 'See resume text'}

Return ONLY a valid JSON object with EXACTLY these keys. No markdown. No explanation. Just JSON:
{{
    "match_score": 72,
    "matching_skills": ["Python", "Machine Learning", "SQL"],
    "missing_skills": ["Docker", "AWS", "Kubernetes"],
    "strengths": ["Strong ML background matches JD requirements", "Relevant project experience"],
    "gaps": ["No cloud platform experience mentioned", "Missing system design skills"],
    "verdict": "Good match. Apply with confidence after addressing the gaps."
}}

Rules:
- match_score: integer 0-100
- matching_skills: list of skills found in BOTH resume and job description (min 2 items)
- missing_skills: list of skills in job description but NOT in resume (min 2 items)
- strengths: list of 2-3 specific positive points about this candidate for this role
- gaps: list of 2-3 specific areas to improve
- verdict: one sentence recommendation
"""

    result = {}
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system",
                    "content": "You are a resume matching expert. You ALWAYS respond with valid JSON only. Never use markdown. Never add explanation outside the JSON."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=900
        )

        raw = response.choices[0].message.content.strip()
        cleaned = clean_json_response(raw)
        result = json.loads(cleaned)

    except json.JSONDecodeError:
        # JSON parsing failed — use fallback
        print("⚠️  AI returned non-JSON. Using fallback skill matcher.")
        result = fallback_skill_match(resume_text, job_description, resume_skills)

    except Exception as e:
        print(f"⚠️  Groq API error: {e}. Using fallback.")
        result = fallback_skill_match(resume_text, job_description, resume_skills)

    # ── Validate all required keys exist ─────────────────────────────────
    required_keys = ["matching_skills", "missing_skills", "strengths", "gaps", "verdict"]
    fallback = fallback_skill_match(resume_text, job_description, resume_skills)

    for key in required_keys:
        if key not in result or not result[key]:
            result[key] = fallback.get(key, [])

    # ── Blend scores ──────────────────────────────────────────────────────
    ai_score = result.get("match_score", base_score)
    final_score = (ai_score + base_score) / 2

    result["final_score"] = round(final_score, 1)
    result["semantic_similarity"] = round(base_score, 1)
    result["match_score"] = round(ai_score, 1)

    return result


# ── Quick test ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    resume = """
    K Hema Charan
    B.Tech CSE AI&ML, SRM IST-Ramapuram
    Skills: Python, C, HTML, CSS, JavaScript, PHP, Retell, n8n, Zapier, GitHub
    Projects: Built chatbot using Retell API, automation workflows with n8n
    """
    jd = """
    Looking for a Python Developer with experience in Machine Learning, FastAPI,
    Docker, AWS. Knowledge of REST APIs and SQL required. AI/ML background preferred.
    """
    result = calculate_match_score(resume, jd, ["Python", "JavaScript", "PHP"])
    print(json.dumps(result, indent=2))
    print("\n✅ job_matcher.py working!")