from app.factory import create_app
from app.infrastructure.qdrant.connection import get_qdrant_manager, reset_qdrant_manager


def test_create_app_smoke():
    reset_qdrant_manager()
    app = create_app()
    assert app.title
    assert get_qdrant_manager() is not None


def test_health_snapshot_disabled():
    import asyncio
    from app.core.config import Settings
    from app.infrastructure.qdrant.connection import QdrantManager

    manager = QdrantManager(Settings(QDRANT_ENABLED=False))
    snapshot = asyncio.run(manager.health_snapshot())
    assert snapshot["connected"] is False
    assert snapshot["detail"] == "QDRANT_ENABLED=false"
