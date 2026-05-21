import json
import mimetypes
import os
import secrets
import uuid

from flask import Flask, redirect, render_template, request, send_file, url_for
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024

APP_ROOT = "/app"
UPLOAD_DIR = os.path.join(APP_ROOT, "uploads")
PROFILE_DIR = os.path.join(APP_ROOT, "profiles")
ALLOWED_BANNER_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}


def ensure_dirs() -> None:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(PROFILE_DIR, exist_ok=True)


def is_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
        return True
    except (TypeError, ValueError):
        return False


def profile_path(profile_id: str) -> str:
    return os.path.join(PROFILE_DIR, f"{profile_id}.json")


def clean_upload_name(filename: str) -> str:
    filename = filename.replace("\\", "/")
    filename = os.path.basename(filename)
    cleaned = secure_filename(filename)
    return cleaned or "banner.bin"


def banner_extension(filename: str) -> str:
    return os.path.splitext(filename.lower())[1]


def save_profile(profile: dict) -> None:
    ensure_dirs()
    with open(profile_path(profile["profile_id"]), "w", encoding="utf-8") as fp:
        json.dump(profile, fp, ensure_ascii=False, indent=2)


def load_profile(profile_id: str) -> dict | None:
    if not is_uuid(profile_id):
        return None
    path = profile_path(profile_id)
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as fp:
            profile = json.load(fp)
    except (OSError, json.JSONDecodeError):
        return None
    if profile.get("profile_id") != profile_id:
        return None
    return profile


def read_banner_preview(banner_path: str) -> tuple[str, str | None]:
    if not banner_path:
        return "", "No banner path is stored for this profile."
    try:
        with open(banner_path, "rb") as fp:
            data = fp.read(4096)
    except OSError:
        return "", "The banner file could not be read."
    return data.decode("utf-8", errors="replace"), None


def uploaded_banner_relative_path(profile_id: str, banner_path: str) -> str | None:
    upload_root = os.path.abspath(os.path.join(UPLOAD_DIR, profile_id))
    candidate = os.path.abspath(banner_path)
    if os.path.commonpath([upload_root, candidate]) != upload_root:
        return None
    if not os.path.isfile(candidate):
        return None
    mime_type, _ = mimetypes.guess_type(candidate)
    if mime_type not in {"image/jpeg", "image/png", "image/gif"}:
        return None
    return os.path.basename(candidate)


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/profile/create")
def create_profile():
    ensure_dirs()
    display_name = request.form.get("display_name", "").strip()
    bio = request.form.get("bio", "").strip()
    banner = request.files.get("banner")

    if banner is None or banner.filename == "":
        return render_template("index.html", error="Please upload a banner image."), 400

    original_name = clean_upload_name(banner.filename)
    if banner_extension(original_name) not in ALLOWED_BANNER_EXTENSIONS:
        return render_template("index.html", error="Only jpg, jpeg, png, and gif banners are accepted."), 400

    profile_id = str(uuid.uuid4())
    profile_upload_dir = os.path.join(UPLOAD_DIR, profile_id)
    os.makedirs(profile_upload_dir, exist_ok=True)

    stored_name = f"{secrets.token_hex(8)}_{original_name}"
    banner_path = os.path.join(profile_upload_dir, stored_name)
    banner.save(banner_path)

    profile = {
        "profile_id": profile_id,
        "display_name": display_name or "Untitled Profile",
        "bio": bio,
        "banner_path": banner_path,
    }
    save_profile(profile)
    return redirect(url_for("show_profile", profile_id=profile_id))


@app.get("/profile/<profile_id>")
def show_profile(profile_id):
    profile = load_profile(profile_id)
    if profile is None:
        return "Profile not found.", 404

    banner_name = uploaded_banner_relative_path(profile_id, profile.get("banner_path", ""))
    banner_url = url_for("uploaded_banner", profile_id=profile_id, filename=banner_name) if banner_name else None
    banner_preview, banner_error = ("", None) if banner_url else read_banner_preview(profile.get("banner_path", ""))
    return render_template(
        "profile.html",
        profile=profile,
        banner_url=banner_url,
        banner_preview=banner_preview,
        banner_error=banner_error,
    )


@app.get("/uploads/<profile_id>/<filename>")
def uploaded_banner(profile_id, filename):
    if not is_uuid(profile_id):
        return "Not found.", 404

    safe_name = clean_upload_name(filename)
    if safe_name != filename:
        return "Not found.", 404

    path = os.path.abspath(os.path.join(UPLOAD_DIR, profile_id, safe_name))
    upload_root = os.path.abspath(os.path.join(UPLOAD_DIR, profile_id))
    if os.path.commonpath([upload_root, path]) != upload_root or not os.path.isfile(path):
        return "Not found.", 404

    return send_file(path)


@app.get("/profile/<profile_id>/edit")
def edit_profile(profile_id):
    profile = load_profile(profile_id)
    if profile is None:
        return "Profile not found.", 404
    return render_template("edit.html", profile=profile)


@app.post("/profile/<profile_id>/update")
def update_profile(profile_id):
    profile = load_profile(profile_id)
    if profile is None:
        return "Profile not found.", 404

    profile["display_name"] = request.form.get("display_name", "").strip() or "Untitled Profile"
    profile["bio"] = request.form.get("bio", "").strip()
    profile["banner_path"] = request.form.get("banner_path", "")
    save_profile(profile)

    return redirect(url_for("show_profile", profile_id=profile_id))


if __name__ == "__main__":
    ensure_dirs()
    app.run(host="0.0.0.0", port=80, threaded=True)
