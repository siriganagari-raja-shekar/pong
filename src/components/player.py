from .shared_resources import PlayerNum
from .shared_resources import PLAYER_KEY_BINDINGS
import pygame
import time
import threading

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
        self.key_mappings = PLAYER_KEY_BINDINGS[player_num]
        self.rect = pygame.Rect(window_width//2 - self.width//2, heading_buffer + 2 if player_num == PlayerNum.ONE else window_height - self.height, self.width, self.height)
        self.player_num = player_num
        self.color = (255, 0, 0) if player_num is PlayerNum.ONE else (0, 0, 255)
        self.heading_buffer = heading_buffer
        self.coordinator_thread = threading.Thread(target=self.speed_coordinator, args=(20,), daemon=True)

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

    
    def countdown(self, number_of_seconds):
        while number_of_seconds:
            time.sleep(1)
            number_of_seconds -= 1

    def increasePaddleSpeed(self):
        self.speed += 2    

    def resetPaddleSpeed(self):
        self.speed = 3    

    def speed_coordinator(self, number_of_seconds):

        while True:
            countdown_thread = threading.Thread(target=self.countdown, args=(number_of_seconds, ), daemon = True)
            worker_thread = threading.Thread(target=self.increasePaddleSpeed, args=(countdown_thread, ), daemon=True)

            countdown_thread.start()
            worker_thread.start()

            worker_thread.join()




