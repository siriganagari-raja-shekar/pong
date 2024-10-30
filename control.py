import pygame
from states.menu import Menu
from states.game import Game
import sys
import os

class Control:
    def __init__(self, **settings):
        self.__dict__.update(settings)
        pygame.init()
        self.done = False
        self.screen = pygame.display.set_mode(self.size)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Pygame demo")
        pygame.display.set_icon(pygame.image.load("./resources/images/pingpong_icon.png"))
        os.environ['SDL_VIDEO_CENTERED'] = '1'

    def setup_states(self, state_dict, start_state):
        self.state_dict = state_dict
        self.state_name = start_state
        self.state = self.state_dict[self.state_name]
    def flip_state(self):
        self.state.done = False
        previous,self.state_name = self.state_name, self.state.next
        self.state.cleanup()
        self.state = self.state_dict[self.state_name]
        self.state.startup()
        self.state.previous = previous
    def update(self, dt):
        if self.state.quit:
            self.done = True
        elif self.state.done:
            self.flip_state()
        self.state.update(self.screen, dt)
    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
            self.state.get_event(event)
    def main_game_loop(self):
        while not self.done:
            delta_time = self.clock.tick(self.fps)/1000.0
            self.event_loop()
            self.update(delta_time)
            pygame.display.update()
  
settings = {
    'size':(500,700),
    'fps' :60
}
  
app = Control(**settings)
state_dict = {
    'menu': Menu(**settings),
    'game': Game(**settings)
}
app.setup_states(state_dict, 'menu')
app.main_game_loop()
pygame.quit()
sys.exit()
