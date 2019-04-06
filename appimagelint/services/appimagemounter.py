import os
import shlex
import subprocess

from ..models import AppImage
from .._logging import make_logger


class AppImageMounter:
    _logger = make_logger("appimagemounter")

    def __init__(self, appimage: AppImage, custom_runtime_path: str = None):
        self._appimage = appimage
        self._custom_runtime = custom_runtime_path

        self._mountpoint: str = None
        self._proc: subprocess.Popen = None

    def mountpoint(self):
        return self._mountpoint

    def mount(self):
        self._logger.debug("mounting AppImage {}".format(self._appimage.path()))

        env = dict(os.environ)

        if self._custom_runtime:
            self._logger.debug("using custom runtime to mount AppImage")
            env["TARGET_APPIMAGE"] = os.path.abspath(self._appimage.path())
            args = [self._custom_runtime]
        else:
            args = [self._appimage.path()]

        args.append("--appimage-mount")

        self._logger.debug("calling {}".format(" ".join((shlex.quote(i) for i in args))))
        self._proc = subprocess.Popen(args, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self._logger.debug("process ID: {}".format(self._proc.pid))

        while True:
            # it's an error if we couldn't read the mountpoint from stdout but the process terminated
            if self._proc.poll() is not None:
                raise OSError("process exited before we could read AppImage mountpoint"
                              "(exit code {})".format(self._proc.poll()))

            line = self._proc.stdout.readline().decode().strip(" \t\n")
            self._logger.debug("read line from stdout: {}".format(line))

            if os.path.exists(line):
                self._mountpoint = line
                break

        self._logger.debug("mount path: {}".format(self._mountpoint))

    def unmount(self):
        self._logger.debug("unmounting AppImage")

        try:
            self._proc.terminate()
            retcode = self._proc.wait(5)
        except subprocess.TimeoutExpired:
            self._logger.debug("failed to terminate process normally, killing")

            try:
                self._proc.kill()
                retcode = self._proc.wait(12)
            except subprocess.TimeoutExpired:
                self._logger.debug("failed to kill process")
            raise

        # TODO: check error code

    def __enter__(self) -> str:
        self.mount()
        return self.mountpoint()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unmount()
        self._mountpoint = None
