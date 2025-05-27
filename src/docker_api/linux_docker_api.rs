use super::DockerApiTrait;

pub(super) struct LinuxDockerApi {
}

impl DockerApiTrait for LinuxDockerApi {
    fn new() -> Self {
        Self {}
    }
}