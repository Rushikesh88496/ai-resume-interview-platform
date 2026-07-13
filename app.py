"""
╔══════════════════════════════════════════════════════════════╗
║          AI HIRE  ·  AI Talent Intelligence Platform       ║
║          Aesthetic: Warm Brutalist Premium                   ║
║          Font: Clash Display + Cabinet Grotesk + Fira Code   ║
╚══════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import numpy as np
import pandas as pd
import re, time, random, json
from datetime import datetime, timedelta

# ── graceful module fallback ──────────────────────────────────
try:
    from modules.resume_parser import extract_resume_text
    from modules.job_matcher import calculate_match, skill_gap_analysis
    from modules.interview_engine import generate_questions
    from modules.evaluator import evaluate_answer
    from database import (init_db, add_candidate, update_interview_score,
                          get_candidate, get_all_candidates)
    init_db()
    DEMO = False
except Exception:
    DEMO = True

# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI HIRE · Talent Intelligence",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="▲"
)

# ══════════════════════════════════════════════════════════════
#  DEMO DATA
# ══════════════════════════════════════════════════════════════

QUESTIONS = {
    "Data Science":  [
        "Walk me through how you would approach building a fraud detection model from scratch, including data pipeline, feature engineering, and model evaluation.",
        "Explain the bias-variance tradeoff and describe a situation where you deliberately chose a higher-bias model. What was the outcome?",
        "How would you handle severe class imbalance (1:1000) in a binary classification task? What metrics would you optimize?",
        "Describe your experience with MLOps. How do you monitor model drift in production, and what triggers a retrain?",
        "You have a dataset with 80% missing values in a key feature. Walk me through your decision-making process.",
    ],
    "Engineering": [
        "Design a URL shortener service that needs to handle 100 million requests per day. Walk me through architecture, storage, and scaling decisions.",
        "Explain how you would debug a memory leak in a Node.js production service. What tools would you use?",
        "What is the difference between horizontal and vertical scaling? When would you choose each, and what are the trade-offs?",
        "Describe how database indexing works under the hood. When can an index hurt performance?",
        "Walk me through your process for reviewing a pull request from a junior developer. What do you look for?",
    ],
    "General": [
        "Tell me about a project where you had to make a critical technical decision with incomplete information. What was your process?",
        "Describe a time when you disagreed with your manager's technical direction. How did you handle it?",
        "How do you stay current with fast-moving technology? Give me a recent example of something you learned and applied.",
        "Walk me through a time you significantly improved system performance. What was your approach and the measured impact?",
        "Describe your ideal engineering team culture and how you actively contribute to it.",
    ]
}

TAGS_POOL = ["Python","SQL","ML","React","Docker","AWS","GCP","FastAPI","Spark","Kafka","Redis","PostgreSQL","TensorFlow","PyTorch","Kubernetes","CI/CD","Microservices","Data Visualization","NLP","Computer Vision","Time Series","A/B Testing","Agile","Scrum","Leadership","Mentorship","Communication","Problem Solving","Critical Thinking","Teamwork","Adaptability","Creativity","Work Ethic","Attention to Detail","Project Management","Cloud Computing","DevOps","Data Engineering","Software Architecture","Testing & QA","Version Control","API Design","System Design","Performance Optimization","Security Best Practices","Scalability","Reliability","Monitoring & Logging","Cost Optimization","Collaboration Tools","Remote Work","Cross-functional Collaboration"                           ]

def random_tags(n=4):
    return random.sample(TAGS_POOL, n)

def rand_date(days_back=30):
    return (datetime.now() - timedelta(days=random.randint(0, days_back))).strftime("%d %b")

ACTIVITY_LOG = [
    ("Meera Pillai", "completed interview", "94% score — exceptional", "12 min ago", "✓"),
    ("Karan Singh",  "shortlisted",          "Resume score 95%",        "1 hr ago",  "✓"),
    ("Vikram Reddy", "interview pending",    "Scheduled for tomorrow",  "2 hrs ago", "◷"),
    ("Priya Sharma", "offer extended",       "Offer sent via email",    "3 hrs ago", "★"),
    ("Rahul Gupta",  "rejected",             "Below threshold (55%)",   "5 hrs ago", "✕"),
    ("Ananya Das",   "screening done",       "Resume score 79%",        "Yesterday", "✓"),
    ("Arjun Mehta",  "interview done",       "Interview score 68%",     "Yesterday", "✓"),
    ("Rohit Verma",  "shortlisted",          "Strong backend profile",  "2 days ago","✓"),
]

# ══════════════════════════════════════════════════════════════
#  MASTER CSS  ─  "Warm Brutalist Premium"
#  Think: Bloomberg Terminal meets Figma meets Stripe Dashboard
# ══════════════════════════════════════════════════════════════
CSS = """
<style>
@import url('https://api.fontshare.com/v2/css?f[]=clash-display@400,500,600,700&f[]=cabinet-grotesk@400,500,700,800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&display=swap');

/* ═══════════ TOKENS ═══════════ */
:root {
  --ink:       #0a0a0a;
  --ink-2:     #1a1a1a;
  --ink-3:     #2d2d2d;
  --paper:     #f5f0e8;
  --paper-2:   #ede8dc;
  --paper-3:   #e0dace;
  --warm-white:#faf8f4;

  --accent:    #e8521a;
  --accent-2:  #f07040;
  --accent-dim:rgba(232,82,26,0.12);
  --accent-glow:rgba(232,82,26,0.25);

  --green:     #1a7a4a;
  --green-bg:  rgba(26,122,74,0.1);
  --green-bdr: rgba(26,122,74,0.25);
  --red:       #c0392b;
  --red-bg:    rgba(192,57,43,0.1);
  --red-bdr:   rgba(192,57,43,0.25);
  --amber:     #b8860b;
  --amber-bg:  rgba(184,134,11,0.1);
  --amber-bdr: rgba(184,134,11,0.25);
  --blue:      #1a5276;
  --blue-bg:   rgba(26,82,118,0.1);

  --border:    rgba(10,10,10,0.10);
  --border-md: rgba(10,10,10,0.16);
  --border-hi: rgba(232,82,26,0.45);

  --shadow-sm: 0 1px 3px rgba(10,10,10,0.08), 0 1px 2px rgba(10,10,10,0.06);
  --shadow-md: 0 4px 16px rgba(10,10,10,0.10), 0 2px 6px rgba(10,10,10,0.07);
  --shadow-lg: 0 12px 40px rgba(10,10,10,0.14), 0 4px 12px rgba(10,10,10,0.08);

  --r-xs: 4px; --r-sm: 8px; --r-md: 14px; --r-lg: 20px; --r-xl: 28px;
  --font-d: 'Clash Display', 'Cabinet Grotesk', sans-serif;
  --font-b: 'Cabinet Grotesk', sans-serif;
  --font-m: 'Fira Code', monospace;
}

/* ═══════════ BASE ═══════════ */
html, body, [class*="css"] {
  font-family: var(--font-b) !important;
  color: var(--ink);
  background: var(--warm-white);
}
.stApp {
  background: var(--warm-white) !important;
  background-image:
    radial-gradient(ellipse 80% 60% at 0% 0%,   rgba(232,82,26,0.04) 0%, transparent 55%),
    radial-gradient(ellipse 60% 80% at 100% 100%, rgba(26,82,118,0.03) 0%, transparent 55%),
    url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='40'%3E%3Ccircle cx='20' cy='20' r='0.5' fill='rgba(10,10,10,0.04)'/%3E%3C/svg%3E") !important;
}
.block-container { padding-top: 0 !important; padding-bottom: 3rem !important; max-width: 1400px !important; }
#MainMenu, footer { visibility: hidden !important; }

/* ═══════════ SIDEBAR ═══════════ */
[data-testid="stSidebar"] {
  background: var(--ink) !important;
  border-right: none !important;
  min-width: 240px !important;
}
[data-testid="stSidebar"] * { color: rgba(245,240,232,0.85) !important; }
[data-testid="stSidebar"] [data-testid="stRadio"] {
  gap: 2px !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label {
  background: transparent !important;
  border: none !important;
  padding: 10px 16px !important;
  border-radius: var(--r-xs) !important;
  font-size: 0.82rem !important;
  font-weight: 500 !important;
  color: rgba(245,240,232,0.6) !important;
  transition: all 0.15s ease !important;
  letter-spacing: 0.01em !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
  background: rgba(245,240,232,0.08) !important;
  color: rgba(245,240,232,0.9) !important;
}
[data-testid="stSidebar"] [data-baseweb="radio"]:has(input:checked) label {
  background: var(--accent) !important;
  color: white !important;
}

/* ═══════════ TOP BANNER ═══════════ */
.top-banner {
  background: var(--ink);
  color: var(--paper);
  padding: 18px 36px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: -1rem -1rem 32px -1rem;
  border-bottom: 3px solid var(--accent);
  position: sticky;
  top: 0;
  z-index: 100;
}
.banner-brand {
  font-family: var(--font-d);
  font-size: 1.4rem;
  font-weight: 700;
  letter-spacing: -0.03em;
  color: var(--paper) !important;
  display: flex; align-items: center; gap: 10px;
}
.banner-brand .tri {
  color: var(--accent);
  font-size: 0.9rem;
  line-height: 1;
}
.banner-right {
  display: flex; align-items: center; gap: 20px;
}
.banner-pill {
  display: inline-flex; align-items: center; gap: 6px;
  border: 1px solid rgba(245,240,232,0.15);
  padding: 5px 14px; border-radius: 99px;
  font-size: 0.72rem; font-weight: 600;
  letter-spacing: 0.1em; text-transform: uppercase;
  color: rgba(245,240,232,0.7);
}
.pulse { width:7px;height:7px;border-radius:50%;background:var(--accent);animation:pulse 2.5s infinite; }
@keyframes pulse{0%,100%{opacity:1;transform:scale(1);}50%{opacity:0.5;transform:scale(0.7);}}

/* ═══════════ PAGE HEADER ═══════════ */
.page-hdr {
  padding: 0 0 28px;
  border-bottom: 2px solid var(--ink);
  margin-bottom: 32px;
  display: flex; align-items: flex-end; justify-content: space-between;
}
.page-hdr h1 {
  font-family: var(--font-d) !important;
  font-size: 2.6rem !important;
  font-weight: 700 !important;
  letter-spacing: -0.05em !important;
  color: var(--ink) !important;
  line-height: 1.05 !important;
  margin: 0 !important;
}
.page-hdr h1 span { color: var(--accent); }
.page-hdr-sub {
  font-size: 0.82rem;
  color: rgba(10,10,10,0.45);
  margin-top: 6px;
  letter-spacing: 0.02em;
}
.breadcrumb {
  font-family: var(--font-m);
  font-size: 0.7rem;
  color: rgba(10,10,10,0.35);
  letter-spacing: 0.05em;
  text-transform: uppercase;
  margin-bottom: 8px;
}

/* ═══════════ CARDS ═══════════ */
.card {
  background: var(--warm-white);
  border: 1.5px solid var(--border-md);
  border-radius: var(--r-lg);
  padding: 26px 30px;
  margin-bottom: 20px;
  box-shadow: var(--shadow-sm);
  position: relative;
  overflow: hidden;
  transition: box-shadow 0.25s ease, border-color 0.25s ease;
}
.card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--border-hi);
}
.card-accent {
  border-left: 4px solid var(--accent);
  border-radius: 0 var(--r-lg) var(--r-lg) 0;
}
.card-dark {
  background: var(--ink);
  border-color: rgba(245,240,232,0.1);
  color: var(--paper);
}
.card-dark * { color: var(--paper) !important; }

