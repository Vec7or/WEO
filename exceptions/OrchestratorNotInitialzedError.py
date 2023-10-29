from exceptions.OrchestratorError import OrchestratorError


class OrchestratorNotInitializedError(OrchestratorError):
    def __init__(self, message="Orchestrator is already initialized"):
        super().__init__(message)
