from enum import Enum


class MoveNotAvailableError(RuntimeError):
    pass


class EmptyFieldError(ValueError):
    pass


class Color(Enum):
    White = 'white'
    Black = 'black'


class Players(Enum):
    White = 0
    Black = 1


class States(Enum):
    IN_PROGRESS = 'IN_PROGRESS'
    PENDING = 'PENDING'

