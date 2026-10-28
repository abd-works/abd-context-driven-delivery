"""A folder a spec rewrites on every run."""

from __future__ import annotations

import os
import shutil
import stat
import time
from pathlib import Path


class OutputFolder:
    """Clears a spec's output folder, waiting out files Windows still holds for deletion."""

    ATTEMPTS = 50
    PAUSE_SECONDS = 0.1

    def __init__(self, path: Path) -> None:
        self.path = path

    def clear(self) -> None:
        if self.path.exists():
            shutil.rmtree(self.path, onexc=self._remove_when_released)

    def _remove_when_released(self, remove, target: str, _error: BaseException) -> None:
        for _ in range(self.ATTEMPTS):
            try:
                os.chmod(target, stat.S_IWRITE)
                remove(target)
                return
            except FileNotFoundError:
                return
            except PermissionError:
                time.sleep(self.PAUSE_SECONDS)
        remove(target)
