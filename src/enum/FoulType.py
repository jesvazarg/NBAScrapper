from enum import Enum


class FoulType(Enum):
    SHOOTING = 'S'
    PERSONAL = 'P'
    LOOSE_BALL = 'L'
    OFFENSIVE = 'O'
    TECHNICAL = 'T'
    AWAY_FROM_PLAY = 'A'
    FLAGRANT = 'F'
