import pygame
from .base import BaseState
from components.shared_resources import COLORS

class Menu(BaseState):

    def __init__(self, **settings):
        BaseState.__init__(self, **settings)
        self.next = "game"
        self.title_font = pygame.font.Font("./resources/fonts/Retro Gaming.ttf", 70)
        self.option_font = pygame.font.Font("./resources/fonts/Retro Gaming.ttf", 30)
        self.option_one_surface = self.option_font.render("Local Multiplayer", False, COLORS["white"])
        self.option_two_surface = self.option_font.render("Join Game Room", False, COLORS["white"])
        self.option_one_rect = self.option_one_surface.get_rect(topleft=(self.size[1]//7, self.size[1]//2))
        self.option_two_rect = self.option_two_surface.get_rect(topleft=(self.size[1]//6, self.size[1]//2 + self.size[1]//10))


    def cleanup(self):
        pass

    def startup(self, persist):
        pass

    def get_event(self, event):


        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.option_one_rect.collidepoint(pygame.mouse.get_pos()):
                self.next = "game"
                self.done = True
            elif self.option_two_rect.collidepoint(pygame.mouse.get_pos()):
                print("Option two not yet implemented")


    def update(self, screen, dt):
        self.draw(screen)

    def draw(self, screen):

        screen.fill(COLORS["black"])
        ping_title_surface = self.title_font.render("Ping ", False, COLORS["red"])
        pong_title_surface = self.title_font.render("Pong!", False, COLORS["blue"])

        screen.blit(ping_title_surface, (self.size[0]//11, self.size[1]//3))
        screen.blit(pong_title_surface, (self.size[1]//3, self.size[1]//3))

        screen.blit(self.option_one_surface, self.option_one_rect)
        screen.blit(self.option_two_surface, self.option_two_rect)
