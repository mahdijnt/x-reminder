"""Application entrypoint for ASGI servers."""

from app.factory import create_app

app = create_app()
