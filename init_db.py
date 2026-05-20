import sqlite3
import os

# 기존 DB 삭제
if os.path.exists("database.db"):
    os.remove("database.db")

conn = sqlite3.connect("database.db")

cur = conn.cursor()

cur.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT,
    role TEXT,
    email TEXT
)
""")

cur.execute("""
CREATE TABLE memos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    title TEXT,
    content TEXT
)
""")

cur.execute("""
CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER,
    user_id INTEGER,
    comment TEXT
)
""")

# 일반 사용자
cur.execute(
    "INSERT INTO users (username, password, role, email) VALUES (?, ?, ?, ?)",
    ("guest", "guest123", "user", "guest@example.com")
)

# 관리자
cur.execute(
    "INSERT INTO users (username, password, role, email) VALUES (?, ?, ?, ?)",
    ("admin", "adminpass", "admin", "admin@example.com")
)

# 매니저
cur.execute(
    "INSERT INTO users (username, password, role, email) VALUES (?, ?, ?, ?)",
    ("manager", "manager123", "manager", "manager@test.com")
)

# guest 메모
cur.execute("""
INSERT INTO memos (user_id, title, content)
VALUES (1, 'My Memo', 'Hello Guest User')
""")

cur.execute("""
INSERT INTO memos (user_id, title, content)
VALUES (1, 'Shopping List', 'apple, banana')
""")

cur.execute("""
INSERT INTO memos (user_id, title, content)
VALUES (1, 'Work Memo', 'Finish Flask project')
""")

# admin 메모 (FLAG 포함)
cur.execute("""
INSERT INTO memos (user_id, title, content)
VALUES (
    2,
    'Admin Secret',
    'FLAG{IDOR_Vulnerability_Found}'
)
""")

cur.execute("""
INSERT INTO memos (user_id, title, content)
VALUES (
    2,
    'Admin Secret',
    'FLAG{basic_idor_success}'
)
""")

# challenge2
cur.execute("""
INSERT INTO comments (post_id, user_id, comment)
VALUES (
    1,
    1,
    'Nice post'
)
""")

cur.execute("""
INSERT INTO comments (post_id, user_id, comment)
VALUES (
    1,
    1,
    'Flask is interesting'
)
""")

cur.execute("""
INSERT INTO comments (post_id, user_id, comment)
VALUES (
    999,
    2,
    'FLAG{api_idor_success}'
)
""")

# challenge4
cur.execute("""
CREATE TABLE files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    filename TEXT
)
""")

cur.execute("""
INSERT INTO files (user_id, filename)
VALUES (1, 'guest_note.txt')
""")

cur.execute("""
INSERT INTO files (user_id, filename)
VALUES (1, 'work.txt')
""")

cur.execute("""
INSERT INTO files (user_id, filename)
VALUES (2, 'admin_secret.txt')
""")

# challenge5
cur.execute("""
CREATE TABLE requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id TEXT,
    user_id INTEGER,
    request_name TEXT,
    approved INTEGER
)
""")

cur.execute("""
INSERT INTO requests (
    ticket_id,
    user_id,
    request_name,
    approved
)
VALUES (
    'REQ-1A7B22',
    1,
    'Access Internal Dashboard',
    0
)
""")

cur.execute("""
INSERT INTO requests (
    ticket_id,
    user_id,
    request_name,
    approved
)
VALUES (
    'REQ-8F2A91',
    2,
    'Top Secret Approval',
    0
)
""")

# challenge6
cur.execute("""
CREATE TABLE share_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    note_key TEXT,
    content TEXT
)
""")

cur.execute("""
INSERT INTO share_notes (user_id, note_key, content)
VALUES (
    1,
    'Z3Vlc3Rfbm90ZQ==',
    'guest shared memo'
)
""")

cur.execute("""
INSERT INTO share_notes (user_id, note_key, content)
VALUES (
    2,
    'YWRtaW5fbm90ZQ==',
    'FLAG{uuid_predict_idor_success}'
)
""")

# challenge7
cur.execute("""
CREATE TABLE blind_notes (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    secret TEXT
)
""")

cur.execute("""
INSERT INTO blind_notes (id, user_id, secret)
VALUES (
    1,
    1,
    'normal note'
)
""")

cur.execute("""
INSERT INTO blind_notes (id, user_id, secret)
VALUES (
    782,
    2,
    'FLAG{blind_idor_success}'
)
""")
conn.commit()
conn.close()

print("Database Initialized")