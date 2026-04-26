"""
GrievAI Production Database — PostgreSQL
Railway.app pe deploy hoga
"""
import os
import psycopg2
import psycopg2.extras
from datetime import datetime

DATABASE_URL = os.environ.get('DATABASE_URL', '')

# Railway sometimes gives postgres:// but psycopg2 needs postgresql://
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)


def get_conn():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


def init_db():
    conn = get_conn()
    cur  = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS otp_verifications (
            id          SERIAL PRIMARY KEY,
            mobile      TEXT NOT NULL,
            otp         TEXT NOT NULL,
            verified    BOOLEAN DEFAULT FALSE,
            created_at  TIMESTAMP DEFAULT NOW(),
            expires_at  TIMESTAMP NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS citizens (
            id           SERIAL PRIMARY KEY,
            mobile       TEXT UNIQUE NOT NULL,
            name         TEXT,
            verified     BOOLEAN DEFAULT FALSE,
            created_at   TIMESTAMP DEFAULT NOW()
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id            SERIAL PRIMARY KEY,
            complaint_id  TEXT UNIQUE NOT NULL,
            citizen_name  TEXT NOT NULL,
            mobile        TEXT NOT NULL,
            mobile_verified BOOLEAN DEFAULT FALSE,
            district      TEXT,
            area          TEXT,
            language      TEXT DEFAULT 'en',
            raw_text      TEXT NOT NULL,
            department    TEXT,
            category      TEXT,
            priority      TEXT DEFAULT 'medium',
            status        TEXT DEFAULT 'open',
            ai_confidence REAL DEFAULT 0.0,
            ai_summary    TEXT,
            eta_days      TEXT,
            officer_name  TEXT,
            dept_full     TEXT,
            created_at    TIMESTAMP DEFAULT NOW(),
            updated_at    TIMESTAMP DEFAULT NOW()
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS timeline_events (
            id           SERIAL PRIMARY KEY,
            complaint_id TEXT NOT NULL REFERENCES complaints(complaint_id),
            event_title  TEXT NOT NULL,
            event_desc   TEXT,
            event_time   TIMESTAMP DEFAULT NOW(),
            status       TEXT DEFAULT 'done'
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            id              SERIAL PRIMARY KEY,
            name            TEXT NOT NULL,
            short_name      TEXT NOT NULL,
            officer_name    TEXT,
            contact         TEXT,
            complaint_count INTEGER DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS analytics_log (
            id          SERIAL PRIMARY KEY,
            event_type  TEXT NOT NULL,
            department  TEXT,
            priority    TEXT,
            language    TEXT,
            logged_at   TIMESTAMP DEFAULT NOW()
        )
    """)

    # Indexes
    cur.execute("CREATE INDEX IF NOT EXISTS idx_complaints_dept   ON complaints(department)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_complaints_status ON complaints(status)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_complaints_mobile ON complaints(mobile)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_otp_mobile        ON otp_verifications(mobile)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_timeline_cid      ON timeline_events(complaint_id)")

    # Seed departments if empty
    cur.execute("SELECT COUNT(*) FROM departments")
    if cur.fetchone()[0] == 0:
        cur.executemany("""
            INSERT INTO departments(name, short_name, officer_name, contact, complaint_count)
            VALUES (%s,%s,%s,%s,%s)
        """, [
            ("Water Supply",      "water",       "Er. Suresh Patel",       "+91-731-2700100", 0),
            ("Roads & PWD",       "roads",       "EE Rakesh Dubey",        "+91-731-2700200", 0),
            ("Electricity",       "electricity", "Er. Anil Sharma",        "+91-731-2700300", 0),
            ("Sanitation",        "sanitation",  "Sanitation Inspector",   "+91-731-2700400", 0),
            ("Public Services",   "services",    "Ward Officer",           "+91-731-2700500", 0),
            ("Healthcare",        "healthcare",  "CMO Dr. Priya Sharma",   "+91-731-2700600", 0),
        ])

    conn.commit()
    cur.close()
    conn.close()
    print("[DB] PostgreSQL initialized successfully.")


def row_to_dict(cur, row):
    if row is None:
        return None
    cols = [desc[0] for desc in cur.description]
    d = {}
    for k, v in zip(cols, row):
        if isinstance(v, datetime):
            d[k] = v.isoformat()
        else:
            d[k] = v
    return d


def rows_to_list(cur, rows):
    return [row_to_dict(cur, r) for r in rows]
