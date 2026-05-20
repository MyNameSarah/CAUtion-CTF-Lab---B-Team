from flask import Blueprint, jsonify, render_template, session, redirect
import sqlite3

challenge2_bp = Blueprint('challenge2', __name__)

DATABASE = "database.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# 문제 설명 페이지
@challenge2_bp.route("/challenge2")
def challenge2():

    if "user" not in session:
        return redirect("/login")

    return render_template("challenge2.html")


# 취약한 API
@challenge2_bp.route("/api/comments/<post_id>")
def comments(post_id):

    if "user" not in session:
        return jsonify({"error": "login required"}), 401

    conn = get_db()

    comments = conn.execute(
        "SELECT * FROM comments WHERE post_id=?",
        (post_id,)
    ).fetchall()

    conn.close()

    result = []

    for comment in comments:
        result.append({
            "id": comment["id"],
            "user_id": comment["user_id"],
            "comment": comment["comment"]
        })

    return jsonify(result)