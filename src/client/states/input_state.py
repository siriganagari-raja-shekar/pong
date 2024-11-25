import pygame
from .base import BaseState
class JoinGameInput(BaseState):
    def __init__(self, **settings):
        super().__init__(**settings)
        self.next = 'multiplayer_game'
        self.time_active = 0
        
        # Input handling
        self.input_text = ""
        self.max_chars = 6
        self.font = pygame.font.Font("./resources/fonts/Retro Gaming.ttf", 32)
        self.heading_font = pygame.font.Font("./resources/fonts/Retro Gaming.ttf", 48)
        self.input_active = True
        
        # Store whether input is valid
        self.input_valid = True
        self.error_message = ""
        self.error_timer = 0
        self.error_display_time = 2  # seconds
    def cleanup(self):
        """Send join key to next state"""
        self.persist = {
            "join_key": self.input_text if self.input_text else None
        }
        return self.persist

    def startup(self, persist):
        """Reset state when starting"""
        self.persist = persist
        self.input_text = ""
        self.input_active = True
        self.input_valid = True
        self.error_message = ""
        self.error_timer = 0

    def get_event(self, event):
        """Handle input events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and len(self.input_text) == self.max_chars:
                # Validate and proceed
                self.done = True
            elif event.key == pygame.K_BACKSPACE:
                # Remove last character
                self.input_text = self.input_text[:-1]
            elif event.key == pygame.K_ESCAPE:
                # Return to menu
                self.next = 'menu'
                self.done = True
            elif len(self.input_text) < self.max_chars and (event.unicode.isalnum() or event.unicode in "-_"):
                # Add character if within limit and is alphanumeric
                self.input_text += event.unicode
    def update(self, dt):
        """Update state"""
        self.time_active += dt
        
        if self.error_timer > 0:
            self.error_timer -= dt
        
    def draw(self, screen):
        """Render the input state"""
        # Colors
        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)
        RED = (255, 0, 0)
        
        # Clear screen
        screen.fill(BLACK)
        
        # Draw heading
        heading_text = "Enter Join Code"
        heading_surface = self.heading_font.render(heading_text, True, WHITE)
        heading_rect = heading_surface.get_rect(center=(self.size[0]//2, self.size[1]//4))
        screen.blit(heading_surface, heading_rect)
        
        # Draw input box
        input_text = self.input_text + ('_' if self.time_active % 1 > 0.5 else ' ')
        input_surface = self.font.render(input_text, True, WHITE)
        input_rect = input_surface.get_rect(center=(self.size[0]//2, self.size[1]//2))
        screen.blit(input_surface, input_rect)
        
        # Draw character count
        count_text = f"{len(self.input_text)}/{self.max_chars}"
        count_surface = self.font.render(count_text, True, WHITE)
        count_rect = count_surface.get_rect(center=(self.size[0]//2, self.size[1]//2 + 50))
        screen.blit(count_surface, count_rect)
        
        # Draw instructions
        instructions = [
            "Enter 6-character join code",
            "Press ENTER when done",
            "Press ESC to return to menu"
        ]

        for i, instruction in enumerate(instructions):
            inst_surface = pygame.font.Font("./resources/fonts/Retro Gaming.ttf", 20).render(
                instruction, True, WHITE
            )
            inst_rect = inst_surface.get_rect(
                center=(self.size[0]//2, self.size[1]*3//4 + i*30)
            )
            screen.blit(inst_surface, inst_rect)
        
        # Draw error message if any
        if self.error_timer > 0:
            error_surface = self.font.render(self.error_message, True, RED)
            error_rect = error_surface.get_rect(center=(self.size[0]//2, self.size[1]//3))
            screen.blit(error_surface, error_rect)