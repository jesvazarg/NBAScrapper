from enum import Enum


class TurnoverType(Enum):
    LOST_BALL = 'LB'
    BAD_PASS = 'BP'
    TRAVELING = 'TR'
    STEP_OUT_OF_BOUNDS = 'SB'
    OFFENSIVE_FOUL = 'OF'
    SHOT_CLOCK = 'SC'
    OUT_OF_BOUNDS_LOST_BALL = 'OL'
    PALMING = 'PA'
