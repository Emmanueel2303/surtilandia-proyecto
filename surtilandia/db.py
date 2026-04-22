import sqlite3
from datetime import datetime, UTC
from pathlib import Path

from flask import current_app, g
from werkzeug.security import generate_password_hash


def get_db():
    if "db" not in g:
        database_path = current_app.config["DATABASE_PATH"]
        needs_directory = database_path != ":memory:"

        if needs_directory:
            Path(database_path).parent.mkdir(parents=True, exist_ok=True)

        connection = sqlite3.connect(database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        g.db = connection

    return g.db


def close_db(_exception=None):
    database = g.pop("db", None)
    if database is not None:
        database.close()


def init_db():
    db = get_db()
    schema_path = Path(__file__).with_name("schema.sql")
    db.executescript(schema_path.read_text(encoding="utf-8"))
    db.commit()


def now_iso():
    return datetime.now(UTC).isoformat()


def seed_demo_data():
    db = get_db()
    existing = db.execute("SELECT COUNT(*) AS total FROM products").fetchone()
    if existing["total"] > 0:
        return

    timestamp = now_iso()
    demo_products = [
        (
            "audifonos-bluetooth-premium",
            "SURTI-TEC-001",
            "Audifonos Bluetooth Premium",
            "Tecnologia",
            54900,
            18,
            "Audio portable con bateria larga y estuche de carga.",
            "Audifonos inalambricos para uso diario, videollamadas y musica.",
            "https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=900&q=80",
        ),
        (
            "organizador-modular-cocina",
            "SURTI-HOG-002",
            "Organizador modular para cocina",
            "Hogar",
            39900,
            11,
            "Organiza especias, recipientes y utensilios en poco espacio.",
            "Sistema modular ideal para optimizar alacenas, estantes y zonas pequenas.",
            "https://images.unsplash.com/photo-1586208958839-06c17cacdf08?auto=format&fit=crop&w=900&q=80",
        ),
        (
            "kit-skincare-diario",
            "SURTI-BEL-003",
            "Kit skincare de rutina diaria",
            "Belleza",
            29900,
            15,
            "Rutina facial basica con productos de uso diario.",
            "Incluye limpieza, hidratacion y cuidado ligero para una rutina practica.",
            "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=900&q=80",
        ),
        (
            "set-cuchillos-soporte",
            "SURTI-COC-004",
            "Set de cuchillos con soporte",
            "Cocina",
            64900,
            9,
            "Set completo para preparacion diaria con soporte incluido.",
            "Cuchillos pensados para cocina domestica y presentacion ordenada.",
            "https://images.unsplash.com/photo-1593618998160-2d03ea5f2e72?auto=format&fit=crop&w=900&q=80",
        ),
    ]

    db.executemany(
        """
        INSERT INTO products (
            slug, reference, name, category, price, stock,
            short_description, details, primary_image, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                slug,
                reference,
                name,
                category,
                price,
                stock,
                short_description,
                details,
                primary_image,
                timestamp,
                timestamp,
            )
            for slug, reference, name, category, price, stock, short_description, details, primary_image in demo_products
        ],
    )
    db.commit()


def seed_admin_user():
    db = get_db()
    existing = db.execute("SELECT COUNT(*) AS total FROM admin_users").fetchone()
    if existing["total"] > 0:
        return

    timestamp = now_iso()
    db.execute(
        """
        INSERT INTO admin_users (username, password_hash, created_at, updated_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            current_app.config["ADMIN_USERNAME"],
            generate_password_hash(current_app.config["ADMIN_PASSWORD"]),
            timestamp,
            timestamp,
        ),
    )
    db.commit()


def init_app(app):
    @app.cli.command("init-db")
    def init_db_command():
        init_db()
        print("Database initialized.")
