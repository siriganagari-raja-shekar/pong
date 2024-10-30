import pygame
from base import BaseState

class Menu(BaseState):

    def __init__(self):
        BaseState.__init__(self)
        self.next = "game"

    def cleanup(self):
        pass

    def startup(self):
        pass

    def get_event(self, event):
        if event == pygame.KEYDOWN:
            print("Menu screen key down")
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.done = True

    def update(self, screen, dt):
        self.draw(screen)

    def draw(self, screen):
        screen.fill((0,0,255))
