"""
Snake Game - A classic snake game implementation using Pygame.
This module provides a fully object-oriented implementation with type annotations.
"""

import json
from random import choice, randint, shuffle
from typing import Tuple, Optional, List, Dict, Set
import pygame as pg


class GameConfig:
    """
    Configuration class containing all game constants and settings.
    Centralizes all configuration values for easy modification.
    """
    
    # Screen dimensions
    SCREEN_WIDTH: int = 640
    SCREEN_HEIGHT: int = 480
    
    # Grid settings
    GRID_SIZE: int = 20
    GRID_WIDTH: int = SCREEN_WIDTH // GRID_SIZE
    GRID_HEIGHT: int = SCREEN_HEIGHT // GRID_SIZE
    
    # Movement directions as (x, y) tuples
    UP: Tuple[int, int] = (0, -1)
    DOWN: Tuple[int, int] = (0, 1)
    LEFT: Tuple[int, int] = (-1, 0)
    RIGHT: Tuple[int, int] = (1, 0)
    
    # Color definitions (RGB tuples)
    BOARD_BACKGROUND_COLOR: Tuple[int, int, int] = (0, 0, 0)
    APPLE_COLOR: Tuple[int, int, int] = (255, 0, 0)
    SNAKE_COLOR: Tuple[int, int, int] = (0, 255, 0)
    STONE_COLOR: Tuple[int, int, int] = (128, 128, 128)  # Gray
    EYE_COLOR: Tuple[int, int, int] = (0, 0, 0)  # Black
    
    # Game speed (cells per second)
    SPEED: float = 3.0  # 3 cells per second
    
    # Snake initial length
    INITIAL_SNAKE_LENGTH: int = 3
    
    # Stone configuration
    MIN_STONES: int = 2
    MAX_STONES: int = 3
    MIN_STONE_CELLS: int = 2
    MAX_STONE_CELLS: int = 4
    
    # Game title
    GAME_TITLE: str = 'Snake!'
    
    # Data file for saving high scores
    DATA_FILE: str = 'game_data.json'
    
    @staticmethod
    def getBorderColor(color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """
        Calculate a darker border color for a given color.
        Used to create visual depth for game objects.
        
        Args:
            color: RGB tuple representing the base color
            
        Returns:
            RGB tuple representing a darker version of the color (67% brightness)
        """
        return tuple(int(c * 0.67) for c in color)
    
    @staticmethod
    def getKeyToDirectionMapping() -> Dict[int, Tuple[int, int]]:
        """
        Get the mapping of pygame key constants to movement directions.
        Includes both arrow keys and WASD keys.
        
        Returns:
            Dictionary mapping pygame key constants to direction tuples
        """
        return {
            pg.K_UP: GameConfig.UP,
            pg.K_RIGHT: GameConfig.RIGHT,
            pg.K_DOWN: GameConfig.DOWN,
            pg.K_LEFT: GameConfig.LEFT,
            pg.K_w: GameConfig.UP,
            pg.K_d: GameConfig.RIGHT,
            pg.K_s: GameConfig.DOWN,
            pg.K_a: GameConfig.LEFT,
        }


class GameDataManager:
    """
    Manages saving and loading game data (high scores).
    Handles file I/O operations for persistent game state.
    """
    
    def __init__(self, dataFile: str = GameConfig.DATA_FILE) -> None:
        """
        Initialize the data manager with a data file path.
        
        Args:
            dataFile: Path to the JSON file for storing game data
        """
        self.dataFile: str = dataFile
    
    def saveMaxLength(self, maxLength: int) -> None:
        """
        Save the maximum snake length (high score) to the data file.
        
        Args:
            maxLength: The maximum length achieved by the snake
        """
        try:
            with open(self.dataFile, 'w', encoding='utf-8') as file:
                json.dump({'max_length': maxLength}, file)
        except IOError as e:
            print(f"Error saving game data: {e}")
    
    def loadMaxLength(self) -> int:
        """
        Load the maximum snake length from the data file.
        Returns 1 if the file doesn't exist or is invalid.
        
        Returns:
            The maximum length stored in the file, or 1 if not found
        """
        try:
            with open(self.dataFile, 'r', encoding='utf-8') as file:
                data: Dict = json.load(file)
                loadedNumber: Optional[int] = data.get('max_length')
                
                if loadedNumber is None or not isinstance(loadedNumber, int):
                    return 1
                
                return max(1, loadedNumber)  # Ensure at least 1
        except (IOError, json.JSONDecodeError, KeyError):
            return 1


class GameObject:
    """
    Base class for all game objects (Apple, Snake).
    Provides common functionality for rendering and positioning.
    """
    
    def __init__(
        self,
        bodyColor: Optional[Tuple[int, int, int]] = None,
        position: Optional[Tuple[int, int]] = None,
        screen: Optional[pg.Surface] = None
    ) -> None:
        """
        Initialize a game object with color and position.
        
        Args:
            bodyColor: RGB tuple representing the object's color
            position: (x, y) tuple representing the object's position
            screen: Pygame surface to draw on (optional, can be set later)
        """
        self.bodyColor: Optional[Tuple[int, int, int]] = bodyColor
        self.position: Tuple[int, int] = position or (
            GameConfig.SCREEN_WIDTH // 2,
            GameConfig.SCREEN_HEIGHT // 2
        )
        self.screen: Optional[pg.Surface] = screen
    
    def setScreen(self, screen: pg.Surface) -> None:
        """
        Set the screen surface for drawing operations.
        
        Args:
            screen: Pygame surface to draw on
        """
        self.screen = screen
    
    def draw(self) -> None:
        """
        Draw the game object on the screen.
        Must be implemented by subclasses.
        """
        pass
    
    def drawSingleTile(
        self,
        position: Optional[Tuple[int, int]] = None,
        color: Optional[Tuple[int, int, int]] = None
    ) -> None:
        """
        Draw a single grid tile at the specified position.
        Used by objects that consist of multiple tiles (like Snake).
        
        Args:
            position: (x, y) tuple for tile position. Uses self.position if None
            color: RGB tuple for tile color. Uses self.bodyColor if None
        """
        if self.screen is None:
            raise ValueError("Screen surface not set. Call setScreen() first.")
        
        if position is None:
            position = self.position
        if color is None:
            color = self.bodyColor
        
        if color is None:
            raise ValueError("Color must be specified")
        
        # Create rectangle for the tile
        rect: pg.Rect = pg.Rect(
            position,
            (GameConfig.GRID_SIZE, GameConfig.GRID_SIZE)
        )
        
        # Draw filled rectangle
        pg.draw.rect(self.screen, color, rect)
        
        # Draw border with darker color
        borderColor: Tuple[int, int, int] = GameConfig.getBorderColor(color)
        pg.draw.rect(self.screen, borderColor, rect, 1)


class Apple(GameObject):
    """
    Represents an apple that the snake can eat.
    Randomly positions itself on the game board.
    """
    
    def __init__(self, screen: Optional[pg.Surface] = None) -> None:
        """
        Initialize an apple with random position.
        
        Args:
            screen: Pygame surface to draw on
        """
        super().__init__(GameConfig.APPLE_COLOR, screen=screen)
        self.randomizePosition()
    
    def randomizePosition(
        self,
        forbiddenPositions: Optional[List[Tuple[int, int]]] = None,
        stonePositions: Optional[Set[Tuple[int, int]]] = None
    ) -> None:
        """
        Set the apple to a random position on the game board.
        Excludes positions that are forbidden (e.g., snake body, stones).
        
        Args:
            forbiddenPositions: List of positions to avoid when placing the apple
            stonePositions: Set of stone positions to avoid
        """
        if forbiddenPositions is None:
            forbiddenPositions = []
        if stonePositions is None:
            stonePositions = set()
        
        # Generate all possible cell positions
        allCells: set = {
            (x * GameConfig.GRID_SIZE, y * GameConfig.GRID_SIZE)
            for x in range(GameConfig.GRID_WIDTH)
            for y in range(GameConfig.GRID_HEIGHT)
        }
        
        # Remove forbidden positions and stone positions
        availableCells: set = allCells - set(forbiddenPositions) - stonePositions
        
        if not availableCells:
            # Fallback to center if no cells available
            self.position = (
                GameConfig.SCREEN_WIDTH // 2,
                GameConfig.SCREEN_HEIGHT // 2
            )
            return
        
        # Choose random position from available cells
        self.position = choice(tuple(availableCells))
    
    def draw(self) -> None:
        """
        Draw the apple on the screen as a circle.
        """
        if self.screen is None:
            raise ValueError("Screen surface not set. Call setScreen() first.")
        
        if self.bodyColor is None:
            raise ValueError("Color must be specified")
        
        # Calculate center and radius for the circle
        centerX: int = self.position[0] + GameConfig.GRID_SIZE // 2
        centerY: int = self.position[1] + GameConfig.GRID_SIZE // 2
        radius: int = GameConfig.GRID_SIZE // 2 - 2
        
        # Draw filled circle
        pg.draw.circle(self.screen, self.bodyColor, (centerX, centerY), radius)
        
        # Draw border with darker color
        borderColor: Tuple[int, int, int] = GameConfig.getBorderColor(self.bodyColor)
        pg.draw.circle(self.screen, borderColor, (centerX, centerY), radius, 1)


class Stone(GameObject):
    """
    Represents a stone obstacle on the game board.
    Stones are groups of 2-4 cells that form obstacles.
    """
    
    def __init__(
        self,
        positions: List[Tuple[int, int]],
        screen: Optional[pg.Surface] = None
    ) -> None:
        """
        Initialize a stone with multiple cell positions.
        
        Args:
            positions: List of (x, y) tuples representing stone cell positions
            screen: Pygame surface to draw on
        """
        super().__init__(GameConfig.STONE_COLOR, screen=screen)
        self.positions: List[Tuple[int, int]] = positions
    
    def draw(self) -> None:
        """
        Draw all stone cells on the screen.
        """
        for position in self.positions:
            self.drawSingleTile(position)
    
    def getPositions(self) -> Set[Tuple[int, int]]:
        """
        Get all stone cell positions as a set.
        
        Returns:
            Set of (x, y) tuples representing stone positions
        """
        return set(self.positions)
    
    @staticmethod
    def generateStoneGroup(
        forbiddenPositions: Set[Tuple[int, int]],
        minCells: int = GameConfig.MIN_STONE_CELLS,
        maxCells: int = GameConfig.MAX_STONE_CELLS
    ) -> List[Tuple[int, int]]:
        """
        Generate a random stone group of 2-4 cells.
        Maximum area is 2x2, and it cannot be a 1x4 line.
        
        Args:
            forbiddenPositions: Set of positions to avoid
            minCells: Minimum number of cells in the stone
            maxCells: Maximum number of cells in the stone
            
        Returns:
            List of (x, y) tuples representing stone cell positions
        """
        # Generate all possible cell positions
        allCells: List[Tuple[int, int]] = [
            (x * GameConfig.GRID_SIZE, y * GameConfig.GRID_SIZE)
            for x in range(GameConfig.GRID_WIDTH)
            for y in range(GameConfig.GRID_HEIGHT)
        ]
        
        # Filter out forbidden positions
        availableCells: List[Tuple[int, int]] = [
            cell for cell in allCells if cell not in forbiddenPositions
        ]
        
        if len(availableCells) < minCells:
            return []
        
        # Try to generate a valid stone group
        for _ in range(100):  # Try up to 100 times
            numCells: int = randint(minCells, maxCells)
            startCell: Tuple[int, int] = choice(availableCells)
            
            # Convert to grid coordinates
            startGridX: int = startCell[0] // GameConfig.GRID_SIZE
            startGridY: int = startCell[1] // GameConfig.GRID_SIZE
            
            # Generate possible stone patterns (2x2 max, not 1x4)
            patterns: List[List[Tuple[int, int]]] = []
            
            # 2x2 square
            if numCells == 4:
                patterns.append([(0, 0), (1, 0), (0, 1), (1, 1)])
            
            # L-shapes and other 3-cell patterns
            if numCells == 3:
                patterns.extend([
                    [(0, 0), (1, 0), (0, 1)],  # L-shape
                    [(0, 0), (1, 0), (1, 1)],  # L-shape rotated
                    [(0, 0), (0, 1), (1, 1)],  # L-shape rotated
                    [(1, 0), (0, 1), (1, 1)],  # L-shape rotated
                ])
            
            # 2-cell patterns (horizontal, vertical, diagonal)
            if numCells == 2:
                patterns.extend([
                    [(0, 0), (1, 0)],  # Horizontal
                    [(0, 0), (0, 1)],  # Vertical
                    [(0, 0), (1, 1)],  # Diagonal
                ])
            
            # Try each pattern
            shuffle(patterns)
            for pattern in patterns:
                stonePositions: List[Tuple[int, int]] = []
                valid: bool = True
                
                for offsetX, offsetY in pattern:
                    gridX: int = startGridX + offsetX
                    gridY: int = startGridY + offsetY
                    
                    # Check bounds
                    if (gridX >= GameConfig.GRID_WIDTH or 
                        gridY >= GameConfig.GRID_HEIGHT or
                        gridX < 0 or gridY < 0):
                        valid = False
                        break
                    
                    cellPos: Tuple[int, int] = (
                        gridX * GameConfig.GRID_SIZE,
                        gridY * GameConfig.GRID_SIZE
                    )
                    
                    # Check if position is forbidden
                    if cellPos in forbiddenPositions:
                        valid = False
                        break
                    
                    stonePositions.append(cellPos)
                
                if valid and len(stonePositions) == numCells:
                    return stonePositions
        
        return []


class Snake(GameObject):
    """
    Represents the snake that the player controls.
    Grows when eating apples and resets when colliding with itself.
    """
    
    def __init__(
        self,
        screen: Optional[pg.Surface] = None,
        forbiddenPositions: Optional[Set[Tuple[int, int]]] = None
    ) -> None:
        """
        Initialize the snake at a random position with random direction.
        
        Args:
            screen: Pygame surface to draw on
            forbiddenPositions: Set of positions to avoid (e.g., stones)
        """
        if forbiddenPositions is None:
            forbiddenPositions = set()
        
        # Generate random start position avoiding forbidden areas
        initialPosition: Tuple[int, int] = self.generateRandomStartPosition(
            forbiddenPositions
        )
        
        super().__init__(GameConfig.SNAKE_COLOR, initialPosition, screen)
        
        # Generate initial snake body with length 3
        self.positions: List[Tuple[int, int]] = self.generateInitialBody(
            initialPosition,
            forbiddenPositions
        )
        
        # Random initial direction
        directions: List[Tuple[int, int]] = [
            GameConfig.UP,
            GameConfig.DOWN,
            GameConfig.LEFT,
            GameConfig.RIGHT
        ]
        self.direction: Tuple[int, int] = choice(directions)
        self.nextDirection: Optional[Tuple[int, int]] = None
        self.isAppleEaten: bool = False
        self.isStopped: bool = False  # True when colliding with stone
    
    @staticmethod
    def generateRandomStartPosition(
        forbiddenPositions: Set[Tuple[int, int]]
    ) -> Tuple[int, int]:
        """
        Generate a random start position that is not near stones.
        
        Args:
            forbiddenPositions: Set of positions to avoid
            
        Returns:
            Random (x, y) position tuple
        """
        # Generate all possible cell positions
        allCells: List[Tuple[int, int]] = [
            (x * GameConfig.GRID_SIZE, y * GameConfig.GRID_SIZE)
            for x in range(GameConfig.GRID_WIDTH)
            for y in range(GameConfig.GRID_HEIGHT)
        ]
        
        # Filter out forbidden positions and nearby positions (2 cells radius)
        availableCells: List[Tuple[int, int]] = []
        for cell in allCells:
            cellGridX: int = cell[0] // GameConfig.GRID_SIZE
            cellGridY: int = cell[1] // GameConfig.GRID_SIZE
            
            # Check if cell or its neighbors are forbidden
            tooClose: bool = False
            for offsetX in range(-5, 6):
                for offsetY in range(-5, 6):
                    checkGridX: int = cellGridX + offsetX
                    checkGridY: int = cellGridY + offsetY
                    
                    if (0 <= checkGridX < GameConfig.GRID_WIDTH and
                        0 <= checkGridY < GameConfig.GRID_HEIGHT):
                        checkPos: Tuple[int, int] = (
                            checkGridX * GameConfig.GRID_SIZE,
                            checkGridY * GameConfig.GRID_SIZE
                        )
                        if checkPos in forbiddenPositions:
                            tooClose = True
                            break
                
                if tooClose:
                    break
            
            if not tooClose:
                availableCells.append(cell)
        
        if not availableCells:
            # Fallback to center if no cells available
            return (
                GameConfig.SCREEN_WIDTH // 2,
                GameConfig.SCREEN_HEIGHT // 2
            )
        
        return choice(availableCells)
    
    @staticmethod
    def generateInitialBody(
        startPosition: Tuple[int, int],
        forbiddenPositions: Set[Tuple[int, int]]
    ) -> List[Tuple[int, int]]:
        """
        Generate initial snake body with length 3.
        
        Args:
            startPosition: Starting position for the snake head
            forbiddenPositions: Set of positions to avoid
            
        Returns:
            List of positions forming the initial snake body
        """
        positions: List[Tuple[int, int]] = [startPosition]
        
        # Try to generate body segments in a random direction
        directions: List[Tuple[int, int]] = [
            GameConfig.UP,
            GameConfig.DOWN,
            GameConfig.LEFT,
            GameConfig.RIGHT
        ]
        shuffle(directions)
        
        currentPos: Tuple[int, int] = startPosition
        for _ in range(GameConfig.INITIAL_SNAKE_LENGTH - 1):
            found: bool = False
            for dx, dy in directions:
                nextPos: Tuple[int, int] = (
                    (currentPos[0] + dx * GameConfig.GRID_SIZE) % GameConfig.SCREEN_WIDTH,
                    (currentPos[1] + dy * GameConfig.GRID_SIZE) % GameConfig.SCREEN_HEIGHT
                )
                
                if nextPos not in forbiddenPositions and nextPos not in positions:
                    positions.append(nextPos)
                    currentPos = nextPos
                    found = True
                    break
            
            if not found:
                # If we can't find a valid position, just use a nearby one
                dx, dy = directions[0]
                nextPos = (
                    (currentPos[0] + dx * GameConfig.GRID_SIZE) % GameConfig.SCREEN_WIDTH,
                    (currentPos[1] + dy * GameConfig.GRID_SIZE) % GameConfig.SCREEN_HEIGHT
                )
                positions.append(nextPos)
                currentPos = nextPos
        
        return positions
    
    def updateDirection(self) -> None:
        """
        Update the snake's direction from the queued next direction.
        Prevents immediate direction changes that could cause instant death.
        """
        if self.nextDirection is not None:
            self.direction = self.nextDirection
            self.nextDirection = None
            # Allow movement again when direction changes
            self.isStopped = False
    
    def move(self) -> None:
        """
        Move the snake one step in the current direction.
        Wraps around screen edges. Grows if an apple was recently eaten.
        Snake stops when colliding with stones.
        """
        # Don't move if stopped (colliding with stone)
        if self.isStopped:
            # Lose one tail cell per tick when stopped
            if len(self.positions) > 1:
                self.positions.pop()
            return
        
        headX, headY = self.getHeadPosition()
        dx, dy = self.direction
        
        # Calculate new head position with screen wrapping
        newHead: Tuple[int, int] = (
            (headX + dx * GameConfig.GRID_SIZE) % GameConfig.SCREEN_WIDTH,
            (headY + dy * GameConfig.GRID_SIZE) % GameConfig.SCREEN_HEIGHT
        )
        
        # Add new head to positions
        self.positions.insert(0, newHead)
        
        # Remove tail if apple wasn't eaten
        if not self.isAppleEaten:
            self.positions.pop()
        else:
            # Reset flag after growing
            self.isAppleEaten = False
    
    def getSegmentColor(self, segmentIndex: int) -> Tuple[int, int, int]:
        """
        Get the color for a snake segment based on its position.
        Creates a gradient: head is brightest, then darker for 5 cells,
        then lighter again in a loop.
        
        Args:
            segmentIndex: Index of the segment (0 is head)
            
        Returns:
            RGB tuple representing the segment color
        """
        baseColor: Tuple[int, int, int] = GameConfig.SNAKE_COLOR
        cycleLength: int = 10  # 5 cells darker + 5 cells lighter
        
        # Calculate position in the cycle
        cyclePos: int = segmentIndex % cycleLength
        
        # Brightest at head (cyclePos 0), darkest at cyclePos 5
        if cyclePos < 5:
            # Getting darker: 100% to 60% brightness
            brightness: float = 1.0 - (cyclePos * 0.08)
        else:
            # Getting lighter: 60% to 100% brightness
            brightness: float = 0.6 + ((cyclePos - 5) * 0.08)
        
        # Apply brightness to color
        return tuple(int(c * brightness) for c in baseColor)
    
    def draw(self) -> None:
        """
        Draw the entire snake by drawing each segment with gradient colors.
        Draws eyes on the head.
        """
        # Draw body segments with gradient colors
        for index, position in enumerate(self.positions):
            segmentColor: Tuple[int, int, int] = self.getSegmentColor(index)
            self.drawSingleTile(position, segmentColor)
        
        # Draw eyes on the head
        self.drawEyes()
    
    def drawEyes(self) -> None:
        """
        Draw two black circles (eyes) on the front side of the snake's head.
        Eyes are positioned based on the snake's direction.
        """
        if self.screen is None or len(self.positions) == 0:
            return
        
        headPos: Tuple[int, int] = self.getHeadPosition()
        headCenterX: int = headPos[0] + GameConfig.GRID_SIZE // 2
        headCenterY: int = headPos[1] + GameConfig.GRID_SIZE // 2
        
        # Eye size and offset
        eyeRadius: int = 3
        eyeOffset: int = 4  # Distance from center
        
        dx, dy = self.direction
        
        # Calculate eye positions based on direction
        # Eyes are on the front side of the head
        if dx == 1:  # Moving right
            eye1X: int = headCenterX + eyeOffset
            eye1Y: int = headCenterY - eyeOffset
            eye2X: int = headCenterX + eyeOffset
            eye2Y: int = headCenterY + eyeOffset
        elif dx == -1:  # Moving left
            eye1X: int = headCenterX - eyeOffset
            eye1Y: int = headCenterY - eyeOffset
            eye2X: int = headCenterX - eyeOffset
            eye2Y: int = headCenterY + eyeOffset
        elif dy == -1:  # Moving up
            eye1X: int = headCenterX - eyeOffset
            eye1Y: int = headCenterY - eyeOffset
            eye2X: int = headCenterX + eyeOffset
            eye2Y: int = headCenterY - eyeOffset
        else:  # Moving down
            eye1X: int = headCenterX - eyeOffset
            eye1Y: int = headCenterY + eyeOffset
            eye2X: int = headCenterX + eyeOffset
            eye2Y: int = headCenterY + eyeOffset
        
        # Draw eyes
        pg.draw.circle(self.screen, GameConfig.EYE_COLOR, (eye1X, eye1Y), eyeRadius)
        pg.draw.circle(self.screen, GameConfig.EYE_COLOR, (eye2X, eye2Y), eyeRadius)
    
    def getHeadPosition(self) -> Tuple[int, int]:
        """
        Get the position of the snake's head.
        
        Returns:
            (x, y) tuple representing the head position
        """
        return self.positions[0]
    
    def checkSelfCollision(self) -> bool:
        """
        Check if the snake's head collides with its body.
        Requires at least 5 segments to allow collision (prevents false positives).
        
        Returns:
            True if the snake collided with itself, False otherwise
        """
        if len(self.positions) <= 4:
            return False
        
        headPosition: Tuple[int, int] = self.getHeadPosition()
        return headPosition in self.positions[1:]
    
    def reset(self, forbiddenPositions: Optional[Set[Tuple[int, int]]] = None) -> None:
        """
        Reset the snake to initial state with random position and direction.
        
        Args:
            forbiddenPositions: Set of positions to avoid when resetting
        """
        if forbiddenPositions is None:
            forbiddenPositions = set()
        
        initialPosition: Tuple[int, int] = self.generateRandomStartPosition(
            forbiddenPositions
        )
        self.positions = self.generateInitialBody(initialPosition, forbiddenPositions)
        
        # Random direction
        directions: List[Tuple[int, int]] = [
            GameConfig.UP,
            GameConfig.DOWN,
            GameConfig.LEFT,
            GameConfig.RIGHT
        ]
        self.direction = choice(directions)
        self.nextDirection = None
        self.isAppleEaten = False
        self.isStopped = False
    
    def checkStoneCollision(self, stonePositions: Set[Tuple[int, int]]) -> bool:
        """
        Check if the snake's head collides with a stone.
        
        Args:
            stonePositions: Set of stone cell positions
            
        Returns:
            True if collision detected, False otherwise
        """
        headPosition: Tuple[int, int] = self.getHeadPosition()
        return headPosition in stonePositions
    
    def eatApple(self) -> None:
        """
        Mark that the snake has eaten an apple.
        The snake will grow on the next move.
        """
        self.isAppleEaten = True


class Game:
    """
    Main game controller class.
    Manages the game loop, input handling, and game state.
    """
    
    def __init__(self) -> None:
        """
        Initialize the game with all necessary components.
        """
        pg.init()
        
        # Create game screen
        self.screen: pg.Surface = pg.display.set_mode(
            (GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT),
            0,
            32
        )
        
        # Initialize data manager
        self.dataManager: GameDataManager = GameDataManager()
        
        # Load and track high score
        self.maxLength: int = self.dataManager.loadMaxLength()
        self.lastMaxLength: int = self.maxLength
        
        # Update caption with max score
        self.updateCaption()
        
        # Initialize game clock for frame rate control
        self.clock: pg.time.Clock = pg.time.Clock()
        
        # Generate stones first
        self.stones: List[Stone] = self.generateStones()
        self.stonePositions: Set[Tuple[int, int]] = self.getAllStonePositions()
        
        # Create game objects (snake and apple need to avoid stones)
        self.snake: Snake = Snake(self.screen, self.stonePositions)
        self.apple: Apple = Apple(self.screen)
        self.apple.randomizePosition(
            forbiddenPositions=self.snake.positions,
            stonePositions=self.stonePositions
        )
        
        # Key to direction mapping
        self.keyToDirection: Dict[int, Tuple[int, int]] = (
            GameConfig.getKeyToDirectionMapping()
        )
    
    def generateStones(self) -> List[Stone]:
        """
        Generate 2-3 random stone groups on the game board.
        
        Returns:
            List of Stone objects
        """
        stones: List[Stone] = []
        forbiddenPositions: Set[Tuple[int, int]] = set()
        numStones: int = randint(GameConfig.MIN_STONES, GameConfig.MAX_STONES)
        
        for _ in range(numStones):
            stonePositions: List[Tuple[int, int]] = Stone.generateStoneGroup(
                forbiddenPositions
            )
            
            if stonePositions:
                stone: Stone = Stone(stonePositions, self.screen)
                stones.append(stone)
                # Add stone positions to forbidden set for next stone
                forbiddenPositions.update(stone.getPositions())
        
        return stones
    
    def getAllStonePositions(self) -> Set[Tuple[int, int]]:
        """
        Get all stone cell positions as a set.
        
        Returns:
            Set of all stone positions
        """
        allPositions: Set[Tuple[int, int]] = set()
        for stone in self.stones:
            allPositions.update(stone.getPositions())
        return allPositions
    
    def updateCaption(self) -> None:
        """
        Update the game window caption with the current max score.
        """
        pg.display.set_caption(
            f'{GameConfig.GAME_TITLE} High Score: {self.maxLength}'
        )
    
    def handleInput(self) -> bool:
        """
        Process all input events (keyboard and window close).
        Returns False if the game should exit, True otherwise.
        
        Returns:
            True to continue game, False to exit
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
            
            elif event.type == pg.KEYDOWN:
                # Handle escape key
                if event.key == pg.K_ESCAPE:
                    return False
                
                # Handle direction keys
                nextDirection: Optional[Tuple[int, int]] = (
                    self.keyToDirection.get(event.key)
                )
                
                if nextDirection is not None:
                    # Prevent moving in opposite direction
                    if not self.isOppositeDirection(
                        self.snake.direction,
                        nextDirection
                    ):
                        self.snake.nextDirection = nextDirection
        
        return True
    
    @staticmethod
    def isOppositeDirection(
        currentDirection: Tuple[int, int],
        newDirection: Tuple[int, int]
    ) -> bool:
        """
        Check if newDirection is opposite to currentDirection.
        
        Args:
            currentDirection: Current movement direction
            newDirection: Proposed new movement direction
            
        Returns:
            True if directions are opposite, False otherwise
        """
        directions: List[Tuple[int, int]] = [
            GameConfig.UP,
            GameConfig.RIGHT,
            GameConfig.DOWN,
            GameConfig.LEFT
        ]
        
        currentIndex: int = directions.index(currentDirection)
        oppositeIndex: int = (currentIndex + 2) % 4
        oppositeDirection: Tuple[int, int] = directions[oppositeIndex]
        
        return newDirection == oppositeDirection
    
    def updateGameState(self) -> None:
        """
        Update all game objects and check for collisions.
        Handles apple eating, snake self-collision, and stone collisions.
        """
        # Update snake direction
        self.snake.updateDirection()
        
        # Check for stone collision before moving
        # Calculate where the head would be after moving
        headX, headY = self.snake.getHeadPosition()
        dx, dy = self.snake.direction
        nextHead: Tuple[int, int] = (
            (headX + dx * GameConfig.GRID_SIZE) % GameConfig.SCREEN_WIDTH,
            (headY + dy * GameConfig.GRID_SIZE) % GameConfig.SCREEN_HEIGHT
        )
        
        # Check if next position is a stone
        if nextHead in self.stonePositions:
            self.snake.isStopped = True
        else:
            # Clear stopped flag if direction is now valid
            self.snake.isStopped = False
        
        # Move snake (will handle stopping internally)
        self.snake.move()
        
        # Check if snake ate the apple
        if self.snake.getHeadPosition() == self.apple.position:
            self.snake.eatApple()
            self.apple.randomizePosition(
                forbiddenPositions=self.snake.positions,
                stonePositions=self.stonePositions
            )
        
        # Check for self-collision
        if self.snake.checkSelfCollision():
            self.snake.reset(self.stonePositions)
            # Reposition apple after snake reset
            self.apple.randomizePosition(
                forbiddenPositions=self.snake.positions,
                stonePositions=self.stonePositions
            )
        
        # Update high score
        currentLength: int = len(self.snake.positions)
        self.lastMaxLength = self.maxLength
        self.maxLength = max(self.maxLength, currentLength)
        
        # Save high score if it changed
        if self.lastMaxLength != self.maxLength:
            self.dataManager.saveMaxLength(self.maxLength)
            self.updateCaption()
    
    def render(self) -> None:
        """
        Render all game objects to the screen.
        """
        # Clear screen with background color
        self.screen.fill(GameConfig.BOARD_BACKGROUND_COLOR)
        
        # Draw game objects (order matters for visual layering)
        for stone in self.stones:
            stone.draw()
        self.apple.draw()
        self.snake.draw()
        
        # Update display
        pg.display.update()
    
    def run(self) -> None:
        """
        Main game loop.
        Runs until the player exits the game.
        Speed is controlled to 3 cells per second.
        """
        running: bool = True
        # Calculate frame rate: 3 cells per second means we need to move
        # every 1/3 seconds. With 60 FPS, that's 20 frames per move.
        framesPerMove: int = int(60 / GameConfig.SPEED)
        frameCounter: int = 0
        
        while running:
            # Control frame rate (60 FPS for smooth rendering)
            self.clock.tick(60)
            
            # Handle input
            running = self.handleInput()
            
            # Update game state at the correct speed (3 cells per second)
            frameCounter += 1
            if frameCounter >= framesPerMove:
                frameCounter = 0
                self.updateGameState()
            
            # Render everything every frame for smooth visuals
            self.render()
        
        # Cleanup
        pg.quit()


def main() -> None:
    """
    Entry point for the game application.
    Creates and runs a new game instance.
    """
    game: Game = Game()
    game.run()


if __name__ == '__main__':
    main()
