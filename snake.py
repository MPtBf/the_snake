"""
Snake class implementation.
"""

from random import choice, shuffle
from typing import Tuple, Optional, List, Set
import pygame as pg
from config import GameConfig
from game_objects import GameObject


class Snake(GameObject):
    """
    Represents the snake that the player controls.
    Grows when eating apples and cuts tail when colliding with itself.
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
        Uses modulo for wrapping around screen edges.
        
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
            
            # Check if cell or its neighbors are forbidden (with wrapping)
            tooClose: bool = False
            for offsetX in range(-2, 3):
                for offsetY in range(-2, 3):
                    # Use modulo for wrapping around screen edges
                    checkGridX: int = (cellGridX + offsetX) % GameConfig.GRID_WIDTH
                    checkGridY: int = (cellGridY + offsetY) % GameConfig.GRID_HEIGHT
                    
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
    
    def updateDirection(self, stonePositions: Optional[Set[Tuple[int, int]]] = None) -> None:
        """
        Update the snake's direction from the queued next direction.
        Prevents immediate direction changes that could cause instant death.
        Prevents 180-degree rotation while colliding with stone.
        
        Args:
            stonePositions: Set of stone positions to check for valid movement
        """
        if self.nextDirection is not None:
            # If stopped on stone, prevent 180-degree rotation
            if self.isStopped and stonePositions is not None:
                # Check if new direction would still hit stone
                headX, headY = self.getHeadPosition()
                dx, dy = self.nextDirection
                nextHead: Tuple[int, int] = (
                    (headX + dx * GameConfig.GRID_SIZE) % GameConfig.SCREEN_WIDTH,
                    (headY + dy * GameConfig.GRID_SIZE) % GameConfig.SCREEN_HEIGHT
                )
                
                # If new direction would hit stone, don't allow it
                if nextHead in stonePositions:
                    # Clear next direction to prevent rotation
                    self.nextDirection = None
                    return
            
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
    
    def checkSelfCollision(self) -> Optional[int]:
        """
        Check if the snake's head collides with its body.
        Requires at least 5 segments to allow collision (prevents false positives).
        
        Returns:
            Index of the collision point in positions list, or None if no collision
        """
        if len(self.positions) <= 4:
            return None
        
        headPosition: Tuple[int, int] = self.getHeadPosition()
        try:
            collisionIndex: int = self.positions.index(headPosition, 1)
            return collisionIndex
        except ValueError:
            return None
    
    def cutTail(self, collisionIndex: int) -> None:
        """
        Cut the snake's tail from the collision point to the end.
        
        Args:
            collisionIndex: Index in positions list where collision occurred
        """
        # Keep head and body up to (but not including) collision point
        self.positions = self.positions[:collisionIndex]
    
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

