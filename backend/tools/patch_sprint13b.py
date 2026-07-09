from pathlib import Path
ROOT = Path(r"E:\GitHub\x-reminder\backend")

# polling_engine
pe = (ROOT / "app/monitoring/polling_engine.py").read_text(encoding="utf-8")
if "notification_service" not in pe:
    pe = pe.replace(
        "from app.services.x_tweet_service import XTweetService",
        "from app.models.x.tweet import FilteredTweet\nfrom app.services.x_tweet_service import XTweetService",
    )
    pe = pe.replace(
        "        metrics: MonitoringMetrics,\n    ) -> None:",
        "        metrics: MonitoringMetrics,\n        notification_service=None,\n    ) -> None:",
    )
    pe = pe.replace(
        "        self._metrics = metrics\n",
        "        self._metrics = metrics\n        self._notification_service = notification_service\n",
    )
    pe = pe.replace(
        "                    await self._processed_repo.touch_pending(app_user_id, item.tweet_id, item.author_id)\n"
        "                    new_processed += 1",
        "                    await self._processed_repo.touch_pending(\n"
        "                        app_user_id,\n"
        "                        item.tweet_id,\n"
        "                        item.author_id,\n"
        "                        list_type=list_type.value,\n"
        "                        username=item.username,\n"
        "                        url=item.url,\n"
        "                        tweet_created_at=item.created_at,\n"
        "                    )\n"
        "                    new_processed += 1\n"
        "                    if self._notification_service is not None:\n"
        "                        tweet = FilteredTweet(\n"
        "                            tweet_id=item.tweet_id,\n"
        "                            author_id=item.author_id,\n"
        "                            username=item.username,\n"
        "                            text=item.text,\n"
        "                            created_at=item.created_at,\n"
        "                            url=item.url,\n"
        "                        )\n"
        "                        await self._notification_service.enqueue_tweet_notification(\n"
        "                            app_user_id,\n"
        "                            tweet,\n"
        "                            list_type=list_type.value,\n"
        "                        )",
    )
    (ROOT / "app/monitoring/polling_engine.py").write_text(pe, encoding="utf-8")
    print("patched polling_engine")

# monitoring_engine
me = (ROOT / "app/monitoring/monitoring_engine.py").read_text(encoding="utf-8")
if "notification_service" not in me:
    me = me.replace(
        "    def __init__(self, settings: Settings, repository: RedisRepository) -> None:",
        "    def __init__(self, settings: Settings, repository: RedisRepository, notification_service=None) -> None:",
    )
    me = me.replace(
        "            self._metrics,\n        )",
        "            self._metrics,\n            notification_service=notification_service,\n        )",
    )
    (ROOT / "app/monitoring/monitoring_engine.py").write_text(me, encoding="utf-8")
    print("patched monitoring_engine")

# factory
fa = (ROOT / "app/factory.py").read_text(encoding="utf-8")
if "notification_engine" not in fa:
    fa = fa.replace(
        "    monitoring_engine = None\n",
        "    monitoring_engine = None\n    notification_engine = None\n",
    )
    insert = """
    if settings.NOTIFICATIONS_ENABLED:
        from app.notifications.engine import NotificationEngine
        from app.repositories.redis_repository import RedisRepository as _RedisRepository

        notification_engine = NotificationEngine(settings, _RedisRepository(redis_manager), redis_manager)
        notification_engine.start()
        app.state.notification_engine = notification_engine

"""
    fa = fa.replace(
        "    if settings.MONITORING_ENABLED:",
        insert + "    if settings.MONITORING_ENABLED:",
    )
    fa = fa.replace(
        "        monitoring_engine = MonitoringEngine(settings, RedisRepository(redis_manager))",
        "        notification_service = notification_engine.service if notification_engine is not None else None\n"
        "        monitoring_engine = MonitoringEngine(\n"
        "            settings,\n"
        "            RedisRepository(redis_manager),\n"
        "            notification_service=notification_service,\n"
        "        )",
    )
    fa = fa.replace(
        "    if monitoring_engine is not None:\n        await monitoring_engine.shutdown()\n",
        "    if notification_engine is not None:\n        await notification_engine.shutdown()\n\n"
        "    if monitoring_engine is not None:\n        await monitoring_engine.shutdown()\n",
    )
    (ROOT / "app/factory.py").write_text(fa, encoding="utf-8")
    print("patched factory")

# health_service
hs = (ROOT / "app/services/health_service.py").read_text(encoding="utf-8")
if "notification_engine" not in hs:
    hs = hs.replace(
        "        monitoring_engine=None,\n    ) -> None:",
        "        monitoring_engine=None,\n        notification_engine=None,\n    ) -> None:",
    )
    hs = hs.replace(
        "        self._monitoring_engine = monitoring_engine\n",
        "        self._monitoring_engine = monitoring_engine\n        self._notification_engine = notification_engine\n",
    )
    block = """
        if self._settings.NOTIFICATIONS_ENABLED:
            if self._notification_engine is None:
                checks[\"notifications\"] = HealthCheckItem(status=\"unavailable\", detail=\"Engine not initialized\")
                overall = \"degraded\" if overall == \"ok\" else overall
            else:
                status = await self._notification_engine.status()
                ok = status.get(\"worker_running\") or not self._settings.NOTIFICATIONS_WORKER_ENABLED
                checks[\"notifications\"] = HealthCheckItem(
                    status=\"ok\" if ok else \"degraded\",
                    detail=f\"queue_depth={status.get('queue_depth', {})}\",
                )
                if not ok:
                    overall = \"degraded\"
        else:
            checks[\"notifications\"] = HealthCheckItem(status=\"disabled\", detail=\"NOTIFICATIONS_ENABLED=false\")

"""
    hs = hs.replace("        return HealthData(", block + "\n        return HealthData(")
    (ROOT / "app/services/health_service.py").write_text(hs, encoding="utf-8")
    print("patched health_service")

