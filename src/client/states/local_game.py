import pygame
from .base import BaseState
from components.player import Player
from components.shared_resources import PlayerNum
from components.ball import Ball
import random
import time
import threading

class LocalGame(BaseState):

    def __init__(self, **settings):
        BaseState.__init__(self, **settings)
        self.next = "end_game"
        self.heading_buffer = 70
        self.players = []
        self.ball = None
        self.score = dict()
        self.persist = dict()
        self.ball_sped_time = None
        self.player_sped_time = None

        self.ball_speed_increase_interval = 15
        self.player_speed_increase_interval = 15

    def cleanup(self):
        return self.persist

    def startup(self, persist):
        self.__resetGame()

    def __resetGame(self):
        self.players = [Player(1, self.size[0], self.size[1], PlayerNum.ONE, self.heading_buffer), Player(2, self.size[0], self.size[1], PlayerNum.TWO, self.heading_buffer)]
        self.ball = Ball(self.size[0], self.heading_buffer, self.size[1], self.players[random.randint(0, 1)])
        self.score = { player.id: 0 for player in self.players }
        self.persist = dict()
        self.ball_sped_time = None
        self.player_sped_time = None

    def __resetPlayerSpeeds(self):
        for player in self.players:
            player.resetPaddleSpeed()
        self.ball_sped_time = time.time()
        self.player_sped_time = time.time()


    def get_event(self, event):
        if event.type == pygame.KEYDOWN:

            for player in self.players:
                if player.key_mappings["left"] == event.key:
                    player.turnLeft()
                elif player.key_mappings["right"] == event.key:
                    player.turnRight()
            
            if not self.ball.isReleased and event.key == pygame.K_SPACE:
                self.ball.releaseBall()
                self.ball_sped_time = time.time()
                self.player_sped_time = time.time()

        
        elif event.type == pygame.KEYUP:

            keys = pygame.key.get_pressed()

            for player in self.players:
                if not keys[player.key_mappings["left"]] and not keys[player.key_mappings["right"]]:
                    player.stopMoving()
                elif event.key == player.key_mappings["left"]:
                    if keys[player.key_mappings["right"]]:
                        player.turnRight()
                    else:
                        player.stopMoving()
                elif event.key == player.key_mappings["right"]:
                    if keys[player.key_mappings["left"]]:
                        player.turnLeft()
                    else:
                        player.stopMoving()

    def update(self, dt):

        for player in self.players:
            player.movePlayer()
        self.ball.move()

        if self.ball.isReleased:
            if self.ball.checkOutOfBounds():
                self.score[self.ball.last_touched_player_id] += 1
                if self.score[self.ball.last_touched_player_id] == 5:
                    self.done = True
                winningPlayer = self.players[0] if self.ball.last_touched_player_id == self.players[0].id else self.players[1]
                self.ball = Ball(self.size[0], self.heading_buffer, self.size[1], winningPlayer)
                self.persist["winning_player"] = 1 if winningPlayer.player_num == PlayerNum.ONE else 2
                self.__resetPlayerSpeeds()

            for player in self.players:
                if self.ball.getRect().colliderect(player.getRect()):
                    self.ball.deflectBall(player)

            if time.time() - self.ball_sped_time >= self.ball_speed_increase_interval:
                self.ball.increaseBallSpeed()
                self.ball_sped_time = time.time()
            
            if time.time() - self.player_sped_time >= self.player_speed_increase_interval:
                for player in self.players:
                    player.increasePaddleSpeed()
                self.player_sped_time = time.time()

    def draw(self, screen):
        
        white, black, red, blue = (255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 0, 255)

        screen.fill(black)


        # Drawing players as rectangles
        for player in self.players:
            pygame.draw.rect(screen, player.color, player.getRect(), border_radius=player.border_radius)

        # Drawing ball as circle
        pygame.draw.circle(screen, white, pygame.Vector2(self.ball.getX(), self.ball.getY()), self.ball.getRadius())

        # Drawing line for scorecard
        pygame.draw.line(screen, white, pygame.Vector2(0, self.heading_buffer), pygame.Vector2(self.size[0], self.heading_buffer))
        
        # Updating score
        game_font = pygame.font.Font("./resources/fonts/Retro Gaming.ttf", 50)
        score_title_surface = game_font.render("Score: ", False, white)
        player1_score_surface = game_font.render(str(self.score[1]), False, red)
        hyphen_score_surface = game_font.render(" - ", False, white)
        player2_score_surface = game_font.render(str(self.score[2]), False, blue)
        screen.blit(score_title_surface, (10, 10))

        score_position_vector = (self.size[0]//2, 10) 

        screen.blit(player1_score_surface, (score_position_vector[0], score_position_vector[1]))
        screen.blit(hyphen_score_surface, (score_position_vector[0] + 25, score_position_vector[1])) 
        screen.blit(player2_score_surface, (score_position_vector[0] + 70, score_position_vector[1]))
