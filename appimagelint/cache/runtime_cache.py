import os
import subprocess
import time

from appimagelint.cache import OutOfDateError, _get_logger
from .io import cache_timeout
from .paths import data_cache_path
from . import CacheBase


class AppImageRuntimeCache(CacheBase):
    @classmethod
    def _cached_runtime_path(cls):
        return os.path.join(data_cache_path(), "runtime")

    @classmethod
    def force_update(cls):
        path = cls._cached_runtime_path()

        try:
            subprocess.check_call([
                "wget", "-q", "https://github.com/AppImage/AppImageKit/releases/download/continuous/runtime-x86_64",
                "-O", path
            ])

            # no need to bother AppImageLauncher etc.
            os.chmod(path, 0o755)
            with open(path, "rb+") as f:
                f.seek(8)
                f.write(b"\x00\x00\x00")

        except Exception:
            # clean up data after exception if possible to make the tool force an update during the next run
            if os.path.exists(path):
                os.remove(path)

            raise


    @classmethod
    def get_data(cls, raise_on_error=False) -> str:
        logger = _get_logger()
        path = cls._cached_runtime_path()

        update_needed = False

        if not os.path.exists(path):
            logger.debug("AppImage runtime file not found")
            update_needed = True
        else:
            mtime = os.path.getmtime(cls._cached_runtime_path())
            if mtime + cache_timeout() < time.time():
                logger.debug("AppImage runtime older than cache timeout")
                update_needed = True

        if update_needed:
            try:
                logger.debug("updating AppImage runtime")
                cls.force_update()
            except Exception:
                # can be handled gracefully by the user, if required
                if raise_on_error:
                    raise
                else:
                    logger.warning("AppImage runtime needs update, but update failed, skipping")

        return path
