import json
import os
import shutil
import threading
import time
import urllib.parse
import uuid
import zipfile


DATA_ROOT = "/data"
QUEUE_DIR = os.path.join(DATA_ROOT, "queue")
THEMES_DIR = os.path.join(DATA_ROOT, "themes")

MAX_FILES = 20
MAX_TOTAL_SIZE = 1024 * 1024
ALLOWED_EXTENSIONS = {".json", ".txt", ".png", ".jpg", ".jpeg", ".gif", ".css"}

_worker_thread: threading.Thread | None = None


def ensure_storage_dirs() -> None:
    os.makedirs(QUEUE_DIR, exist_ok=True)
    os.makedirs(THEMES_DIR, exist_ok=True)


def is_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
        return True
    except (TypeError, ValueError):
        return False


def theme_root(theme_id: str) -> str:
    return os.path.join(THEMES_DIR, theme_id)


def write_status(theme_id: str, state: str, message: str, details: dict | None = None) -> None:
    root = theme_root(theme_id)
    os.makedirs(root, exist_ok=True)
    payload = {"state": state, "message": message}
    if details:
        payload["details"] = details
    with open(os.path.join(root, "status.json"), "w", encoding="utf-8") as fp:
        json.dump(payload, fp)


def reset_theme_dirs(theme_id: str) -> None:
    root = theme_root(theme_id)
    os.makedirs(root, exist_ok=True)
    for name in ("source", "public", "review"):
        path = os.path.join(root, name)
        shutil.rmtree(path, ignore_errors=True)
        os.makedirs(path, exist_ok=True)


def is_directory_entry(entry: zipfile.ZipInfo) -> bool:
    return entry.is_dir() or entry.filename.endswith("/") or entry.filename.endswith("\\")


def validate_entries(entries: list[zipfile.ZipInfo]) -> None:
    if len(entries) > MAX_FILES:
        raise ValueError("Theme Pack contains too many files.")

    total_size = sum(entry.file_size for entry in entries)
    if total_size > MAX_TOTAL_SIZE:
        raise ValueError("Theme Pack is too large.")

    for entry in entries:
        raw_name = entry.filename
        lower_name = raw_name.lower()
        _, ext = os.path.splitext(lower_name)

        if not raw_name or "\x00" in raw_name:
            raise ValueError("Theme Pack contains an invalid filename.")
        if raw_name.startswith("/"):
            raise ValueError("Absolute paths are not allowed.")
        if len(raw_name) >= 2 and raw_name[1] == ":":
            raise ValueError("Windows absolute paths are not allowed.")
        if "../" in raw_name:
            raise ValueError("Parent directory segments are not allowed.")
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError("Theme Pack contains a file type that is not allowed.")


def vulnerable_store_entries(theme_id: str, archive: zipfile.ZipFile, entries: list[zipfile.ZipInfo]) -> None:
    root = theme_root(theme_id)
    root_abs = os.path.abspath(root)
    source_base = os.path.abspath(os.path.join(root, "source"))

    for entry in entries:
        decoded_name = urllib.parse.unquote(entry.filename)
        slash_name = decoded_name.replace("\\", "/")
        normalized_name = os.path.normpath(slash_name)

        if normalized_name in ("", "."):
            continue
        if os.path.isabs(normalized_name):
            raise ValueError("Absolute paths are not allowed.")
        if len(normalized_name) >= 2 and normalized_name[1] == ":":
            raise ValueError("Windows absolute paths are not allowed.")

        target_path = os.path.abspath(os.path.join(source_base, normalized_name))
        if os.path.commonpath([root_abs, target_path]) != root_abs:
            raise ValueError("Theme Pack path is not allowed.")

        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with archive.open(entry) as src, open(target_path, "wb") as dst:
            shutil.copyfileobj(src, dst, length=64 * 1024)


def find_theme_source_dir(theme_id: str) -> str:
    source_dir = os.path.abspath(os.path.join(theme_root(theme_id), "source"))
    root_manifest = os.path.join(source_dir, "manifest.json")
    if os.path.isfile(root_manifest):
        return source_dir

    children = []
    if os.path.isdir(source_dir):
        for name in os.listdir(source_dir):
            child = os.path.abspath(os.path.join(source_dir, name))
            if os.path.isdir(child) and os.path.commonpath([source_dir, child]) == source_dir:
                children.append(child)

    manifest_dirs = [child for child in children if os.path.isfile(os.path.join(child, "manifest.json"))]
    if len(manifest_dirs) == 1:
        return manifest_dirs[0]
    if len(manifest_dirs) > 1:
        raise ValueError("manifest.json was found in multiple folders.")

    raise ValueError("manifest.json is missing.")


