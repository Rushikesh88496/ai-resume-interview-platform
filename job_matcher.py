from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from groq import Groq
import os
from dotenv import load_dotenv

# -------------------- LOAD MODELS --------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# -------------------- HELPER: Extract Skills --------------------
def extract_skills(text):
    """
    Extract potential skills from text using simple keyword logic.
    """
    skill_keywords = [
        "python", "machine learning", "deep learning", "nlp",
        "tensorflow", "pytorch", "scikit-learn", "fastapi",
        "sql", "power bi", "tableau", "excel",
        "aws", "azure", "gcp",
        "mongodb", "postgresql", "cassandra",
        "spark", "hadoop",
        "html", "css", "javascript",
        "numpy", "pandas", "matplotlib", "seaborn",
        "bert", "llm",
        "git", "github"
    ]

    text = text.lower()
    return {skill for skill in skill_keywords if skill in text}


# -------------------- MAIN MATCH FUNCTION --------------------
def calculate_match(resume_text, job_description):

    # 1️⃣ Semantic Similarity (Reduced Weight)
    resume_embedding = model.encode([resume_text])
    job_embedding = model.encode([job_description])

    semantic_similarity = cosine_similarity(resume_embedding, job_embedding)[0][0]
    semantic_score = semantic_similarity * 100

    # 2️⃣ Skill Extraction
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_description)
    matched_skills = resume_skills.intersection(job_skills)

    # 3️⃣ Core Skill Weighting (Most Important)
    core_skills = {
        "python", "machine learning", "deep learning", "nlp",
        "tensorflow", "scikit-learn", "fastapi", "sql"
    }

    core_required = job_skills.intersection(core_skills)
    core_matched = matched_skills.intersection(core_skills)

    if len(core_required) > 0:
        core_score = (len(core_matched) / len(core_required)) * 100
    else:
        core_score = 80

    # 4️⃣ General Skill Score
    if len(job_skills) > 0:
        general_score = (len(matched_skills) / len(job_skills)) * 100
    else:
        general_score = 80

    # 5️⃣ FINAL SMART WEIGHTED SCORE
    final_score = (
        semantic_score * 0.2 +   # reduce semantic dominance
        core_score * 0.6 +       # core skills dominate
        general_score * 0.2      # bonus overlap
    )

    # 6️⃣ Internship Boost
    if "intern" in job_description.lower():
        final_score *= 1.15

    # 7️⃣ Guarantee Minimum if Core Strong
    if core_score >= 80:
        final_score = max(final_score, 75)

    # 8️⃣ Clamp to realistic maximum
    final_score = min(final_score, 95)

    return round(final_score, 2)


# -------------------- SKILL GAP ANALYSIS (Groq LLM) --------------------
def skill_gap_analysis(resume_text, job_description):

    prompt = f"""
    Compare the following resume and job description carefully.

    Provide:
    1. Missing Skills (only important missing skills)
    2. Strong Skills (skills clearly matching the job)
    3. Overall Fit Summary (short paragraph)

    Resume:
    {resume_text}

    Job Description:
    {job_description}
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content