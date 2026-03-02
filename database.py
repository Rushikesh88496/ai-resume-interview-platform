import sqlite3

DB_NAME = "hiring.db"


# ---------------- INITIALIZE DATABASE ----------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            name TEXT PRIMARY KEY,
            resume_score REAL,
            interview_score REAL
        )
    """)

    conn.commit()
    conn.close()


# ---------------- ADD CANDIDATE (SAFE INSERT) ----------------
def add_candidate(name, resume_score):
    name = name.strip()

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Check if candidate exists
    c.execute("SELECT name FROM candidates WHERE LOWER(name) = LOWER(?)", (name,))
    existing = c.fetchone()

    if existing is None:
        # Insert new candidate
        c.execute("""
            INSERT INTO candidates (name, resume_score, interview_score)
            VALUES (?, ?, NULL)
        """, (name, float(resume_score)))
    else:
        # Update resume score only (keep interview_score intact)
        c.execute("""
            UPDATE candidates
            SET resume_score = ?
            WHERE LOWER(name) = LOWER(?)
        """, (float(resume_score), name))

    conn.commit()
    conn.close()


# ---------------- UPDATE INTERVIEW SCORE ----------------
def update_interview_score(name, interview_score):
    name = name.strip()

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        UPDATE candidates
        SET interview_score = ?
        WHERE LOWER(name) = LOWER(?)
    """, (float(interview_score), name))

    conn.commit()
    conn.close()


# ---------------- GET SINGLE CANDIDATE ----------------
def get_candidate(name):
    name = name.strip()

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        SELECT name, resume_score, interview_score
        FROM candidates
        WHERE LOWER(name) = LOWER(?)
    """, (name,))

    data = c.fetchone()
    conn.close()

    return data


# ---------------- GET ALL CANDIDATES ----------------
def get_all_candidates():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        SELECT name, resume_score, interview_score
        FROM candidates
    """)

    data = c.fetchall()
    conn.close()

    return data