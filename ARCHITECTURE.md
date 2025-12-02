# Software Architecture

This document provides a detailed overview of the Self-Playing Chessboard software architecture, component interactions, and data flow.

## System Overview

```mermaid
graph TD
    A[ChessGame<br/>Main Orchestrator<br/>GameSupervisor/ChessGame.py] --> B[Player Layer<br/>Input/AI]
    A --> C[Feedback Layer<br/>Output]

    B --> D[GameInterface<br/>Game State<br/>GameFiles/GameInterface.py]
    C --> E[BoardLogic<br/>Movement Translation<br/>Supervisor/BoardMovementLogic.py]

    D --> F[StateManager<br/>Chess Logic<br/>GameFiles/StateManager.py]
    E --> G[ChessBoard<br/>Hardware Control<br/>BoardFiles/ChessBoard.py]

    C --> H[Lights & Sound]

    style A fill:#e1f5ff
    style F fill:#ffe1e1
    style G fill:#e1ffe1
```

## Layer Architecture

### 1. Orchestration Layer

**ChessGame** (`GameSupervisor/ChessGame.py`)
- Main game loop and event handling
- Coordinates all subsystems
- Manages game modes (Human vs Human, Human vs AI, AI vs AI)
- Handles reset button events and mode switching
- Error handling and exception management

```python
class ChessGame:
    - backends: Dict[str, GameInterface]  # Different game modes
    - board: BoardLogic                    # Physical board controller
    - lights: LightsInterface              # LED feedback
    - audio: SoundController               # Audio feedback
```

### 2. Player Layer

Players interact with the game through a common interface:

```mermaid
classDiagram
    Player <|-- StandardChessJoycon
    Player <|-- UCIPlayer
    Player <|-- WhiteDemo
    Player <|-- BlackDemo

    class Player {
        <<abstract>>
        +GameInterface board
        +make_move(source, dest)
        +my_turn()
        +upgrade_pawn(pawn)
    }

    class StandardChessJoycon {
        +ButtonEventJoyCon
        +RumbleJoyCon
        +stick_event()
        +piece_selection()
        +move_selection()
    }

    class UCIPlayer {
        +subprocess engine
        +think_time
        +send(message)
        +wait_for_token(token)
    }

    class WhiteDemo {
        +demo_logic()
    }

    class BlackDemo {
        +demo_logic()
    }
```

#### StandardChessJoycon (`JoyconInterface/Joycon.py`)
- Interfaces with Nintendo Joy-Con controllers via Bluetooth
- Implements directional piece selection algorithm
- State machine: `piece_selection` → `move_selection` → `execute`
- Stick monitoring thread for real-time input
- Haptic feedback via rumble

**Selection Algorithm**:
```
Current piece position → Joystick angle → Find closest piece
   in direction using vector math and distance scoring
```

#### UCIPlayer (`CPUChessPlayers/UCIPlayer.py`)
- Communicates with UCI chess engines via subprocess
- Manages engine lifecycle (uci, ucinewgame, position, go, stop)
- Converts between FEN strings and game state
- Handles pawn promotion decisions
- Optional pondering for faster responses

**UCI Communication Flow**:

```mermaid
sequenceDiagram
    participant GI as GameInterface
    participant UP as UCIPlayer
    participant Engine as UCI Engine

    GI->>UP: my_turn()
    UP->>UP: Generate FEN position
    UP->>Engine: position fen [FEN_STRING]
    UP->>Engine: go infinite
    Note over UP,Engine: Think for configured time
    UP->>Engine: stop
    Engine->>UP: bestmove e2e4
    UP->>UP: Parse move (source=e2, dest=e4)
    UP->>GI: make_move(e2, e4)
```

#### Demo Bots (`CPUChessPlayers/DemonstrationBots.py`)
- Simple AI for demonstration mode
- WhiteDemo and BlackDemo instances
- Useful for testing board movements

### 3. Game State Layer

```mermaid
graph TD
    A[GameInterface<br/>Abstract Layer] --> B[StateManager<br/>Chess Engine]

    A --> |"make_move(source, dest)"| B
    A --> |"get_square(square)"| B
    A --> |"get_valid_moves(square)"| B
    A --> |"signal_player()"| C[Active Player]
    A --> |"wait_for_upgrade(pawn)"| C

    style A fill:#fff4e1
    style B fill:#e1f5ff
```

#### StateManager (`GameFiles/StateManager.py`)

**Class Hierarchy**:

```mermaid
classDiagram
    InternalBoard <|-- ChessLogic
    ChessLogic <|-- Simulator

    class InternalBoard {
        +List~List~Piece~~ board
        +List~Piece~ captured
        +String turn
        +get_square(square)
        +set_square(square, piece)
        +named_to_numeric(square)
        +initialize_board()
    }

    class ChessLogic {
        +is_movable(piece, square)
        +simulate_move(piece, square)
        +move_piece(source, dest)
        +generate_fen_string()
        +run_check_cycle()
        +checkmate_test()
    }

    class Simulator {
        +deepcopy of board state
        +test moves without affecting real game
    }
```

**Core Responsibilities**:
- 8x8 board state representation
- Full chess rule implementation
- Move validation and legal move generation
- Check, checkmate, and stalemate detection
- FEN string generation for UCI engines
- Special move handling (castling, en passant, pawn promotion)
- Move history tracking

**Move Validation Process**:

```mermaid
flowchart TD
    A[Player attempts move] --> B{Square occupied<br/>by player's piece?}
    B -->|No| C[InvalidMove Exception]
    B -->|Yes| D[Get piece.get_possible_moves]
    D --> E{Destination in<br/>possible moves?}
    E -->|No| C
    E -->|Yes| F[Create Simulator copy of board]
    F --> G[Execute move on Simulator]
    G --> H{Is player's king<br/>in check?}
    H -->|Yes| C
    H -->|No| I[Move is valid]
    I --> J[Execute on real board]
    J --> K[Update game state]
    K --> L[Check for check/checkmate]
```

#### ChessPieces (`GameFiles/ChessPieces.py`)

Each piece type implements its own move logic:
```python
class Piece:
    def get_possible_moves(self) -> List[str]

class Pawn(Piece):      # Forward movement, diagonal capture, en passant
class Rook(Piece):      # Horizontal/vertical lines
class Knight(Piece):    # L-shaped jumps
class Bishop(Piece):    # Diagonal lines
class Queen(Piece):     # Combines rook and bishop
class King(Piece):      # One square any direction + castling
```

Special pieces:
- `GhostPawn`: Represents en passant target square
- `SuperPawn`: Wrapper for promoted pawn

### 4. Movement Translation Layer

**BoardMovementLogic** (`GameSupervisor/BoardMovementLogic.py`)
- Translates chess moves to physical board movements
- Handles piece capture routing
- Manages castling rook movements
- Coordinates pawn promotion with hardware

```mermaid
sequenceDiagram
    participant BL as BoardLogic
    participant CB as ChessBoard
    participant Motor as MotorManager
    participant Mag as MagnetManager

    BL->>CB: move_piece(e2, e4)
    CB->>Motor: move_axes to e2
    Motor->>Motor: Execute movement
    CB->>Mag: activate()
    CB->>Motor: move_axes to e4
    Motor->>Motor: Execute movement
    CB->>Mag: pulse(strength)
    Note over Mag: Secure piece attachment
    CB->>Mag: deactivate()
```

### 5. Hardware Control Layer

```mermaid
graph TD
    A[ChessBoard<br/>Hardware Manager<br/>BoardFiles/ChessBoard.py] --> B[MotorManager]
    A --> C[MagnetManager]
    A --> D[CaptureManager]

    B --> E[SerialAxis<br/>Arduino Control]
    B --> F[DualAxis<br/>Direct GPIO]

    C --> G[GPIO PWM<br/>Electromagnet]

    D --> H[Slot Management<br/>Captured Pieces]

    style A fill:#e1f5ff
    style E fill:#ffe1e1
    style F fill:#ffe1e1
```

#### MotorManager (`BoardFiles/MotorManager.py`)

**SerialAxis** (Primary implementation):

```mermaid
graph LR
    A[Python<br/>Raspberry Pi] -->|Serial USB| B[Arduino]
    B --> C[Stepper Driver X]
    B --> D[Stepper Driver Y]
    C --> E[X-Axis Motor]
    D --> F[Y-Axis Motor]

    style A fill:#e1f5ff
    style B fill:#ffe1e1
```

**Protocol**:
```
Command: MV <y_pos> <x_pos> <y_delay> <x_delay>
Response: Status acknowledgment

Multiple commands queued with | separator:
"MV 50 50 45 45|MV 75 75 85 85"
```

**DualAxis** (Alternative implementation):
- Direct GPIO control of stepper motors
- Threaded execution for X and Y axes
- Limit switch homing and calibration

#### Coordinate Transformation

Chess notation → Motor coordinates via bilinear interpolation:

```mermaid
flowchart LR
    A["Chess Square<br/>'E4'"] --> B["Convert to Grid<br/>row=4, col=5"]
    B --> C["Normalize<br/>x=0.571, y=0.429"]
    C --> D["Bilinear Interpolation<br/>Using 4 corner points"]
    D --> E["Motor Coordinates<br/>x_motor, y_motor"]

    style A fill:#e1ffe1
    style E fill:#ffe1e1
```

Formula accounts for:
- Board rotation
- Non-square board dimensions
- Physical misalignment

#### MagnetManager (`BoardFiles/MagnetManager.py`)
- GPIO control of electromagnet
- PWM support for variable strength
- Pulse mode for secure attachment

#### CaptureManagement (`BoardFiles/CaptureManagement.py`)
- Manages captured piece storage slots
- Routes captured pieces off-board
- Tracks slot availability
- Handles piece return during reset

### 6. Feedback Layer

#### NeoPixel Lights (`NeopixelLights/LightManager.py`)

```mermaid
graph TD
    A[LightsInterface] --> B[LightManager]
    B --> C[Current Player Indicator]
    B --> D[Selected Piece Highlight]
    B --> E[Valid Move Indicators]
    B --> F[Pre-game Animations]
    B --> G[Post-game Celebrations]

    style A fill:#fff4e1
    style B fill:#e1f5ff
```

**Color Scheme**:
- White: White team indicator
- Blue: Selected piece
- Green: Valid move destinations
- Red: Black team indicator
- Animations: Rainbow patterns for game events

#### Sound System (`SoundPlayer/`)

**SoundController** (`GameSupervisor/SoundController.py`)
- High-level audio coordination
- Background music management
- Event-triggered sound effects

**SoundManager** (`SoundPlayer/SoundManager.py`)
- Audio playback engine
- Multiple simultaneous tracks
- Voice clips for instructions

**Audio Events**:
- Game intro/outro music
- Check notification
- Checkmate celebration
- Stalemate sound
- Move confirmation beeps
- Pawn promotion instructions

## Data Flow Examples

### Human vs AI Move

```mermaid
sequenceDiagram
    participant JS as Joy-Con Stick
    participant SM as StickMonitor
    participant JC as StandardChessJoycon
    participant Lights as LightsInterface
    participant GI as GameInterface
    participant State as StateManager
    participant CG as ChessGame
    participant BL as BoardLogic
    participant CB as ChessBoard
    participant UCI as UCIPlayer
    participant Engine as Chess Engine

    JS->>SM: Joystick moved
    SM->>JC: stick_event()
    JC->>JC: Calculate angle, find closest piece
    JC->>Lights: Highlight selected piece

    Note over JC: Player presses X
    JC->>Lights: Show valid moves
    Note over JC: Player selects destination, presses X

    JC->>GI: make_move(source, dest)
    GI->>State: move_piece(source, dest)
    State->>State: Validate and update
    State-->>CG: Move confirmed

    CG->>BL: move_piece(source, dest)
    BL->>CB: Execute physical movement
    CB->>CB: Move magnet and piece

    CG->>State: Check for check/checkmate
    CG->>UCI: signal_player() - AI turn

    UCI->>Engine: position + go infinite
    Engine-->>UCI: bestmove e7e5
    UCI->>GI: make_move(e7, e5)

    Note over GI,CB: Repeat validation and physical movement
```

### Castling Move

```mermaid
sequenceDiagram
    participant P as Player
    participant State as StateManager
    participant CG as ChessGame
    participant BL as BoardLogic
    participant CB as ChessBoard

    P->>State: Select King, choose castling square
    State->>State: Validate castling requirements
    Note over State: - King/rook haven't moved<br/>- No pieces between<br/>- Not in/through check

    State->>State: castle() - calculate rook destination
    State->>CG: Castling callback
    CG->>CG: Store rook move

    CG->>BL: move_piece(King to destination)
    BL->>CB: Execute King movement

    CG->>BL: move_intermediate(Rook movement)
    BL->>CB: Execute Rook via L-shaped path
```

### En Passant

```mermaid
sequenceDiagram
    participant P as Player
    participant State as StateManager
    participant CG as ChessGame
    participant BL as BoardLogic
    participant Capture as CaptureManager

    P->>State: Black pawn e7→e5 (2 squares)
    State->>State: Create GhostPawn at e6

    Note over P: White pawn at d5 sees e6 as valid move
    P->>State: Move white pawn to e6

    State->>State: Detect GhostPawn capture
    State->>State: Get linked black pawn at e5
    State->>State: Remove black pawn from board

    State->>CG: Capture callback
    CG->>BL: capture(black_pawn)
    BL->>Capture: Route to storage slot
```

## Threading Model