# dependencies health
dep = (ROOT / "app/core/dependencies.py").read_text(encoding="utf-8")
if "_notification_engine_from_request" not in dep:
    dep = dep.replace(
        "def _monitoring_engine_from_request(request: Request):\n"
        "    return getattr(request.app.state, \"monitoring_engine\", None)\n",
        "def _monitoring_engine_from_request(request: Request):\n"
        "    return getattr(request.app.state, \"monitoring_engine\", None)\n\n\n"
        "def _notification_engine_from_request(request: Request):\n"
        "    return getattr(request.app.state, \"notification_engine\", None)\n",
    )
    dep = dep.replace(
        "        monitoring_engine=_monitoring_engine_from_request(request),\n    )",
        "        monitoring_engine=_monitoring_engine_from_request(request),\n"
        "        notification_engine=_notification_engine_from_request(request),\n    )",
    )
    (ROOT / "app/core/dependencies.py").write_text(dep, encoding="utf-8")
    print("patched dependencies")

# jobs.py simplify
jobs = (ROOT / "app/notifications/jobs.py").read_text(encoding="utf-8")
if "get_tweet_for_notification" in jobs:
    jobs = '''from __future__ import annotations

import logging

from app.core.config import Settings
from app.models.x.tweet import FilteredTweet
from app.notifications.service import NotificationService
from app.repositories.x_processed_tweet_repository import ProcessedTweetRepository

logger = logging.getLogger(__name__)


class NotificationJobs:
    def __init__(
        self,
        settings: Settings,
        processed_repo: ProcessedTweetRepository,
        notification_service: NotificationService,
    ) -> None:
        self._settings = settings
        self._processed_repo = processed_repo
        self._notification_service = notification_service

    async def process_pending(self, app_user_id: str, *, limit: int = 50) -> dict:
        pending = await self._processed_repo.list_pending(app_user_id, limit=limit)
        enqueued = 0
        skipped = 0
        for item in pending:
            record = item["record"]
            meta = item.get("meta") or {}
            list_type = meta.get("list_type", "following")
            created_at = record.tweet_created_at or record.processed_time
            url = record.url or f"https://x.com/i/web/status/{record.tweet_id}"
            tweet = FilteredTweet(
                tweet_id=record.tweet_id,
                author_id=record.author_id,
                username=record.username or record.author_id,
                text="",
                created_at=created_at,
                url=url,
            )
            ok = await self._notification_service.enqueue_tweet_notification(
                app_user_id,
                tweet,
                list_type=list_type,
            )
            if ok:
                enqueued += 1
            else:
                skipped += 1
        summary = {"app_user_id": app_user_id, "pending_scanned": len(pending), "enqueued": enqueued, "skipped": skipped}
        logger.info("notification_pending_processed", extra=summary)
        return summary
'''
    (ROOT / "app/notifications/jobs.py").write_text(jobs, encoding="utf-8")
    print("patched jobs")

# engine.py jobs init
eng = (ROOT / "app/notifications/engine.py").read_text(encoding="utf-8")
if "tweet_service" in eng:
    eng = eng.replace(
        "from app.services.x_tweet_service import XTweetService\nfrom app.services.x_token_service import XTokenService\n"
        "from app.infrastructure.x.rate_limit_state import XRateLimitStateStore\nfrom app.infrastructure.x.token_store import XTokenStore\n",
        "",
    )
    eng = eng.replace(
        "        token_store = XTokenStore(repository, settings)\n"
        "        token_service = XTokenService(settings, token_store)\n"
        "        rate_limit_store = XRateLimitStateStore(repository)\n"
        "        tweet_service = XTweetService(settings, token_service, rate_limit_store, processed_repo)\n"
        "        self._jobs = NotificationJobs(settings, processed_repo, self._service, tweet_service)\n",
        "        self._jobs = NotificationJobs(settings, processed_repo, self._service)\n",
    )
    (ROOT / "app/notifications/engine.py").write_text(eng, encoding="utf-8")
    print("patched engine")

# .env.example
env = (ROOT / ".env.example").read_text(encoding="utf-8")
if "NOTIFICATIONS_ENABLED" not in env:
    env = env.rstrip() + "\n\nNOTIFICATIONS_ENABLED=true\nNOTIFICATIONS_WORKER_ENABLED=true\nNOTIFICATIONS_QUEUE_NAME=notifications:jobs\nNOTIFICATIONS_RETRY_MAX_ATTEMPTS=5\nNOTIFICATIONS_RETRY_BASE_DELAY_SECONDS=60\nNOTIFICATIONS_FAILURE_QUEUE_TTL_SECONDS=2592000\nNOTIFICATIONS_HISTORY_TTL_SECONDS=604800\nNOTIFICATIONS_BATCH_WINDOW_SECONDS=30\nNOTIFICATIONS_BATCH_MAX_SIZE=5\nNOTIFICATIONS_WORKER_CONCURRENCY=2\nNOTIFICATIONS_TELEGRAM_RATE_PER_CHAT=1.0\nNOTIFICATIONS_TELEGRAM_RATE_GLOBAL=25.0\nTELEGRAM_BOT_TOKEN=\n"
    (ROOT / ".env.example").write_text(env + "\n", encoding="utf-8")
    print("patched env")