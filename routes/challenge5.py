from flask import Blueprint, render_template
from flask import request, redirect, session
import sqlite3

challenge5_bp = Blueprint('challenge5', __name__)

DATABASE = "database.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# 문제 페이지
@challenge5_bp.route("/challenge5")
def challenge5():

    if "user" not in session:
        return redirect("/login")

    conn = get_db()

    requests_data = conn.execute(
        "SELECT * FROM requests"
    ).fetchall()

    conn.close()

    return render_template(
        "challenge5.html",
        requests=requests_data,
        role=session["role"]
    )


# 취약한 승인 기능
@challenge5_bp.route("/internal-api/v2/process")
def approve():

    if "user" not in session:
        return redirect("/login")

    ticket_id = request.args.get("ticket")

    conn = get_db()

    # 의도적인 취약점:
    # admin 권한 검증 없음
    conn.execute(
        "UPDATE requests SET approved=1 WHERE ticket_id=?",
        (ticket_id,)
    )

    conn.commit()

    approved_request = conn.execute(
        "SELECT * FROM requests WHERE ticket_id=?",
        (ticket_id,)
    ).fetchone()

    conn.close()

    return render_template(
        "approved.html",
        request_data=approved_request
    )