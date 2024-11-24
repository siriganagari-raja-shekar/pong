# 🏓 PING PONG MULTIPLAYER 🏓

An awesome multiplayer Ping Pong game featuring both local and online gameplay! Challenge your friends sitting next to you or across the internet in intense paddle-to-paddle action! Built with Python and Pygame.

![Ping Pong Game](game_screenshot.png)

## ✨ Features

- 🎮 Two exciting game modes:
  - 🏠 Local multiplayer on the same computer
  - 🌐 Online multiplayer over the network
- 🎯 Smooth player movement
- 🏆 Live score tracking
- 🎨 Retro-style graphics
- 🔊 Classic pong sounds

## 🎮 How to Play

### 🚀 Quick Start - Local Multiplayer

1. Clone this repository:
```bash
git clone https://github.com/your-username/ping-pong.git
cd ping-pong
```

2. Install dependencies:
```bash
pip install -e .
```

3. Start the game:
```bash
python -m src.client.control
```

4. Select "Local Multiplayer" from the menu
5. Play against your friend on the same keyboard!

### 🌐 Quick Start - Online Multiplayer

#### Starting a Game (Host)

1. Start the server first:
```bash
python -m src.server.app
```

2. In a new terminal, start the game:
```bash
python -m src.client.control
```

3. Select "Create Game Room" from the menu
4. The game will display a join code. Share this code with your friend!

#### Joining a Game

1. Start the game:
```bash
python -m src.client.control
```

2. Select "Join Game Room" from the menu
3. Enter the join code shared by the host
4. Get ready to play!

### 🎹 Controls

Local Multiplayer:
- Player 1: `A` and `D` keys to move up and down
- Player 2: `Left` and `Right` arrow keys to move up and down

Online Multiplayer:
- Both players: `A` and `D` keys to move up and down

Common Controls:
- `SPACE`: Start round

## 🎯 Game Rules

- First player to score 5 points wins!
- Don't let the ball pass your paddle
- The ball speeds up as the rally continues
- Missing the ball gives your opponent a point

## 🧱 Technical Details

- Built with Python 3.8+
- Uses Pygame for graphics
- WebSocket-based networking for online multiplayer
- Client-server architecture
- State management system for game flow

## 🛠️ Development

Want to contribute? Great!

1. Fork the repo
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♂️ Support

Found a bug? Have a suggestion? Open an issue or contact me!

---

Made with ❤️ and Python. Happy Ponging! 🏓
