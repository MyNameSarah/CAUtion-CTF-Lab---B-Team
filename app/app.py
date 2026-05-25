import os
from flask import Flask, request, render_template

app = Flask(__name__)

CHAR_BLACKLIST = ["&", "|", "`", "$", "(", ")", "{", "}", ">", "<", "\n", "\r"]

KEYWORD_BLACKLIST = [
    "cat", "flag", "more", "less", "head", "tail",
    "tac", "grep", "awk", "sed", "cut", "strings",
    "xxd", "od", "nl", "vi", "nano", "python", "perl",
    "ruby", "php", "curl", "wget", "nc", "bash", "sh",
]

def is_safe(host):
    for char in CHAR_BLACKLIST:
        if char in host:
            return False, "허용되지 않는 문자입니다."
    host_lower = host.lower()
    for kw in KEYWORD_BLACKLIST:
        if kw in host_lower:
            return False, f"허용되지 않는 명령어입니다: '{kw}'"
    return True, None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/lookup", methods=["POST"])
def lookup():
    host = request.form.get("host", "").strip()

    if not host:
        return render_template("index.html", error="호스트명을 입력하세요.")

    safe, error_msg = is_safe(host)
    if not safe:
        return render_template("index.html", error=error_msg)

    cmd = f"nslookup {host}"
    result = os.popen(cmd).read()

    return render_template("index.html", result=result, host=host)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