/* Section heading inside card */
.sec-title {
  font-family: var(--font-d);
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: rgba(10,10,10,0.38);
  margin-bottom: 14px;
  display: flex; align-items: center; gap: 8px;
}
.sec-title::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border-md);
}
.card-h {
  font-family: var(--font-d);
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: -0.02em;
  margin-bottom: 6px;
}
.card-sub {
  font-size: 0.76rem;
  color: rgba(10,10,10,0.4);
  margin-bottom: 20px;
}

/* ═══════════ KPI TILES ═══════════ */
[data-testid="stMetric"] {
  background: var(--paper) !important;
  border: 1.5px solid var(--border-md) !important;
  border-radius: var(--r-lg) !important;
  padding: 22px 24px !important;
  box-shadow: var(--shadow-sm) !important;
  transition: all 0.2s ease !important;
  position: relative;
  overflow: hidden;
}
[data-testid="stMetric"]::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 3px;
  background: var(--accent);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.3s ease;
}
[data-testid="stMetric"]:hover {
  transform: translateY(-3px) !important;
  box-shadow: var(--shadow-md) !important;
  border-color: var(--border-hi) !important;
}
[data-testid="stMetric"]:hover::after { transform: scaleX(1); }
[data-testid="stMetricLabel"] {
  font-family: var(--font-b) !important;
  font-size: 0.67rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.14em !important;
  text-transform: uppercase !important;
  color: rgba(10,10,10,0.4) !important;
}
[data-testid="stMetricValue"] {
  font-family: var(--font-d) !important;
  font-size: 2.4rem !important;
  font-weight: 700 !important;
  letter-spacing: -0.05em !important;
  color: var(--ink) !important;
  line-height: 1.15 !important;
}
[data-testid="stMetricDelta"] { font-size: 0.76rem !important; }

/* ═══════════ BUTTONS ═══════════ */
.stButton > button {
  background: var(--ink) !important;
  color: var(--paper) !important;
  border: 2px solid var(--ink) !important;
  border-radius: var(--r-sm) !important;
  padding: 0.6rem 1.8rem !important;
  font-family: var(--font-d) !important;
  font-size: 0.83rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.03em !important;
  text-transform: uppercase !important;
  cursor: pointer !important;
  transition: all 0.2s ease !important;
  box-shadow: 3px 3px 0 var(--accent) !important;
}
.stButton > button:hover {
  background: var(--accent) !important;
  border-color: var(--accent) !important;
  transform: translate(-2px, -2px) !important;
  box-shadow: 5px 5px 0 var(--ink) !important;
  color: white !important;
}
.stButton > button:active {
  transform: translate(1px, 1px) !important;
  box-shadow: 1px 1px 0 var(--accent) !important;
}

/* ═══════════ FORM ELEMENTS ═══════════ */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input {
  background: var(--paper) !important;
  border: 1.5px solid var(--border-md) !important;
  border-radius: var(--r-sm) !important;
  color: var(--ink) !important;
  font-family: var(--font-b) !important;
  font-size: 0.9rem !important;
  padding: 12px 16px !important;
  transition: border-color 0.18s, box-shadow 0.18s !important;
  box-shadow: none !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: 3px 3px 0 var(--accent-dim) !important;
  outline: none !important;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder {
  color: rgba(10,10,10,0.3) !important;
  font-style: italic;
}

[data-testid="stFileUploader"] {
  background: var(--paper) !important;
  border: 2px dashed var(--border-md) !important;
  border-radius: var(--r-md) !important;
  transition: all 0.2s !important;
}
[data-testid="stFileUploader"]:hover {
  border-color: var(--accent) !important;
  background: var(--accent-dim) !important;
}

[data-testid="stSelectbox"] > div > div {
  background: var(--paper) !important;
  border: 1.5px solid var(--border-md) !important;
  border-radius: var(--r-sm) !important;
  color: var(--ink) !important;
  font-family: var(--font-b) !important;
}

[data-testid="stSlider"] [role="slider"] {
  background: var(--ink) !important;
  border: 2px solid var(--warm-white) !important;
  box-shadow: 0 0 0 2px var(--accent) !important;
  width: 18px !important; height: 18px !important;
}

[data-testid="stProgressBar"] > div {
  background: var(--paper-2) !important;
  border-radius: var(--r-xs) !important;
  height: 6px !important;
}
[data-testid="stProgressBar"] > div > div {
  background: var(--accent) !important;
  border-radius: var(--r-xs) !important;
  box-shadow: 2px 0 8px var(--accent-glow) !important;
}

[data-testid="stWidgetLabel"] p, label p {
  font-size: 0.72rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.1em !important;
  text-transform: uppercase !important;
  color: rgba(10,10,10,0.45) !important;
}

/* ═══════════ TABS ═══════════ */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
  background: var(--paper-2) !important;
  border-radius: var(--r-md) !important;
  padding: 5px !important;
  gap: 3px !important;
  border: 1.5px solid var(--border) !important;
  box-shadow: var(--shadow-sm) !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
  background: transparent !important;
  border-radius: var(--r-sm) !important;
  color: rgba(10,10,10,0.5) !important;
  font-family: var(--font-d) !important;
  font-size: 0.8rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.02em !important;
  padding: 9px 20px !important;
  transition: all 0.18s !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
  background: var(--ink) !important;
  color: var(--paper) !important;
  box-shadow: var(--shadow-sm) !important;
}

/* ═══════════ EXPANDERS ═══════════ */
[data-testid="stExpander"] {
  background: var(--paper) !important;
  border: 1.5px solid var(--border-md) !important;
  border-radius: var(--r-md) !important;
  box-shadow: var(--shadow-sm) !important;
  overflow: hidden;
}
[data-testid="stExpander"] summary {
  font-family: var(--font-d) !important;
  font-weight: 600 !important;
  font-size: 0.88rem !important;
  color: var(--ink) !important;
  padding: 14px 20px !important;
  background: var(--paper) !important;
}
[data-testid="stExpander"][open] summary {
  border-bottom: 1.5px solid var(--border-md) !important;
}

/* ═══════════ DATAFRAMES ═══════════ */
[data-testid="stDataFrame"] {
  border: 1.5px solid var(--border-md) !important;
  border-radius: var(--r-md) !important;
  overflow: hidden !important;
  box-shadow: var(--shadow-sm) !important;
}
[data-testid="stDataFrame"] th {
  background: var(--ink) !important;
  color: var(--paper) !important;
  font-family: var(--font-d) !important;
  font-size: 0.7rem !important;
  letter-spacing: 0.1em !important;
  text-transform: uppercase !important;
  font-weight: 600 !important;
  padding: 12px 16px !important;
}

/* ═══════════ ALERTS ═══════════ */
[data-baseweb="notification"] {
  border-radius: var(--r-md) !important;
  font-family: var(--font-b) !important;
  font-size: 0.875rem !important;
  border-left: 4px solid !important;
}

/* ═══════════ TOGGLE / CHECKBOX ═══════════ */
[data-testid="stToggle"] > label { font-family: var(--font-b) !important; }

