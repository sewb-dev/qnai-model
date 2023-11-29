from enum import Enum


class GenerationStatus(Enum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"


class Environment(Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "test"
