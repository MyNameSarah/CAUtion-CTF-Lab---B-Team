import json
import os
import uuid
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template, request
from werkzeug.utils import secure_filename

from worker import DATA_ROOT, QUEUE_DIR, THEMES_DIR, ensure_storage_dirs, find_theme_source_dir, start_worker


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024


def is_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
        return True
    except (TypeError, ValueError):
        return False


def theme_root(theme_id: str) -> str:
    return os.path.join(THEMES_DIR, theme_id)


def status_path(theme_id: str) -> str:
    return os.path.join(theme_root(theme_id), "status.json")


def published_path(theme_id: str) -> str:
    return os.path.join(theme_root(theme_id), "published.json")


def write_status(theme_id: str, state: str, message: str) -> None:
    path = status_path(theme_id)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fp:
        json.dump({"state": state, "message": message}, fp)


def read_status(theme_id: str) -> dict:
    path = status_path(theme_id)
    if not os.path.exists(path):
        return {"state": "processing", "message": "Theme is still being processed. Refresh later."}
    try:
        with open(path, "r", encoding="utf-8") as fp:
            return json.load(fp)
    except (OSError, json.JSONDecodeError):
        return {"state": "failed", "message": "Storage status could not be read."}


def is_theme_published(theme_id: str) -> bool:
    return os.path.isfile(published_path(theme_id))


def write_published_theme(theme_id: str, manifest: dict) -> None:
    payload = {
        "theme_id": theme_id,
        "name": manifest.get("name", "Untitled theme"),
        "version": manifest.get("version", "unknown"),
        "published_at": datetime.now(timezone.utc).isoformat(),
    }
    with open(published_path(theme_id), "w", encoding="utf-8") as fp:
        json.dump(payload, fp)


def safe_public_target(public_dir: str, relative_path: str) -> str | None:
    public_abs = os.path.abspath(public_dir)
    normalized = os.path.normpath(relative_path.replace("\\", "/"))
    if normalized in ("", ".") or os.path.isabs(normalized) or normalized.startswith(".."):
        return None
    target = os.path.abspath(os.path.join(public_abs, normalized))
    if os.path.commonpath([public_abs, target]) != public_abs:
        return None
    return target


def load_theme_manifest(theme_id: str) -> dict:
    try:
        source_dir = find_theme_source_dir(theme_id)
        manifest_path = os.path.join(source_dir, "manifest.json")
        with open(manifest_path, "r", encoding="utf-8") as fp:
            manifest = json.load(fp)
    except (OSError, ValueError, json.JSONDecodeError):
        return {}
    return manifest if isinstance(manifest, dict) else {}


def load_preview_text(theme_id: str, manifest: dict) -> str:
    public_dir = os.path.join(theme_root(theme_id), "public")
    entry = manifest.get("entry", "assets/preview.txt")
    preview_target = safe_public_target(public_dir, entry) if isinstance(entry, str) else None
    if preview_target is None or not os.path.isfile(preview_target):
        preview_target = safe_public_target(public_dir, "assets/preview.txt")

    if preview_target is None or not os.path.isfile(preview_target):
        return ""

    with open(preview_target, "rb") as fp:
        return fp.read(2048).decode("utf-8", errors="replace")


def load_theme_css(theme_id: str) -> str:
    public_dir = os.path.join(theme_root(theme_id), "public")
    css_target = safe_public_target(public_dir, "css/style.css")
    if css_target is None or not os.path.isfile(css_target):
        return ""

    with open(css_target, "rb") as fp:
        return fp.read(8192).decode("utf-8", errors="replace")


@app.post("/internal/theme/import")
def import_theme():
    uploaded = request.files.get("theme_pack") or request.files.get("file")
    if uploaded is None or uploaded.filename == "":
        return "Missing Theme Pack ZIP.", 400

    filename = secure_filename(uploaded.filename)
    if not filename.lower().endswith(".zip"):
        return "Only .zip files are accepted.", 400

    theme_id = str(uuid.uuid4())
    root = theme_root(theme_id)
    os.makedirs(os.path.join(root, "source"), exist_ok=True)
    os.makedirs(os.path.join(root, "public"), exist_ok=True)
    os.makedirs(os.path.join(root, "review"), exist_ok=True)
    write_status(theme_id, "processing", "Theme is still being processed. Refresh later.")

    os.makedirs(QUEUE_DIR, exist_ok=True)
    uploaded.save(os.path.join(QUEUE_DIR, f"{theme_id}.zip"))
    return jsonify({"theme_id": theme_id})


