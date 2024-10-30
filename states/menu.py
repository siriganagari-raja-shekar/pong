import pygame
from .base import BaseState

class Menu(BaseState):

    def __init__(self, **settings):
        BaseState.__init__(self, **settings)
        self.next = "game"

    def cleanup(self):
        pass

    def startup(self):
        pass

    def get_event(self, event):
        if event.type == pygame.KEYDOWN:
            print("Menu screen key down")
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.done = True

    def update(self, screen, dt):
        self.draw(screen)

    def draw(self, screen):
        screen.fill((0,0,255))
