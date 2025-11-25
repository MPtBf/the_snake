"""
Game objects: base class, apple, and stone.
"""

from random import choice, randint, random
from typing import Tuple, Optional, List, Set
import pygame as pg
from config import GameConfig


class GameObject:
    """
    Base class for all game objects (Apple, Snake, Stone).
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
        
        # We'll draw the tile at multiple offsets to support wrapping
        # (so a segment moving across the edge can appear on both sides).
        screenRect: pg.Rect = self.screen.get_rect()
        tileSize = (GameConfig.GRID_SIZE, GameConfig.GRID_SIZE)

        for offsetX in (-GameConfig.SCREEN_WIDTH, 0, GameConfig.SCREEN_WIDTH):
            for offsetY in (-GameConfig.SCREEN_HEIGHT, 0, GameConfig.SCREEN_HEIGHT):
                drawPos = (position[0] + offsetX, position[1] + offsetY)
                rect = pg.Rect(drawPos, tileSize)
                # Only draw if visible on the screen
                if rect.colliderect(screenRect):
                    pg.draw.rect(self.screen, color, rect)
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
        # Current visible apple position (pixel coords)
        self.position = (0, 0)
        # Next decided spawn position (preview) - pixel coords
        self.nextPosition: Optional[Tuple[int, int]] = None
        # Appearance animation state
        self.isAppearing: bool = False
        self.appearTimer: float = 0.0
        self.appearDuration: float = 0.28
        # Initial placement
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
        # Reset any appearance animation
        self.isAppearing = False
        self.appearTimer = 0.0

    def decideNextPosition(
        self,
        forbiddenPositions: Optional[List[Tuple[int, int]]] = None,
        stonePositions: Optional[Set[Tuple[int, int]]] = None,
    ) -> None:
        """
        Decide a next spawn position and store it in `nextPosition`.
        Does not move the visible apple.
        """
        if forbiddenPositions is None:
            forbiddenPositions = []
        if stonePositions is None:
            stonePositions = set()

        allCells: set = {
            (x * GameConfig.GRID_SIZE, y * GameConfig.GRID_SIZE)
            for x in range(GameConfig.GRID_WIDTH)
            for y in range(GameConfig.GRID_HEIGHT)
        }
        availableCells: set = allCells - set(forbiddenPositions) - stonePositions
        if not availableCells:
            self.nextPosition = (GameConfig.SCREEN_WIDTH // 2, GameConfig.SCREEN_HEIGHT // 2)
            return
        self.nextPosition = choice(tuple(availableCells))

    def startAppearance(self) -> None:
        """Animate the apple appearing (growing) at `self.position`."""
        self.isAppearing = True
        self.appearTimer = 0.0
    
    def draw(self) -> None:
        """
        Draw the apple on the screen as a circle.
        """
        if self.screen is None:
            raise ValueError("Screen surface not set. Call setScreen() first.")
        
        if self.bodyColor is None:
            raise ValueError("Color must be specified")
        
        # Calculate center and animated radius for the circle
        centerX: int = self.position[0] + GameConfig.GRID_SIZE // 2
        centerY: int = self.position[1] + GameConfig.GRID_SIZE // 2

        baseRadius = int(GameConfig.GRID_SIZE * 0.8 / 2)
        drawRadius = baseRadius
        if self.isAppearing:
            # Advance timer (caller is responsible for updating appearTimer)
            # Use ease-out scale for appearance
            t = min(1.0, self.appearTimer / max(1e-6, self.appearDuration))
            ease = 1.0 - (1.0 - t) ** 2
            drawRadius = max(1, int(baseRadius * ease))

        # Draw filled circle
        pg.draw.circle(self.screen, self.bodyColor, (centerX, centerY), drawRadius)

        # Draw border with darker color
        borderColor: Tuple[int, int, int] = GameConfig.getBorderColor(self.bodyColor)
        pg.draw.circle(self.screen, borderColor, (centerX, centerY), drawRadius, 1)


class Stone(GameObject):
    """
    Represents a stone obstacle on the game board.
    Stones are groups of cells that form obstacles.
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
        existingStones: List['Stone'] = None
    ) -> List[Tuple[int, int]]:
        """
        Generate a random stone group with randomized size and cell placement.
        Uses random to fill a grid area instead of hardcoded patterns.
        
        Args:
            forbiddenPositions: Set of positions to avoid
            existingStones: List of existing stones to check distance from
            
        Returns:
            List of (x, y) tuples representing stone cell positions
        """
        if existingStones is None:
            existingStones = []
        
        # Randomize stone size (width x height)
        stoneWidth: int = randint(
            GameConfig.MIN_STONE_SIZE,
            GameConfig.MAX_STONE_SIZE
        )
        stoneHeight: int = randint(
            GameConfig.MIN_STONE_SIZE,
            GameConfig.MAX_STONE_SIZE
        )
        
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
        
        if len(availableCells) < stoneWidth * stoneHeight:
            return []
        
        # Try to generate a valid stone group
        for _ in range(200):  # Try up to 200 times
            # Choose random starting position
            startCell: Tuple[int, int] = choice(availableCells)
            
            # Convert to grid coordinates
            startGridX: int = startCell[0] // GameConfig.GRID_SIZE
            startGridY: int = startCell[1] // GameConfig.GRID_SIZE
            
            # Check if this position is far enough from existing stones
            tooClose: bool = False
            for existingStone in existingStones:
                for stonePos in existingStone.positions:
                    stoneGridX: int = stonePos[0] // GameConfig.GRID_SIZE
                    stoneGridY: int = stonePos[1] // GameConfig.GRID_SIZE
                    
                    # Calculate distance (with wrapping)
                    distX: int = min(
                        abs(startGridX - stoneGridX),
                        abs(startGridX - stoneGridX + GameConfig.GRID_WIDTH),
                        abs(startGridX - stoneGridX - GameConfig.GRID_WIDTH)
                    )
                    distY: int = min(
                        abs(startGridY - stoneGridY),
                        abs(startGridY - stoneGridY + GameConfig.GRID_HEIGHT),
                        abs(startGridY - stoneGridY - GameConfig.GRID_HEIGHT)
                    )
                    
                    # Check if too close (considering stone size)
                    maxDist: int = max(distX, distY)
                    if maxDist < GameConfig.MIN_STONE_DISTANCE:
                        tooClose = True
                        break
                
                if tooClose:
                    break
            
            if tooClose:
                continue
            
            # Generate stone by randomly filling the grid area
            stonePositions: List[Tuple[int, int]] = []
            
            # Randomly decide which cells in the grid to fill
            for offsetX in range(stoneWidth):
                for offsetY in range(stoneHeight):
                    # Random inclusion chance with bias to inner cells for larger stones
                    includeChance: float = 0.5
                    isLargeStone: bool = stoneWidth >= 3 and stoneHeight >= 3
                    isInnerCell: bool = (
                        0 < offsetX < stoneWidth - 1 and
                        0 < offsetY < stoneHeight - 1
                    )
                    if isLargeStone:
                        includeChance = 0.9 if isInnerCell else 0.5
                    if random() < includeChance or len(stonePositions) < 2:
                        gridX: int = (startGridX + offsetX) % GameConfig.GRID_WIDTH
                        gridY: int = (startGridY + offsetY) % GameConfig.GRID_HEIGHT
                        
                        cellPos: Tuple[int, int] = (
                            gridX * GameConfig.GRID_SIZE,
                            gridY * GameConfig.GRID_SIZE
                        )
                        
                        # Check if position is forbidden
                        if cellPos not in forbiddenPositions:
                            stonePositions.append(cellPos)
            
            # Ensure we have at least 2 cells
            if len(stonePositions) >= 2:
                return stonePositions
        
        return []

