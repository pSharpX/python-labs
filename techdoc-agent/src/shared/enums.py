from enum import Enum


class Stage(str, Enum):
    INITIALIZE = "initialize"
    REQUIREMENTS = "requirements"
    TECHNICAL_ARCHITECTURE = "technical_architecture"
    FINANCIAL_ESTIMATION = "financial_estimation"
    APPROVAL = "approval"
    DONE = "done"

class UserAction(str, Enum):
    APPROVE = "approve"
    REQUEST_CHANGES = "request_changes"  # change the financial estimate
    CHANGE_REQUIREMENTS = "change_requirements"  # change the customer requirements
    PROVIDE_INFORMATION = "provide_information"  # answer the analyst's questions