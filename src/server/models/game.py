from components.player import Player
from components.shared_resources import PlayerNum
from components.ball import Ball
from components.shared_resources import MULTIPLAYER_KEY_BINDINGS
import random
import pygame
import time

class MultiplayerGame:
    def __init__(self, **settings):
        self.__dict__.update(settings)
        self.heading_buffer = 70
        self.players = []
        self.ball = None
        self.score = dict()
        self.round_in_progress = False
        self.players_joined = False
        self.done = False
        self.persist = dict()
        self.ball_sped_time = None
        self.player_sped_time = None

        self.ball_speed_increase_interval = 15
        self.player_speed_increase_interval = 15

    def create_player(self, player_num):
        if player_num == PlayerNum.ONE:
            self.players.append(Player(1, self.size[0], self.size[1], PlayerNum.ONE, self.heading_buffer))
        else:
            self.players.append(Player(2, self.size[0], self.size[1], PlayerNum.TWO, self.heading_buffer))
        if len(self.players) == 2:
            self.startup()
            self.players_joined = True
        
    
    def startup(self):
        self.__resetGame()

    def __resetGame(self):
        self.ball = Ball(self.size[0], self.heading_buffer, self.size[1], self.players[random.randint(0, 1)])
        self.score = { player.id: 0 for player in self.players }
        self.ball_sped_time = None
        self.player_sped_time = None

    def handle_player_event(self, event, playerNum):
        for player in self.players:
            if player.player_num == playerNum:
                self.handle_event(event, player)
    
    def handle_event(self, event, player):

        if event["type"] == pygame.KEYDOWN:
            
            if event["key"] in MULTIPLAYER_KEY_BINDINGS["left"]:
                player.turnLeft()
            elif event["key"] in MULTIPLAYER_KEY_BINDINGS["right"]:
                player.turnRight()
            
            if not self.ball.isReleased and event["key"] == MULTIPLAYER_KEY_BINDINGS["release"] and player.id == self.ball.last_touched_player_id:
                self.ball.releaseBall()
                self.ball.round_in_progress = True
                self.ball_sped_time = time.time()
                self.player_sped_time = time.time()

        
        elif event["type"] == pygame.KEYUP:

            keys = set(event["keys"])

            if not keys.intersection(MULTIPLAYER_KEY_BINDINGS["left"]) and not keys.intersection(MULTIPLAYER_KEY_BINDINGS["right"]):
                player.stopMoving()
            elif event["key"] in MULTIPLAYER_KEY_BINDINGS["left"]:
                if keys.intersection(MULTIPLAYER_KEY_BINDINGS["right"]):
                    player.turnRight()
                else:
                    player.stopMoving()
            elif event["key"] in MULTIPLAYER_KEY_BINDINGS["right"]:
                if keys.intersection(MULTIPLAYER_KEY_BINDINGS["left"]):
                    player.turnLeft()
                else:
                    player.stopMoving()

    def update(self):

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
                self.persist["winning_player"] = PlayerNum.ONE if winningPlayer.player_num == PlayerNum.ONE else PlayerNum.TWO

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

    def get_players_state(self):
        player_states = []
        for player in self.players:
            player_states.append({
                "id": player.id,
                "x": player.getRect().x,
                "y": player.getRect().y,
                "width": player.width,
                "height": player.height,
                "player_num": player.player_num,
                "border_radius": player.border_radius
            })
        return player_states

    def get_state(self):
        event = {
            "players_joined": self.players_joined,
            "ball": {
                "x": self.ball.getX(),
                "y": self.ball.getY(),
                "radius": self.ball.getRadius()
            },
            "players": self.get_players_state(),
            "score": self.score
        }
        return event

