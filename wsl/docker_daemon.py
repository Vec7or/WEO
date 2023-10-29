import os
import subprocess
import tempfile

class DockerdScript:

    def __init__(self):
        self._file_path = None

    def __enter__(self):
        file = tempfile.NamedTemporaryFile(delete=False, delete_on_close=False)
        file.write(self._script().encode())
        self._file_path = file.name
        file.close()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.remove(self._file_path)

    def get_path(self) -> str:
        return self._file_path

    @staticmethod
    def _script() -> str:
        return """#!/bin/sh
nohup dockerd &
bg %1
"""


class DockerDaemon:
    def __init__(self, instance_name: str):
        self.task = None
        self._instance_name = instance_name

    @property
    def stdout(self):
        return self.task.stdout.read()

    @property
    def stderr(self):
        return self.task.stderr.read()

    def __enter__(self):
        self.task = subprocess.Popen(
            ['wsl.exe', '-u', "root", '-d', self._instance_name, "/usr/bin/dockerd"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.task.terminate()
