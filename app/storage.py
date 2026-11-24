"""Small JSON persistence layer. Writes replace files atomically within one process."""
import json
import os
import tempfile
from pathlib import Path
from threading import RLock

STORE_LOCK = RLock()


class JsonStore:
    def __init__(self, path: str | Path, default):
        self.path = Path(path)
        self.default = default

    def read(self):
        with STORE_LOCK:
            if not self.path.exists():
                return self.default.copy()
            try:
                with self.path.open(encoding="utf-8") as f:
                    value = json.load(f)
            except (json.JSONDecodeError, OSError) as exc:
                raise RuntimeError(f"Cannot read valid JSON from {self.path}") from exc
            if not isinstance(value, list):
                raise RuntimeError(f"Expected a JSON list in {self.path}")
            return value

    def write(self, records):
        with STORE_LOCK:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            fd, temp_name = tempfile.mkstemp(prefix=f".{self.path.name}.", dir=self.path.parent)
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    json.dump(records, f, indent=2, ensure_ascii=False)
                    f.write("\n")
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(temp_name, self.path)
            finally:
                if os.path.exists(temp_name):
                    os.unlink(temp_name)
