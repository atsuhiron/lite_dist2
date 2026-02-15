from enum import StrEnum, auto


class StudyStatus(StrEnum):
    wait = auto()
    running = auto()
    done = auto()
    not_found = auto()
