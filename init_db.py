import sqlite3
import os


if os.path.exists("database.db"):
    os.remove("database.db")

conn = sqlite3.connect("database.db")
cur = conn.cursor()

# users
cur.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT,
    role TEXT
)
""")

# share notes
cur.execute("""
CREATE TABLE share_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    note_key TEXT,
    content TEXT
)
""")

cur.execute(
    "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
    ("guest", "guest123", "user")
)

cur.execute(
    "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
    ("admin", "admin123", "admin")
)

cur.execute("""
INSERT INTO share_notes (
    user_id,
    note_key,
    content
)
VALUES (
    1,
    'Z3Vlc3Rfbm90ZQ==',
    'guest shared memo'
)
""")

cur.execute("""
INSERT INTO share_notes (
    user_id,
    note_key,
    content
)
VALUES (
    2,
    'aW50ZXJuYWxfYmFja3Vw',
    'FLAG{c7f_2nc0d3d_1D0r_3uCces2}'
)
""")

cur.execute("""
INSERT INTO share_notes (
    user_id,
    note_key,
    content
)
VALUES (
    2,
    'YWRtaW5fbm90ZQ==',
    'No useful information was found in this object.'
)
""")

cur.execute("""
INSERT INTO share_notes (
    user_id,
    note_key,
    content
)
VALUES (
    2,
    'c2VjcmV0X2FyY2hpdmU=',
    'No useful information was found in this object.'
)
""")

cur.execute("""
INSERT INTO share_notes (
    user_id,
    note_key,
    content
)
VALUES (
    2,
    'aW50ZXJuYWxfbm90ZXM=',
    'No useful information was found in this object.'
)
""")

cur.execute("""
INSERT INTO share_notes (
    user_id,
    note_key,
    content
)
VALUES (
    2,
    'YmFja3VwX29sZA==',
    'No useful information was found in this object.'
)
""")

cur.execute("""
INSERT INTO share_notes (
    user_id,
    note_key,
    content
)
VALUES (
    2,
    'cHJpdmF0ZV9kb2Nz',
    'No useful information was found in this object.'
)
""")

cur.execute("""
INSERT INTO share_notes (
    user_id,
    note_key,
    content
)
VALUES (
    2,
    'cHJvZF9iYWNrdXA=',
    'No useful information was found in this object.'
)
""")

conn.commit()
conn.close()