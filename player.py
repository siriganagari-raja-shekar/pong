from player_key_mappings import PlayerNum
from player_key_mappings import player_key_mappings
import pygame

class Player:

    def __init__(self, id, window_width, window_height, player_num, heading_buffer):
        
        self.id = id
        self.width = 50
        self.height = 7.5
        self.limit_left = 0
        self.limit_right = window_width
        self.speed = 3
        self.border_radius = 10
        self.isMoving = False
        self.direction = ""
        self.key_mappings = player_key_mappings[player_num]
        self.rect = pygame.Rect(window_width//2 - self.width//2, heading_buffer + 2 if player_num == PlayerNum.ONE else window_height - self.height, self.width, self.height)
        self.player_num = player_num
        self.color = (255, 0, 0) if player_num is PlayerNum.ONE else (0, 0, 255)
        self.heading_buffer = heading_buffer

    def movePlayer(self):

        if self.isMoving:
            delta = 1
            if self.direction == "left":
                self.rect.x -= min(self.speed, self.rect.x - delta)
            else:
                self.rect.x += min(self.speed, self.limit_right - self.rect.x - self.width - delta)


    def getRect(self):
        return self.rect

    def turnLeft(self):
        self.isMoving = True
        self.direction = "left"

    def turnRight(self):
        self.isMoving = True
        self.direction = "right"

    def stopMoving(self):
        self.isMoving = False
