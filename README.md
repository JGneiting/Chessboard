# Self-Playing Chessboard
### AKA: Wizard's Chess

A physical chessboard that uses electromagnets and a motorized XY-axis system to autonomously move chess pieces, allowing players to enjoy chess without physically touching the pieces.

![Board with Lights](docs/images/board_lights.png)

## Project Description

This project is a chessboard capable of allowing two users to play chess without the need for either user to move the pieces. To accomplish this, the chessboard is built using two IoT devices (Raspberry Pi 4 and Arduino Nano) running four major systems:

1. **The dual-axis system** - Responsible for moving the electromagnet
2. **The chess backend** - Runs the chess game according to official rules
3. **The Neopixel lights** - Assists in user piece selection
4. **The audio system** - Enhances the chess experience

### The Arduino Nano

The Arduino Nano handles the dual-axis system, receiving serial commands from the Raspberry Pi to drive two stepper motors simultaneously with precise timing (delays given in microseconds).

### The Raspberry Pi 4

The Raspberry Pi integrates all remaining systems to create one cohesive product. This includes the chess game logic, LED control, audio playback, and the input system. Currently, input is accomplished using a pair of Nintendo Switch Joy-Cons connected via Bluetooth.

## How to Play

The method of input is the Nintendo Joy-Con. Taking your turn comes in two stages: piece selection and move selection.

### Stage 1: Piece Selection

Use the joystick to move between your pieces until you find the piece you would like to move, then select it using the "Confirm Selection" button (X or Down). The Joy-Con will highlight valid pieces you can move.

### Stage 2: Move Selection

Select one of the valid moves for your chosen piece (the Joy-Con will vibrate if there are no valid moves). Confirming the selection will execute your move on the board. Pressing the "Deselect Piece" button (A or Left) allows you to return to Stage 1 and choose a different piece.

### Joy-Con Controls

- **Recalibrate**: Hold ZL/ZR to recalibrate joystick center
- **Select Piece/Move**: Move joystick in the desired direction
- **Confirm Selection**: Press X or Down button
- **Cancel/Deselect**: Press A or Left button
- **Quick Reset**: Hold reset button for 2 seconds to restart game
- **Mode Switch**: Hold reset button for 4 seconds to toggle between player and demo modes

### Interpreting the Board Lights

The Neopixel Light System uses yellow and green cursors to indicate selections. Each pair of lights indicates a row and column:

- **Yellow Lights**: Used during Stage 1 (piece selection) to indicate the piece you wish to move
- **Green Lights**: Added during Stage 2 (move selection) to indicate where the piece will move (only valid moves are shown)

## Game Modes

### Human vs Human
Two players each use a Joy-Con controller (left or right) to take turns selecting and moving their pieces. The board physically executes each move.

### Human vs AI
One Joy-Con for the human player, while a UCI chess engine calculates opponent moves. Supported engines include Stockfish, Leela Chess Zero, Komodo, and Maia networks.

### AI vs AI (Demo Mode)
Two chess engines play autonomously - great for demonstrations and testing. Access this mode by holding the reset button for 4 seconds during startup.

## Project Development

Development began in July 2022 and consisted of three main phases:

### Planning Phase

This phase involved scoping out parts online and designing the board in CAD. The process required modeling each component to ensure compatibility, including:
- The complete dual-axis gantry system
- Individual chess pieces with magnetic bases
- The laser-cut acrylic chessboard

### Hardware Development

The hardware phase involved printing and laser cutting all designed pieces, assembling components, and soldering electronic circuits to protoboards. The final configuration includes:
- XY-axis gantry with stepper motors and limit switches
- Electromagnet carriage for piece manipulation
- NeoPixel LED strips for square highlighting
- Audio system for sound effects and voice guidance
- Nintendo Joy-Con controllers (Bluetooth)
- Physical reset button

### Software Development

Much of the development time was spent on the software to control the chessboard. The code is primarily written in Python, with the Arduino code written in C++. The software architecture includes:

- Hardware control layer for motors, magnets, and LEDs
- Chess game logic with full rule implementation
- Player interface abstraction
- UCI chess engine integration
- Movement planning and collision avoidance
- Audio management system

## Problems Encountered

### General Manufacturing Issues

Issues largely out of my control included 3D printer breakdowns, file issues for laser cutting, and failed prints. These had to be handled case-by-case and often set development back several days.

### Dual-Axis Movement Speed

Initially, the Raspberry Pi handled the stepper motor control, but it was too slow. The precise timing required for stepper motor pulses caused sluggish movement, and the problem compounded as additional systems (each requiring their own thread) were added.

