import streamlit as st
import matplotlib.pyplot as plt
import re
import pandas as pd
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from modules.resume_parser import extract_resume_text
from modules.job_matcher import calculate_match, skill_gap_analysis
from modules.interview_engine import generate_questions
from modules.evaluator import evaluate_answer

from database import (
    init_db,
    add_candidate,
    update_interview_score,
    get_candidate,
    get_all_candidates
)

# -------------------------------------------------
# INITIALIZE DATABASE & PAGE CONFIG
# -------------------------------------------------
init_db()

st.set_page_config(page_title="AI Hiring Platform", layout="wide", initial_sidebar_state="expanded")

# -------------------------------------------------
# CUSTOM CSS (Dark Theme, Glass Cards, Typography)
# -------------------------------------------------
st.markdown("""
<style>
    /* Professional Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Dark Corporate Background */
    .stApp {
        background-color: #0f172a; /* Tailwind Slate 900 */
        color: #f8fafc;
    }

    /* Glass-style elements */
    .glass-card {
        background: rgba(30, 41, 59, 0.7); /* Slate 800 with transparency */
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }

    /* Modern Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 14px 0 rgba(37, 99, 235, 0.39);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4);
    }

    /* Styled KPI Blocks */
    [data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 12px;
        box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.05);
    }
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #38bdf8 !important; /* Tailwind Sky 400 */
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #f8fafc !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# Set matplotlib dark background for better blending
plt.style.use("dark_background")

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------
if "questions" not in st.session_state:
    st.session_state.questions = []
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "scores" not in st.session_state:
    st.session_state.scores = []
if "evaluation_report" not in st.session_state:
    st.session_state.evaluation_report = None
if "candidate_login" not in st.session_state:
    st.session_state.candidate_login = None

# -------------------------------------------------
# SIDEBAR NAVIGATION
# -------------------------------------------------
with st.sidebar:
    st.markdown("<h2>🌐 Portal Navigation</h2>", unsafe_allow_html=True)
    role = st.radio("Select Access Level", ["👔 Recruiter", "🎓 Candidate"])
    role = "Recruiter" if "Recruiter" in role else "Candidate"
    
    st.markdown("---")
    
    # Nested navigation for Recruiter
    if role == "Recruiter":
        st.markdown("### 📌 Workspace Options")
        recruiter_nav = st.radio(
            "Go to:", 
            ["📄 Resume Screening", "🏆 Leaderboard", "📊 Analytics Dashboard"]
        )
    else:
        st.info("Please log in using your registered candidate name on the main panel to begin your assessment.")

# -------------------------------------------------
# MAIN INTERFACE
# -------------------------------------------------
st.title("🚀 AI Hiring Intelligence Platform")
st.markdown(f"<p style='color:#94a3b8; margin-bottom: 2rem;'>Operating Mode: <b>{role}</b></p>", unsafe_allow_html=True)

# =========================================================
# ===================== RECRUITER =========================
# =========================================================
if role == "Recruiter":

    if recruiter_nav == "📄 Resume Screening":
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.header("📄 Resume Screening & Analysis")

        col_left, col_right = st.columns([1, 1])
        
        with col_left:
            candidate_name = st.text_input("👤 Candidate Full Name")
            uploaded_file = st.file_uploader("Upload Candidate Resume (PDF)", type="pdf")
            
            cutoff = st.slider("🎯 Target Match Cutoff (%)", 0, 100, 65)
            resume_weight = st.slider("⚖️ Resume Weight vs Interview (%)", 0, 100, 60)
            interview_weight = 100 - resume_weight

        with col_right:
            job_description = st.text_area("📋 Target Job Description", height=250)

        if uploaded_file:
            st.success("✅ Document uploaded securely.")

        if uploaded_file and job_description and candidate_name:
            if st.button("Analyze Profile"):
                with st.spinner("Running deep analysis..."):
                    resume_text = extract_resume_text(uploaded_file)
                    resume_score = calculate_match(resume_text, job_description)

                st.markdown("---")
                st.subheader("📊 Match Results")
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.metric("Profile Alignment", f"{resume_score}%")
                with col2:
                    st.markdown("**🧠 Skill Gap Analysis**")
                    st.write(skill_gap_analysis(resume_text, job_description))

                if resume_score >= cutoff:
                    st.success(f"✅ **{candidate_name}** meets the threshold and has been shortlisted.")
                    add_candidate(candidate_name, resume_score)
                else:
                    st.error(f"❌ **{candidate_name}** did not meet the required threshold.")
        st.markdown('</div>', unsafe_allow_html=True)

        # FINAL DASHBOARD PREVIEW
        if candidate_name:
            candidate = get_candidate(candidate_name)
            if candidate and candidate[2] is not None:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                name, resume_score, interview_score = candidate

                final_score = round(
                    (resume_score * resume_weight / 100) +
                    (interview_score * interview_weight / 100), 2
                )

                st.subheader(f"📈 Final Assessment Overview: {name}")
                kpi1, kpi2, kpi3 = st.columns(3)
                kpi1.metric("Resume Match", f"{resume_score}%")
                kpi2.metric("Interview Rating", f"{interview_score}%")
                kpi3.metric("Composite Score", f"{final_score}%")

                fig, ax = plt.subplots(figsize=(6, 3))
                ax.bar(["Resume", "Interview", "Composite Score"],
                       [resume_score, interview_score, final_score], color=['#3b82f6', '#8b5cf6', '#10b981'])
                ax.set_ylim(0, 100)
                ax.set_ylabel("Score %")
                
                # Make chart background transparent
                fig.patch.set_alpha(0.0)
                ax.patch.set_alpha(0.0)
                st.pyplot(fig)
                st.markdown('</div>', unsafe_allow_html=True)

    elif recruiter_nav == "🏆 Leaderboard":
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.header("🏆 Live Candidate Leaderboard")

        data = get_all_candidates()

        if data:
            df = pd.DataFrame(data, columns=["Candidate", "Resume Score", "Interview Score"])
            df["Resume Score"] = pd.to_numeric(df["Resume Score"], errors="coerce")
            df["Interview Score"] = pd.to_numeric(df["Interview Score"], errors="coerce")

            df = df.sort_values(by="Interview Score", ascending=False)
            df.reset_index(drop=True, inplace=True)
            df.index += 1

            st.dataframe(df.style.background_gradient(cmap='Blues', subset=['Interview Score']), use_container_width=True)
        else:
            st.info("Awaiting candidate data. Run some screenings first.")
        st.markdown('</div>', unsafe_allow_html=True)

    elif recruiter_nav == "📊 Analytics Dashboard":
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.header("📊 Recruitment Intelligence")

        data = get_all_candidates()

        if data:
            df = pd.DataFrame(data, columns=["Candidate", "Resume Score", "Interview Score"])
            df["Resume Score"] = pd.to_numeric(df["Resume Score"], errors="coerce")
            df["Interview Score"] = pd.to_numeric(df["Interview Score"], errors="coerce")
            df["Status"] = df["Interview Score"].apply(lambda x: "🟢 Selected" if x >= 60 else "🔴 Rejected")

            total = len(df)
            selected = len(df[df["Interview Score"] >= 60])
            rejected = total - selected
            selection_rate = round((selected / total) * 100, 2) if total > 0 else 0

            top_candidate = df.sort_values(by="Interview Score", ascending=False).iloc[0]["Candidate"] if total > 0 else "N/A"

            # KPI ROW
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("👥 Total", total)
            c2.metric("🟢 Selected", selected)
            c3.metric("🔴 Rejected", rejected)
            c4.metric("📈 Pass Rate", f"{selection_rate}%")
            c5.metric("🏆 Top Performer", top_candidate)

            st.markdown("<br>", unsafe_allow_html=True)

            # CHART ROW 1
            colA, colB = st.columns(2)
            with colA:
                st.markdown("**Selection Distribution**")
                fig1, ax1 = plt.subplots(figsize=(4, 4))
                ax1.pie([selected, rejected], labels=["Selected", "Rejected"], autopct="%1.1f%%", 
                        startangle=90, colors=['#10b981', '#ef4444'])
                ax1.axis("equal")
                fig1.patch.set_alpha(0.0)
                st.pyplot(fig1)

            with colB:
                st.markdown("**Interview Score Distribution**")
                fig2, ax2 = plt.subplots(figsize=(5, 4))
                ax2.hist(df["Interview Score"].dropna(), bins=6, color="#6366f1", edgecolor="black")
                ax2.set_xlabel("Score")
                ax2.set_ylabel("Count")
                fig2.patch.set_alpha(0.0)
                ax2.patch.set_alpha(0.0)
                st.pyplot(fig2)

            st.markdown("<br>", unsafe_allow_html=True)

            # CHART ROW 2
            colC, colD = st.columns(2)
            with colC:
                st.markdown("**Resume vs Interview Performance**")
                fig3, ax3 = plt.subplots(figsize=(5, 4))
                ax3.scatter(df["Resume Score"], df["Interview Score"], color="#f59e0b")
                ax3.set_xlabel("Resume Score")
                ax3.set_ylabel("Interview Score")
                fig3.patch.set_alpha(0.0)
                ax3.patch.set_alpha(0.0)
                st.pyplot(fig3)

            with colD:
                st.markdown("**Candidate Ranking Data**")
                ranking_df = df.sort_values(by="Interview Score", ascending=False).reset_index(drop=True)
                ranking_df.index += 1
                st.dataframe(ranking_df, use_container_width=True)

            # INSIGHTS
            st.markdown("---")
            st.markdown("### 🧠 Automated Insights")
            if len(df.dropna()) > 1:
                correlation = df["Resume Score"].corr(df["Interview Score"])
                st.info(f"**Correlation (Resume vs Interview):** {round(correlation, 2)}")
                if correlation > 0.6:
                    st.success("Strong positive correlation. Your resume screening criteria accurately predicts interview success.")
                elif correlation > 0.3:
                    st.warning("Moderate correlation detected. Consider refining your job description requirements.")
                else:
                    st.error("Weak correlation. Candidates with great resumes are struggling in interviews. Reassess screening metrics.")
            else:
                st.info("Not enough data to generate correlation insights.")

        else:
            st.info("No analytics available. Add candidates to generate insights.")
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# ===================== CANDIDATE =========================
# =========================================================
if role == "Candidate":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.header("🎓 Candidate Assessment Portal")

    candidate_login = st.text_input("Enter Your Registered Full Name").strip()

    if candidate_login:
        candidate = get_candidate(candidate_login)

        if candidate is None:
            st.error("🚫 Profile not found or not shortlisted. Please contact the recruiter.")
            st.stop()

        name, resume_score, interview_score = candidate

        # If interview already completed
        if interview_score is not None:
            st.success("✅ Assessment already completed.")
            st.metric("Your Final Assessment Score", f"{interview_score}%")
            st.stop()

        # Reset state for new candidate session
        if st.session_state.get("active_candidate") != candidate_login:
            st.session_state.active_candidate = candidate_login
            with st.spinner("Generating personalized technical assessment..."):
                st.session_state.questions = generate_questions("Technical Interview")
            st.session_state.current_question = 0
            st.session_state.scores = []
            st.session_state.evaluated = False
            st.session_state.evaluation_report = None

        questions = st.session_state.questions
        q_index = st.session_state.current_question
        total_questions = len(questions)

        st.progress(q_index / total_questions, text=f"Question {q_index + 1} of {total_questions}")

        if q_index < total_questions:
            question = questions[q_index]

            st.markdown(f"### ❓ Question {q_index + 1}")
            st.info(question)

            answer = st.text_area("✍️ Your Answer", key=f"{candidate_login}_answer_{q_index}", height=150)

            if not st.session_state.evaluated:
                if st.button("Submit Answer"):
                    if answer.strip():
                        with st.spinner("Evaluating response..."):
                            evaluation = evaluate_answer(question, answer)

                            match = re.search(r'(\d+)\s*out of\s*10', evaluation, re.IGNORECASE)
                            score = int(match.group(1)) * 10 if match else 0

                            st.session_state.scores.append(score)
                            st.session_state.evaluation_report = evaluation
                            st.session_state.evaluated = True
                    else:
                        st.warning("Please provide an answer before submitting.")

            if st.session_state.evaluated:
                st.markdown("### 🤖 AI Evaluation")
                st.write(st.session_state.evaluation_report)

                if st.button("Next Question ➡️"):
                    st.session_state.current_question += 1
                    st.session_state.evaluated = False
                    st.rerun()
        else:
            st.balloons()
            st.success("🎉 Assessment Completed Successfully!")

            final_score = round(sum(st.session_state.scores) / len(st.session_state.scores), 2)
            update_interview_score(candidate_login, final_score)

            st.metric("Final Recorded Score", f"{final_score}%")

            if final_score >= 60:
                st.success("🎉 Congratulations! You have PASSED the technical threshold.")
            else:
                st.error("❌ Unfortunately, you did not meet the required threshold this time.")

            # Clear session state
            st.session_state.active_candidate = None
            st.session_state.questions = []
            st.session_state.current_question = 0
            st.session_state.scores = []
            st.session_state.evaluated = False
            st.session_state.evaluation_report = None

    st.markdown('</div>', unsafe_allow_html=True)