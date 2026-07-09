"""Monitoring engine package."""

from app.monitoring.models import JobType, JobPayload, JobStatus

__all__ = ["JobType", "JobPayload", "JobStatus"]


def get_monitoring_engine_class():
    from app.monitoring.monitoring_engine import MonitoringEngine

    return MonitoringEngine
