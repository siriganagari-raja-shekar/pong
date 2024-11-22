from enum import IntEnum
import pygame

class PlayerNum(IntEnum):
    ONE = 1
    TWO = 2


PLAYER_KEY_BINDINGS = { 
    PlayerNum.ONE : { "left": pygame.K_a, "right": pygame.K_d}, 
    PlayerNum.TWO : { "left": pygame.K_LEFT, "right": pygame.K_RIGHT}
}

MULTIPLAYER_KEY_BINDINGS = {
    "left": { pygame.K_a, pygame.K_LEFT},
    "right": { pygame.K_d, pygame.K_RIGHT},
    "release": pygame.K_SPACE
}
COLORS = {
    "white" : (255, 255, 255),
    "black" : (0, 0, 0),
    "red" : (255, 0, 0),
    "blue" : (0, 0, 255)
}
