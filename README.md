# 🤖 AI Resume Analyzer

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Groq](https://img.shields.io/badge/Groq_LLaMA--3-F55036?style=for-the-badge&logo=meta&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

**An AI-powered full-stack web app that analyzes your resume against any job description, scores the match, identifies skill gaps, and generates a personalized cover letter — all in under 20 seconds.**

[🚀 Live Demo](#) · [📖 Documentation](#) · [🐛 Report Bug](../../issues)

</div>

---

## 📸 Screenshots

> Upload PDF → Paste JD → Get instant AI analysis

| Resume Upload & Analysis | Skills Match Dashboard |
|---|---|
| ![Upload Screen](<img width="1891" height="878" alt="image" src="https://github.com/user-attachments/assets/088a024f-1460-45d3-9025-c60e9bc4500d" />
| ![Dashboard]<img width="1797" height="856" alt="image" src="https://github.com/user-attachments/assets/579a1ce4-65d2-4ab1-842f-f6dc28ba9dbc" />

|![Upload Screen](<img width="1847" height="840" alt="image" src="https://github.com/user-attachments/assets/8d272ed5-80e4-49fe-8a80-56fb2970f869" />


---

## ✨ Features

- 📄 **PDF Resume Parsing** — Extracts text from any resume PDF using PyMuPDF
- 🎯 **Semantic Match Scoring** — Scores resume vs job description using cosine similarity on sentence embeddings (not just keyword matching)
- 🤖 **AI Skill Extraction** — Groq LLaMA-3 70B extracts skills, experience, education as structured JSON
- ❌ **Gap Analysis** — Shows exactly which skills you're missing for the role
- ✍️ **Cover Letter Generator** — Generates a personalized, role-specific cover letter in seconds
- ⚡ **FastAPI Backend** — REST API with 5 endpoints, auto-generated docs at `/docs`
- 🖥️ **Streamlit Frontend** — Clean interactive UI with no HTML/CSS required

---

## 🏗️ Architecture

```
User (Browser)
     │
     ▼
┌─────────────────┐         ┌──────────────────────────────────────┐
│  Streamlit UI   │─HTTP──▶│           FastAPI Backend             │
│   (app.py)      │◀─JSON──│              (main.py)                │
└─────────────────┘         └──────┬──────────┬──────────┬─────────┘
                                   │          │          │
                             ┌─────▼──┐  ┌────▼───┐  ┌──▼──────────┐
                             │PyMuPDF │  │ Groq   │  │Sentence     │
                             │PDF     │  │LLaMA-3 │  │Transformers │
                             │Parser  │  │70B API │  │+ Cosine Sim │
                             └────────┘  └────────┘  └─────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|---|---|---|
| **Frontend** | Streamlit | Python-only UI, no HTML/CSS needed |
| **Backend** | FastAPI + Uvicorn | Fast async REST API, auto-docs at /docs |
| **PDF Parsing** | PyMuPDF (fitz) | Most reliable Python PDF extractor |
| **AI Model** | Groq LLaMA-3 70B | Free, fastest LLM inference (750 tok/sec) |
| **Embeddings** | sentence-transformers | Converts text to semantic vectors locally |
| **Similarity** | scikit-learn cosine_similarity | Mathematical resume-JD matching |
| **Secrets** | python-dotenv | Loads API keys from .env safely |

---

## 📁 Project Structure

```
ai-resume-analyzer/
│
├── app.py                  # Streamlit frontend UI
├── main.py                 # FastAPI backend — all endpoints
├── pdf_parser.py           # PDF → raw text extraction
├── skill_extractor.py      # AI skill/education/experience extraction
├── job_matcher.py          # Semantic match scoring + gap analysis
├── cover_letter.py         # AI cover letter generation
│
├── requirements.txt        # All Python dependencies
├── .env                    # 🔒 Secret keys (NOT pushed to GitHub)
├── .gitignore              # Keeps .env and venv out of git
└── README.md
```

---

## ⚙️ How It Works

### Step 1 — PDF Parsing
```python
# PyMuPDF opens the PDF and extracts text page by page
doc = fitz.open(stream=pdf_bytes, filetype="pdf")
text = "".join(page.get_text() for page in doc)
```

### Step 2 — AI Skill Extraction
```python
# Groq LLaMA-3 70B returns structured JSON from unstructured resume text
response = client.chat.completions.create(
    model="llama3-70b-8192",
    messages=[{"role": "user", "content": f"Extract skills from: {resume_text}"}]
)
# Returns: { "name": "...", "skills": [...], "experience_years": 2, ... }
```

### Step 3 — Semantic Match Scoring
```python
# Convert both texts to 384-dim vectors, then measure angle between them
resume_vec = model.encode([resume_text])   # sentence-transformers
jd_vec     = model.encode([job_description])
score      = cosine_similarity(resume_vec, jd_vec)[0][0] * 100
# Understands meaning, not just keywords
```

### Step 4 — Cover Letter Generation
```python
# Groq generates a personalized letter using both resume + JD as context
letter = client.chat.completions.create(
    model="llama3-70b-8192",
    messages=[{"role": "user", "content": f"Write cover letter for: {resume} applying to: {jd}"}]
)
```

---

## 🚀 Run Locally

### Prerequisites
- Python 3.11+
- Free Groq API key from [console.groq.com](https://console.groq.com) (no credit card)

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/ai-resume-analyzer.git
cd ai-resume-analyzer
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your API key
```bash
# Create a .env file in the root folder
echo "GROQ_API_KEY=your_key_here" > .env
```

### 5. Run both servers

**Terminal 1 — FastAPI backend:**
```bash
uvicorn main:app --reload
# Running at http://localhost:8000
# API docs at http://localhost:8000/docs
```

**Terminal 2 — Streamlit frontend:**
```bash
streamlit run app.py
# Opens at http://localhost:8501
```

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/parse-resume` | Upload PDF → structured JSON |
| `POST` | `/match-job` | Resume text + JD → match score |
| `POST` | `/generate-cover-letter` | Resume + JD → cover letter |
| `POST` | `/full-analysis` | All-in-one analysis |

> Full interactive docs available at `http://localhost:8000/docs` when running locally.

---

## 📦 Installation (requirements.txt)

```
fastapi
uvicorn
streamlit
pymupdf
groq
python-dotenv
sentence-transformers
scikit-learn
python-multipart
langchain
langchain-groq
chromadb
requests
```

---

## 🔑 Environment Variables

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=gsk_your_groq_api_key_here
```

Get your free key at [console.groq.com](https://console.groq.com) — no credit card required.

> ⚠️ Never commit `.env` to GitHub. It is already in `.gitignore`.

---

## 🤝 Contributing

Pull requests are welcome!

1. Fork the repo
2. Create your branch: `git checkout -b feature/your-feature`
3. Commit: `git commit -m 'Add your feature'`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 👨‍💻 Author

**K Hema Charan**
B.Tech CSE (AI & ML) — SRM IST Ramapuram

---

<div align="center">
⭐ If this project helped you, please give it a star!
</div>