**Solution**: Delegating the dual-axis system to the Arduino Nano freed up computing power on the Pi for other systems. As a bonus, C++ code ran significantly faster than Python, greatly improving movement speed.

### Piece Interference

This was the hardest problem to solve. Pieces needed to slide past each other reliably, but the electromagnet had to be strong enough to overcome friction without pulling nearby pieces. The solution involved:

1. **Material Change**: Switching from 3D-printed PLA to laser-cut acrylic to reduce friction
2. **Three Piece Redesigns**:
   - Version 1: Three magnets in a triangle (too much edge magnetism)
   - Version 2: One central magnet (insufficient holding force)
   - Version 3: Two stacked central magnets (optimal balance)
3. **Algorithm Tweaks**: Special handling for knight moves to avoid collisions

The final design uses two magnets stacked in the center of each piece, maintaining a strong magnetic field directly under the piece while minimizing interference with adjacent pieces.

## Lessons Learned

### Good Code Documentation is Important

Returning to code after months away was extremely difficult without proper documentation. A few well-placed comments detailing what each function does would have made refactoring and polishing much easier.

### Look at Issues from Every Angle

The piece interference problem taught this lesson. After trying electromagnet strength adjustments, board materials, and algorithm tweaks, the breakthrough came from reconsidering the pieces themselves - something that hadn't been initially considered. This experience helped solve the movement speed issue faster by considering all options, including the Arduino solution.

### Use Version Control

A near-disaster where the source code was almost deleted made version control an immediate priority. Setting up a Git repository provided peace of mind that weeks of work wouldn't be lost in an instant. While the backup has never been needed, the security it provides is invaluable.

## The Final Product

The final system includes an audio component that plays various audio tracks (selected from favorite games and movies) to create a more immersive experience. Different audio tracks play during specific game events, along with standard background music.

After hundreds of hours of work, the final product is a board that can play chess. However, the potential goes far beyond chess. Because of the removable nature of the chessboard itself, any game board designed for it could be used. This makes it truly a system capable of turning any board game into a hybrid between the physical world and the realm of technology.

The potential for such a system is limitless. If sister boards were created, it would be possible to play board games with friends and family while still interacting with the physical world without being in the same location. The final product as of now is just the beginning of what this project can become.

---

## Technical Details

### Software Architecture

**📖 [Full Architecture Documentation](ARCHITECTURE.md)** - Detailed software architecture with diagrams, data flow examples, and technical deep-dives.

**Module Overview**:

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

### Chess Engine Integration (UCI Protocol)

- Full UCI (Universal Chess Interface) protocol implementation
- Support for Stockfish, Leela Chess Zero, and Maia networks
- Configurable think time and engine parameters
- FEN position management for engine communication
- Automatic pawn promotion handling

### Intelligent Movement System

**Standard Moves**: Direct linear path from source to destination with electromagnet activation and pulsing for secure piece attachment.

**Knight Moves**: Curved intermediate path to prevent collisions with adjacent pieces. The system calculates waypoints for smooth L-shaped movement while maintaining magnetic grip.

**Castling**: Executes coordinated two-piece movement - king moves to destination, then rook follows via intermediate path. Handles both kingside and queenside castling.

**En Passant & Pawn Promotion**: Full support for special chess moves with audio-guided pawn promotion selection. Captured pieces are automatically moved to storage slots.

### Coordinate System

Uses bilinear interpolation to handle real-world board imperfections:
- Four corner calibration points define the playable area
- Converts chess notation (A1-H8) to precise motor coordinates
- Compensates for board rotation, skew, and non-square alignment

### Motion Control Protocol

The Arduino receives queued move commands via serial communication:

```
MV <y_pos> <x_pos> <y_delay> <x_delay>  # Synchronized movement
HOME                                     # Return to origin and calibrate
```

Commands can be chained with `|` separator for efficient execution. Delays are specified in microseconds for precise stepper motor control.

### Game State Management

- Full chess rule implementation with move validation
- Check and checkmate detection
- Stalemate detection
- FEN string generation for engine communication
- Move history tracking

## Credits

**UCI Chess Engines**:
- [Stockfish](https://stockfishchess.org/) - Open-source chess engine
- [Leela Chess Zero](https://lczero.org/) - Neural network chess engine
- [Maia Chess](https://maiachess.com/) - Human-like chess AI

**Technologies**:
- UCI Protocol (Universal Chess Interface)
- pyjoycon library for Joy-Con support
- RPi.GPIO and pyserial for hardware control