import pygame
from .player import Player
from .shared_resources import PlayerNum
import time
import threading

class Ball:

    def __init__(self, window_width, limitTop, limitBottom, startPlayer:Player) -> None:
        self.radius = 7.5
        self.limitX = window_width
        self.limitTop = limitTop
        self.limitBottom = limitBottom
        self.speed = pygame.Vector2(3, 3)
        self.startPlayer = startPlayer
        self.rect = self.getStartPos()
        self.last_touched_player_id = self.startPlayer.id
        self.isReleased = False
        self.unReleasedSpeed = pygame.Vector2(1, 0)
        self.coordinator_thread = threading.Thread(target=self.speed_coordinator, args=(10,), daemon=True)
    
    def move(self):
        if not self.isReleased:
            xLeftLimit, xRightLimit = self.radius, self.startPlayer.width - self.radius
            currX = self.rect.centerx - self.startPlayer.getRect().x
            if currX + self.unReleasedSpeed.x > xRightLimit:
                self.unReleasedSpeed.x = -1
            elif currX + self.unReleasedSpeed.x < xLeftLimit: 
                self.unReleasedSpeed.x = 1

            self.rect.centerx = int(self.unReleasedSpeed.x) + self.startPlayer.getRect().x + currX
            if self.startPlayer.isMoving:
                if self.startPlayer.direction == "right":
                    self.rect.centerx += self.startPlayer.speed
                else:
                    self.rect.centerx -= self.startPlayer.speed
            return
        if self.rect.centerx + self.speed.x > self.limitX - self.radius or self.rect.centerx + self.speed.x < self.radius:
            self.speed.x = -self.speed.x
        self.rect.centerx += int(self.speed.x)
        self.rect.centery += int(self.speed.y)

    def checkOutOfBounds(self):

        if self.rect.centery > self.limitBottom - self.radius or self.rect.centery < self.limitTop + self.radius:
            return True
        else:
            return False

    def deflectBall(self, player: Player):
        if player.player_num == PlayerNum.ONE:
            self.last_touched_player_id = 1
            normal = pygame.Vector2(0, 1)
        elif player.player_num == PlayerNum.TWO:
            self.last_touched_player_id = 2
            normal = pygame.Vector2(0, -1)
        else:
            normal = None

        if normal:
            self.speed.reflect_ip(normal)

    def releaseBall(self):
        self.isReleased = True
        self.deflectBall(self.startPlayer)
        # self.coordinator_thread.start()

    def getX(self):
        return self.rect.centerx

    def getY(self):
        return self.rect.centery
    
    def getRadius(self):
        return self.radius

    def getRect(self):
        return self.rect

    def getStartPos(self):
        
        xCord = self.startPlayer.getRect().x
        yCord = self.startPlayer.getRect().y + self.startPlayer.height if self.startPlayer.player_num == PlayerNum.ONE else self.startPlayer.getRect().y - self.startPlayer.height - self.radius
        return pygame.Rect(xCord, yCord, self.radius * 2, self.radius * 2)
    
    def countdown(self, number_of_seconds):
        while number_of_seconds:
            time.sleep(1)
            number_of_seconds -= 1

    def increaseBallSpeed(self):
        if self.speed.x < 0:
            self.speed.x += -1
        else:
            self.speed.x += 1

        if self.speed.y < 0:
            self.speed.y += -1
        else:
            self.speed.y += 1

    def speed_coordinator(self, number_of_seconds):

        while True:
            countdown_thread = threading.Thread(target=self.countdown, args=(number_of_seconds, ), daemon = True)
            worker_thread = threading.Thread(target=self.increaseBallSpeed, args=(countdown_thread, ), daemon=True)

            countdown_thread.start()
            worker_thread.start()

            worker_thread.join()



