
import pygame
from .base import BaseState
from components.player import Player
from components.shared_resources import PlayerNum
from components.ball import Ball
import random
from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosedError
import json
import asyncio
import threading
import queue
from queue import Empty
import inspect

class MultiplayerGameState(BaseState):

    def __init__(self, **settings):
        BaseState.__init__(self, **settings)
        self.next = "end_game"
        self.heading_buffer = 70

    def __resetGame(self):

        self.next = "end_game"
        self.players = []
        self.score = dict()
        self.persist = dict()
        self.websocket_thread = None
        self.join_key = None
        self.watch_key = None
        self.players_joined = False
        self.server_connected = False
        self.server_error = None

        # Queue for sending messages to websocket
        self.outgoing_queue = queue.Queue()
        # Queue for receiving messages from websocket
        self.incoming_queue = queue.Queue()

    def startup(self, persist):
        self.__resetGame()
        if persist and persist["join_key"]:
            print("Join key found. Joining game")
            self.initialize_connection(persist["join_key"])
        else:
            self.initialize_connection()

    
    async def _websocket_handler(self, join_key=None):
        """Handles the websocket connection and message processing"""
        uri = "ws://localhost:8001"
        try:
            async with connect(uri, ping_timeout=5, ping_interval=5) as websocket:
                self.server_connected = True
                event = {
                    "type": "init"
                }
                if join_key:
                    event["join"] = join_key

                await websocket.send(json.dumps(event))

                # Start a task to handle outgoing messages
                send_task = asyncio.create_task(self._handle_outgoing_messages(websocket))


                async for message in websocket:
                    data = json.loads(message)
                    await self._process_message(data, join_key)
                
                send_task.cancel()
        except ConnectionClosedError:
            self.server_error = {
                "message": "Server closed connection unexpectedly"
            }
            print(f"Connection closed")
        except TimeoutError:
            self.server_error = {
                "message": "Server timed out"
            }
            print(f"Timeout error")
        except Exception as e:
            self.server_error = {
                "message": "Error connecting to server"
            }
            print(f"WebSocket error: {e}")

        if not self.done and not self.server_error:
            self.server_error = {
                "message": "Server disconnected unexpectedly"
            }

    
    async def _handle_outgoing_messages(self, websocket):
        """Handles sending messages from the outgoing queue to the websocket"""
        while True:
            try:
                # Check if there are messages to send
                while not self.outgoing_queue.empty():
                    message = self.outgoing_queue.get_nowait()
                    await websocket.send(json.dumps(message))
                    self.outgoing_queue.task_done()
                
                # Small delay to prevent busy waiting
                await asyncio.sleep(0.01)
            except Exception as e:
                print(f"Error sending message: {e}")


    async def _process_message(self, data, join_key):
        """Processes incoming websocket messages"""
        if not join_key and data["type"] == "init":
            self.join_key = data["join"]
            self.watch_key = data["watch"]
        elif data["type"] == "game_state_in_progress":
            self.handle_game_state(data)
        elif data["type"] == "game_state_ended":
            self.handle_game_end(data)
        elif data["type"] == "error":
            self.server_error = {
                "message": data["message"]
            }
            print(f"Server error: {data['message']}")
            return False
        return True
    
    def handle_game_state(self, data):
        self.players_joined = True
        self.incoming_queue.put(data)

    def _run_websocket_thread(self, join_key=None):
        """Runs the websocket connection in an asyncio event loop"""
        asyncio.run(self._websocket_handler(join_key))

    def initialize_connection(self, join_key=None):
        """Initializes the websocket connection either as host or joining player"""
        if self.websocket_thread and self.websocket_thread.is_alive():
            print("Connection already active")
            return

        self.websocket_thread = threading.Thread(
            target=self._run_websocket_thread,
            args=(join_key,)
        )
        self.websocket_thread.daemon = True
        self.websocket_thread.start()

    def cleanup(self):
        """Cleanup method to handle connection termination"""
        if self.websocket_thread and self.websocket_thread.is_alive():
            # Implement any necessary cleanup
            self.websocket_thread = None

        return self.persist

    def get_event(self, event):
        """
        Sends player input events to the server
        player_input: dict containing player input data
        """

        if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            if self.server_error:
                if event.key == pygame.K_ESCAPE:
                    self.done = True
                    self.next = "menu"
            else:
                outgoing_event = {
                    "type": "player_input",
                    "input_event": {
                        "type": event.type,
                        "key": event.key,
                        "keys": pygame.key.get_pressed()
                    }
                }
                if self.players_joined:
                    self.outgoing_queue.put(outgoing_event)

    def update(self, dt):
        
        try:
            try:
                data = self.incoming_queue.get_nowait()

                if "players" in data:
                    self.players = data["players"]
                
                if "ball" in data:
                    self.ball = data["ball"]

                if "score" in data:
                    self.score = data["score"]
                        
                self.incoming_queue.task_done()
                
            except Empty:
                # No messages this frame, game continues
                pass
            
        except Exception as e:
            print(f"Error updating game state: {e}")
        

    def handle_game_end(self, data):
        self.done = True
        self.persist["winning_player"] = data["winning_player"]

    def draw(self, screen):
        
        white, black, red, blue = (255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 0, 255)

        screen.fill(black)


        if self.players_joined and self.ball and self.players and not self.server_error:
            # Drawing players as rectangles
            for player in self.players:
                pygame.draw.rect(screen, red if player["player_num"] == PlayerNum.ONE else blue, pygame.Rect(player["x"], player["y"], player["width"], player["height"]), border_radius=player["border_radius"])

            # Drawing ball as circle
            pygame.draw.circle(screen, white, pygame.Vector2(self.ball["x"], self.ball["y"]), self.ball["radius"])

            # Drawing line for scorecard
            pygame.draw.line(screen, white, pygame.Vector2(0, self.heading_buffer), pygame.Vector2(self.size[0], self.heading_buffer))
            
            # Updating score
            game_font = pygame.font.Font("./resources/fonts/Retro Gaming.ttf", 50)
            score_title_surface = game_font.render("Score: ", False, white)
            player1_score_surface = game_font.render(str(self.score['1']), False, red)
            hyphen_score_surface = game_font.render(" - ", False, white)
            player2_score_surface = game_font.render(str(self.score['2']), False, blue)
            screen.blit(score_title_surface, (10, 10))

            score_position_vector = (self.size[0]//2, 10) 

            screen.blit(player1_score_surface, (score_position_vector[0], score_position_vector[1]))
            screen.blit(hyphen_score_surface, (score_position_vector[0] + 25, score_position_vector[1])) 
            screen.blit(player2_score_surface, (score_position_vector[0] + 70, score_position_vector[1]))
        
        elif self.server_error:

            medium_font = pygame.font.Font("./resources/fonts/Retro Gaming.ttf", 20)
            small_font = pygame.font.Font("./resources/fonts/Retro Gaming.ttf", 15)
            error_surface = medium_font.render("Error: " + self.server_error["message"], False, white)
            error_rect = error_surface.get_rect(center=(self.size[0]//2, self.size[1]//2))
            screen.blit(error_surface, error_rect)

            # Display message to return to main menu
            return_surface = small_font.render("Press ESC to return to menu", False, white)
            return_rect = return_surface.get_rect(center=(self.size[0]//2, self.size[1]//2 + 50))
            screen.blit(return_surface, return_rect)
        
        elif not self.server_connected:
            # Display connecting to server message
            medium_font = pygame.font.Font("./resources/fonts/Retro Gaming.ttf", 20)
            small_font = pygame.font.Font("./resources/fonts/Retro Gaming.ttf", 15)
            error_surface = medium_font.render("Connecting to server...", False, white)
            error_rect = error_surface.get_rect(center=(self.size[0]//2, self.size[1]//2))
            screen.blit(error_surface, error_rect)

        else:
            # Create different font sizes
            large_font = pygame.font.Font("./resources/fonts/Retro Gaming.ttf", 30)
            medium_font = pygame.font.Font("./resources/fonts/Retro Gaming.ttf", 20)
            small_font = pygame.font.Font("./resources/fonts/Retro Gaming.ttf", 15)

            # Render text surfaces
            waiting_surface = large_font.render("Waiting for players...", False, white)
            
            # Calculate center positions
            screen_center_x = self.size[0] // 2
            screen_center_y = self.size[1] // 2
            
            # Position waiting text
            waiting_rect = waiting_surface.get_rect(center=(screen_center_x, screen_center_y - 50))
            screen.blit(waiting_surface, waiting_rect)

            # Display join key and instructions if available
            if self.join_key:
                join_key_surface = medium_font.render(f"Join Key: {self.join_key}", False, white)
                instruction_surface = small_font.render("Share this key with other players to join!", False, white)
                
                # Center align join key and instruction
                join_key_rect = join_key_surface.get_rect(center=(screen_center_x, screen_center_y + 20))
                instruction_rect = instruction_surface.get_rect(center=(screen_center_x, screen_center_y + 70))
                
                screen.blit(join_key_surface, join_key_rect)
                screen.blit(instruction_surface, instruction_rect)
