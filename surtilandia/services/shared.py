import re


def format_currency(value):
    digits = f"{int(value):,}".replace(",", ".")
    return f"${digits}"


def slugify(value):
    normalized = re.sub(r"[^a-zA-Z0-9\s-]", "", value).strip().lower()
    return re.sub(r"[-\s]+", "-", normalized)
