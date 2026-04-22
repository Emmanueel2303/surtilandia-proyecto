from pathlib import Path


def get_base_config():
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "data"
    upload_dir = base_dir / "surtilandia" / "static" / "uploads"

    return {
        "SECRET_KEY": "surtilandia-demo-secret",
        "DATA_DIR": str(data_dir),
        "DATABASE_PATH": str(data_dir / "surtilandia.sqlite3"),
        "UPLOAD_DIR": str(upload_dir),
        "MAX_CONTENT_LENGTH": 8 * 1024 * 1024,
        "ADMIN_USERNAME": "surtiadmin",
        "ADMIN_PASSWORD": "SurtiDemo2026!",
    }
