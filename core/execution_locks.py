import os
from contextlib import contextmanager
from pathlib import Path
from time import sleep, time

from settings import PROJECT_ROOT


LOCK_STALE_SECONDS = 6 * 60 * 60
LOCK_WAIT_SECONDS = 30 * 60


@contextmanager
def named_execution_lock(name, lock_dir=None):
    lock_root = Path(lock_dir or PROJECT_ROOT / ".pipeline-locks")
    lock_root.mkdir(parents=True, exist_ok=True)
    lock_path = lock_root / f"{_safe_lock_name(name)}.lock"
    started = time()

    while True:
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w", encoding="utf-8") as lock_file:
                lock_file.write(str(os.getpid()))
            break
        except FileExistsError:
            try:
                if time() - lock_path.stat().st_mtime > LOCK_STALE_SECONDS:
                    lock_path.unlink()
                    continue
            except FileNotFoundError:
                continue
            if time() - started > LOCK_WAIT_SECONDS:
                raise TimeoutError(f"Tempo excedido aguardando lock: {name}")
            sleep(1)

    try:
        yield
    finally:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


def _safe_lock_name(name):
    return "".join(
        character if character.isalnum() or character in {"_", "-", "."} else "_"
        for character in str(name)
    ).strip("_") or "pipeline"


__all__ = ["named_execution_lock"]
