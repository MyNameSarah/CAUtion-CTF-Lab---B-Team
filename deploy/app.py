from flask import Flask, request, render_template
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    error_msg = ""

    if request.method == 'POST':
        user_input = request.form.get('username', '')

        blacklist = [' ', '--', '/*']
        for word in blacklist:
            if word in user_input:
                return render_template('index.html', error_msg="[WAF] Blocked Keyword Detected!")

        conn = get_db_connection()
        query = f"SELECT username, dummy_pw FROM accounts WHERE username='{user_input}'"
        
        try:
            results = conn.execute(query).fetchall()
        except sqlite3.Error:
            error_msg = "Database Syntax Error!"
        finally:
            conn.close()

    return render_template('index.html', results=results, error_msg=error_msg)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)