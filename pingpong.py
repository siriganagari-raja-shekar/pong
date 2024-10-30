import pygame
import os
from player import Player
from player_key_mappings import PlayerNum
from ball import Ball


class PingPong:

    def __init__(self):

        os.environ['SDL_VIDEO_CENTERED'] = '1'

        pygame.init()
        self.window_width, self.window_height = 500, 700
        self.window = pygame.display.set_mode((self.window_width,self.window_height))
        pygame.display.set_caption("Pygame demo")
        pygame.display.set_icon(pygame.image.load("pingpong_icon.png"))
        self.clock = pygame.time.Clock()
        self.running = True
        self.heading_buffer = 70
        self.players = [Player(1, self.window_width, self.window_height, PlayerNum.ONE, self.heading_buffer), Player(2, self.window_width, self.window_height, PlayerNum.TWO, self.heading_buffer)]
        self.ball = Ball(self.window_width, self.heading_buffer, self.window_height, self.players[0])
        self.score = { player.id: 0 for player in self.players }

    def process_input(self):

        eventList = pygame.event.get()
        for event in eventList:
            if event.type == pygame.QUIT:
                self.running = False
                break

            elif event.type == pygame.KEYDOWN:
                
                for player in self.players:
                    if player.key_mappings["left"] == event.key:
                        player.turnLeft()
                    elif player.key_mappings["right"] == event.key:
                        player.turnRight()
                
                if not self.ball.isReleased and event.key == pygame.K_SPACE:
                    self.ball.releaseBall()


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


    def update(self):

        for player in self.players:
            player.movePlayer()
        self.ball.move()

        if self.ball.isReleased:
        
            if self.ball.checkOutOfBounds():
                self.score[self.ball.last_touched_player_id] += 1
                winningPlayer = self.players[0] if self.ball.last_touched_player_id == self.players[0].id else self.players[1]
                self.ball = Ball(self.window_width, self.heading_buffer, self.window_height, winningPlayer)

            for player in self.players:
                if self.ball.getRect().colliderect(player.getRect()):
                    self.ball.deflectBall(player)
        
    
    def render(self):

    
        white, black, red, blue = (255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 0, 255)

        self.window.fill(black)


        # Drawing players as rectangles
        for player in self.players:
            pygame.draw.rect(self.window, player.color, player.getRect(), border_radius=player.border_radius)

        # Drawing ball as circle
        pygame.draw.circle(self.window, white, pygame.Vector2(self.ball.getX(), self.ball.getY()), self.ball.getRadius())

        # Drawing line for scorecard
        pygame.draw.line(self.window, white, pygame.Vector2(0, self.heading_buffer), pygame.Vector2(self.window_width, self.heading_buffer))
        
        # Updating score
        game_font = pygame.font.Font("./fonts/Retro Gaming.ttf", 50)
        score_title_surface = game_font.render("Score: ", False, white)
        player1_score_surface = game_font.render(str(self.score[1]), False, red)
        hyphen_score_surface = game_font.render(" - ", False, white)
        player2_score_surface = game_font.render(str(self.score[2]), False, blue)
        self.window.blit(score_title_surface, (10, 10))

        score_position_vector = (self.window_width//2, 10) 

        self.window.blit(player1_score_surface, (score_position_vector[0], score_position_vector[1]))
        self.window.blit(hyphen_score_surface, (score_position_vector[0] + 25, score_position_vector[1])) 
        self.window.blit(player2_score_surface, (score_position_vector[0] + 70, score_position_vector[1]))

         
        pygame.display.update()

    def run(self):
        while self.running:
            self.process_input()
            self.update()
            self.render()
            self.clock.tick(60)


game = PingPong()
game.run()
pygame.display.quit()
