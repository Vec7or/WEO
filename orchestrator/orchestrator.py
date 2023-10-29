import os
import re
import secrets
import string
import random
from tempfile import TemporaryDirectory

from semver import Version

from config.version import WEO_VERSION
from config.weo_config import WeoConfig
from config.wsl_config import WslConfig
from exceptions.EnvironmentExistsError import EnvironmentExistsError
from exceptions.EnvironmentNotFoundError import EnvironmentNotFoundError
from exceptions.ImageNotSupportedError import ImageNotSupportedError
from exceptions.OrchestratorIncompatibleError import OrchestratorIncompatibleError
from exceptions.UserNotFoundError import UserNotFoundError
from wsl.docker_daemon import DockerDaemon
from wsl.wsl_api import WslApi


class Orchestrator:

    def __init__(self, orchestrator_instance_name: str, wsl_api: WslApi):
        self._instance_name = orchestrator_instance_name
        self._wsl_api = wsl_api
        self._rootfs_file_name = "rootfs.tar.bz2"

    def _prepare_dockerfile(self, docker_image: str, local: str | None, target_dir: str):
        if not local:
            self._wsl_api.run_command_in_instance(
                self._instance_name, f"cd {target_dir} && echo 'FROM {docker_image}' > Dockerfile")
            return
        docker_image = os.path.abspath(docker_image)
        match local:
            case "FILE":
                self._wsl_api.run_command_in_instance(
                    self._instance_name,
                    f"cd {target_dir} && cp {WslApi.linuxify(docker_image)} Dockerfile"
                )
            case "DIR":
                if docker_image[-1] == "/" or docker_image[-1] == "\\":
                    docker_image = docker_image[:-1]
                docker_image = docker_image + "/*"
                self._wsl_api.run_command_in_instance(
                    self._instance_name,
                    f"cd {target_dir} && cp -r {WslApi.linuxify(docker_image)} ./"
                )
            case _:
                raise RuntimeError("Unexpected local value")

    def _create_image(self, tmp_docker_tag: str, target_dir: str) -> None:
        with DockerDaemon(self._instance_name):
            self._wsl_api.run_command_in_instance(self._instance_name,
                                                  f"cd '{target_dir}' && docker build -t {tmp_docker_tag} .")

    def _get_docker_user(self, tmp_docker_tag: str) -> str:
        with DockerDaemon(self._instance_name):
            user = self._wsl_api.run_command_in_instance(self._instance_name,
                                                         "docker image inspect --format '{{.Config.User}}' " + str(
                                                             tmp_docker_tag))
        if user.strip() == "":
            user = "root"
        return user

    def _get_rootfs(self, tmp_docker_tag: str, target_dir: str) -> None:
        with DockerDaemon(self._instance_name):
            container_id = self._wsl_api.run_command_in_instance(self._instance_name,
                                                                 f"docker create {tmp_docker_tag}")
            container_id = container_id.strip()
            self._wsl_api.run_command_in_instance(self._instance_name,
                                                  f"docker build -t {tmp_docker_tag} {target_dir} && "
                                                  f"docker export {container_id} -o {target_dir}/rootfs.tar.gz && "
                                                  f"mkdir {target_dir}/rootfs && "
                                                  f"tar -xf {target_dir}/rootfs.tar.gz  -C {target_dir}/rootfs/ && "
                                                  f"docker remove {container_id}")

    def _config_rootfs(self, lnx_tmp_dir: str, user: str, docker_image: str, local: str | None):
        wsl_config = WslConfig(
            self._wsl_api,
            self._instance_name,
            f"{lnx_tmp_dir}/rootfs{WslConfig.CONFIG_PATH}")
        wsl_config.user = user
        weo_config = WeoConfig(
            self._wsl_api,
            self._instance_name,
            f"{lnx_tmp_dir}/rootfs{WeoConfig.CONFIG_PATH}")
        weo_config.version = WEO_VERSION
        weo_config.base_image = docker_image
        if local:
            weo_config.base_image_local = "true"
        else:
            weo_config.base_image_local = "false"

        wsl_config.write_config()
        weo_config.write_config()

    def _change_password_rootfs(self, lnx_tmp_dir: str, user: str, password: str):
        passwd_file_path = f"{lnx_tmp_dir}/rootfs/etc/passwd"
        shadow_file_path = f"{lnx_tmp_dir}/rootfs/etc/shadow"
        passwd_file_exists = self._wsl_api.file_exists_in_instance(self._instance_name, passwd_file_path)
        shadow_file_exists = self._wsl_api.file_exists_in_instance(self._instance_name, shadow_file_path)
        if not passwd_file_exists or not shadow_file_exists:
            raise ImageNotSupportedError()

        user_line = self._wsl_api.run_command_in_instance(
            self._instance_name,
            f"cat {passwd_file_path} | grep {user}")
        user_line = user_line.strip()
        p = re.compile('(?P<username>[^:]*):(?P<shadow_value>[^:]*)(?P<rest>.*$)')
        result = p.match(user_line)
        if not result:
            raise UserNotFoundError()
        new_line = result.group("username") + ":x" + result.group("rest")
        new_line = re.escape(new_line)
        new_line = new_line.replace("/", "\\/")
        user_line = re.escape(user_line)
        user_line = user_line.replace("/", "\\/")
        self._wsl_api.run_command_in_instance(
            self._instance_name,
            f"sed -i 's/^.*{user_line}.*$/{new_line}/' {passwd_file_path}")

        salt = secrets.token_urlsafe(nbytes=30)
        password = password.replace('"', '\\"')
        passwd_line = self._wsl_api.run_command_in_instance(
            self._instance_name,
            f"mkpasswd -m sha512 -S {salt} \"{password}\"")
        passwd_line = passwd_line.strip()
        shadow_line = self._wsl_api.run_command_in_instance(
            self._instance_name,
            f"cat {shadow_file_path} | grep {user}")
        shadow_line = shadow_line.strip()
        p = re.compile('(?P<username>[^:]*):(?P<shadow_value>[^:]*)(?P<rest>.*$)')
        result = p.match(shadow_line)
        new_line = result.group("username") + f":{passwd_line}" + result.group("rest")
        new_line = re.escape(new_line)
        new_line = new_line.replace("/", "\\/")
        shadow_line = re.escape(shadow_line)
        shadow_line = shadow_line.replace("/", "\\/")
        self._wsl_api.run_command_in_instance(
            self._instance_name,
            f"sed -i 's/^.*{shadow_line}.*$/{new_line}/' {shadow_file_path}")

    def _pack_rootfs(self, tmp_dir: str):
        self._wsl_api.run_command_in_instance(self._instance_name,
                                              f"cd '{tmp_dir}' && tar -cjf {self._rootfs_file_name} -C rootfs .")

    def _move_rootfs(self, src_dir: str, target_dir: str):
        self._wsl_api.run_command_in_instance(self._instance_name,
                                              f"cd {src_dir} && mv {self._rootfs_file_name} {WslApi.linuxify(target_dir)}")

    def _cleanup_docker(self):
        with DockerDaemon(self._instance_name):
            self._wsl_api.run_command_in_instance(self._instance_name,
                                                  "echo y | docker system prune -a")

    def create(self, docker_image: str, environment_name: str, local: str | None, environment_password: str,
               user: str | None = None) -> None:
        if self._wsl_api.instance_exists(environment_name):
            raise EnvironmentExistsError()
        tmp_docker_tag = "weo:" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
        with TemporaryDirectory() as temp_dir:
            lnx_tmp_dir = '/tmp/' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            self._wsl_api.run_command_in_instance(self._instance_name, f"mkdir -p {lnx_tmp_dir}")
            try:
                self._prepare_dockerfile(docker_image, local, lnx_tmp_dir)
                self._create_image(tmp_docker_tag, lnx_tmp_dir)
                if not user:
                    user = self._get_docker_user(tmp_docker_tag)
                self._get_rootfs(tmp_docker_tag, lnx_tmp_dir)
                self._config_rootfs(lnx_tmp_dir, user, docker_image, local)
                self._change_password_rootfs(lnx_tmp_dir, user, environment_password)
                self._pack_rootfs(lnx_tmp_dir)
                self._move_rootfs(lnx_tmp_dir, temp_dir)
                rootfs_image = os.path.join(temp_dir, self._rootfs_file_name)
                self._wsl_api.create_instance(environment_name, rootfs_image)

            finally:
                self._wsl_api.run_command_in_instance(self._instance_name, f"rm -r {lnx_tmp_dir}")
                self._cleanup_docker()

    def remove(self, environment_name: str) -> None:
        if not self._wsl_api.instance_exists(environment_name):
            raise EnvironmentNotFoundError()
        weo_config = WeoConfig(self._wsl_api, environment_name)
        weo_config.read_config()
        if not Version.is_compatible(Version.parse(WEO_VERSION), Version.parse(weo_config.version)):
            raise OrchestratorIncompatibleError()
        self._wsl_api.remove_instance(environment_name)
