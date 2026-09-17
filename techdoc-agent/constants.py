from typing import Literal

Priority = Literal["must", "should", "could", "to_be_defined"]
Criticality = Literal["critical", "important", "desirable"]
AnalysisStatus = Literal["analyzing", "awaiting_client_information", "ready_for_architecture"]

STATUS_PRIORITY = {
    "analyzing": 1,
    "awaiting_client_information": 2,
    "ready_for_architecture": 3,
}