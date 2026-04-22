import os

from surtilandia import create_app


app = create_app()


if __name__ == "__main__":
    app.run(
        host=os.environ.get("SURTI_HOST", "127.0.0.1"),
        port=int(os.environ.get("SURTI_PORT", "8000")),
        debug=os.environ.get("SURTI_DEBUG", "0") == "1",
    )
