# API Documentation

The application does not expose a REST or HTTP API. All functionality is accessed through the Streamlit UI.

However, the following internal Python APIs (module functions) serve as the application's programmable interface.

## Module: `modules/resume_parser.py`

### `extract_resume_text(uploaded_file) -> str`

Parses a PDF resume file and extracts its text content.

- **Parameters**:
  - `uploaded_file`: A file-like object (typically `st.file_uploader` output)
- **Returns**: Raw text string extracted from all PDF pages
- **Dependencies**: `pypdf.PdfReader`
- **Example**:
  ```python
  from modules.resume_parser import extract_resume_text
  text = extract_resume_text(uploaded_file)
  ```

---

## Module: `modules/job_matcher.py`

### `calculate_match(resume_text, job_description) -> float`

Computes a match score between a resume and a job description using a weighted combination of semantic similarity, core skill matching, and general skill matching.

**Scoring Formula:**

```
semantic_score = cosine_similarity(embed(resume), embed(jd)) × 100
core_score     = (core_matched_skills / core_required_skills) × 100
general_score  = (matched_skills / jd_skills) × 100
final_score    = semantic_score × 0.2 + core_score × 0.6 + general_score × 0.2
```

- **Adjustments**:
  - Internship roles: `final_score ×= 1.15`
  - If core_score ≥ 80: `final_score = max(final_score, 75)`
  - Clamped to max 95%
- **Parameters**: Both are plain text strings
- **Returns**: Float 0.0 – 95.0
- **Dependencies**: `sentence-transformers`, `scikit-learn`, `Groq`

### `skill_gap_analysis(resume_text, job_description) -> str`

Uses Groq LLM to generate a detailed skill gap analysis.

- **Parameters**: Both are plain text strings
- **Returns**: Markdown-formatted string containing:
  - Missing Skills (important gaps)
  - Strong Skills (matching skills)
  - Overall Fit Summary
- **LLM Model**: `llama-3.1-8b-instant` (temperature 0.3)
- **Example**:
  ```python
  from modules.job_matcher import calculate_match, skill_gap_analysis
  score = calculate_match(resume_text, jd_text)
  analysis = skill_gap_analysis(resume_text, jd_text)
  ```

### `extract_skills(text) -> set`

Internal helper. Extracts skills from text using keyword matching against a predefined list of ~30 skill terms (Python, SQL, ML, AWS, Docker, etc.).

---

## Module: `modules/interview_engine.py`

### `generate_questions(job_description) -> list[str]`

Generates 5 technical interview questions using Groq LLM based on a job description.

- **Parameters**: `job_description` — plain text
- **Returns**: List of exactly 5 question strings
- **LLM Model**: `llama-3.1-8b-instant` (temperature 0.3)
- **Prompt**: Asks for valid JSON `{"questions": [...]}` and strips markdown wrappers
- **Error Handling**: Returns empty list `[]` on parse failure
- **Example**:
  ```python
  from modules.interview_engine import generate_questions
  questions = generate_questions("Senior ML Engineer with NLP experience")
  ```

---

## Module: `modules/evaluator.py`

### `evaluate_answer(question, answer) -> str`

Evaluates a candidate's answer to an interview question using Groq LLM.

- **Parameters**:
  - `question`: The interview question text
  - `answer`: The candidate's written response
- **Returns**: Markdown-formatted evaluation containing:
  - Score: X out of 10
  - Strengths
  - Weaknesses
  - Improvement Suggestions
- **LLM Model**: `llama-3.1-8b-instant` (temperature 0.3)
- **Example**:
  ```python
  from modules.evaluator import evaluate_answer
  feedback = evaluate_answer("Explain the bias-variance tradeoff", "The bias-variance tradeoff is...")
  ```

---

## Module: `database.py`

SQLite database operations. Database file: `hiring.db`.

### `init_db() -> None`

Creates the `candidates` table if it does not exist.

### `add_candidate(name: str, resume_score: float) -> None`

Inserts a new candidate or updates the resume score of an existing one.

- Case-insensitive name matching
- Interview score is preserved on update (not overwritten)

### `update_interview_score(name: str, interview_score: float) -> None`

Updates the interview score for an existing candidate.

### `get_candidate(name: str) -> tuple | None`

Returns `(name, resume_score, interview_score)` or `None`.

### `get_all_candidates() -> list[tuple]`

Returns all rows as `[(name, resume_score, interview_score), ...]`.

---

## Internal Scoring Weights (app.py)

The recruiter can configure two key scoring parameters:

| Parameter | Default | Range | Purpose |
|-----------|---------|-------|---------|
| Match Threshold | 65% | 0–100 | Minimum resume-JD match score to pass screening |
| Resume Weight | 60% | 0–100 | Weight of resume score in the composite (interview = 100% - resume weight) |

### Composite Score Formula

```
composite = resume_score × (resume_weight / 100) + interview_score × ((100 - resume_weight) / 100)
```

### Interview Pass/Fail Threshold

A candidate passes the interview if their average score across all questions is **≥ 60%**.
