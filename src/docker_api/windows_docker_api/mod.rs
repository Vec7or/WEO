mod windows_helper_instance;

use windows_helper_instance::WindowsHelperInstance;
use super::DockerApiTrait;

pub(super) struct WindowsDockerApi {
    windows_helper_instance: WindowsHelperInstance,
}

impl DockerApiTrait for WindowsDockerApi {
    fn new() -> Self {
        let instance = Self {
            windows_helper_instance: WindowsHelperInstance::new(),
        };
        return instance;
    }
}