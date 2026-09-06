import os
import platform
import subprocess
import time

from appimagelint.cache import _get_cache_logger
from .io import cache_timeout
from . import CacheBase


class AppImageRuntimeCache(CacheBase):
    _RUNTIME_ARCHITECTURES = {
        "aarch64": "aarch64",
        "amd64": "x86_64",
        "arm64": "aarch64",
        "x86_64": "x86_64",
    }

    @classmethod
    def _runtime_architecture(cls) -> str:
        machine = platform.machine().lower()

        try:
            return cls._RUNTIME_ARCHITECTURES[machine]
        except KeyError:
            raise RuntimeError(
                "unsupported host architecture {!r}; supported architectures are aarch64 and x86_64".format(machine)
            )

    @classmethod
    def _cache_file_name(cls) -> str:
        return "runtime-{}".format(cls._runtime_architecture())

    @classmethod
    def _find_cache_files(cls):
        yield from super()._find_cache_files()

        # AppImage runtimes used to be stored as simply "runtime". Continue to
        # accept that cache on x86_64, where it was the only runtime available.
        if cls._runtime_architecture() != "x86_64":
            return

        for directory, is_fallback in (
            (cls._user_cache_base_path(), False),
            (cls._bundled_cache_base_path(), True),
        ):
            legacy_path = os.path.join(directory, "runtime")
            if os.path.exists(legacy_path):
                yield legacy_path, is_fallback

    @classmethod
    def _cached_runtime_path(cls, save_to_bundled_cache: bool = False):
        if save_to_bundled_cache:
            cache_dir = cls._bundled_cache_base_path()
        else:
            cache_dir = cls._user_cache_base_path()

        return os.path.join(cache_dir, cls._cache_file_name())

    @classmethod
    def update_now(cls, save_to_bundled_cache: bool = False):
        path = cls._cached_runtime_path(save_to_bundled_cache=save_to_bundled_cache)
        architecture = cls._runtime_architecture()

        os.makedirs(os.path.dirname(path), exist_ok=True)

        try:
            subprocess.check_call([
                "wget", "-q", "https://github.com/AppImage/type2-runtime/releases/download/continuous/runtime-{}".format(
                    architecture
                ),
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
        logger = _get_cache_logger()

        runtime_path = None

        # this is somewhat pessimistic; but hey, you're free prove me wrong below!
        update_needed = False

        for path, is_fallback in cls._find_cache_files():
            if os.path.exists(path):
                # just a fancy debug message, we don't necessarily have to update, the file might be recent enough
                if is_fallback:
                    logger.debug("Found runtime in fallback cache")

                mtime = os.path.getmtime(path)

                if mtime + cache_timeout() < time.time():
                    logger.debug("Cached AppImage runtime older than cache timeout")
                    update_needed = True

                runtime_path = path
                break

        else:
            logger.debug("AppImage runtime file not found")
            update_needed = True

        if update_needed:
            try:
                logger.debug("updating AppImage runtime")
                cls.update_now(save_to_bundled_cache=False)

            except:
                # can be handled gracefully by the user, if required, unless there's no fallback
                if runtime_path is None or raise_on_error:
                    if runtime_path is None:
                        logger.error("runtime not found locally and failed to download and cache runtime")

                    raise

                else:
                    logger.warning("AppImage runtime needs update, but update failed, skipping")

            else:
                runtime_path = cls._cached_runtime_path(save_to_bundled_cache=False)

        return runtime_path
