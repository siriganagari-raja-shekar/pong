import asyncio

import logging
from websockets.asyncio.server import serve, broadcast
import json
import secrets
from websockets.exceptions import ConnectionClosedError

from server.models.game import MultiplayerGame
from components.shared_resources import PlayerNum

# logging.basicConfig(format="%(message)s", level=logging.DEBUG)

JOIN={}
WATCH={}

settings = {
    "size": (500, 700),
    "fps": 30
}

async def error(websocket, message):
    event = {
        "type": "error",
        "message": message
    }
    await websocket.send(json.dumps(event))

async def send_game_state(websocket, game, connected):
    try:
        while not game.done:
            if game.players_joined:
                # Create game state event
                game.update()
                state = game.get_state()
                state["type"] = "game_state_in_progress"

                # Send to all connected clients
                try:
                    broadcast(connected, json.dumps(state))
                except Exception as e:
                    logging.error(f"Error broadcasting game state: {e}")
                        
                # Control the update rate
            await asyncio.sleep(1/game.fps)
        
        if game.done:
            # Send to all connected clients
            event = {
                "type": "game_state_ended",
                "winning_player": game.persist["winning_player"],
                "score": game.score
            }
            await broadcast(connected, json.dumps(event))

    except ConnectionClosedError:
        raise  # Propagate to parent
    except Exception as e:
        logging.error(f"Error in send_game_state: {e}")
        raise

    print("Reached end of game or disconnected")


async def handle_input(websocket, game, playerNum, connected):
    async for message in websocket:
        try:
            event = json.loads(message)
            if event["type"] == "player_input" and game.players_joined:
                # Update player position based on input
                game.handle_player_event(event["input_event"], playerNum)
        except ConnectionClosedError:
            raise
        except Exception as e:
            print(f"Error handling input: {e}")
            raise

# async def play(websocket, game, playerNum, connected):
#     try:
#         # Run both tasks concurrently
#         await asyncio.gather(
#             send_game_state(websocket, game, connected),
#             handle_input(websocket, game, playerNum, connected)
#         )
#     except ConnectionClosedError:
#         print("Connection closed by other player in play function")
#         for client in connected:
#             if client != websocket:
#                 await error(client, "Game disconnected by other player")
#                 await client.close()
#     except Exception as e:
#         logging.error(f"Error in play function: {e}")
    
async def play(websocket, game, playerNum, connected):
    try:
        # Create tasks explicitly so we can cancel them
        state_task = asyncio.create_task(send_game_state(websocket, game, connected))
        input_task = asyncio.create_task(handle_input(websocket, game, playerNum, connected))
        
        # Wait for either task to complete (or raise an exception)
        done, pending = await asyncio.wait(
            [state_task, input_task],
            return_when=asyncio.FIRST_COMPLETED
        )

        # Cancel the remaining task
        for task in pending:
            task.cancel()
            
        # If we get here, one of the tasks completed or raised an exception
        for task in done:
            # Re-raise any exceptions
            await task

    except ConnectionClosedError:
        logging.info(f"Player {playerNum} disconnected")
        print(f"Player {playerNum} disconnected")
        # Notify other clients
        for client in connected:
            if client != websocket:
                try:
                    await error(client, "Other player disconnected")
                    await client.close()
                except Exception as e:
                    logging.error(f"Error notifying client of disconnect: {e}")
    
    except Exception as e:
        logging.error(f"Error in play: {e}")
        # Notify all clients of error
        for client in connected:
            try:
                await error(client, "Game ended due to an error")
                await client.close()
            except Exception as e:
                logging.error(f"Error notifying client of error: {e}")
    
    finally:
        # Clean up
        connected.remove(websocket)
        game.done = True  # Mark game as done
        try:
            await websocket.close()
        except Exception:
            pass


async def start(websocket):

    game = MultiplayerGame(**settings)
    connected = {websocket}

    join_key = secrets.token_urlsafe(4)
    watch_key = secrets.token_urlsafe(4)
    print(f"Join key: {join_key}")
    print(f"Watch key: {watch_key}")
    JOIN[join_key] = game, connected
    WATCH[watch_key] = game, connected
    
    try:
        event = {
            "type": "init",
            "join": join_key,
            "watch": watch_key
        }
        await websocket.send(json.dumps(event))

        print("First player started game")

        game.create_player(PlayerNum.ONE)
        
        await play(websocket, game, PlayerNum.ONE, connected)

    finally:
        print("Cleaning up games. In finally block")
        if join_key in JOIN:
            del JOIN[join_key]
        if watch_key in WATCH:
            del WATCH[watch_key]


async def join(websocket, join_key):

    try:
        game, connected = JOIN[join_key]
    except KeyError:
        await error(websocket, "Game not found")
        return
    
    connected.add(websocket)
    try:
        print("Second player joined the game")

        game.create_player(PlayerNum.TWO)
        
        await play(websocket, game, PlayerNum.TWO, connected)
    
    finally:
        if websocket in connected:
            connected.remove(websocket)


async def watch(websocket, watch_key):

    try:
        game, connected = WATCH[watch_key]
    except KeyError:
        await error(websocket, "Game not found")
        return

    connected.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        connected.remove(websocket)

async def handler(websocket):
    
    message = await websocket.recv()
    event = json.loads(message)
    print(f"Received event: {event}")
    assert event["type"] == "init"

    if "join" in event:
        await join(websocket, event["join"])
    elif "watch" in event:
        await watch(websocket, event["watch"])
    else:
        await start(websocket)


async def main():
    async with serve(handler, "", 8001):
        await asyncio.get_running_loop().create_future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
