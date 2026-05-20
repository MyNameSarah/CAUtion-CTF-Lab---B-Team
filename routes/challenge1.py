from flask import Blueprint, render_template, request, redirect, session
import sqlite3

challenge1_bp = Blueprint('challenge1', __name__)

DATABASE = "database.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Challenge 1 메인 페이지
@challenge1_bp.route("/challenge1")
def challenge1():

    if "user" not in session:
        return redirect("/login")

    conn = get_db()

    memos = conn.execute(
        "SELECT * FROM memos WHERE user_id=?",
        (session["user_id"],)
    ).fetchall()

    conn.close()

    return render_template(
        "challenge1.html",
        memos=memos
    )


# 취약한 메모 조회
@challenge1_bp.route("/memo")
def memo():

    if "user" not in session:
        return redirect("/login")

    memo_id = request.args.get("id")

    conn = get_db()

    # 의도적 IDOR 취약점
    memo = conn.execute(
        "SELECT * FROM memos WHERE id=?",
        (memo_id,)
    ).fetchone()

    conn.close()

    if not memo:
        return "Memo Not Found"

    return render_template(
        "memo.html",
        memo=memo
    )