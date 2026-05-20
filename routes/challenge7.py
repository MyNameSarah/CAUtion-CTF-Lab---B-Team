from flask import Blueprint, jsonify
from flask import render_template, request
from flask import redirect, session
import sqlite3

challenge7_bp = Blueprint('challenge7', __name__)

DATABASE = "database.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# 문제 페이지
@challenge7_bp.route("/challenge7")
def challenge7():

    if "user" not in session:
        return redirect("/login")

    return render_template("challenge7.html")


# Blind API
@challenge7_bp.route("/api/note/check")
def check_note():

    if "user" not in session:
        return jsonify({"error": "login required"}), 401

    note_id = request.args.get("id")

    conn = get_db()

    note = conn.execute(
        "SELECT * FROM blind_notes WHERE id=?",
        (note_id,)
    ).fetchone()

    conn.close()

    if note:
        return "", 200
    
    return "", 404

@challenge7_bp.route("/api/note/view")
def view_note():

    if "user" not in session:
        return "Unauthorized", 401

    note_id = request.args.get("id")

    conn = get_db()

    note = conn.execute(
        "SELECT * FROM blind_notes WHERE id=?",
        (note_id,)
    ).fetchone()

    conn.close()

    if not note:
        return "Not Found", 404

    # 의도적 취약점
    return note["secret"]