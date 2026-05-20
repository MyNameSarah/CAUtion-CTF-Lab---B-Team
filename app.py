from flask import Flask, redirect, session

from routes.auth import auth_bp
from routes.challenge1 import challenge1_bp
from routes.challenge2 import challenge2_bp
from routes.challenge3 import challenge3_bp
from routes.challenge4 import challenge4_bp
from routes.challenge5 import challenge5_bp
from routes.challenge6 import challenge6_bp
from routes.challenge7 import challenge7_bp

app = Flask(__name__)

app.secret_key = "super-secret-key"


# Blueprint 등록
app.register_blueprint(auth_bp)
app.register_blueprint(challenge1_bp)
app.register_blueprint(challenge2_bp)
app.register_blueprint(challenge3_bp)
app.register_blueprint(challenge4_bp)
app.register_blueprint(challenge5_bp)
app.register_blueprint(challenge6_bp)
app.register_blueprint(challenge7_bp)

@app.route("/")
def index():

    if "user" not in session:
        return redirect("/login")

    return redirect("/home")


@app.route("/home")
def home():

    if "user" not in session:
        return redirect("/login")

    return f'''
    <h1>IDOR Wargame</h1>

    <p>Welcome {session["user"]}</p>

    <ul>
    <li><a href="/challenge1">Challenge 1 - Basic Memo IDOR</a></li>
    <li><a href="/challenge2">Challenge 2 - API Comment IDOR</a></li>
    <li><a href="/challenge3">Challenge 3 - Profile Update IDOR</a></li>
    <li><a href="/challenge4">Challenge 4 - File Download IDOR</a></li>
    <li><a href="/challenge5">Challenge 5 - Vertical Privilege Escalation</a></li>
    <li><a href="/challenge6">Challenge 6 - UUID Predict IDOR</a></li>
    <li><a href="/challenge7">Challenge 7 - Blind IDOR</a></li>
</ul>

    <br>

    <a href="/logout">Logout</a>
    '''


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)