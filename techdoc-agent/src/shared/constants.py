from typing import Literal

Priority = Literal["must", "should", "could", "to_be_defined"]
Criticality = Literal["critical", "important", "desirable"]
AnalysisStatus = Literal["analyzing", "awaiting_client_information", "ready_for_architecture"]

STATUS_PRIORITY = {
    "analyzing": 1,
    "awaiting_client_information": 2,
    "ready_for_architecture": 3,
}

ServiceCategory = Literal[
    "Assessment",
    "Implementación",
    "Migración",
    "Consultoría",
    "Seguridad",
    "Desarrollo IA",
    "Continuidad",
    "Compliance",
    "Consultoría / Desarrollo",
    "Desarrollo",
    "Workshop",
    "Soporte",
    "Seguridad / Consultoría",
    "Outsourcing",
    "Recruiting",
    "Managed Service",
    "Licenciamiento",
    "Capacitación",
]