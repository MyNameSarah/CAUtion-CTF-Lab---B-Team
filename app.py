import os
from flask import Flask, request, render_template, render_template_string, abort
import html

app = Flask(__name__)

profiles = [
    {
    'id': 0,
    'name': 'Caution',
    'bio': 'This is test profile',
    'color': '#ffffff'
    }
]

def check_ssti_payload(input_string):
    blacklist_path = '/app/secret_filters.txt'
    
    if os.path.exists(blacklist_path):
        with open(blacklist_path, 'r') as f:
            blacklist = [line.strip().lower() for line in f if line.strip()]
    else:
        blacklist = ['class', 'mro', 'config'] 

    for bad in blacklist:
        if bad in input_string.lower():
            return True
    return False

@app.route('/')
def index():
    return render_template('list.html', profiles=profiles)

@app.route('/create')
def create_page():
    return render_template('index.html')

@app.route('/profile', methods=['POST'])
def profile():
    user_name = request.form.get('name', 'Guest')
    user_bio = request.form.get('bio', 'Hello, world!')
    card_color = request.form.get('color', '#ffffff')

    if check_ssti_payload(user_bio):
        return "보안 정책에 의해 차단된 키워드가 포함되어 있습니다. (No Hack!)", 400

    new_profile = {
        'id': len(profiles),
        'name': html.escape(user_name), 
        'bio': user_bio,
        'color': html.escape(card_color)
    }
    profiles.append(new_profile)

    return render_profile(new_profile)

@app.route('/view/<int:profile_id>')
def view_profile(profile_id):
    if profile_id < 0 or profile_id >= len(profiles):
        abort(404)
    
    target_profile = profiles[profile_id]
    return render_profile(target_profile)

def render_profile(p):

    profile_template = f"""
    {{% extends "layout.html" %}}
    {{% block content %}}
    <div class="container mt-5 text-center">
        <div class="card mx-auto" style="width: 24rem; background-color: {p['color']}; border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
            <div class="card-body">
                <img src="https://api.dicebear.com/7.x/avataaars/svg?seed={p['name']}" alt="avatar" class="rounded-circle mb-3" width="100">
                <h2 class="card-title">{p['name']}</h2>
                <hr>
                <div class="card-text text-muted">
                    {p['bio']}
                </div>
            </div>
        </div>
        <div class="mt-4">
            <a href="/" class="btn btn-secondary">목록으로</a>
            <a href="/create" class="btn btn-primary">새 프로필 등록</a>
        </div>
    </div>
    {{% endblock %}}
    """
    try:
        return render_template_string(profile_template)
    except Exception as e:
        return f"Rendering Error : {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
