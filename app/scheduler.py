import threading
from datetime import datetime, timezone
from time import sleep

from app.config import scheduler_horizon_values, settings
from app.db import SessionLocal
from app.materialization import materialize_full_run


class SchedulerState:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.started = False
        self.last_run_started_at: str | None = None
        self.last_run_finished_at: str | None = None
        self.last_status: str = "idle"
        self.last_error: str | None = None
        self.run_count: int = 0

    def snapshot(self) -> dict:
        with self.lock:
            return {
                "enabled": settings.scheduler_enabled,
                "started": self.started,
                "interval_seconds": settings.scheduler_interval_seconds,
                "horizons": scheduler_horizon_values(),
                "last_run_started_at": self.last_run_started_at,
                "last_run_finished_at": self.last_run_finished_at,
                "last_status": self.last_status,
                "last_error": self.last_error,
                "run_count": self.run_count,
            }


class MaterializationScheduler:
    def __init__(self) -> None:
        self.state = SchedulerState()
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def start(self) -> None:
        if not settings.scheduler_enabled or self.state.started:
            return
        self._stop_event.clear()
        self.state.started = True
        self.state.last_status = "starting"
        self._thread = threading.Thread(target=self._run_loop, name="materialization-scheduler", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if not self.state.started:
            return
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        self.state.started = False
        self.state.last_status = "stopped"

    def run_once(self) -> dict:
        with self.state.lock:
            self.state.last_run_started_at = datetime.now(timezone.utc).isoformat()
            self.state.last_status = "running"
            self.state.last_error = None
        db = SessionLocal()
        try:
            summary = materialize_full_run(db, scheduler_horizon_values())
        except Exception as exc:
            db.rollback()
            with self.state.lock:
                self.state.last_run_finished_at = datetime.now(timezone.utc).isoformat()
                self.state.last_status = "failed"
                self.state.last_error = str(exc)
            raise
        finally:
            db.close()
        with self.state.lock:
            self.state.last_run_finished_at = datetime.now(timezone.utc).isoformat()
            self.state.last_status = "success"
            self.state.run_count += 1
        return summary

    def _run_loop(self) -> None:
        if settings.scheduler_run_on_startup and not self._stop_event.is_set():
            try:
                self.run_once()
            except Exception:
                pass
        while not self._stop_event.is_set():
            sleep(settings.scheduler_interval_seconds)
            if self._stop_event.is_set():
                break
            try:
                self.run_once()
            except Exception:
                pass


scheduler = MaterializationScheduler()
