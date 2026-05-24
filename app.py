from flask import Flask, redirect, session

from routes.auth import auth_bp
from routes.challenge import challenge_bp

app = Flask(__name__)

app.secret_key = "super-secret-key"

app.register_blueprint(auth_bp)
app.register_blueprint(challenge_bp)

@app.route("/")
def index():

    if "user" not in session:
        return redirect("/login")

    return redirect("/challenge")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)