```mermaid
graph TD
    A[Main Thread<br/>ChessGame.run_game] --> B[StickMonitor Thread<br/>Left Joy-Con]
    A --> C[StickMonitor Thread<br/>Right Joy-Con]
    A --> D[UCI Engine Process<br/>subprocess]
    A --> E[Serial Communication<br/>blocking]

    B --> F[Poll joystick every 100ms]
    C --> G[Poll joystick every 100ms]
    D --> H[stdin/stdout communication]
    E --> I[Wait for Arduino ACK]

    style A fill:#e1f5ff
    style B fill:#fff4e1
    style C fill:#fff4e1
    style D fill:#ffe1e1
    style E fill:#e1ffe1
```

## Error Handling

Exception hierarchy:

```mermaid
graph TD
    A[Exception] --> B[TurnError]
    A --> C[InvalidMove]
    A --> D[Check]
    A --> E[Checkmate]
    A --> F[Stalemate]
    A --> G[PawnUpgrade]
    A --> H[BackendSwitch]
    A --> I[UnknownSquare]
    A --> J[TeamError]
    A --> K[PlayerError]

    B -.->|Wrong player moving| L[Handle: Show lights/sound]
    C -.->|Illegal move| L
    D -.->|King in check| M[Internal - check cycle]
    E -.->|Game over| N[Victory sequence]
    F -.->|Draw| N
    G -.->|Needs promotion| O[Show promotion menu]
    H -.->|Mode switch| P[Switch backend]

    style E fill:#ffe1e1
    style F fill:#fff4e1
    style G fill:#e1ffe1
```

Exceptions bubble up from StateManager → GameInterface → ChessGame, where they're caught and handled appropriately (e.g., play sound, show lights, execute final move for checkmate).

## Configuration Points

### Hardware Calibration
- `ChessBoard.py`: Corner positions (`sq_1` through `sq_4`)
- `MotorManager.py`: Motor delay settings (`travel_speed`, `move_speed`) - lower values = faster
- `MagnetManager.py`: PWM duty cycle for electromagnet strength

### Game Configuration
- `ChessGame.py`: UCI engine paths and arguments
- `UCIPlayer.py`: Think time (`think_time` variable)
- `Joycon.py`: Joystick tolerance and selection algorithm tuning

### GPIO Pin Mapping
- `BoardFiles/__init__.py`: Pin definitions for buttons and peripherals
- `MotorManager.py`: Stepper driver pins (enable, step, direction, limits)
- `MagnetManager.py`: Electromagnet control pin
- `LightManager.py`: NeoPixel data pin

## Extension Points

### Adding New Player Types
```python
class MyPlayer(Player):
    def __init__(self, game_interface):
        super().__init__(game_interface)

    def my_turn(self):
        # Calculate move
        self.make_move(source, dest)

    def upgrade_pawn(self, pawn):
        return "Queen"  # or other piece
```

### Adding New Chess Engines
```python
UCIPlayer(
    backend,
    "/path/to/engine",
    "engine_executable",
    args=["--option1=value1", "--option2=value2"]
)
```

### Customizing Movement Patterns
Override methods in `ChessBoard`:
- `move_piece()` for standard moves
- `move_between()` for special paths (currently used for knights)
- `move_intermediate()` for multi-waypoint moves

## Performance Considerations

**Move Execution Time**:
- Standard move: ~2-5 seconds (depends on distance)
- Knight move: ~3-6 seconds (curved path)
- Castling: ~5-8 seconds (two-piece move)
- Capture: +2-3 seconds (additional routing to storage)

**UCI Engine Think Time**:
- Default: 3 seconds per move
- Configurable in `UCIPlayer.think_time`
- Affects game pace significantly

**Motor Speed vs Accuracy Trade-off**:

Note: These values represent **motor step delays** sent to the Arduino (in microseconds). Lower delay values = faster movement.

- `travel_speed=45`: Lower delay → **Fast movement** when repositioning without piece attached
- `move_speed=85`: Higher delay → **Slower movement** for secure piece transport
- **Lower delay values** = Faster but less precise, higher risk of piece slipping
- **Higher delay values** = Slower but more controlled, secure piece attachment

## Future Architecture Considerations

**Potential Enhancements**:
1. Piece detection via hall effect sensors (eliminate need for game state tracking)
2. Web interface layer (WebSocket communication with browser client)
3. Game recording to PGN format (add PGNWriter module)
4. Opening book integration (database layer for stored positions)
5. Elo rating system for human players (persistent storage layer)
6. Computer vision for automatic calibration (CV module interfacing with camera)

---

**Last Updated**: Based on codebase state as of latest commit
