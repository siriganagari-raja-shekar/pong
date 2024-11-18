from enum import Enum
import pygame

class PlayerNum(Enum):
    ONE = 1
    TWO = 2


PLAYER_KEY_BINDINGS = { 
    PlayerNum.ONE : { "left": pygame.K_a, "right": pygame.K_d}, 
    PlayerNum.TWO : { "left": pygame.K_LEFT, "right": pygame.K_RIGHT}
}

COLORS = {
    "white" : (255, 255, 255),
    "black" : (0, 0, 0),
    "red" : (255, 0, 0),
    "blue" : (0, 0, 255)
}
