# Architecture

## Overview

Apex Hire is a monolithic Python application built with Streamlit. It serves as both the frontend and backend, providing a single-page web application with role-based views for recruiters and candidates.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Streamlit Runtime                            │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    app.py (Orchestrator)                     │   │
│  │  ┌───────────────────────────────────────────────────────┐  │   │
│  │  │  Session State Management                              │  │   │
│  │  │  - questions, scores, q_idx, active_cand, notes       │  │   │
│  │  │  - screen_hist, compare_list, jd_store, config vars   │  │   │
│  │  └───────────────────────────────────────────────────────┘  │   │
│  │                                                              │   │
│  │  ┌─────────────┐    ┌──────────────────┐    ┌────────────┐  │   │
│  │  │ CSS / Theme │    │  Component       │    │ Matplotlib │  │   │
│  │  │ (Warm       │    │  Helpers         │    │ Charts     │  │   │
│  │  │  Brutalist) │    │  (skbar, pill,   │    │ (funnel,   │  │   │
│  │  │             │    │   tags, sec, etc) │    │  hist, pie)│  │   │
│  │  └─────────────┘    └──────────────────┘    └────────────┘  │   │
│  │                                                              │   │
│  │  ┌──────────────────────────────────────────────────────┐   │   │
│  │  │  View Router (sidebar radio selection)               │   │   │
│  │  │                                                      │   │   │
│  │  │  Recruiter Views:  ┌────────────┐  Candidate Views: │   │   │
│  │  │  - Command Center   │  Role      │  - Login Screen   │   │   │
│  │  │  - Resume Screening │  Toggle    │  - Assessment     │   │   │
│  │  │  - Candidate        │ (sidebar)  │  - Results        │   │   │
│  │  │    Profiles         └────────────┘                   │   │   │
│  │  │  - Leaderboard                                       │   │   │
│  │  │  - Analytics Suite                                   │   │   │
│  │  │  - Comparison Tool                                   │   │   │
│  │  │  - Job Board                                         │   │   │
│  │  │  - Settings                                          │   │   │
│  │  └──────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
┌─────────────────────┐ ┌────────────┐ ┌──────────────┐
│    modules/         │ │ database   │ │   Groq API   │
│                     │ │ .py        │ │  (External)  │
│ resume_parser.py    │ │            │ │              │
│ job_matcher.py      │ │ SQLite     │ │ llama-3.1-   │
│ interview_engine.py │ │ hiring.db  │ │ 8b-instant   │
│ evaluator.py        │ │            │ │              │
└─────────────────────┘ └────────────┘ └──────────────┘
```

## Mode Selection

The app determines its operating mode on startup:

```python
try:
    from modules.resume_parser import extract_resume_text
    from modules.job_matcher import calculate_match, skill_gap_analysis
    from modules.interview_engine import generate_questions
    from modules.evaluator import evaluate_answer
    from database import init_db, add_candidate, update_interview_score,
                         get_candidate, get_all_candidates
    init_db()
    DEMO = False
except Exception:
    DEMO = True
```

- **Live Mode** — All modules imported successfully. Uses real AI inference.
- **Demo Mode** — Module imports failed (e.g., missing GROQ_API_KEY). Falls back to random/mock data with simulated delays.

## Data Flow

### Resume Screening Flow

```
1. User uploads PDF → pypdf extracts text (resume_parser.py)
2. User pastes JD → stored in session_state.jd_store
3. Click "Analyze Profile"
   └─▶ calculate_match(resume_text, jd)
       ├─ Semantic similarity (sentence-transformers, cosine)
       ├─ Skill extraction (keyword matching)
       ├─ Core skill weighting (6 key skills)
       ├─ Weighted final score
       └─ Returns 0-95%
   └─▶ skill_gap_analysis(resume_text, jd)
       └─ LLM prompt → returns markdown analysis
4. Results displayed: score, gap analysis, skills bars, tags
5. If score ≥ threshold → candidate saved to SQLite
```

### Interview Flow

```
1. Candidate enters name → looked up in SQLite
2. If not found → error; if already interviewed → show results
3. 5 questions generated (random sample from hardcoded bank, or LLM)
4. For each question:
   ├─ Candidate writes answer (min 5 words)
   ├─ Click "Submit Answer"
   └─▶ evaluate_answer(question, answer)
       └─ LLM prompt → score X/10 + feedback
   ├─ Score saved to session state
   └─ "Next Question" or "View Final Results"
5. Final score = average of all question scores
6. Result saved to SQLite via update_interview_score()
```

### Analytics Flow

```
1. Query all candidates from SQLite (get_all_candidates)
2. Compute KPIs (total, done, selected, rejected, pending, rates)
3. Render matplotlib charts:
   ├─ Hiring funnel (horizontal bar)
   ├─ Score distribution (histogram)
   ├─ Department breakdown (horizontal bar)
   ├─ 30-day trends (line chart, simulated)
   ├─ Correlation scatter (resume vs interview)
   └─ Pie chart (selection split)
4. AI Insights generated from computed statistics
```

## Theme / Design System

The UI follows a "Warm Brutalist Premium" design:

- **Colors**: Dark ink (#0a0a0a) sidebar, warm paper (#f5f0e8) backgrounds, orange accent (#e8521a)
- **Typography**: Clash Display (headings), Cabinet Grotesk (body), Fira Code (monospace)
- **Components**: Cards, pills, tags, skill bars, activity feed rows, timeline steps, insight boxes, leaderboard rows, comparison bars
- **Animations**: fadeUp for cards, slideIn for candidate cards, pulse for live indicator, hover effects on metrics and buttons

## State Management

All UI state is stored in `st.session_state`:

| Key | Type | Purpose |
|-----|------|---------|
| `questions` | list | Current interview questions |
| `q_idx` | int | Current question index |
| `scores` | list | Per-question scores |
| `eval_report` | str | Last evaluation feedback |
| `evaluated` | bool | Whether current question was evaluated |
| `active_cand` | str | Currently logged-in candidate name |
| `notes` | dict | Recruiter notes per candidate |
| `screen_hist` | list | Resume screening history for session |
| `compare_list` | list | Candidates added to comparison |
| `jd_store` | str | Stored job description text |
| `threshold` | int | Match threshold percentage |
| `rw` | int | Resume weight percentage |
