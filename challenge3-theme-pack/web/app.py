import io
import os
import uuid
import zipfile

import requests
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

STORAGE_URL = os.environ.get("STORAGE_URL", "http://ch3-storage:80").rstrip("/")


def is_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
        return True
    except (TypeError, ValueError):
        return False


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/sample-theme.zip")
def sample_theme_zip():
    manifest = """{
  "name": "Northline Field Notes",
  "description": "A newsroom-style public profile for upload research notes",
  "version": "1.2",
  "entry": "assets/preview.txt"
}
"""
    preview = "A compact public page for sharing file upload research notes, archive tests, and weekly CTF progress."
    css = """.theme-surface {
  --paper: #fffaf7;
  --ink: #18212f;
  --muted: #64748b;
  --rose: #be3455;
  --sky: #dbeafe;
  --gold: #f4b740;
  padding: 36px;
  border-radius: 8px;
  color: var(--ink);
  background:
    radial-gradient(circle at 12% 18%, rgba(190, 52, 85, 0.2), transparent 28%),
    linear-gradient(135deg, var(--paper), var(--sky));
}

.theme-surface .theme-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 30px;
}

.theme-surface .theme-nav strong {
  font-size: 0.95rem;
}

.theme-surface .theme-nav span,
.theme-surface .theme-kicker {
  color: var(--rose);
  font-size: 0.74rem;
  font-weight: 850;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.theme-surface .theme-hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 300px;
  gap: 24px;
  align-items: stretch;
}

.theme-surface .theme-copy {
  min-height: 360px;
  display: grid;
  align-content: center;
}

.theme-surface .profile-card {
  margin: 0 auto;
  overflow: hidden;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 22px 50px rgba(24, 33, 47, 0.12);
}

.theme-surface .profile-banner {
  min-height: 170px;
  background:
    linear-gradient(135deg, rgba(190, 52, 85, 0.9), rgba(24, 33, 47, 0.92)),
    linear-gradient(90deg, #ffe4e6, #dbeafe);
}

.theme-surface .profile-body {
  padding: 22px;
}

.theme-surface .profile-body strong {
  display: block;
  margin-bottom: 8px;
  font-size: 1.2rem;
}

.theme-surface .profile-body p {
  margin: 0;
  color: var(--muted);
}

.theme-surface h3 {
  margin: 0 0 14px;
  color: var(--ink);
  font-size: clamp(2.4rem, 6vw, 4.8rem);
  line-height: 0.95;
}

.theme-surface .theme-description,
.theme-surface .theme-version {
  color: var(--muted);
}

.theme-surface .theme-description {
  max-width: 42rem;
  font-size: 1.08rem;
}

.theme-surface .theme-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 24px;
}

.theme-surface .theme-actions span {
  border: 1px solid rgba(190, 52, 85, 0.25);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.72);
  padding: 8px 12px;
  color: var(--rose);
  font-weight: 800;
}

.theme-surface .theme-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-top: 24px;
}

.theme-surface .theme-grid article,
.theme-surface .theme-note {
  border: 1px solid #ead7dc;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.78);
  padding: 18px;
}

.theme-surface .theme-grid span {
  display: block;
  margin-bottom: 12px;
  color: var(--rose);
  font-weight: 900;
}

.theme-surface .theme-grid strong,
.theme-surface .theme-note strong {
  display: block;
  margin-bottom: 8px;
}

.theme-surface .theme-grid p,
.theme-surface .theme-note p {
  margin: 0;
  color: var(--muted);
}

.theme-surface .theme-note {
  margin-top: 14px;
  border-left: 5px solid var(--gold);
}

@media (max-width: 760px) {
  .theme-surface .theme-hero,
  .theme-surface .theme-grid {
    grid-template-columns: 1fr;
  }
  .theme-surface .theme-copy {
    min-height: 0;
  }
}
"""

    png_1x1 = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
        b"\x00\x00\x00\rIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe"
        b"\x02\xfeA\xe2!\xbc\x00\x00\x00\x00IEND\xaeB`\x82"
    )

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", manifest)
        archive.writestr("assets/preview.txt", preview)
        archive.writestr("assets/banner.png", png_1x1)
        archive.writestr("css/style.css", css)
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name="sample-theme.zip",
    )


@app.post("/upload")
def upload():
    uploaded = request.files.get("theme_pack")
    if uploaded is None or uploaded.filename == "":
        return render_template("result.html", error="Please choose a Theme Pack ZIP file."), 400

    filename = secure_filename(uploaded.filename)
    if not filename.lower().endswith(".zip"):
        return render_template("result.html", error="Only .zip Theme Pack files are accepted."), 400

    try:
        response = requests.post(
            f"{STORAGE_URL}/internal/theme/import",
            files={
                "theme_pack": (
                    filename,
                    uploaded.stream,
                    uploaded.mimetype or "application/zip",
                )
            },
            timeout=8,
        )
    except requests.RequestException:
        return render_template("result.html", error="Storage service is not available."), 502

    if response.status_code != 200:
        return render_template("result.html", error=response.text.strip() or "Storage rejected the upload."), 400

    try:
        data = response.json()
    except ValueError:
        return render_template("result.html", error="Storage returned an invalid response."), 502

    theme_id = data.get("theme_id", "")
    if not is_uuid(theme_id):
        return render_template("result.html", error="Storage returned an invalid theme id."), 502

    return render_template("result.html", theme_id=theme_id)


@app.get("/theme/<theme_id>")
def theme(theme_id):
    if not is_uuid(theme_id):
        return render_template("theme.html", error="Invalid theme id."), 404

    try:
        response = requests.get(f"{STORAGE_URL}/internal/theme/{theme_id}/preview", timeout=8)
    except requests.RequestException:
        return render_template("theme.html", theme_id=theme_id, error="Storage service is not available."), 502

    return render_template("theme.html", theme_id=theme_id, storage_html=response.text)


@app.route("/theme/<theme_id>/publish", methods=["GET", "POST"])
def publish(theme_id):
    if not is_uuid(theme_id):
        return render_template("publish.html", error="Invalid theme id."), 404

    try:
        response = requests.request(
            request.method,
            f"{STORAGE_URL}/internal/theme/{theme_id}/publish",
            timeout=8,
        )
    except requests.RequestException:
        return render_template("publish.html", theme_id=theme_id, error="Storage service is not available."), 502

    return render_template("publish.html", theme_id=theme_id, storage_html=response.text)


@app.get("/theme/<theme_id>/live")
def live(theme_id):
    if not is_uuid(theme_id):
        return render_template("live.html", error="Invalid theme id."), 404

    try:
        response = requests.get(f"{STORAGE_URL}/internal/theme/{theme_id}/live", timeout=8)
    except requests.RequestException:
        return render_template("live.html", theme_id=theme_id, error="Storage service is not available."), 502

    return render_template("live.html", theme_id=theme_id, storage_html=response.text)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, threaded=True)
