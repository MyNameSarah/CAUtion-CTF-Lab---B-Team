from flask import Blueprint, render_template
from flask import request, redirect, session
import sqlite3

challenge6_bp = Blueprint('challenge6', __name__)

DATABASE = "database.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# 문제 페이지
@challenge6_bp.route("/challenge6")
def challenge6():

    if "user" not in session:
        return redirect("/login")

    return render_template("challenge6.html")


# 공유 노트 조회
@challenge6_bp.route("/share/<note_key>")
def share(note_key):

    if "user" not in session:
        return redirect("/login")

    conn = get_db()

    # note_key만 신뢰
    note = conn.execute(
        "SELECT * FROM share_notes WHERE note_key=?",
        (note_key,)
    ).fetchone()

    conn.close()

    if not note:
        return "Shared note not found"

    return render_template(
        "shared_note.html",
        note=note
    )