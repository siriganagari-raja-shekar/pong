import asyncio

import logging
from websockets.asyncio.server import serve, broadcast
import json
import secrets

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
        try:
            await broadcast(connected, json.dumps(event))
        except Exception as e:
                logging.error(f"Error sending game state: {e}")


async def handle_input(websocket, game, playerNum):
    print(f"In handle input to check if playerNum is PlayerNum: {isinstance(playerNum, PlayerNum)}")
    async for message in websocket:
        try:
            event = json.loads(message)
            if event["type"] == "player_input" and game.players_joined:
                # Update player position based on input
                game.handle_player_event(event["input_event"], playerNum)
        except Exception as e:
            logging.error(f"Error handling input: {e}")

async def play(websocket, game, playerNum, connected):
    try:
        # Run both tasks concurrently
        await asyncio.gather(
            send_game_state(websocket, game, connected),
            handle_input(websocket, game, playerNum)
        )
    except Exception as e:
        logging.error(f"Error in play function: {e}")
    finally:
        for client in connected:
            client.close()



async def start(websocket):

    game = MultiplayerGame(**settings)
    connected = {websocket}

    # join_key = secrets.token_urlsafe(12)
    join_key = "123456"
    watch_key = secrets.token_urlsafe(12)
    print(f"Join key: {join_key}")
    print(f"Watch key: {watch_key}")
    JOIN["123456"] = game, connected
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
        del JOIN[join_key]
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
        connected.remove(websocket)


async def watch(websocket, watch_key):

    try:
        game, connected = WATCH[watch_key]
    except KeyError:
        await error(websocket, "Game not found")
        return

    connected.add(websocket)
    try:
        await replay(websocket, game)
        await websocket.wait_closed()
    finally:
        connected.remove(websocket)

async def handler(websocket):
    
    message = await websocket.recv()
    event = json.loads(message)
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
