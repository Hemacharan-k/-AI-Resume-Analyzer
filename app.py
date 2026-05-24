import streamlit as st
import requests
import json

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="🤖",
    layout="wide"
)

API_URL = "http://localhost:8000"

# ── Header ────────────────────────────────────────────────────────────────
st.title("🤖 AI Resume Analyzer")
st.markdown("**Upload your resume + paste a job description → Get AI-powered match analysis**")
st.divider()

# ── Inputs ────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Your Resume")
    uploaded_file = st.file_uploader(
        "Upload Resume PDF",
        type=["pdf"],
        help="Upload your resume as a PDF file"
    )

with col2:
    st.subheader("💼 Job Description")
    job_description = st.text_area(
        "Paste the full job description here",
        height=200,
        placeholder="Copy and paste the complete job description from LinkedIn / Naukri..."
    )
    company_name = st.text_input("Company Name", placeholder="e.g. Google, Swiggy, Zepto")

# ── Analyze Button ────────────────────────────────────────────────────────
if st.button("🚀 Analyze Now", type="primary", use_container_width=True):

    if not uploaded_file:
        st.error("⚠️ Please upload your resume PDF!")
    elif not job_description.strip():
        st.error("⚠️ Please paste the job description!")
    else:
        with st.spinner("🤖 AI is analyzing your resume... (15–20 seconds)"):
            try:
                response = requests.post(
                    f"{API_URL}/full-analysis",
                    files={"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")},
                    data={
                        "job_description": job_description,
                        "company_name": company_name or "the company"
                    },
                    timeout=90
                )

                if response.status_code == 200:
                    result = response.json()
                    resume_data  = result.get("resume_data", {})
                    match_data   = result.get("match_analysis", {})
                    cover_letter = result.get("cover_letter", "")

                    st.success("✅ Analysis Complete!")
                    st.divider()

                    # ── MATCH SCORE ───────────────────────────────────────
                    score = match_data.get("final_score", match_data.get("match_score", 0))
                    try:
                        score = float(score)
                    except (TypeError, ValueError):
                        score = 0.0

                    sem_score = match_data.get("semantic_similarity", score)

                    col_a, col_b, col_c, col_d = st.columns(4)
                    with col_a:
                        emoji = "🟢" if score >= 70 else "🟡" if score >= 50 else "🔴"
                        st.metric("Overall Match", f"{emoji} {score:.0f}%")
                    with col_b:
                        st.metric("Semantic Match", f"{sem_score:.0f}%")
                    with col_c:
                        exp = resume_data.get("experience_years", "N/A")
                        st.metric("Experience", f"{exp} yrs")
                    with col_d:
                        verdict_label = "✅ Apply!" if score >= 65 else "⚠️ Needs Work" if score >= 40 else "🔴 Big Gaps"
                        st.metric("Verdict", verdict_label)

                    st.progress(min(score / 100.0, 1.0))

                    # Short verdict text
                    verdict = match_data.get("verdict", "")
                    if verdict:
                        st.info(f"💬 {verdict}")

                    st.divider()

                    # ── SKILLS ANALYSIS ───────────────────────────────────
                    st.subheader("🎯 Skills Analysis")

                    matching = match_data.get("matching_skills", [])
                    missing  = match_data.get("missing_skills", [])

                    # Ensure they are lists (guard against None or string)
                    if not isinstance(matching, list):
                        matching = []
                    if not isinstance(missing, list):
                        missing = []

                    col_x, col_y = st.columns(2)

                    with col_x:
                        st.markdown("#### ✅ Matching Skills")
                        if matching:
                            for skill in matching:
                                st.markdown(f"- ✅ **{skill}**")
                        else:
                            # Fallback: show skills from resume_data that appear in JD
                            resume_skills = resume_data.get("skills", [])
                            jd_lower = job_description.lower()
                            found_in_jd = [s for s in resume_skills if s.lower() in jd_lower]
                            if found_in_jd:
                                for skill in found_in_jd:
                                    st.markdown(f"- ✅ **{skill}**")
                            else:
                                st.info("No direct skill matches detected. Try pasting a more detailed job description.")

                    with col_y:
                        st.markdown("#### ❌ Missing Skills (Learn These!)")
                        if missing:
                            for skill in missing:
                                st.markdown(f"- ❌ **{skill}**")
                        else:
                            # Fallback: show JD keywords not in resume
                            resume_text_lower = resume_data.get("raw_text", "").lower()
                            tech_words = ["docker", "kubernetes", "aws", "azure", "gcp",
                                          "fastapi", "flask", "django", "react", "angular",
                                          "machine learning", "deep learning", "sql", "postgresql",
                                          "pytorch", "tensorflow", "langchain", "spark", "kafka"]
                            jd_lower = job_description.lower()
                            not_in_resume = [w.title() for w in tech_words
                                             if w in jd_lower and w not in resume_text_lower]
                            if not_in_resume:
                                for skill in not_in_resume[:6]:
                                    st.markdown(f"- ❌ **{skill}**")
                            else:
                                st.success("Great coverage! Your resume matches most JD keywords.")

                    st.divider()

                    # ── STRENGTHS & GAPS ──────────────────────────────────
                    st.subheader("💪 Strengths & Gaps")
                    col_s, col_g = st.columns(2)

                    with col_s:
                        st.markdown("#### 💪 Your Strengths")
                        strengths = match_data.get("strengths", [])
                        if not isinstance(strengths, list) or not strengths:
                            # Fallback strengths based on resume data
                            skills_count = len(resume_data.get("skills", []))
                            strengths = [
                                f"Listed {skills_count} technical skills" if skills_count else "Technical background present",
                                f"Relevant degree: {resume_data.get('education', 'CS/Engineering')}",
                                "AI/ML coursework aligns with modern tech roles"
                            ]
                        for s in strengths:
                            st.success(f"✓ {s}")

                    with col_g:
                        st.markdown("#### ⚠️ Gaps to Address")
                        gaps = match_data.get("gaps", [])
                        if not isinstance(gaps, list) or not gaps:
                            # Fallback gaps
                            gaps = [
                                "Add deployed project links to resume",
                                "Quantify achievements with metrics (e.g. reduced time by X%)",
                                "Mention specific tools from job description if you know them"
                            ]
                        for g in gaps:
                            st.warning(f"! {g}")

                    st.divider()

                    # ── RESUME SUMMARY ────────────────────────────────────
                    st.subheader("📊 Resume Summary")
                    col_m, col_n = st.columns(2)

                    with col_m:
                        name = resume_data.get("name", "Not detected")
                        edu  = resume_data.get("education", "Not detected")
                        st.write(f"**👤 Name:** {name}")
                        st.write(f"**🎓 Education:** {edu}")
                        email = resume_data.get("email", "")
                        if email:
                            st.write(f"**📧 Email:** {email}")

                    with col_n:
                        skills = resume_data.get("skills", [])
                        if skills:
                            st.write(f"**🛠️ Skills Found ({len(skills)}):**")
                            st.write(", ".join(skills))
                        summary = resume_data.get("summary", "")
                        if summary:
                            st.write(f"**📝 Summary:** {summary}")

                    st.divider()

                    # ── COVER LETTER ──────────────────────────────────────
                    st.subheader("📝 AI-Generated Cover Letter")
                    if cover_letter:
                        st.text_area(
                            "Copy and customize this cover letter:",
                            value=cover_letter,
                            height=320
                        )
                        st.download_button(
                            label="⬇️ Download Cover Letter as .txt",
                            data=cover_letter,
                            file_name=f"cover_letter_{(company_name or 'company').replace(' ', '_')}.txt",
                            mime="text/plain"
                        )
                    else:
                        st.warning("Cover letter generation failed. Try again.")

                else:
                    st.error(f"❌ API returned error {response.status_code}: {response.text}")

            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to FastAPI server! Make sure it is running.")
                st.code("# Open a terminal and run:\nuvicorn main:app --reload", language="bash")

            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. The AI is taking too long. Try again.")

            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")
                st.exception(e)