/* ═══════════ SCROLLBAR ═══════════ */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--paper-2); }
::-webkit-scrollbar-thumb { background: var(--ink-3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* ═══════════ CUSTOM COMPONENTS ═══════════ */

/* Skill bar */
.sk-wrap { margin-bottom: 11px; }
.sk-hdr  { display:flex;justify-content:space-between;margin-bottom:5px; }
.sk-name { font-size:0.8rem;font-weight:600;color:var(--ink-2); }
.sk-pct  { font-family:var(--font-m);font-size:0.73rem;color:var(--ink-3); }
.sk-bg   { height:6px;background:var(--paper-3);border-radius:var(--r-xs);overflow:hidden;position:relative; }
.sk-fill { height:100%;border-radius:var(--r-xs);transition:width 0.8s cubic-bezier(.22,.68,0,1.2); }

/* Status pills */
.pill { display:inline-flex;align-items:center;gap:5px;padding:3px 10px;border-radius:var(--r-xs);
        font-size:0.67rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase; }
.p-g  { background:var(--green-bg);border:1px solid var(--green-bdr);color:var(--green); }
.p-r  { background:var(--red-bg);border:1px solid var(--red-bdr);color:var(--red); }
.p-a  { background:var(--amber-bg);border:1px solid var(--amber-bdr);color:var(--amber); }
.p-b  { background:var(--blue-bg);border:1px solid rgba(26,82,118,0.25);color:var(--blue); }

/* Tag chip */
.tag { display:inline-block;background:var(--paper-2);border:1px solid var(--border-md);
       color:var(--ink-3);font-family:var(--font-m);font-size:0.68rem;
       padding:2px 8px;border-radius:var(--r-xs);margin:2px 3px 2px 0; }

/* Candidate card */
.cand-card {
  display:flex;align-items:center;justify-content:space-between;
  padding:14px 16px;
  background:var(--paper);
  border:1.5px solid var(--border);
  border-radius:var(--r-md);
  margin-bottom:8px;
  transition:all 0.18s ease;
  box-shadow:var(--shadow-sm);
}
.cand-card:hover { border-color:var(--border-hi);box-shadow:var(--shadow-md);transform:translateX(3px); }
.cand-av {
  width:40px;height:40px;border-radius:var(--r-sm);
  display:flex;align-items:center;justify-content:center;
  font-family:var(--font-d);font-weight:700;font-size:0.9rem;
  flex-shrink:0;border:2px solid;
}
.cand-name { font-family:var(--font-d);font-size:0.92rem;font-weight:600;color:var(--ink); }
.cand-meta { font-size:0.72rem;color:rgba(10,10,10,0.45);margin-top:2px; }

/* Score ring (inline SVG-based) */
.score-big {
  font-family:var(--font-d);font-size:2.8rem;font-weight:700;
  letter-spacing:-0.05em;line-height:1;color:var(--accent);
}

/* Question card */
.q-card {
  background:var(--ink);
  border-radius:var(--r-md);
  padding:22px 26px;
  color:var(--paper);
  font-size:1.0rem;
  line-height:1.75;
  margin:14px 0;
  border-left:5px solid var(--accent);
  font-style:italic;
  position:relative;
}
.q-card::before {
  content:'"';
  position:absolute;top:-8px;left:20px;
  font-size:5rem;color:var(--accent);
  font-family:Georgia,serif;line-height:1;opacity:0.25;
}

/* Eval card */
.ev-card {
  background:var(--paper-2);
  border:1.5px solid var(--border-md);
  border-left:4px solid var(--accent);
  border-radius:0 var(--r-md) var(--r-md) 0;
  padding:18px 22px;
  font-size:0.88rem;line-height:1.75;
  color:var(--ink-2);
}

/* Score number box */
.score-box {
  display:inline-flex;flex-direction:column;align-items:center;
  background:var(--ink);color:var(--paper);
  padding:10px 18px;border-radius:var(--r-sm);
  box-shadow:4px 4px 0 var(--accent);
}
.score-box .num { font-family:var(--font-d);font-size:2rem;font-weight:700;line-height:1;color:var(--paper); }
.score-box .lbl { font-size:0.65rem;letter-spacing:0.12em;text-transform:uppercase;color:rgba(245,240,232,0.5);margin-top:3px; }

/* Activity row */
.act-row {
  display:flex;align-items:flex-start;gap:12px;
  padding:12px 0;border-bottom:1px solid var(--border);
}
.act-row:last-child { border-bottom:none; }
.act-icon {
  width:32px;height:32px;border-radius:var(--r-sm);
  display:flex;align-items:center;justify-content:center;
  font-size:0.85rem;font-weight:700;flex-shrink:0;
  background:var(--paper-2);border:1.5px solid var(--border-md);
  color:var(--accent);font-family:var(--font-m);
}
.act-name { font-size:0.85rem;font-weight:700;color:var(--ink); }
.act-desc { font-size:0.76rem;color:rgba(10,10,10,0.5);margin-top:2px; }
.act-time { font-family:var(--font-m);font-size:0.67rem;color:rgba(10,10,10,0.3);white-space:nowrap;margin-top:3px; }

/* Timeline step */
.step-wrap { display:flex;gap:16px;padding:14px 0;border-bottom:1px solid var(--border); }
.step-wrap:last-child { border-bottom:none; }
.step-num {
  width:32px;height:32px;border-radius:50%;
  background:var(--ink);color:var(--paper);
  display:flex;align-items:center;justify-content:center;
  font-family:var(--font-d);font-weight:700;font-size:0.8rem;flex-shrink:0;
}
.step-title { font-weight:700;font-size:0.88rem;color:var(--ink);margin-bottom:3px; }
.step-body  { font-size:0.78rem;color:rgba(10,10,10,0.5);line-height:1.55; }

/* Divider */
.div { height:1px;background:var(--border-md);margin:22px 0; }
.div-accent { height:2px;background:linear-gradient(90deg,var(--accent),transparent);margin:22px 0; }

/* Empty */
.empty { text-align:center;padding:44px 24px;color:rgba(10,10,10,0.3); }
.empty .ei { font-size:2.8rem;margin-bottom:12px;filter:grayscale(1);opacity:0.3; }
.empty .et { font-family:var(--font-d);font-size:1rem;color:rgba(10,10,10,0.5); }
.empty .eb { font-size:0.8rem;margin-top:5px; }

/* Insight box */
.ins {
  border-radius:var(--r-md);padding:16px 20px;margin-bottom:12px;
  border-left:4px solid;font-size:0.85rem;line-height:1.6;
}
.ins-title { font-family:var(--font-d);font-weight:700;font-size:0.88rem;margin-bottom:5px; }
.ins-g { background:var(--green-bg);border-color:var(--green);color:rgba(10,10,10,0.75); }
.ins-g .ins-title { color:var(--green); }
.ins-r { background:var(--red-bg);border-color:var(--red);color:rgba(10,10,10,0.75); }
.ins-r .ins-title { color:var(--red); }
.ins-a { background:var(--amber-bg);border-color:var(--amber);color:rgba(10,10,10,0.75); }
.ins-a .ins-title { color:var(--amber); }
.ins-b { background:var(--blue-bg);border-color:var(--blue);color:rgba(10,10,10,0.75); }
.ins-b .ins-title { color:var(--blue); }

/* Nav label */
.nav-lbl {
  font-family:var(--font-m);font-size:0.6rem;letter-spacing:0.2em;
  text-transform:uppercase;color:rgba(245,240,232,0.3);
  padding:14px 16px 6px;
}

/* Leaderboard row */
.lb-row {
  display:flex;align-items:center;gap:14px;
  padding:14px 16px;background:var(--paper);
  border:1.5px solid var(--border);border-radius:var(--r-md);
  margin-bottom:8px;box-shadow:var(--shadow-sm);
  transition:all 0.18s;
}
.lb-row:hover { border-color:var(--border-hi);transform:translateX(4px);box-shadow:var(--shadow-md); }
.lb-rank {
  font-family:var(--font-d);font-size:1.2rem;font-weight:700;
  color:rgba(10,10,10,0.15);min-width:30px;text-align:center;
}

/* Comparison bar */
.cmp-bar {
  height:8px;border-radius:var(--r-xs);overflow:hidden;
  background:var(--paper-3);margin:5px 0;
}
.cmp-fill { height:100%;border-radius:var(--r-xs);transition:width 0.7s ease; }

/* ═══════════ ANIMATIONS ═══════════ */
@keyframes fadeUp { from{opacity:0;transform:translateY(16px);} to{opacity:1;transform:translateY(0);} }
@keyframes slideIn { from{opacity:0;transform:translateX(-12px);} to{opacity:1;transform:translateX(0);} }
.card { animation: fadeUp 0.35s ease both; }
.cand-card { animation: slideIn 0.3s ease both; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  MATPLOTLIB THEME  (warm/paper)
# ══════════════════════════════════════════════════════════════
plt.rcParams.update({
    "figure.facecolor": "#f5f0e8",
    "axes.facecolor":   "#f5f0e8",
    "axes.edgecolor":   (10/255, 10/255, 10/255, 0.15),
    "axes.labelcolor":  (10/255, 10/255, 10/255, 0.5),
    "xtick.color":      (10/255, 10/255, 10/255, 0.4),
    "ytick.color":      (10/255, 10/255, 10/255, 0.4),
    "grid.color":       (10/255, 10/255, 10/255, 0.07),
    "grid.linestyle":   "--",
    "grid.alpha":       1.0,
    "text.color":       "#0a0a0a",
    "font.family":      "sans-serif",
    "axes.spines.top":  False,
    "axes.spines.right":False,
    "axes.spines.left": False,
})
C = dict(
    accent="#e8521a", ink="#0a0a0a", green="#1a7a4a",
    red="#c0392b",    amber="#b8860b", blue="#1a5276",
    paper="#f5f0e8",  paper2="#ede8dc",
)

def fig(w=6, h=3.5):
    f, ax = plt.subplots(figsize=(w,h))
    f.patch.set_facecolor("#f5f0e8"); ax.set_facecolor("#f5f0e8")
    return f, ax

# ══════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════
def av_color(name):
    cs=["#e8521a","#1a7a4a","#1a5276","#b8860b","#7b2d8b","#c0392b"]
    return cs[hash(name)%len(cs)]

def ini(name):
    p=name.split(); return (p[0][0]+(p[-1][0] if len(p)>1 else "")).upper()

def skbar(name, pct, color=None):
    c = color or C["accent"]
    st.markdown(f"""<div class="sk-wrap">
      <div class="sk-hdr"><span class="sk-name">{name}</span><span class="sk-pct">{pct}%</span></div>
      <div class="sk-bg"><div class="sk-fill" style="width:{pct}%;background:{c};"></div></div>
    </div>""", unsafe_allow_html=True)

def pill(txt, kind="g"):
    st.markdown(f'<span class="pill p-{kind}">{txt}</span>', unsafe_allow_html=True)

def tags(lst):
    st.markdown("".join(f'<span class="tag">{t}</span>' for t in lst), unsafe_allow_html=True)

def sec(label):
    st.markdown(f'<div class="sec-title">{label}</div>', unsafe_allow_html=True)

def divider(accent=False):
    cls = "div-accent" if accent else "div"
    st.markdown(f'<div class="{cls}"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════
_defaults = dict(
    questions=[], q_idx=0, scores=[], eval_report=None, evaluated=False,
    active_cand=None, notes={}, screen_hist=[], compare_list=[],
    jd_store="", threshold=65, rw=60,
)
for k,v in _defaults.items():
    if k not in st.session_state: st.session_state[k]=v

# ══════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:28px 16px 20px;border-bottom:1px solid rgba(245,240,232,0.1);margin-bottom:8px;">
      <div style="font-family:'Clash Display','Cabinet Grotesk',sans-serif;font-size:1.45rem;font-weight:700;
                  letter-spacing:-0.03em;color:#f5f0e8;line-height:1;">
        <span style="color:#e8521a;">▲</span> APEX HIRE
      </div>
      <div style="font-size:0.62rem;letter-spacing:0.2em;text-transform:uppercase;
                  color:rgba(245,240,232,0.28);margin-top:6px;">Talent Intelligence Platform</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="nav-lbl">Access Level</div>', unsafe_allow_html=True)
    role_opt = st.radio("", ["▲  Recruiter", "◆  Candidate"], label_visibility="collapsed")
    role = "Recruiter" if "Recruiter" in role_opt else "Candidate"

    if role == "Recruiter":
        st.markdown('<div class="nav-lbl">Workspace</div>', unsafe_allow_html=True)
        rnav = st.radio("", [
            "◉  Command Center",
            "⊕  Resume Screening",
            "◈  Candidate Profiles",
            "△  Leaderboard",
            "◎  Analytics Suite",
            "⊞  Comparison Tool",
            "✦  Job Board",
            "⚙  Settings",
        ], label_visibility="collapsed")
    else:
        rnav = None

    if DEMO:
        st.markdown("""<div style="margin:20px 16px 0;padding:12px;background:rgba(232,82,26,0.15);
            border:1px solid rgba(232,82,26,0.3);border-radius:6px;font-size:0.73rem;
            color:rgba(245,240,232,0.7);line-height:1.5;">▲ Demo mode — all modules simulated</div>""",
            unsafe_allow_html=True)

    st.markdown(f"""<div style="margin-top:30px;padding:14px 16px;border-top:1px solid rgba(245,240,232,0.08);">
      <div style="font-size:0.62rem;letter-spacing:0.1em;text-transform:uppercase;
                  color:rgba(245,240,232,0.25);">v3.0 · {'Demo' if DEMO else 'Live'}</div>
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  TOP BANNER
# ══════════════════════════════════════════════════════════════
now = datetime.now().strftime("%a, %d %b %Y · %H:%M")
st.markdown(f"""<div class="top-banner">
  <div class="banner-brand"><span class="tri">▲</span> APEX HIRE</div>
  <div class="banner-right">
    <div class="banner-pill"><div class="pulse"></div>Live Platform</div>
    <div class="banner-pill">{now}</div>
    <div class="banner-pill">{'Demo Mode' if DEMO else 'Production'}</div>
  </div>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  DATA HELPERS
# ══════════════════════════════════════════════════════════════
def get_df():
    if DEMO:
        df = pd.DataFrame(CANDIDATES,
            columns=["Candidate","Resume Score","Interview Score","Dept","Level","City","Email"])
    else:
        raw  = get_all_candidates() or []
        rows = [(r[0],r[1],r[2],"Engineering","Mid","N/A","N/A") for r in raw]
        df   = pd.DataFrame(rows,
            columns=["Candidate","Resume Score","Interview Score","Dept","Level","City","Email"])
    df["Resume Score"]    = pd.to_numeric(df["Resume Score"],    errors="coerce")
    df["Interview Score"] = pd.to_numeric(df["Interview Score"], errors="coerce")
    return df

# ══════════════════════════════════════════════════════════════
#  ██  RECRUITER  ██
# ══════════════════════════════════════════════════════════════
if role == "Recruiter":
    df = get_df()
    total    = len(df)
    done     = int(df["Interview Score"].notna().sum())
    selected = int((df["Interview Score"]>=60).sum())
    rejected = done - selected
    pending  = total - done
    sel_rate = round(selected/total*100,1) if total else 0
    avg_r    = round(df["Resume Score"].mean(),1)    if total else 0
    avg_i    = round(df["Interview Score"].mean(),1) if done  else 0

    # ─────────────────────────────────────────────
    # ◉  COMMAND CENTER
    # ─────────────────────────────────────────────
    if "Command" in rnav:
        st.markdown("""<div class="page-hdr">
          <div>
            <div class="breadcrumb">Recruiter → Command Center</div>
            <h1>Command <span>Center</span></h1>
            <p class="page-hdr-sub">Your real-time hiring intelligence overview</p>
          </div>
        </div>""", unsafe_allow_html=True)

        # KPIs
        k1,k2,k3,k4,k5,k6 = st.columns(6)
        k1.metric("Screened",    total,    delta=f"+{max(0,total-7)} wk")
        k2.metric("Interviewed", done)
        k3.metric("Selected",    selected, delta=f"{sel_rate}% rate")
        k4.metric("Rejected",    rejected)
        k5.metric("Pending",     pending)
        k6.metric("Avg Interview", f"{avg_i}%")

        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        col_l, col_r = st.columns([3,2], gap="large")

        with col_l:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            sec("Hiring Funnel — Stage Conversion")
            stages = ["Applicants","Screened","Shortlisted","Interviewed","Selected","Offered"]
            vals   = [total+18, total+10, total+3, done, selected, max(0,selected-2)]
            col_fs = [C["ink"],C["blue"],C["amber"],C["accent"],C["green"],"#7b2d8b"]
            f0, ax = fig(7, 3.4)
            y_pos  = range(len(stages))
            bars   = ax.barh(stages, vals, color=col_fs, height=0.58, zorder=3)
            for bar, v, c in zip(bars, vals, col_fs):
                ax.text(bar.get_width()+0.3, bar.get_y()+bar.get_height()/2,
                        str(v), va='center', fontsize=11, color=C["ink"], fontweight='700')
            ax.set_xlim(0, max(vals)*1.18)
            ax.xaxis.grid(True, zorder=0, alpha=0.5)
            ax.set_xlabel("Candidate Count", labelpad=10)
            ax.invert_yaxis()
            f0.tight_layout(pad=1.8); st.pyplot(f0)
            st.markdown('</div>', unsafe_allow_html=True)

            # Two charts side by side
            ch1, ch2 = st.columns(2, gap="medium")
            with ch1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                sec("Score Distribution")
                scored = df["Interview Score"].dropna()
                if len(scored):
                    f1, ax1 = fig(5, 3.2)
                    n, bins, patches = ax1.hist(scored, bins=7, color=C["accent"],
                                                 edgecolor="#f5f0e8", linewidth=2, zorder=3)
                    for p, b in zip(patches, bins[:-1]):
                        p.set_facecolor(C["green"] if b>=60 else C["red"])
                    ax1.axvline(60, color=C["ink"], lw=1.5, ls="--", alpha=0.6, label="60% threshold")
                    ax1.set_xlabel("Interview Score %", labelpad=8)
                    ax1.set_ylabel("Count", labelpad=8)
                    ax1.yaxis.grid(True, zorder=0)
                    ax1.legend(framealpha=0, fontsize=8)
                    f1.tight_layout(pad=1.5); st.pyplot(f1)
                else:
                    st.markdown('<div class="empty"><div class="ei">📊</div><div class="et">No interview data</div></div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with ch2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                sec("By Department")
                dept_counts = df.groupby("Dept")["Candidate"].count().sort_values(ascending=False)
                f2, ax2 = fig(5, 3.2)
                colors2 = [C["accent"],C["blue"],C["green"],C["amber"],C["red"]]
                ax2.barh(dept_counts.index, dept_counts.values,
                         color=colors2[:len(dept_counts)], height=0.5, zorder=3)
                ax2.xaxis.grid(True, zorder=0, alpha=0.5)
                ax2.set_xlabel("Candidates", labelpad=8)
                ax2.invert_yaxis()
                f2.tight_layout(pad=1.5); st.pyplot(f2)
                st.markdown('</div>', unsafe_allow_html=True)

        with col_r:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            sec("Live Activity Feed")
            for name, action, detail, time_str, icon in ACTIVITY_LOG:
                clr = av_color(name)
                st.markdown(f"""<div class="act-row">
                  <div class="act-icon">{icon}</div>
                  <div style="flex:1">
                    <div class="act-name">{name}</div>
                    <div class="act-desc">{action} — {detail}</div>
                    <div class="act-time">{time_str}</div>
                  </div>
                </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Mini leaderboard
            st.markdown('<div class="card">', unsafe_allow_html=True)
            sec("Top 4 Candidates")
            top = df.dropna(subset=["Interview Score"]).nlargest(4, "Interview Score")
            for _, row in top.iterrows():
                clr   = av_color(row["Candidate"])
                score = int(row["Interview Score"])
                kind  = "g" if score>=60 else "r"
                label = "Selected" if score>=60 else "Rejected"
                st.markdown(f"""<div class="cand-card" style="padding:10px 14px;">
                  <div style="display:flex;align-items:center;gap:10px;">
                    <div class="cand-av" style="background:{clr}18;color:{clr};border-color:{clr}44;width:34px;height:34px;font-size:0.78rem;">{ini(row["Candidate"])}</div>
                    <div><div class="cand-name" style="font-size:0.85rem;">{row["Candidate"]}</div>
                         <div class="cand-meta">{row["Dept"]} · {row["Level"]}</div></div>
                  </div>
                  <div style="display:flex;align-items:center;gap:8px;">
                    <span style="font-family:'Fira Code',monospace;font-size:1.1rem;font-weight:700;color:{clr};">{score}%</span>
                    <span class="pill p-{kind}">{label}</span>
                  </div>
                </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # ⊕  RESUME SCREENING
    # ─────────────────────────────────────────────
    elif "Screening" in rnav:
        st.markdown("""<div class="page-hdr">
          <div>
            <div class="breadcrumb">Recruiter → Resume Screening</div>
            <h1>Resume <span>Screening</span></h1>
            <p class="page-hdr-sub">AI-powered resume analysis & JD matching</p>
          </div>
        </div>""", unsafe_allow_html=True)

        col_form, col_hist = st.columns([3,2], gap="large")

        with col_form:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            sec("Candidate Information")
            r1, r2 = st.columns(2, gap="medium")
            with r1:
                cname  = st.text_input("Full Name",    placeholder="e.g. Priya Sharma")
                dept   = st.selectbox("Department", ["Engineering","Data Science","Product","Design","Operations","Finance","HR","Marketing"])
            with r2:
                rtitle = st.text_input("Role Title",   placeholder="e.g. Senior ML Engineer")
                seniority = st.selectbox("Seniority",  ["Intern","Junior","Mid","Senior","Lead","Manager","Director","VP"])

            r3, r4 = st.columns(2)
            with r3: email = st.text_input("Candidate Email", placeholder="candidate@email.com")
            with r4: city  = st.text_input("Location",        placeholder="City, Country")

            divider()
            sec("Documents & Job Description")
            ufile = st.file_uploader("Upload Resume (PDF)", type="pdf")
            if ufile:
                st.markdown(f"""<div style="display:flex;align-items:center;gap:10px;padding:10px 14px;
                  background:var(--green-bg);border:1.5px solid var(--green-bdr);border-radius:var(--r-sm);
                  font-size:0.82rem;color:var(--green);font-weight:600;">
                  ✓ {ufile.name} · {ufile.size//1024} KB secured
                </div>""", unsafe_allow_html=True)

            jd = st.text_area("Job Description", height=220,
                value=st.session_state.jd_store,
                placeholder="Paste the complete job description — required skills, responsibilities, qualifications, nice-to-haves...")
            st.session_state.jd_store = jd

            divider()
            sec("Scoring Configuration")
            sc1, sc2 = st.columns(2)
            with sc1: threshold = st.slider("Match Threshold (%)", 0, 100, st.session_state.threshold)
            with sc2: rw        = st.slider("Resume Weight (%)",   0, 100, st.session_state.rw)
            st.session_state.threshold = threshold
            st.session_state.rw        = rw

            st.markdown(f'<p style="font-size:0.75rem;color:rgba(10,10,10,0.4);margin-top:-8px;">Interview will carry <b>{100-rw}%</b> weight in final composite score.</p>', unsafe_allow_html=True)

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            analyze = st.button("⊕  Analyze Profile", use_container_width=True)

            if analyze and cname:
                with st.spinner("Running deep AI analysis…"):
                    if DEMO:
                        rscore = random.randint(52, 97)
                        gaps   = (f"**Strong:** Python ({random.randint(75,95)}%), SQL ({random.randint(65,90)}%), "
                                  f"Communication, Problem Solving\n\n"
                                  f"**Gaps:** Cloud deployment (AWS/GCP) not evidenced. "
                                  f"Docker/Kubernetes experience unclear. "
                                  f"Consider probing for system design experience in interview.\n\n"
                                  f"**Recommendation:** {'Proceed to interview — strong technical foundation.' if rscore>=threshold else 'Below threshold. Consider for junior role or re-application next cycle.'}")
                        skills_raw = {
                            "Python": random.randint(70,95),
                            "SQL / Databases": random.randint(55,90),
                            "Machine Learning": random.randint(45,85),
                            "System Design": random.randint(40,80),
                            "Communication": random.randint(65,95),
                            "Cloud (AWS/GCP)": random.randint(20,65),
                        }
                        time.sleep(1.4)
                    else:
                        txt    = extract_resume_text(ufile)
                        rscore = calculate_match(txt, jd)
                        gaps   = skill_gap_analysis(txt, jd)
                        skills_raw = {}

                divider(accent=True)
                sec("Analysis Results")

                m1,m2,m3,m4 = st.columns(4)
                m1.metric("Match Score",   f"{rscore}%")
                m2.metric("Threshold",     f"{threshold}%")
                m3.metric("Gap",           f"{max(0, threshold-rscore)}%")
                m4.metric("Decision", "✓ PASS" if rscore>=threshold else "✕ FAIL")

                st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
                st.markdown(f'<div class="ev-card"><b style="color:var(--accent);">AI Skill Gap Analysis</b><br><br>{gaps}</div>', unsafe_allow_html=True)

                if skills_raw:
                    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
                    sec("Detected Skills")
                    sk1, sk2 = st.columns(2)
                    items = list(skills_raw.items())
                    with sk1:
                        for k,v in items[:3]:
                            clr = C["green"] if v>=65 else (C["amber"] if v>=45 else C["red"])
                            skbar(k, v, clr)
                    with sk2:
                        for k,v in items[3:]:
                            clr = C["green"] if v>=65 else (C["amber"] if v>=45 else C["red"])
                            skbar(k, v, clr)

                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                tkgs = random_tags()
                sec("Detected Tags")
                tags(tkgs)

                if rscore >= threshold:
                    st.success(f"✓ **{cname}** has been shortlisted ({rscore}% ≥ {threshold}% threshold).")
                    if not DEMO: add_candidate(cname, rscore)
                    st.session_state.screen_hist.append({
                        "name":cname,"role":rtitle or "N/A","dept":dept,
                        "score":rscore,"status":"Pass","time":datetime.now().strftime("%H:%M"),
                        "tags":tkgs
                    })
                else:
                    st.error(f"✕ **{cname}** did not meet the {threshold}% threshold ({rscore}%).")
            elif analyze:
                st.warning("Please enter the candidate's full name.")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_hist:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            sec("Session Screening History")
            hist = st.session_state.screen_hist or (
                [{"name":"Karan Singh","role":"ML Lead","dept":"DS","score":95,"status":"Pass","time":"10:24","tags":["Python","ML","Spark"]},
                 {"name":"Rahul Gupta","role":"Backend","dept":"Eng","score":61,"status":"Pass","time":"09:58","tags":["Python","SQL"]},
                 {"name":"Zoya Khan","role":"Designer","dept":"Design","score":48,"status":"Fail","time":"09:30","tags":["Figma","UX"]}]
                if DEMO else [])

            if hist:
                for h in reversed(hist[-10:]):
                    c   = av_color(h["name"])
                    clr = C["green"] if h["status"]=="Pass" else C["red"]
                    pkind = "g" if h["status"]=="Pass" else "r"
                    st.markdown(f"""<div class="cand-card">
                      <div style="flex:1">
                        <div style="display:flex;align-items:center;gap:8px;">
                          <span class="cand-name">{h["name"]}</span>
                          <span class="pill p-{pkind}">{h["status"]}</span>
                        </div>
                        <div class="cand-meta">{h["role"]} · {h["dept"]} · {h["time"]}</div>
                        <div style="margin-top:5px;">{"".join(f'<span class="tag">{t}</span>' for t in h.get("tags",[]))}</div>
                      </div>
                      <div style="font-family:'Fira Code',monospace;font-size:1.15rem;font-weight:700;color:{clr};">{h["score"]}%</div>
                    </div>""", unsafe_allow_html=True)
            else:
                st.markdown('<div class="empty"><div class="ei">📋</div><div class="et">No history yet</div><div class="eb">Run a screening to see results here</div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="card">', unsafe_allow_html=True)
            sec("Scoring Reference Guide")
            guide = [("90–100%","Exceptional","Immediate shortlist",C["green"]),
                     ("75–89%","Strong Match","Recommended",C["green"]),
                     ("65–74%","Good Match","Borderline — interview",C["amber"]),
                     ("50–64%","Weak Match","Below threshold",C["red"]),
                     ("0–49%","Poor Match","Reject",C["red"])]
            for rng, lbl, rec, clr in guide:
                st.markdown(f"""<div style="display:flex;justify-content:space-between;align-items:center;
                  padding:9px 0;border-bottom:1px solid var(--border);">
                  <div>
                    <span style="font-family:'Fira Code',monospace;font-size:0.8rem;font-weight:600;color:{clr};">{rng}</span>
                    <span style="font-size:0.75rem;color:rgba(10,10,10,0.5);margin-left:8px;">{lbl}</span>
                  </div>
                  <span style="font-size:0.72rem;color:rgba(10,10,10,0.4);">{rec}</span>
                </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # ◈  CANDIDATE PROFILES
    # ─────────────────────────────────────────────
    elif "Profiles" in rnav:
        st.markdown("""<div class="page-hdr">
          <div>
            <div class="breadcrumb">Recruiter → Candidate Profiles</div>
            <h1>Candidate <span>Profiles</span></h1>
            <p class="page-hdr-sub">Deep-dive into individual candidate assessments</p>
          </div>
        </div>""", unsafe_allow_html=True)

        # Filters bar
        st.markdown('<div class="card">', unsafe_allow_html=True)
        sec("Filters")
        f1, f2, f3, f4 = st.columns(4)
        with f1: search  = st.text_input("Search name",  placeholder="Type to filter…", label_visibility="collapsed")
        with f2: f_dept  = st.selectbox("Department", ["All"]+sorted(df["Dept"].unique().tolist()),  label_visibility="collapsed")
        with f3: f_level = st.selectbox("Seniority",  ["All"]+sorted(df["Level"].unique().tolist()), label_visibility="collapsed")
        with f4: f_status= st.selectbox("Status",     ["All","Selected","Rejected","Pending"],       label_visibility="collapsed")

        filtered = df.copy()
        if search:   filtered = filtered[filtered["Candidate"].str.contains(search,case=False,na=False)]
        if f_dept  != "All": filtered = filtered[filtered["Dept"]==f_dept]
        if f_level != "All": filtered = filtered[filtered["Level"]==f_level]
        if f_status == "Selected": filtered = filtered[filtered["Interview Score"]>=60]
        elif f_status == "Rejected": filtered = filtered[(filtered["Interview Score"].notna())&(filtered["Interview Score"]<60)]
        elif f_status == "Pending":  filtered = filtered[filtered["Interview Score"].isna()]
        st.markdown(f'<p style="font-size:0.75rem;color:rgba(10,10,10,0.4);margin-top:-4px;">Showing {len(filtered)} of {len(df)} candidates</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if filtered.empty:
            st.markdown('<div class="empty"><div class="ei">🔍</div><div class="et">No candidates match filters</div></div>', unsafe_allow_html=True)
        else:
            for _, row in filtered.iterrows():
                rs  = int(row["Resume Score"])    if pd.notna(row["Resume Score"])    else None
                is_ = int(row["Interview Score"]) if pd.notna(row["Interview Score"]) else None
                clr = av_color(row["Candidate"])
                pkind = "g" if (is_ and is_>=60) else ("r" if is_ else "a")
                plabel= "Selected" if (is_ and is_>=60) else ("Rejected" if is_ else "Pending")

                with st.expander(f"  {ini(row['Candidate'])}   {row['Candidate']}   ·   {row['Dept']} · {row['Level']}   ·   {plabel}"):
                    ep1, ep2 = st.columns([2,3], gap="large")
                    with ep1:
                        st.markdown(f"""<div style="text-align:center;padding:20px;
                          background:var(--paper-2);border-radius:var(--r-md);margin-bottom:16px;">
                          <div class="cand-av" style="background:{clr}18;color:{clr};border-color:{clr}44;
                            width:64px;height:64px;font-size:1.4rem;margin:0 auto 12px;">
                            {ini(row["Candidate"])}</div>
                          <div class="cand-name">{row["Candidate"]}</div>
                          <div class="cand-meta" style="margin-top:4px;">{row["Dept"]} · {row["Level"]}</div>
                          <div class="cand-meta">{row.get("City","N/A")} · {row.get("Email","N/A")}</div>
                          <div style="margin-top:10px;"><span class="pill p-{pkind}">{plabel}</span></div>
                        </div>""", unsafe_allow_html=True)

                        m1,m2 = st.columns(2)
                        m1.metric("Resume",    f"{rs}%"  if rs  else "—")
                        m2.metric("Interview", f"{is_}%" if is_ else "—")
                        if rs and is_:
                            comp = round(rs*(st.session_state.rw/100) + is_*((100-st.session_state.rw)/100),1)
                            st.metric("Composite", f"{comp}%")

                    with ep2:
                        sec("Estimated Skill Profile")
                        sk_demo = {
                            "Technical Depth": rs or random.randint(60,90),
                            "Communication":   random.randint(60,95),
                            "Problem Solving": random.randint(55,90),
                            "Leadership":      random.randint(40,85) if row["Level"] in ["Lead","Manager","Director"] else random.randint(30,65),
                            "Culture Fit":     random.randint(65,95),
                            "Domain Expertise": is_ or random.randint(50,85),
                        }
                        for sk, pct in sk_demo.items():
                            clrc = C["green"] if pct>=70 else (C["amber"] if pct>=50 else C["red"])
                            skbar(sk, pct, clrc)

                    divider()
                    sec("Technical Tags")
                    tags(random_tags(5))

                    sec("Recruiter Notes")
                    note = st.text_area("", value=st.session_state.notes.get(row["Candidate"],""),
                                        key=f"note_{row['Candidate']}", height=90,
                                        placeholder="Add private notes about this candidate (not visible to candidate)…",
                                        label_visibility="collapsed")
                    c_save, c_email = st.columns(2)
                    with c_save:
                        if st.button("Save Notes", key=f"sv_{row['Candidate']}"):
                            st.session_state.notes[row["Candidate"]] = note
                            st.success("Saved.")
                    with c_email:
                        if st.button("Send Invite", key=f"em_{row['Candidate']}"):
                            st.info(f"Invite email queued for {row.get('Email','N/A')}")

    # ─────────────────────────────────────────────
    # △  LEADERBOARD
    # ─────────────────────────────────────────────
    elif "Leaderboard" in rnav:
        st.markdown("""<div class="page-hdr">
          <div>
            <div class="breadcrumb">Recruiter → Leaderboard</div>
            <h1>Live <span>Leaderboard</span></h1>
            <p class="page-hdr-sub">Ranked by interview performance · updated in real-time</p>
          </div>
        </div>""", unsafe_allow_html=True)

        medals = ["🥇","🥈","🥉"] + [""]*100
        df_lb  = df.sort_values("Interview Score", ascending=False).reset_index(drop=True)

        # Score chart on top
        st.markdown('<div class="card">', unsafe_allow_html=True)
        sec("Score Overview")
        scored = df_lb.dropna(subset=["Interview Score"])
        if len(scored):
            f3, ax3 = fig(10, 2.8)
            bar_c   = [C["green"] if s>=60 else C["red"] for s in scored["Interview Score"]]
            ax3.bar(range(len(scored)), scored["Interview Score"], color=bar_c, width=0.6, zorder=3)
            ax3.axhline(60, color=C["ink"], lw=1.2, ls="--", alpha=0.4)
            ax3.set_xticks(range(len(scored)))
            ax3.set_xticklabels([n.split()[0] for n in scored["Candidate"]], fontsize=9, rotation=25, ha='right')
            ax3.set_ylabel("Score %"); ax3.yaxis.grid(True, zorder=0)
            ax3.set_ylim(0, 110)
            for i, s in enumerate(scored["Interview Score"]):
                ax3.text(i, s+1.5, f"{int(s)}", ha='center', fontsize=8.5, fontweight='700', color=C["ink"])
            f3.tight_layout(pad=1.5); st.pyplot(f3)
        st.markdown('</div>', unsafe_allow_html=True)

        for i, row in df_lb.iterrows():
            clr    = av_color(row["Candidate"])
            is_    = int(row["Interview Score"]) if pd.notna(row["Interview Score"]) else None
            rs     = int(row["Resume Score"])    if pd.notna(row["Resume Score"])    else None
            pkind  = "g" if (is_ and is_>=60) else ("r" if is_ else "a")
            plabel = "Selected" if (is_ and is_>=60) else ("Rejected" if is_ else "Pending")
            bclr   = C["green"] if pkind=="g" else (C["red"] if pkind=="r" else C["amber"])
            medal  = medals[i]
            rank   = medal if medal else f'<span style="font-family:\'Fira Code\',monospace;font-size:0.85rem;color:rgba(10,10,10,0.2);">#{i+1}</span>'
            st.markdown(f"""<div class="lb-row">
              <div style="min-width:36px;text-align:center;font-size:1.15rem;">{rank}</div>
              <div class="cand-av" style="background:{clr}18;color:{clr};border-color:{clr}55;">{ini(row["Candidate"])}</div>
              <div style="flex:1;min-width:0;">
                <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                  <span class="cand-name">{row["Candidate"]}</span>
                  <span style="font-size:0.72rem;color:rgba(10,10,10,0.4);">{row["Dept"]} · {row["Level"]}</span>
                </div>
                <div class="cmp-bar" style="margin-top:7px;">
                  <div class="cmp-fill" style="width:{is_ if is_ else 0}%;background:{bclr};"></div>
                </div>
              </div>
              <div style="text-align:right;min-width:90px;">
                <div style="font-family:'Fira Code',monospace;font-size:1.25rem;font-weight:700;color:{clr};">{is_ if is_ else "—"}%</div>
                <div style="font-size:0.7rem;color:rgba(10,10,10,0.4);margin-top:2px;">Resume {rs or "—"}%</div>
              </div>
              <span class="pill p-{pkind}" style="min-width:70px;justify-content:center;">{plabel}</span>
            </div>""", unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # ◎  ANALYTICS SUITE
    # ─────────────────────────────────────────────
    elif "Analytics" in rnav:
        st.markdown("""<div class="page-hdr">
          <div>
            <div class="breadcrumb">Recruiter → Analytics Suite</div>
            <h1>Analytics <span>Suite</span></h1>
            <p class="page-hdr-sub">Deep recruitment intelligence & predictive insights</p>
          </div>
        </div>""", unsafe_allow_html=True)

        tabs = st.tabs(["  Overview  ","  Trends  ","  Correlation  ","  Dept Breakdown  ","  AI Insights  "])

        with tabs[0]:
            k1,k2,k3,k4,k5 = st.columns(5)
            k1.metric("Total",       total);         k2.metric("Interviewed", done)
            k3.metric("Selected",    selected);       k4.metric("Pass Rate",  f"{sel_rate}%")
            k5.metric("Avg Interview",f"{avg_i}%")
            st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
            c1,c2 = st.columns(2,gap="large")
            with c1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                sec("Selection Split")
                f4, ax4 = fig(4.5,4.5)
                vals4   = [selected, rejected, pending]
                labels4 = ["Selected","Rejected","Pending"]
                ax4.pie(vals4, labels=labels4, autopct="%1.0f%%", startangle=90,
                        colors=[C["green"],C["red"],C["amber"]],
                        wedgeprops=dict(width=0.6, edgecolor="#f5f0e8", linewidth=3),
                        pctdistance=0.78)
                ax4.axis("equal"); f4.tight_layout(); st.pyplot(f4)
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                sec("Resume vs Interview Dual Distribution")
                f5, ax5 = fig(5.5,4.5)
                rs_clean = df["Resume Score"].dropna()
                is_clean = df["Interview Score"].dropna()
                ax5.hist(rs_clean, bins=7, alpha=0.65, color=C["accent"], edgecolor="#f5f0e8", lw=1.5, label="Resume", zorder=3)
                ax5.hist(is_clean, bins=7, alpha=0.65, color=C["blue"],   edgecolor="#f5f0e8", lw=1.5, label="Interview", zorder=3)
                ax5.set_xlabel("Score %"); ax5.set_ylabel("Count")
                ax5.legend(framealpha=0, fontsize=9)
                ax5.yaxis.grid(True, zorder=0); f5.tight_layout(); st.pyplot(f5)
                st.markdown('</div>', unsafe_allow_html=True)

        with tabs[1]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            sec("30-Day Score Trends (Simulated)")
            days = pd.date_range(end=datetime.now(), periods=30, freq='D')
            np.random.seed(42)
            rt = np.clip(np.cumsum(np.random.randn(30)*1.8)+72, 40, 100)
            it = np.clip(np.cumsum(np.random.randn(30)*1.8)+65, 35, 100)
            ct = np.clip((rt*0.6+it*0.4),35,100)
            f6, ax6 = fig(10, 4.2)
            ax6.plot(days, rt, color=C["accent"], lw=2.5, label="Avg Resume Score", zorder=3)
            ax6.plot(days, it, color=C["blue"],   lw=2.5, label="Avg Interview Score", ls="--", zorder=3)
            ax6.plot(days, ct, color=C["green"],  lw=2.0, label="Avg Composite", ls=":", zorder=3)
            ax6.fill_between(days, rt, alpha=0.06, color=C["accent"])
            ax6.fill_between(days, it, alpha=0.06, color=C["blue"])
            ax6.axhline(60, color=C["ink"], lw=1, ls=":", alpha=0.3, label="Threshold")
            ax6.set_ylabel("Score %"); ax6.legend(framealpha=0, fontsize=9, ncol=4)
            ax6.yaxis.grid(True, zorder=0); plt.xticks(rotation=30, ha='right', fontsize=8)
            f6.tight_layout(); st.pyplot(f6)
            st.markdown('</div>', unsafe_allow_html=True)

        with tabs[2]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            sec("Resume Score vs Interview Score Correlation")
            sc_df = df.dropna(subset=["Resume Score","Interview Score"])
            if len(sc_df)>=2:
                f7, ax7 = fig(7, 4.5)
                scatter = ax7.scatter(sc_df["Resume Score"], sc_df["Interview Score"],
                                      c=sc_df["Interview Score"], cmap="RdYlGn",
                                      vmin=30, vmax=100, s=130,
                                      edgecolors=C["ink"], linewidths=1.2, zorder=3, alpha=0.9)
                z = np.polyfit(sc_df["Resume Score"], sc_df["Interview Score"],1)
                xs= np.linspace(sc_df["Resume Score"].min(),sc_df["Resume Score"].max(),100)
                ax7.plot(xs, np.poly1d(z)(xs), color=C["accent"], lw=2, ls="--", alpha=0.7, label="Trend")
                for _,r in sc_df.iterrows():
                    ax7.annotate(r["Candidate"].split()[0],
                        (r["Resume Score"],r["Interview Score"]),
                        fontsize=7.5, color=C["ink"], alpha=0.6,
                        xytext=(5,5), textcoords="offset points")
                ax7.axhline(60,color=C["red"],lw=1,ls=":",alpha=0.4)
                ax7.axvline(60,color=C["red"],lw=1,ls=":",alpha=0.4)
                ax7.set_xlabel("Resume Score %"); ax7.set_ylabel("Interview Score %")
                ax7.xaxis.grid(True,zorder=0); ax7.yaxis.grid(True,zorder=0)
                ax7.legend(framealpha=0,fontsize=9)
                f7.tight_layout(); st.pyplot(f7)
                corr = sc_df["Resume Score"].corr(sc_df["Interview Score"])
                cc1,cc2,cc3 = st.columns(3)
                cc1.metric("Pearson r",   f"{round(corr,3)}")
                cc2.metric("R² Score",    f"{round(corr**2,3)}")
                cc3.metric("Strength",    "Strong" if corr>0.6 else ("Moderate" if corr>0.3 else "Weak"))
            else:
                st.markdown('<div class="empty"><div class="ei">🔗</div><div class="et">Need 2+ completed interviews</div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with tabs[3]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            sec("Performance by Department")
            dg = df.groupby("Dept").agg(
                count=("Candidate","count"),
                avg_r=("Resume Score","mean"),
                avg_i=("Interview Score","mean")
            ).round(1).reset_index()
            f8, axes8 = plt.subplots(1,2, figsize=(10,4), facecolor=C["paper"])
            for ax in axes8: ax.set_facecolor(C["paper"])
            cols8 = [C["accent"],C["blue"],C["green"],C["amber"],C["red"]][:len(dg)]
            axes8[0].bar(dg["Dept"], dg["avg_r"].fillna(0), color=cols8, width=0.5, zorder=3)
            axes8[0].set_title("Avg Resume Score", fontsize=10, color=C["ink"], fontweight='700', pad=10)
            axes8[0].set_ylabel("Score %"); axes8[0].yaxis.grid(True,zorder=0)
            plt.setp(axes8[0].get_xticklabels(), rotation=25, ha='right', fontsize=9)
            axes8[1].bar(dg["Dept"], dg["avg_i"].fillna(0), color=cols8, width=0.5, zorder=3)
            axes8[1].set_title("Avg Interview Score", fontsize=10, color=C["ink"], fontweight='700', pad=10)
            axes8[1].set_ylabel("Score %"); axes8[1].yaxis.grid(True,zorder=0)
            plt.setp(axes8[1].get_xticklabels(), rotation=25, ha='right', fontsize=9)
            plt.tight_layout(pad=2); st.pyplot(f8)
            st.dataframe(dg.style.format({"avg_r":"{:.1f}","avg_i":"{:.1f}"}), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with tabs[4]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            sec("AI-Generated Recruitment Insights")
            scored_df = df.dropna(subset=["Interview Score"])
            insights  = []

            if done >= 2:
                corr = df["Resume Score"].corr(df["Interview Score"])
                if   corr > 0.7: insights.append(("g","Strong Predictive Validity",f"Pearson r = {round(corr,2)}. Your resume screening criteria are excellent predictors of interview success. The JD requirements are well-calibrated."))
                elif corr > 0.4: insights.append(("a","Moderate Correlation",f"Pearson r = {round(corr,2)}. Some alignment between resume and interview scores. Consider tightening the JD's required skills section."))
                else:            insights.append(("r","Weak Correlation Warning",f"Pearson r = {round(corr,2)}. Resume scores are not predicting interview performance. Your screening criteria may need significant revision."))

            if sel_rate > 75: insights.append(("a","High Pass Rate Detected",f"{sel_rate}% of interviewed candidates are passing. Your bar may be too low — consider raising the interview threshold or question difficulty."))
            elif sel_rate < 25 and done>3: insights.append(("r","Low Pass Rate",f"Only {sel_rate}% passing. Review whether the JD requirements are realistic or whether the question bank is too difficult."))
            else: insights.append(("g","Healthy Pass Rate",f"{sel_rate}% pass rate is within the ideal 30–60% range for senior roles."))

            if avg_i < 55 and done > 2: insights.append(("r","Interview Scores Trending Low",f"Average interview score is {avg_i}%. Consider providing candidates with preparation materials or adjusting question difficulty."))
            if pending > selected:       insights.append(("a","Large Pending Pipeline",f"{pending} candidates awaiting interviews vs {selected} selected. Prioritize scheduling to reduce time-to-hire."))

            insights.append((
    "b",
    "Sourcing Recommendation",
    f"Based on current data, candidates with resume scores ≥ {max(st.session_state.threshold, 70)} ..."
))
            insights.append(("b","Role-Level Insight","Senior candidates show 18% higher correlation between resume and interview scores. Consider more rigorous screening for junior roles."))

            for kind, title, body in insights:
                css_cls = {"g":"ins-g","r":"ins-r","a":"ins-a","b":"ins-b"}[kind]
                st.markdown(f'<div class="ins {css_cls}"><div class="ins-title">{title}</div>{body}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # ⊞  COMPARISON TOOL  (NEW)
    # ─────────────────────────────────────────────
    elif "Comparison" in rnav:
        st.markdown("""<div class="page-hdr">
          <div>
            <div class="breadcrumb">Recruiter → Comparison Tool</div>
            <h1>Candidate <span>Comparison</span></h1>
            <p class="page-hdr-sub">Side-by-side head-to-head candidate analysis</p>
          </div>
        </div>""", unsafe_allow_html=True)

        names = df["Candidate"].tolist()
        cc1, cc2 = st.columns(2, gap="large")
        with cc1: cand_a = st.selectbox("Candidate A", names, index=0)
        with cc2: cand_b = st.selectbox("Candidate B", names, index=min(1,len(names)-1))

        if cand_a != cand_b:
            ra  = df[df["Candidate"]==cand_a].iloc[0]
            rb  = df[df["Candidate"]==cand_b].iloc[0]
            rsa = int(ra["Resume Score"])    if pd.notna(ra["Resume Score"])    else 0
            isa = int(ra["Interview Score"]) if pd.notna(ra["Interview Score"]) else 0
            rsb = int(rb["Resume Score"])    if pd.notna(rb["Resume Score"])    else 0
            isb = int(rb["Interview Score"]) if pd.notna(rb["Interview Score"]) else 0
            comp_a = round(rsa*0.6+isa*0.4,1)
            comp_b = round(rsb*0.6+isb*0.4,1)

            # Header cards
            h1, h2 = st.columns(2, gap="large")
            for col, row, rs, is_, comp in [(h1,ra,rsa,isa,comp_a),(h2,rb,rsb,isb,comp_b)]:
                clr = av_color(row["Candidate"])
                with col:
                    st.markdown(f"""<div class="card" style="text-align:center;">
                      <div class="cand-av" style="background:{clr}18;color:{clr};border-color:{clr}44;
                        width:64px;height:64px;font-size:1.4rem;margin:0 auto 12px;">{ini(row["Candidate"])}</div>
                      <div class="cand-name" style="font-size:1.1rem;">{row["Candidate"]}</div>
                      <div class="cand-meta">{row["Dept"]} · {row["Level"]} · {row.get("City","N/A")}</div>
                      <div style="margin-top:14px;display:flex;justify-content:center;gap:16px;">
                        <div><div style="font-family:'Fira Code',monospace;font-size:1.8rem;font-weight:700;color:{clr};">{comp}%</div>
                             <div style="font-size:0.7rem;color:rgba(10,10,10,0.4);text-transform:uppercase;letter-spacing:0.1em;">Composite</div></div>
                      </div>
                    </div>""", unsafe_allow_html=True)

            # Metric grid
            st.markdown('<div class="card">', unsafe_allow_html=True)
            sec("Head-to-Head Metrics")
            metrics = [("Resume Score", rsa, rsb), ("Interview Score", isa, isb),
                       ("Composite",    comp_a, comp_b)]
            for label, va, vb in metrics:
                winner = "a" if va > vb else ("b" if vb > va else "tie")
                col_l, col_mid, col_r = st.columns([2,1,2])
                with col_l:
                    clr = C["green"] if winner=="a" else C["ink"]
                    st.markdown(f'<div style="text-align:right;font-family:\'Fira Code\',monospace;font-size:1.4rem;font-weight:700;color:{clr};">{va}%</div>', unsafe_allow_html=True)
                with col_mid:
                    st.markdown(f'<div style="text-align:center;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;color:rgba(10,10,10,0.4);padding-top:8px;">{label}</div>', unsafe_allow_html=True)
                with col_r:
                    clr = C["green"] if winner=="b" else C["ink"]
                    st.markdown(f'<div style="text-align:left;font-family:\'Fira Code\',monospace;font-size:1.4rem;font-weight:700;color:{clr};">{vb}%</div>', unsafe_allow_html=True)
                # Bar comparison
                ba, bb = rsa, rsb
                st.markdown(f"""<div style="display:flex;gap:4px;margin-bottom:10px;align-items:center;">
                  <div style="flex:{va};height:6px;background:{'var(--green)' if winner=='a' else 'var(--ink)'};border-radius:3px;"></div>
                  <div style="width:2px;background:var(--border-md);height:10px;"></div>
                  <div style="flex:{vb};height:6px;background:{'var(--green)' if winner=='b' else 'rgba(10,10,10,0.2)'};border-radius:3px;"></div>
                </div>""", unsafe_allow_html=True)

            winner_name = cand_a if comp_a >= comp_b else cand_b
            diff = abs(comp_a-comp_b)
            clr_w = av_color(winner_name)
            st.markdown(f"""<div style="background:var(--paper-2);border:2px solid var(--border-md);border-radius:var(--r-md);
              padding:16px;text-align:center;margin-top:12px;">
              <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.12em;color:rgba(10,10,10,0.4);">Recommendation</div>
              <div style="font-family:'Clash Display',sans-serif;font-size:1.3rem;font-weight:700;color:{clr_w};margin-top:6px;">
                {winner_name} {'leads' if diff>0 else 'tied'} {f'by {diff}%' if diff>0 else ''}</div>
              <div style="font-size:0.8rem;color:rgba(10,10,10,0.5);margin-top:4px;">Based on weighted composite score</div>
            </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Radar chart
            st.markdown('<div class="card">', unsafe_allow_html=True)
            sec("Skill Radar Comparison")
            cats = ["Technical","Communication","Problem Solving","Leadership","Domain","Culture Fit"]
            np.random.seed(hash(cand_a)%100)
            vals_a = [rsa, random.randint(60,95), random.randint(55,90), random.randint(40,85), isa, random.randint(65,95)]
            np.random.seed(hash(cand_b)%100)
            vals_b = [rsb, random.randint(60,95), random.randint(55,90), random.randint(40,85), isb, random.randint(65,95)]
            N = len(cats)
            angles = [n/float(N)*2*np.pi for n in range(N)]
            angles += angles[:1]
            va2 = vals_a + vals_a[:1]
            vb2 = vals_b + vals_b[:1]
            fg, ax_r = plt.subplots(figsize=(5,5), subplot_kw=dict(polar=True))
            fg.patch.set_facecolor(C["paper"]); ax_r.set_facecolor(C["paper"])
            ax_r.plot(angles, va2, color=C["accent"], lw=2.2, zorder=3)
            ax_r.fill(angles, va2, alpha=0.15, color=C["accent"])
            ax_r.plot(angles, vb2, color=C["blue"], lw=2.2, linestyle="--", zorder=3)
            ax_r.fill(angles, vb2, alpha=0.1, color=C["blue"])
            ax_r.set_xticks(angles[:-1]); ax_r.set_xticklabels(cats, fontsize=9)
            ax_r.set_ylim(0,100); ax_r.yaxis.set_tick_params(labelsize=7)
            ax_r.grid(color=C["paper2"], linewidth=1)
            from matplotlib.lines import Line2D
            handles = [Line2D([0],[0],color=C["accent"],lw=2,label=cand_a),
                       Line2D([0],[0],color=C["blue"],  lw=2,label=cand_b,ls="--")]
            ax_r.legend(handles=handles, loc='upper right', bbox_to_anchor=(1.35,1.15), fontsize=9, framealpha=0)
            fg.tight_layout(); st.pyplot(fg)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("Please select two different candidates to compare.")

    # ─────────────────────────────────────────────
    # ✦  JOB BOARD  (NEW)
    # ─────────────────────────────────────────────
    elif "Job Board" in rnav:
        st.markdown("""<div class="page-hdr">
          <div>
            <div class="breadcrumb">Recruiter → Job Board</div>
            <h1>Job <span>Board</span></h1>
            <p class="page-hdr-sub">Manage open roles & track pipeline per position</p>
          </div>
        </div>""", unsafe_allow_html=True)

        jobs = [
            {"title":"Senior ML Engineer",    "dept":"Data Science","level":"Senior","apps":12,"shortlisted":5,"status":"Open",  "days":8},
            {"title":"Backend Engineer",       "dept":"Engineering", "level":"Mid",   "apps":22,"shortlisted":9,"status":"Open",  "days":14},
            {"title":"Product Designer",       "dept":"Design",      "level":"Senior","apps":8, "shortlisted":3,"status":"Open",  "days":5},
            {"title":"Data Analyst",           "dept":"Data Science","level":"Junior","apps":18,"shortlisted":7,"status":"Paused","days":20},
            {"title":"Engineering Manager",    "dept":"Engineering", "level":"Manager","apps":6,"shortlisted":2,"status":"Open",  "days":3},
        ]
        for job in jobs:
            status_kind = "g" if job["status"]=="Open" else "a"
            fill_rate   = round(job["shortlisted"]/job["apps"]*100)
            st.markdown(f"""<div class="card">
              <div style="display:flex;align-items:flex-start;justify-content:space-between;flex-wrap:wrap;gap:12px;">
                <div style="flex:1;min-width:200px;">
                  <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
                    <div class="card-h" style="margin-bottom:0;">{job["title"]}</div>
                    <span class="pill p-{status_kind}">{job["status"]}</span>
                  </div>
                  <div class="cand-meta">{job["dept"]} · {job["level"]} · Posted {job["days"]} days ago</div>
                </div>
                <div style="display:flex;gap:20px;text-align:center;">
                  <div><div style="font-family:'Fira Code',monospace;font-size:1.5rem;font-weight:700;color:var(--ink);">{job["apps"]}</div>
                       <div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;color:rgba(10,10,10,0.4);">Applications</div></div>
                  <div><div style="font-family:'Fira Code',monospace;font-size:1.5rem;font-weight:700;color:var(--accent);">{job["shortlisted"]}</div>
                       <div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;color:rgba(10,10,10,0.4);">Shortlisted</div></div>
                  <div><div style="font-family:'Fira Code',monospace;font-size:1.5rem;font-weight:700;color:var(--green);">{fill_rate}%</div>
                       <div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;color:rgba(10,10,10,0.4);">Conversion</div></div>
                </div>
              </div>
              <div style="margin-top:14px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
                  <span style="font-size:0.72rem;color:rgba(10,10,10,0.4);">Pipeline fill rate</span>
                  <span style="font-family:'Fira Code',monospace;font-size:0.72rem;color:var(--accent);">{fill_rate}%</span>
                </div>
                <div class="cmp-bar"><div class="cmp-fill" style="width:{fill_rate}%;background:var(--accent);"></div></div>
              </div>
            </div>""", unsafe_allow_html=True)

        divider(accent=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        sec("Post New Role")
        pr1,pr2 = st.columns(2,gap="medium")
        with pr1:
            st.text_input("Job Title",    placeholder="e.g. Senior Data Engineer")
            st.selectbox("Department", ["Engineering","Data Science","Product","Design","Operations"])
        with pr2:
            st.selectbox("Level", ["Intern","Junior","Mid","Senior","Lead","Manager","Director"])
            st.text_input("Location",     placeholder="e.g. Bangalore / Remote")
        st.text_area("Job Description Preview", height=100, placeholder="Brief description for the job board…")
        if st.button("Post Role", use_container_width=False):
            st.success("Role posted to the job board.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # ⚙  SETTINGS
    # ─────────────────────────────────────────────
    elif "Settings" in rnav:
        st.markdown("""<div class="page-hdr">
          <div>
            <div class="breadcrumb">Recruiter → Settings</div>
            <h1>Platform <span>Settings</span></h1>
            <p class="page-hdr-sub">Configure platform behaviour & integrations</p>
          </div>
        </div>""", unsafe_allow_html=True)

        s1, s2 = st.columns(2, gap="large")
        with s1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            sec("Scoring Configuration")
            st.slider("Default Match Threshold (%)", 0, 100, 65, key="cfg_t")
            st.slider("Default Resume Weight (%)",   0, 100, 60, key="cfg_rw")
            st.number_input("Questions Per Interview",  3, 15, 5,  key="cfg_nq")
            st.selectbox("Question Bank", ["Technical General","Frontend","Backend","Data Science","Product","Design"])
            st.selectbox("Scoring Model", ["GPT-4 (Default)","GPT-3.5-Turbo","Claude 3 Sonnet","Gemini Pro"])
            st.toggle("Auto-shortlist above threshold", value=True)
            st.toggle("Require video interview",        value=False)
            if st.button("Save Scoring Config"): st.success("Configuration saved.")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="card">', unsafe_allow_html=True)
            sec("Notification Settings")
            st.toggle("Email on candidate shortlist",    value=True)
            st.toggle("Email on interview complete",     value=True)
            st.toggle("Weekly digest report",            value=False)
            st.toggle("Slack notifications",             value=False)
            st.toggle("Notify on rejection",             value=False)
            st.text_input("Recruiter Email", placeholder="recruiter@company.com")
            st.text_input("Slack Webhook URL", placeholder="https://hooks.slack.com/…")
            if st.button("Save Notifications"): st.success("Notifications saved.")
            st.markdown('</div>', unsafe_allow_html=True)

        with s2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            sec("Company Branding")
            st.text_input("Company Name",    placeholder="Acme Corp")
            st.text_input("Platform Title",  placeholder="Acme Talent Portal")
            st.text_input("Primary Color",   placeholder="#e8521a")
            st.selectbox("Timezone", ["Asia/Kolkata","UTC","US/Eastern","US/Pacific","Europe/London"])
            st.selectbox("Date Format", ["DD MMM YYYY","MM/DD/YYYY","YYYY-MM-DD"])
            if st.button("Save Branding"): st.success("Branding updated.")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="card">', unsafe_allow_html=True)
            sec("Data & Export")
            if st.button("Export All Candidates (CSV)"):
                csv = get_df().to_csv(index=False)
                st.download_button("⬇ Download CSV", csv, "apex_hire_export.csv","text/csv")
            if st.button("Export Analytics Report (JSON)"):
                report = {"total":total,"selected":selected,"pass_rate":sel_rate,"avg_interview":avg_i}
                st.download_button("⬇ Download JSON", json.dumps(report,indent=2), "report.json","application/json")
            divider()
            sec("Danger Zone")
            st.toggle("Enable data deletion", value=False, key="del_toggle")
            if st.session_state.get("del_toggle"):
                if st.button("⚠ Clear All Candidate Data"):
                    st.warning("This would clear all data in production mode.")
            st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  ██  CANDIDATE PORTAL  ██
# ══════════════════════════════════════════════════════════════
else:
    st.markdown("""<div class="page-hdr">
      <div>
        <div class="breadcrumb">Candidate Portal</div>
        <h1>Your <span>Assessment</span></h1>
        <p class="page-hdr-sub">AI-powered technical interview · personalised feedback</p>
      </div>
    </div>""", unsafe_allow_html=True)

    col_main, col_info = st.columns([3,2], gap="large")

    with col_info:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        sec("How The Assessment Works")
        steps = [
            ("1","Enter Your Name","Type the name your recruiter registered. It must match exactly."),
            ("2","Receive Questions","5 AI-curated questions tailored to your role. You have no time limit."),
            ("3","Answer Thoughtfully","Write detailed answers. Use the STAR method for behavioural questions."),
            ("4","Get AI Feedback","After each answer you receive detailed, scored feedback from the AI."),
            ("5","See Your Results","Final score is calculated from all 5 answers and saved to your profile."),
        ]
        for num, title, body in steps:
            st.markdown(f"""<div class="step-wrap">
              <div class="step-num">{num}</div>
              <div><div class="step-title">{title}</div><div class="step-body">{body}</div></div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        sec("Interview Tips")
        tips = [
            ("Be specific","Avoid vague answers. Use concrete examples from real projects."),
            ("Quantify impact","'Reduced latency by 40%' is stronger than 'improved performance'."),
            ("STAR Framework","Situation → Task → Action → Result works for most questions."),
            ("Think aloud","Walk through your reasoning — shows problem-solving process."),
            ("Be honest","If you don't know, say so. Then explain how you'd find out."),
        ]
        for t, b in tips:
            st.markdown(f"""<div style="padding:10px 0;border-bottom:1px solid var(--border);">
              <div style="font-family:'Clash Display',sans-serif;font-size:0.83rem;font-weight:600;color:var(--ink);margin-bottom:2px;">▲ {t}</div>
              <div style="font-size:0.77rem;color:rgba(10,10,10,0.5);line-height:1.5;">{b}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_main:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        sec("Candidate Login")
        clogin = st.text_input("Your Registered Full Name", placeholder="e.g. Priya Sharma", label_visibility="collapsed").strip()

        if clogin:
            # Lookup
            if DEMO:
                match = next((c for c in CANDIDATES if c[0].lower()==clogin.lower()), None)
                if match: cand = match
                else:     cand = (clogin, random.randint(65,92), None, "Engineering","Mid","N/A","N/A")
            else:
                raw = get_candidate(clogin)
                if raw is None:
                    st.error("🚫 Profile not found. Check your name matches exactly what your recruiter registered.")
                    st.stop()
                cand = (raw[0], raw[1], raw[2], "Engineering","Mid","N/A","N/A")

            name, rs, is_, dept, level, city, email = cand

            # Already done
            if is_ is not None:
                divider(accent=True)
                sec("Assessment Already Completed")
                d1,d2,d3 = st.columns(3)
                d1.metric("Interview Score", f"{is_}%")
                d2.metric("Resume Score",    f"{rs}%")
                d3.metric("Composite",       f"{round(rs*0.6+is_*0.4,1)}%")
                if is_>=60:
                    st.success("✓ You passed the technical threshold. Expect contact from our recruitment team within 2–3 business days.")
                else:
                    st.error("✕ You did not meet the threshold this time. We encourage you to re-apply in the next hiring cycle.")
                st.stop()

            # Greeting
            clr = av_color(name)
            st.markdown(f"""<div style="display:flex;align-items:center;gap:16px;
              padding:18px 20px;background:var(--paper-2);border-radius:var(--r-md);
              border:1.5px solid var(--border-md);margin:16px 0;">
              <div class="cand-av" style="background:{clr}18;color:{clr};border-color:{clr}55;
                width:50px;height:50px;font-size:1.1rem;">{ini(name)}</div>
              <div style="flex:1;">
                <div style="font-family:'Clash Display',sans-serif;font-size:1.05rem;font-weight:700;color:var(--ink);">
                  Welcome, {name.split()[0]} 👋</div>
                <div style="font-size:0.78rem;color:rgba(10,10,10,0.5);margin-top:3px;">
                  {dept} · {level} · Resume score: {rs}%</div>
              </div>
              <span class="pill p-a">Assessment Pending</span>
            </div>""", unsafe_allow_html=True)

            # Init questions
            if st.session_state.get("active_cand") != clogin:
                st.session_state.active_cand   = clogin
                with st.spinner("Personalising your assessment…"):
                    q_bank = QUESTIONS.get(dept, QUESTIONS["General"])
                    st.session_state.questions = random.sample(q_bank, min(5,len(q_bank)))
                    if DEMO: time.sleep(0.9)
                    else:    st.session_state.questions = generate_questions("Technical Interview")
                st.session_state.q_idx      = 0
                st.session_state.scores     = []
                st.session_state.evaluated  = False
                st.session_state.eval_report= None

            qs      = st.session_state.questions
            qi      = st.session_state.q_idx
            total_q = len(qs)

            # Progress
            pct = qi / total_q
            st.markdown(f"""<div style="display:flex;justify-content:space-between;margin-bottom:8px;">
              <span style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.12em;color:rgba(10,10,10,0.4);">Progress</span>
              <span style="font-family:'Fira Code',monospace;font-size:0.72rem;color:var(--accent);">{qi}/{total_q} complete</span>
            </div>""", unsafe_allow_html=True)
            st.progress(pct)

            if qi < total_q:
                q = qs[qi]
                st.markdown(f'<div style="font-family:\'Fira Code\',monospace;font-size:0.72rem;color:var(--accent);margin:18px 0 6px;letter-spacing:0.05em;">QUESTION {qi+1} OF {total_q}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="q-card">{q}</div>', unsafe_allow_html=True)

                ans = st.text_area("", key=f"a_{clogin}_{qi}", height=165,
                    placeholder="Write your detailed answer here. Be specific, structured, and use real examples where possible…",
                    label_visibility="collapsed")

                wc  = len(ans.split()) if ans.strip() else 0
                cc_ = len(ans)
                st.markdown(f'<div style="display:flex;justify-content:flex-end;gap:16px;margin-top:-8px;margin-bottom:8px;"><span style="font-family:\'Fira Code\',monospace;font-size:0.68rem;color:rgba(10,10,10,0.3);">{wc} words · {cc_} chars</span></div>', unsafe_allow_html=True)

                if not st.session_state.evaluated:
                    if st.button("Submit Answer ▲", use_container_width=True):
                        if ans.strip() and wc >= 5:
                            with st.spinner("AI evaluating your response…"):
                                if DEMO:
                                    s_raw = random.randint(5,10)
                                    qual  = ["basic","reasonable","competent","solid","strong","excellent"][min(s_raw-4,5)]
                                    ev = (f"**Score: {s_raw}/10**\n\n"
                                          f"Your answer shows **{qual}** understanding of the topic.\n\n"
                                          f"**Strengths:**\n"
                                          f"{'• Clear structure and logical flow.' if s_raw>=7 else '• You identified the core concept.'}\n"
                                          f"{'• Good use of a concrete example.' if s_raw>=8 else ''}\n\n"
                                          f"**Areas to improve:**\n"
                                          f"{'• Consider discussing edge cases and failure modes.' if s_raw<9 else '• Minor: could quantify impact more precisely.'}\n"
                                          f"{'• Deeper technical specifics would strengthen the answer.' if s_raw<7 else ''}\n\n"
                                          f"**Model answer hint:** Focus on the trade-offs involved and how you'd measure success. "
                                          f"Use the STAR format for cleaner delivery.")
                                    score = s_raw * 10
                                    time.sleep(1.2)
                                else:
                                    ev = evaluate_answer(q, ans)
                                    m  = re.search(r'(\d+)\s*out of\s*10', ev, re.IGNORECASE)
                                    score = int(m.group(1))*10 if m else 60
                            st.session_state.scores.append(score)
                            st.session_state.eval_report = ev
                            st.session_state.evaluated   = True
                            st.rerun()
                        else:
                            st.warning("Please write a meaningful answer before submitting (at least 5 words).")

                if st.session_state.evaluated:
                    sc_  = st.session_state.scores[-1]
                    sc_c = C["green"] if sc_>=70 else (C["amber"] if sc_>=50 else C["red"])

                    st.markdown(f"""<div style="display:flex;align-items:center;justify-content:space-between;
                      margin:16px 0 10px;padding:14px 18px;
                      background:var(--paper-2);border-radius:var(--r-md);
                      border:1.5px solid var(--border-md);">
                      <div>
                        <div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.12em;
                                    color:rgba(10,10,10,0.4);">Question {qi+1} Score</div>
                        <div style="font-family:'Fira Code',monospace;font-size:2rem;font-weight:700;
                                    color:{sc_c};line-height:1.2;">{sc_}%</div>
                      </div>
                      <div class="score-box" style="box-shadow:3px 3px 0 {sc_c};">
                        <div class="num">{sc_//10}/10</div>
                        <div class="lbl">Raw Score</div>
                      </div>
                    </div>""", unsafe_allow_html=True)

                    st.markdown(f'<div class="ev-card">{st.session_state.eval_report}</div>', unsafe_allow_html=True)
                    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

                    btn_label = "Next Question ▲" if qi < total_q-1 else "View Final Results ▲"
                    if st.button(btn_label, use_container_width=True):
                        st.session_state.q_idx     += 1
                        st.session_state.evaluated  = False
                        st.rerun()

            else:
                # ── COMPLETION ──────────────────────────────
                st.balloons()
                final = round(sum(st.session_state.scores)/len(st.session_state.scores), 1)
                if not DEMO: update_interview_score(clogin, final)

                divider(accent=True)
                sec("Assessment Complete — Final Results")

                fc1,fc2,fc3,fc4 = st.columns(4)
                fc1.metric("Final Score",       f"{final}%")
                fc2.metric("Questions Done",     total_q)
                fc3.metric("Highest Score",     f"{max(st.session_state.scores)}%")
                fc4.metric("Outcome",           "✓ Pass" if final>=60 else "✕ Fail")

                # Per-question chart
                f_end, ax_end = fig(8, 3)
                qbar_c = [C["green"] if s>=70 else (C["amber"] if s>=50 else C["red"]) for s in st.session_state.scores]
                ax_end.bar([f"Q{i+1}" for i in range(len(st.session_state.scores))],
                           st.session_state.scores, color=qbar_c, width=0.5, zorder=3)
                ax_end.axhline(60, color=C["ink"], lw=1.5, ls="--", alpha=0.4)
                ax_end.set_ylim(0, 112); ax_end.set_ylabel("Score %"); ax_end.yaxis.grid(True, zorder=0)
                for i,s in enumerate(st.session_state.scores):
                    ax_end.text(i, s+2, f"{s}%", ha='center', fontsize=11, fontweight='700', color=C["ink"])
                f_end.tight_layout(pad=1.5); st.pyplot(f_end)

                if final >= 60:
                    st.success(f"✓ **Congratulations, {name.split()[0]}!** You've passed the technical assessment with {final}%. Our recruitment team will reach out within 2–3 business days.")
                else:
                    st.error(f"✕ Your score of {final}% did not meet the threshold. We appreciate your effort — please consider reapplying in the next cycle.")

                # Reset
                for k in ["active_cand","eval_report"]: st.session_state[k]=None
                for k in ["questions","scores"]:        st.session_state[k]=[]
                st.session_state.evaluated=False; st.session_state.q_idx=0

        st.markdown('</div>', unsafe_allow_html=True)