def load_manifest(source_dir: str) -> dict:
    manifest_path = os.path.join(source_dir, "manifest.json")
    if not os.path.isfile(manifest_path):
        raise ValueError("manifest.json is missing.")

    with open(manifest_path, "r", encoding="utf-8") as fp:
        manifest = json.load(fp)

    required = ("name", "description", "version", "entry")
    if not isinstance(manifest, dict) or any(not isinstance(manifest.get(key), str) for key in required):
        raise ValueError("manifest.json has an invalid format.")

    entry = os.path.normpath(manifest["entry"].replace("\\", "/")).replace(os.sep, "/")
    if entry in ("", ".") or os.path.isabs(entry) or entry.startswith(".."):
        raise ValueError("manifest entry is invalid.")
    if not (entry.startswith("assets/") or entry.startswith("css/")):
        raise ValueError("manifest entry must point to a public theme asset.")

    _, ext = os.path.splitext(entry.lower())
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("manifest entry points to an unsupported file type.")

    return manifest


def copy_public_assets(theme_id: str, source_dir: str) -> list[str]:
    root = theme_root(theme_id)
    source_dir = os.path.abspath(source_dir)
    public_dir = os.path.abspath(os.path.join(root, "public"))

    shutil.rmtree(public_dir, ignore_errors=True)
    os.makedirs(public_dir, exist_ok=True)

    copied: list[str] = []
    for top_level in ("assets", "css"):
        source_top = os.path.abspath(os.path.join(source_dir, top_level))
        if not os.path.isdir(source_top):
            continue
        if os.path.commonpath([source_dir, source_top]) != source_dir:
            continue

        for current_root, _, files in os.walk(source_top):
            for filename in files:
                _, ext = os.path.splitext(filename.lower())
                if ext not in ALLOWED_EXTENSIONS:
                    continue

                source_path = os.path.abspath(os.path.join(current_root, filename))
                if os.path.commonpath([source_top, source_path]) != source_top:
                    continue

                rel_path = os.path.relpath(source_path, source_dir)
                target_path = os.path.abspath(os.path.join(public_dir, rel_path))
                if os.path.commonpath([public_dir, target_path]) != public_dir:
                    continue

                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                shutil.copy2(source_path, target_path)
                copied.append(rel_path.replace(os.sep, "/"))

    return copied


def process_theme_zip(theme_id: str, zip_path: str) -> None:
    write_status(theme_id, "processing", "Theme is still being processed. Refresh later.")

    with zipfile.ZipFile(zip_path) as archive:
        entries = [entry for entry in archive.infolist() if not is_directory_entry(entry)]
        validate_entries(entries)
        vulnerable_store_entries(theme_id, archive, entries)

    source_dir = find_theme_source_dir(theme_id)
    manifest = load_manifest(source_dir)
    copied = copy_public_assets(theme_id, source_dir)
    write_status(
        theme_id,
        "processed",
        "Theme was processed successfully.",
        {"name": manifest["name"], "version": manifest["version"], "public_files": copied},
    )


def process_queue_once() -> None:
    ensure_storage_dirs()
    for filename in sorted(os.listdir(QUEUE_DIR)):
        if not filename.endswith(".zip"):
            continue

        theme_id = filename[:-4]
        if not is_uuid(theme_id):
            continue

        zip_path = os.path.join(QUEUE_DIR, filename)
        try:
            process_theme_zip(theme_id, zip_path)
        except (OSError, zipfile.BadZipFile, json.JSONDecodeError, ValueError) as exc:
            reset_theme_dirs(theme_id)
            write_status(theme_id, "failed", str(exc))
        finally:
            try:
                os.remove(zip_path)
            except FileNotFoundError:
                pass


def worker_loop() -> None:
    while True:
        process_queue_once()
        time.sleep(1)


def start_worker() -> None:
    global _worker_thread
    if _worker_thread is not None and _worker_thread.is_alive():
        return
    _worker_thread = threading.Thread(target=worker_loop, name="theme-storage-worker", daemon=True)
    _worker_thread.start()
