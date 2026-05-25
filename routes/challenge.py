from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import session

import sqlite3

challenge_bp = Blueprint('challenge', __name__)

DATABASE = "database.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# 문제 페이지
@challenge_bp.route("/challenge")
def challenge():

    if "user" not in session:
        return redirect("/login")

    return render_template("challenge.html")


# Blind check API
@challenge_bp.route("/api/share/check")
def check_share():

    if "user" not in session:
        return "Unauthorized", 401

    key = request.args.get("key")

    conn = get_db()

    note = conn.execute(
        "SELECT * FROM share_notes WHERE note_key=?",
        (key,)
    ).fetchone()

    conn.close()

    if note:
        return "", 200

    return "", 404


@challenge_bp.route("/share/<note_key>")
def share(note_key):
    if "user" not in session:
        return redirect("/login")

    conn = get_db()

    note = conn.execute(
        "SELECT * FROM share_notes WHERE note_key=?",
        (note_key,)
    ).fetchone()

    conn.close()

    if not note:
        return "Shared note not found"

    return render_template("shared_note.html", note=note)