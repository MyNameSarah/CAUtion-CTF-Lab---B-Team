from flask import Blueprint, render_template, request, redirect, session
import sqlite3

challenge3_bp = Blueprint('challenge3', __name__)

DATABASE = "database.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# 문제 메인 페이지
@challenge3_bp.route("/challenge3")
def challenge3():

    if "user" not in session:
        return redirect("/login")

    conn = get_db()

    user = conn.execute(
        "SELECT * FROM users WHERE id=?",
        (session["user_id"],)
    ).fetchone()

    conn.close()

    return render_template(
        "challenge3.html",
        user=user
    )


# 프로필 수정
@challenge3_bp.route("/profile/update", methods=["POST"])
def update_profile():

    if "user" not in session:
        return redirect("/login")

    user_id = request.form["user_id"]
    email = request.form["email"]

    conn = get_db()

    # 의도적인 IDOR 취약점
    conn.execute(
        "UPDATE users SET email=? WHERE id=?",
        (email, user_id)
    )

    conn.commit()

    updated_user = conn.execute(
        "SELECT * FROM users WHERE id=?",
        (user_id,)
    ).fetchone()

    conn.close()

    return render_template(
        "profile.html",
        user=updated_user
    )