@app.get("/internal/theme/<theme_id>/preview")
def preview(theme_id):
    if not is_uuid(theme_id):
        return render_template("preview.html", state="failed", message="Invalid theme id."), 404

    root = theme_root(theme_id)
    if not os.path.isdir(root):
        return render_template("preview.html", state="failed", message="Theme was not found."), 404

    status = read_status(theme_id)
    state = status.get("state", "processing")
    message = status.get("message", "Theme is still being processed. Refresh later.")
    if state != "processed":
        return render_template("preview.html", state=state, message=message)

    manifest = load_theme_manifest(theme_id)
    preview_text = load_preview_text(theme_id, manifest)
    theme_css = load_theme_css(theme_id)

    return render_template(
        "preview.html",
        state="processed",
        message=message,
        is_published=is_theme_published(theme_id),
        manifest=manifest,
        preview_text=preview_text,
        theme_css=theme_css,
    )


@app.get("/internal/theme/<theme_id>/live")
def live(theme_id):
    if not is_uuid(theme_id):
        return render_template("live.html", published=False, message="Invalid theme id."), 404

    root = theme_root(theme_id)
    if not os.path.isdir(root):
        return render_template("live.html", published=False, message="Theme was not found."), 404
    if not is_theme_published(theme_id):
        return render_template("live.html", published=False, message="Theme has not been published yet.")

    manifest = load_theme_manifest(theme_id)
    preview_text = load_preview_text(theme_id, manifest)
    theme_css = load_theme_css(theme_id)
    return render_template(
        "live.html",
        published=True,
        message="Published theme is active.",
        manifest=manifest,
        preview_text=preview_text,
        theme_css=theme_css,
    )


@app.route("/internal/theme/<theme_id>/publish", methods=["GET", "POST"])
def publish(theme_id):
    if not is_uuid(theme_id):
        return render_template("publish.html", published=False, message="Invalid theme id."), 404

    root = theme_root(theme_id)
    if not os.path.isdir(root):
        return render_template("publish.html", published=False, message="Theme was not found."), 404

    status = read_status(theme_id)
    state = status.get("state", "processing")
    if state == "processing":
        return render_template(
            "publish.html",
            published=False,
            message="Theme is still being processed. Refresh later.",
        )
    if state != "processed":
        return render_template(
            "publish.html",
            published=False,
            message="Theme cannot be published because processing did not complete.",
        )

    manifest = load_theme_manifest(theme_id)
    preview_text = load_preview_text(theme_id, manifest)
    theme_css = load_theme_css(theme_id)
    write_published_theme(theme_id, manifest)

    flag = None
    review_note = None
    approval_path = os.path.join(root, "review", "approval.json")
    if not os.path.exists(approval_path):
        return render_template(
            "publish.html",
            published=True,
            message="Theme published successfully.",
            manifest=manifest,
            preview_text=preview_text,
            theme_css=theme_css,
            review_note="Release review metadata is not attached.",
        )

    try:
        with open(approval_path, "r", encoding="utf-8") as fp:
            approval = json.load(fp)
    except json.JSONDecodeError:
        review_note = "Internal review metadata must be valid JSON."
        approval = None
    except OSError:
        review_note = "Internal review metadata was ignored."
        approval = None

    if review_note is None:
        if not isinstance(approval, dict):
            review_note = "Release review metadata must be a JSON object."
        elif "approved" not in approval:
            review_note = "Review metadata must contain a single approval decision: approved."
        elif not isinstance(approval.get("approved"), bool):
            review_note = "approved must be a boolean value."
        elif approval.get("approved") is True:
            with open("/flag.txt", "r", encoding="utf-8") as fp:
                flag = fp.read().strip()
        else:
            review_note = "Theme was reviewed but not approved for release token."

    return render_template(
        "publish.html",
        published=True,
        message="Theme published successfully.",
        manifest=manifest,
        preview_text=preview_text,
        theme_css=theme_css,
        review_note=review_note,
        flag=flag,
    )


if __name__ == "__main__":
    ensure_storage_dirs()
    start_worker()
    app.run(host="0.0.0.0", port=80, threaded=True, use_reloader=False)
