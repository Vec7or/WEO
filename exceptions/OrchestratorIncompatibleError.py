from exceptions.OrchestratorError import OrchestratorError


class OrchestratorIncompatibleError(OrchestratorError):
    def __init__(self, message="Orchestrator version is incompatible"):
        super().__init__(message)
