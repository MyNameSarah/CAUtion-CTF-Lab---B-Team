from flask import Blueprint, render_template, request, redirect
from flask import session, send_from_directory
import sqlite3

challenge4_bp = Blueprint('challenge4', __name__)

DATABASE = "database.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# 문제 페이지
@challenge4_bp.route("/challenge4")
def challenge4():

    if "user" not in session:
        return redirect("/login")

    conn = get_db()

    files = conn.execute(
        "SELECT * FROM files WHERE user_id=?",
        (session["user_id"],)
    ).fetchall()

    conn.close()

    return render_template(
        "challenge4.html",
        files=files
    )


# 취약한 다운로드
@challenge4_bp.route("/download")
def download():

    if "user" not in session:
        return redirect("/login")

    file_id = request.args.get("file")

    conn = get_db()

    file = conn.execute(
        "SELECT * FROM files WHERE id=?",
        (file_id,)
    ).fetchone()

    conn.close()

    if not file:
        return "File Not Found"

    # 의도적인 IDOR 취약점
    return send_from_directory(
        "static/uploads",
        file["filename"],
        as_attachment=True
    )