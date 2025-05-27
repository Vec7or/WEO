trait Factory {
    fn create_instance(&self) -> Option<Self::Item>;
}

struct OrchestratorFactory {
    orchestrator: Option<Orchestrator>,
}

impl Factory for OrchestratorFactory {
    type Item = Orchestrator;

    fn create_instance(&self) -> Option<Self::Item> {
        match &self.orchestrator {
            Some(Orchestrator::Docker) => Some(Orchestrator::Docker),
            Some(Orchestrator::WSL) => Some(Orchestrator::WSL),
            _ => None,
        }
    }
}

impl OrchestratorFactory {
    #[cfg(target_os = "windows")]
    fn new(orchestrator: Option<Orchestrator>) -> Self {
        OrchestratorFactory { orchestrator }
    }

    #[cfg(target_os = "linux")]
    fn new(orchestrator: Option<Orchestrator>) -> Self {
        OrchestratorFactory { orchestrator }
    }
}