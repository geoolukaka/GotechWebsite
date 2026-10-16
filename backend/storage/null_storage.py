import datetime
import itertools

from .base import SubmissionStorage


class NullStorage(SubmissionStorage):
    """STORAGE_BACKEND=none: no database. Inquiries go to WhatsApp only.

    Keeps a short in-memory list so /api/submissions still works until the
    server restarts. Nothing is written to disk.
    """

    durable = False

    def __init__(self, keep: int = 100):
        self._items = []
        self._keep = keep
        self._ids = itertools.count(1)

    def save_submission(self, data: dict) -> str:
        record_id = str(next(self._ids))
        self._items.append(
            {"id": record_id,
             "created_at": datetime.datetime.utcnow().isoformat() + "Z",
             **data}
        )
        self._items = self._items[-self._keep:]
        return record_id

    def list_submissions(self, limit: int = 50) -> list:
        return list(reversed(self._items))[:limit]
