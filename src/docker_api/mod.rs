#[cfg(target_os = "windows")]
mod windows_docker_api;
#[cfg(target_os = "windows")]
use windows_docker_api::WindowsDockerApi;
#[cfg(target_os = "linux")]
mod linux_docker_api;
#[cfg(target_os = "linux")]
use linux_docker_api::LinuxDockerApi;

trait DockerApiTrait {
    fn new() -> Self;
}

pub struct DockerApi {
    #[cfg(target_os = "windows")]
    instance: WindowsDockerApi,
    #[cfg(target_os = "linux")]
    instance: LinuxDockerApi,
}

impl DockerApi {
    pub fn new() -> Self {
        #[cfg(target_os = "windows")]
        let instance = WindowsDockerApi::new();
        #[cfg(target_os = "linux")]
        let instance = LinuxDockerApi::new();
        Self { instance }
    }

    // Define common methods for Docker API
}