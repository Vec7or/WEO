enum OrchestratorType {
    WSL,
    Native,
}

struct Orchestrator {
    orchestrator_type: OrchestratorType,
}

impl Orchestrator {
    fn new(orchestrator_type: OrchestratorType) -> Self {
        Orchestrator { orchestrator_type }
    }

    fn orchestrate(&self) {
        match self.orchestrator_type {
            OrchestratorType::WSL => println!("Orchestrating with WSL..."),
            OrchestratorType::Native => println!("Orchestrating with Native..."),
        }
    }
}