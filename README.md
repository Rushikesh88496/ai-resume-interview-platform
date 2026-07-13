# ▲ Apex Hire — AI Talent Intelligence Platform

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-resume-interview-platform-b2evnrryqmbuyrz7fz3snk.streamlit.app/)

An AI-powered recruitment intelligence platform built with Streamlit. It screens resumes, matches candidates to job descriptions, conducts AI-driven technical interviews, evaluates answers, and provides actionable analytics — all from a single dashboard.

## Features

- **Resume Screening** — Upload PDF resumes, parse text, and match against job descriptions using semantic similarity and skill extraction (sentence-transformers + Groq LLM).
- **AI Skill Gap Analysis** — Identifies missing and strong skills by comparing resumes against job descriptions via Groq's Llama 3.1.
- **AI Interview Engine** — Generates 5 role-specific technical interview questions dynamically using LLM.
- **Answer Evaluation** — Candidate answers are scored out of 10 with strengths, weaknesses, and improvement suggestions via LLM.
- **Candidate Portal** — Candidates log in, answer personalised questions, receive instant AI feedback, and see their final composite score.
- **Command Center** — Real-time KPI dashboard: total screened, interviewed, selected, rejected, pending, pass rate, average scores.
- **Leaderboard** — Ranked candidate list by interview performance with visual score bars.
- **Candidate Profiles** — Deep-dive individual profiles with skill radars, recruiter notes, and email invite.
- **Analytics Suite** — Tabbed analytics: score distribution, 30-day trends, resume-vs-interview correlation, department breakdown, AI-generated recruitment insights.
- **Comparison Tool** — Head-to-head candidate comparison with composite scores, metric bars, skill radar charts, and AI recommendation.
- **Job Board** — Manage open roles with pipeline tracking per position (applicants, shortlisted, conversion rate).
- **Activity Feed** — Real-time live feed of candidate actions (screened, shortlisted, interviewed, offered, rejected).
- **Platform Settings** — Configurable scoring thresholds, question banks, notification preferences, company branding, and data export (CSV / JSON).
- **Demo Mode** — Fully simulated data for evaluation; runs without API keys or module dependencies.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Streamlit (Python) |
| **Backend** | Python — Streamlit orchestration, SQLite persistence |
| **Database** | SQLite (`hiring.db`) |
| **AI / LLM** | Groq API (`llama-3.1-8b-instant`) |
| **Embeddings** | `sentence-transformers` (`all-MiniLM-L6-v2`) |
| **PDF Parsing** | `pypdf` |
| **Data** | `pandas`, `numpy` |
| **Visualisation** | `matplotlib` |
| **Vector Similarity** | `scikit-learn` (cosine similarity) |
| **Other** | `python-dotenv` |

## Architecture

```
User (Browser)
    │
    ▼
┌──────────────────────────────────────────────────────┐
│                  Streamlit App (app.py)               │
│  ┌──────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ Recruiter│  │   Candidate  │  │   Demo Mode    │  │
│  │  Views   │  │    Portal    │  │  (Simulated)   │  │
│  └──────────┘  └──────────────┘  └────────────────┘  │
└──────────┬───────────────────────┬───────────────────┘
           │                       │
           ▼                       ▼
┌──────────────────┐    ┌──────────────────────┐
│    modules/      │    │    database.py        │
│ ┌──────────────┐ │    │  SQLite (hiring.db)   │
│ │resume_parser │ │    └──────────────────────┘
│ │job_matcher   │ │
│ │interview_    │ │
│ │engine        │ │
│ │evaluator     │ │
│ └──────────────┘ │
└───────┬──────────┘
        │
        ▼
┌────────────────┐
│   Groq API     │
│ (Llama 3.1-8B) │
└────────────────┘
```

The app operates in one of two modes:
- **Live mode** — uses `modules/` for resume parsing, JD matching, question generation, and answer evaluation. Requires a `GROQ_API_KEY`.
- **Demo mode** — falls back when modules fail to import; generates random scores and mock data for evaluation without external dependencies.

## Folder Structure

```
ai_interview_hackathon/
├── app.py                  # Main Streamlit application (1947 lines)
├── database.py             # SQLite CRUD operations for candidates
├── requirements.txt        # Python package dependencies
├── .env.example            # Environment variable template
├── .gitignore              # Git ignore rules
├── hiring.db               # SQLite database (auto-created)
├── assets/
│   └── logo.png            # Application logo
├── docs/
│   ├── architecture.md     # Architecture documentation
│   ├── api.md              # API documentation
│   └── database.md         # Database schema documentation
├── modules/
│   ├── resume_parser.py    # PDF resume text extraction
│   ├── job_matcher.py      # JD matching & skill gap analysis
│   ├── interview_engine.py # AI question generation
│   └── evaluator.py        # Answer evaluation & scoring
└── __pycache__/            # Python cache (ignored by git)
```

