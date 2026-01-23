import logging
import threading
import traceback
from collections import deque
from datetime import datetime, timezone
from itertools import count


class LogBuffer(logging.Handler):
    def __init__(self, max_entries=500):
        super().__init__()
        self._entries = deque(maxlen=max_entries)
        self._lock = threading.Lock()
        self._counter = count(1)

    def emit(self, record):
        try:
            timestamp = datetime.now(timezone.utc).isoformat()
            details = None
            if record.exc_info:
                details = "".join(traceback.format_exception(*record.exc_info)).strip()
            entry = {
                "id": f"{int(datetime.now().timestamp())}-{next(self._counter)}",
                "timestamp": timestamp,
                "level": record.levelname.lower(),
                "logger": record.name,
                "message": record.getMessage(),
                "details": details,
            }
            with self._lock:
                self._entries.append(entry)
        except Exception:
            # Avoid recursive logging failures
            pass

    def get_entries(self):
        with self._lock:
            return list(self._entries)

    def clear(self):
        with self._lock:
            self._entries.clear()


log_buffer = LogBuffer()
