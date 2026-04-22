from pathlib import Path
from uuid import uuid4

from flask import current_app
from werkzeug.utils import secure_filename


def save_uploaded_images(files):
    saved_paths = []
    upload_dir = Path(current_app.config["UPLOAD_DIR"])
    upload_dir.mkdir(parents=True, exist_ok=True)

    for file in files:
        if file is None or not file.filename:
            continue

        filename = secure_filename(file.filename)
        if not filename:
            continue

        unique_name = f"{uuid4().hex}-{filename}"
        destination = upload_dir / unique_name
        file.save(destination)
        saved_paths.append(f"/static/uploads/{unique_name}")

    return saved_paths