## Installation

### Prerequisites

- Python 3.10+
- pip
- (Optional) Groq API key for live AI features

### Clone

```bash
git clone https://github.com/YOUR_USERNAME/ai-resume-interview-platform.git
cd ai-resume-interview-platform
```

### Backend (all-in-one)

```bash
# Create virtual environment
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Setup Environment Variables

```bash
cp .env.example .env
# Edit .env and add your Groq API key
```

### Run

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`.

### Demo Mode

To run without any API keys, simply start the app. If the module imports fail, the app falls back to Demo Mode with simulated data and random scores.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Yes (live mode) | API key for Groq LLM access |

## API Overview

The application does not expose a REST API. All interactions happen through the Streamlit UI.

### Internal Module APIs

| Module | Function | Purpose |
|--------|----------|---------|
| `modules/resume_parser.py` | `extract_resume_text(uploaded_file)` | Extracts text from PDF resumes |
| `modules/job_matcher.py` | `calculate_match(resume_text, job_description)` | Returns match score (0-95%) using semantic + skill weighting |
| `modules/job_matcher.py` | `skill_gap_analysis(resume_text, job_description)` | Returns LLM-generated gap analysis |
| `modules/interview_engine.py` | `generate_questions(job_description)` | Returns 5 generated interview questions |
| `modules/evaluator.py` | `evaluate_answer(question, answer)` | Returns scored evaluation (X/10) |
| `database.py` | `init_db()`, `add_candidate()`, `update_interview_score()`, `get_candidate()`, `get_all_candidates()` | SQLite database operations |

### Job Matcher Scoring Algorithm (`calculate_match`)

```
Final Score = (Semantic Similarity × 0.2)
            + (Core Skill Match × 0.6)
            + (General Skill Match × 0.2)
```

- Internship roles receive a 1.15× multiplier.
- If core skill match ≥ 80%, the minimum final score is 75%.
- Result is clamped to a maximum of 95%.

## Authentication

The platform has **no external authentication provider**. Access control is role-based within the UI:

1. **Sidebar Role Toggle** — Users switch between "Recruiter" and "Candidate" using a radio button.
2. **Candidate Login** — Candidates enter their registered full name. The app looks up the name in the SQLite database. If found, the candidate proceeds to their assessment. If the name is not found, an error is shown.
3. **No Passwords** — There are no user accounts, passwords, or OAuth flows. This is suitable for internal / pilot-stage recruitment tools.

## User Roles

### Recruiter

Full access to all workspace views:

- Command Center (KPIs, funnel, activity feed)
- Resume Screening (upload, match, analyse)
- Candidate Profiles (browse, filter, add notes, send invites)
- Leaderboard (ranked by interview score)
- Analytics Suite (trends, correlation, department breakdown, AI insights)
- Comparison Tool (head-to-head candidate comparison)
- Job Board (manage roles, post new positions)
- Settings (scoring config, notifications, branding, data export)

### Candidate

Limited to the Candidate Portal:

- View assessment instructions and interview tips
- Enter registered name to log in
- Answer 5 AI-generated questions with instant feedback
- View final score and pass/fail outcome

## Screenshots

> *Screenshots will be added after deployment. The UI features a "Warm Brutalist Premium" design with a dark sidebar, warm paper backgrounds, and orange (#e8521a) accent.*

## Future Improvements

- [ ] **User Authentication** — Add OAuth (Google, GitHub) or JWT-based login for recruiters and candidates.
- [ ] **Email Notifications** — Integrate SendGrid / Resend for automated candidate invite and status emails.
- [ ] **Database Migration** — Replace SQLite with PostgreSQL for production scalability.
- [ ] **Video Interviews** — Integrate WebRTC or a third-party video SDK for live interviews.
- [ ] **Resume Parsing Enhancement** — Use LLM-based structured extraction (JSON schema) instead of keyword matching.
- [ ] **Multi-language Support** — Add i18n for international recruitment.
- [ ] **Bulk CSV Upload** — Allow recruiters to upload candidate lists in bulk.
- [ ] **Calendar Integration** — Google Calendar / Calendly for interview scheduling.
- [ ] **CI/CD Pipeline** — GitHub Actions for linting, testing, and deployment.
- [ ] **Docker Deployment** — Containerize the application for one-command deployments.

## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m 'Add amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Author

Built with Python, Streamlit, and Groq AI.
