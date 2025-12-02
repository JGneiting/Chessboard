# Self-Playing Chessboard

A physical chessboard that uses electromagnets and a motorized XY-axis system to autonomously move chess pieces. Features support for human vs human, human vs AI, and AI vs AI gameplay with LED feedback and sound effects.

## Overview

This project creates a fully automated chess experience where pieces physically move across the board. The system supports:

- **Human vs Human**: Two players using Nintendo Joy-Con controllers
- **Human vs AI**: Play against powerful chess engines (Stockfish, Leela Chess Zero, Maia)
- **AI vs AI**: Watch chess engines battle each other in demo mode
- **Visual Feedback**: NeoPixel LED strips highlight selected pieces and valid moves
- **Audio Feedback**: Sound effects for game events and voice instructions for pawn promotion
- **UCI Engine Support**: Compatible with any UCI-compliant chess engine

## Hardware

**Platform**: Raspberry Pi with Arduino motor controller

**Movement System**:
- XY-Axis gantry with stepper motors and limit switches
- Electromagnet carriage for piece manipulation
- Serial communication for motor control

**User Interface**:
- NeoPixel LED strips for square highlighting
- Audio system for sound effects and voice guidance
- Nintendo Joy-Con controllers (Bluetooth) for player input
- Physical reset button for game control

**Chess Pieces**: Modified to contain ferromagnetic material for electromagnetic manipulation

## Software Architecture

### Module Structure

```
├── BoardFiles/              # Hardware control layer
│   ├── ChessBoard.py       # Main board controller
│   ├── MotorManager.py     # Stepper motor control
│   ├── MagnetManager.py    # Electromagnet control
│   └── CaptureManagement.py # Captured piece handling
├── GameFiles/              # Chess game logic
│   ├── StateManager.py     # Board state and move validation
│   ├── ChessPieces.py      # Piece behavior and rules
│   ├── GameInterface.py    # Player interface abstraction
│   └── ChessErrors.py      # Game exceptions
├── GameSupervisor/         # High-level game control
│   ├── ChessGame.py        # Main game loop
│   ├── BoardMovementLogic.py # Movement planning
│   └── SoundController.py  # Audio management
├── CPUChessPlayers/        # AI player implementations
│   ├── UCIPlayer.py        # UCI chess engine interface
│   └── DemonstrationBots.py # Demo mode players
├── JoyconInterface/        # Joy-Con controller support
│   └── Joycon.py          # Controller input handling
├── NeopixelLights/         # LED control
│   └── LightManager.py    # Light patterns and feedback
└── SoundPlayer/            # Audio system
    └── SoundManager.py    # Sound effects and voice
```

### Key Features

#### Chess Engine Integration (UCI Protocol)
- Stockfish support
- Leela Chess Zero / Maia networks
- Configurable think time and parameters
- FEN position management
- Automatic pawn promotion

#### Movement System
- Precision square-to-square movement
- Knight piece handling (curved path to avoid collisions)
- Castling support with rook repositioning
- En passant capture handling
- Automatic piece capture to designated slots

#### Game State Management
- Full chess rule implementation
- Check and checkmate detection
- Stalemate detection
- Move validation
- FEN string generation for engine communication

#### User Interface
- Joy-Con joystick for intuitive piece selection
- Smart directional selection algorithm (finds closest piece in joystick direction)
- LED square highlighting for selected pieces and valid moves
- Move confirmation with visual and haptic feedback
- Audio-guided pawn promotion menu

## How It Works

### Game Modes

**Human vs Human**
- Each player uses a Joy-Con controller (left or right)
- Players take turns selecting and moving their pieces
- Board physically executes each move

**Human vs AI**
- One Joy-Con for the human player
- UCI chess engine calculates opponent moves
- Supported engines: Stockfish, Leela Chess Zero, Komodo, Maia networks

**AI vs AI (Demo Mode)**
- Two chess engines play autonomously
- Great for demonstrations and testing
- Switch modes by holding reset button for 4 seconds during startup

### Joy-Con Controls

1. **Recalibrate**: Hold ZL/ZR to recalibrate joystick center
2. **Select Piece**: Move joystick toward desired piece
3. **Confirm Selection**: Press X or Down button
4. **Select Destination**: Move joystick toward target square
5. **Execute Move**: Press X or Down button
6. **Cancel**: Press A or Left button to reselect piece

### Reset and Replay
- **Quick Reset**: Hold reset button for 2 seconds to restart game
- **Mode Switch**: Hold reset button for 4 seconds to toggle between Joy-Con and Demo modes
- Board automatically returns all pieces to starting positions

## Technical Highlights

### Intelligent Movement System

**Standard Moves**
- Direct linear path from source to destination
- Electromagnet activation and pulsing for secure piece attachment
- Speed optimization based on whether piece is attached

**Knight Moves**
- Curved intermediate path to prevent collisions with adjacent pieces
- Calculates waypoints for smooth L-shaped movement
- Maintains magnetic grip throughout complex path

**Castling**
- Executes two-piece coordinated movement
- King moves to destination, then rook follows via intermediate path
- Properly handles both kingside and queenside castling

**En Passant & Pawn Promotion**
- Full support for special chess moves
- Audio-guided pawn promotion selection
- Captured pieces automatically moved to storage slots

### Coordinate System

Uses bilinear interpolation to handle real-world board imperfections:
- Four corner calibration points define playable area
- Converts chess notation (A1-H8) to precise motor coordinates
- Compensates for board rotation, skew, and non-square alignment

### Chess Engine Integration

Communicates with UCI engines via subprocess:
- FEN position tracking for board state
- Move history in UCI format
- Pondering support for faster AI responses
- Configurable think time and engine parameters

### Motion Control

Arduino receives queued move commands via serial:
```
MV <y_pos> <x_pos> <y_delay> <x_delay>  # Synchronized movement
HOME                                     # Return to origin and calibrate
```

Commands can be chained with `|` separator for efficient execution.

## Credits

**UCI Chess Engines**:
- [Stockfish](https://stockfishchess.org/) - Open-source chess engine
- [Leela Chess Zero](https://lczero.org/) - Neural network chess engine
- [Maia Chess](https://maiachess.com/) - Human-like chess AI

**Technologies**:
- UCI Protocol (Universal Chess Interface)
- pyjoycon library for Joy-Con support
- RPi.GPIO and pyserial for hardware control
