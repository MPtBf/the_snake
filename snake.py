"""
Snake class implementation.
"""

from random import choice
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
        
        # Generate initial snake body with length 3 and set initial direction
        self.positions, self.direction = self.generateInitialBody(
            initialPosition,
            forbiddenPositions
        )
        self.nextDirection: Optional[Tuple[int, int]] = None
        self.isAppleEaten: bool = False
        self.isStopped: bool = False  # True when colliding with stone
        
        # Animation system - interpolated positions for jerky movement
        self.renderPositions: List[Tuple[float, float]] = [
            (float(pos[0]), float(pos[1])) for pos in self.positions
        ]
        self.animationTimers: List[float] = [0.0] * len(self.positions)
        self.animationTypes: List[str] = ['idle'] * len(self.positions)  # 'idle', 'move', 'twitch', 'shrink', 'grow'
        self.previousTailPosition: Optional[Tuple[int, int]] = None
        self.isGrowing: bool = False
        self.isShrinking: bool = False
        self.twitchDirection: Optional[Tuple[int, int]] = None
        # Track shrinking tail segments separately
        self.shrinkingSegments: List[Tuple[Tuple[float, float], float, Tuple[int, int]]] = []  # (renderPos, timer, targetPos)
    
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
    ) -> tuple:
        """
        Generate initial snake body with length 3.
        
        Args:
            startPosition: Starting position for the snake head
            forbiddenPositions: Set of positions to avoid
            
        Returns:
            List of positions forming the initial snake body
        """
        # Choose a single direction for the snake so the head and tail align.
        directions: List[Tuple[int, int]] = [
            GameConfig.UP,
            GameConfig.DOWN,
            GameConfig.LEFT,
            GameConfig.RIGHT
        ]
        direction: Tuple[int, int] = choice(directions)

        # Build body so that segments trail behind the head in the opposite
        # direction of movement. This guarantees the head is facing the
        # same direction as the rest of the body.
        positions: List[Tuple[int, int]] = [startPosition]
        dx, dy = direction
        currentPos = startPosition
        for _ in range(GameConfig.INITIAL_SNAKE_LENGTH - 1):
            nextPos = (
                (currentPos[0] - dx * GameConfig.GRID_SIZE) % GameConfig.SCREEN_WIDTH,
                (currentPos[1] - dy * GameConfig.GRID_SIZE) % GameConfig.SCREEN_HEIGHT,
            )
            # If next position is forbidden or already occupied, try adjacent offsets
            if nextPos in forbiddenPositions or nextPos in positions:
                # Try orthogonal fallbacks
                for odx, ody in directions:
                    candidate = (
                        (currentPos[0] - odx * GameConfig.GRID_SIZE) % GameConfig.SCREEN_WIDTH,
                        (currentPos[1] - ody * GameConfig.GRID_SIZE) % GameConfig.SCREEN_HEIGHT,
                    )
                    if candidate not in forbiddenPositions and candidate not in positions:
                        nextPos = candidate
                        break
            positions.append(nextPos)
            currentPos = nextPos

        return positions, direction
    
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
        # Track previous tail position for trail particles
        if len(self.positions) > 0:
            self.previousTailPosition = self.positions[-1]

        # Remember previous render positions so we can start animations
        # of all segments from their previous rendered locations.
        prevRender: List[Tuple[float, float]] = list(self.renderPositions)
        
        # Don't move if stopped (colliding with stone)
        if self.isStopped:
            # Lose one tail cell per tick when stopped
            if len(self.positions) > 1:
                # Start shrink animation for tail
                tailPos = self.positions[-1]
                targetPos = self.positions[-2] if len(self.positions) > 1 else tailPos
                # Add to shrinking segments list
                self.shrinkingSegments.append((
                    (float(tailPos[0]), float(tailPos[1])),  # render position
                    0.0,  # timer
                    targetPos  # target position to animate to
                ))
                # Remove from positions
                self.positions.pop()
                # Remove corresponding animation data
                if len(self.renderPositions) > len(self.positions):
                    self.renderPositions.pop()
                    self.animationTimers.pop()
                    self.animationTypes.pop()
            return
        
        headX, headY = self.getHeadPosition()
        dx, dy = self.direction
        
        # Calculate new head position with screen wrapping
        newHead: Tuple[int, int] = (
            (headX + dx * GameConfig.GRID_SIZE) % GameConfig.SCREEN_WIDTH,
            (headY + dy * GameConfig.GRID_SIZE) % GameConfig.SCREEN_HEIGHT
        )
        
        # Add new head to logical positions
        self.positions.insert(0, newHead)

        # Build new renderPositions so that every segment will animate
        # from its previous rendered location to the new logical cell.
        newRender: List[Tuple[float, float]] = []
        # Head render starts from previous head render (if available)
        if len(prevRender) > 0:
            newRender.append((float(prevRender[0][0]), float(prevRender[0][1])))
        else:
            newRender.append((float(headX), float(headY)))

        # For following segments, they should start from the previous
        # segment's render position (shifted by one).
        for i in range(1, len(self.positions)):
            if i - 1 < len(prevRender):
                newRender.append((float(prevRender[i - 1][0]), float(prevRender[i - 1][1])))
            else:
                # Fallback to logical position
                newRender.append((float(self.positions[i][0]), float(self.positions[i][1])))

        # Insert animation metadata for all segments
        self.renderPositions = newRender
        self.animationTimers = [0.0] * len(self.positions)
        self.animationTypes = ['move'] * len(self.positions)
        
        # Remove tail if apple wasn't eaten. When removing we need to
        # animate tail shrink separately so keep a shrinking segment.
        if not self.isAppleEaten:
            if len(self.positions) > 1:
                tailPos = self.positions[-1]
                # Store shrinking visual copy
                targetPos = self.positions[-2] if len(self.positions) > 1 else tailPos
                self.shrinkingSegments.append((
                    (float(tailPos[0]), float(tailPos[1])),
                    0.0,
                    targetPos
                ))
            # Actually remove the last logical segment
            self.positions.pop()
            # Also remove the render/animation metadata for the popped tail
            if len(self.renderPositions) > len(self.positions):
                self.renderPositions = self.renderPositions[:len(self.positions)]
                self.animationTimers = self.animationTimers[:len(self.positions)]
                self.animationTypes = self.animationTypes[:len(self.positions)]
        else:
            # Growing - new tail segment animates from previous tail position
            self.isGrowing = True
            if len(self.positions) > 1:
                tailIdx = len(self.positions) - 1
                if tailIdx < len(self.renderPositions):
                    # Start grow animation
                    self.animationTimers[tailIdx] = 0.0
                    self.animationTypes[tailIdx] = 'grow'
                    # Set initial render to previous tail so it animates in
                    if self.previousTailPosition:
                        self.renderPositions[tailIdx] = (
                            float(self.previousTailPosition[0]),
                            float(self.previousTailPosition[1])
                        )
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

        # Use linear fade from head (bright) to tail (slightly dim), but
        # avoid modulo cycles that make the last tail sporadically darker.
        total: int = max(1, len(self.positions))
        minBrightness: float = 0.6
        # segmentIndex 0 -> brightness 1.0; segmentIndex (total-1) -> minBrightness
        t: float = segmentIndex / max(1, total - 1)
        brightness: float = 1.0 - t * (1.0 - minBrightness)
        return tuple(int(c * brightness) for c in baseColor)
    
    def updateAnimation(self, deltaTime: float, stonePosition: Optional[Tuple[int, int]] = None) -> None:
        """
        Update animation timers and interpolated positions for jerky movement.
        
        Args:
            deltaTime: Time elapsed since last frame
            stonePosition: Position of stone if colliding (for twitch animation)
        """
        # Update shrinking segments
        aliveShrinking: List[Tuple[Tuple[float, float], float, Tuple[int, int]]] = []
        for renderPos, timer, targetPos in self.shrinkingSegments:
            timer += deltaTime
            progress = min(1.0, timer / GameConfig.TAIL_SHRINK_ANIMATION_DURATION)
            targetFloat = (float(targetPos[0]), float(targetPos[1]))
            newRenderPos = (
                renderPos[0] + (targetFloat[0] - renderPos[0]) * progress,
                renderPos[1] + (targetFloat[1] - renderPos[1]) * progress
            )
            if progress < 1.0:
                aliveShrinking.append((newRenderPos, timer, targetPos))
        self.shrinkingSegments = aliveShrinking
        
        # Update all animation timers
        for i in range(len(self.animationTimers)):
            self.animationTimers[i] += deltaTime
            
            animType = self.animationTypes[i]
            targetPos = (float(self.positions[i][0]), float(self.positions[i][1]))
            currentRender = self.renderPositions[i]
            
            if animType == 'move':
                # Quick movement animation
                progress = min(1.0, self.animationTimers[i] / GameConfig.MOVE_ANIMATION_DURATION)
                # Use ease-out curve for quick snap
                easeProgress = 1.0 - (1.0 - progress) ** 3

                # Compute delta taking wrapping into account so segments
                # take the shortest path across edges.
                dx = targetPos[0] - currentRender[0]
                dy = targetPos[1] - currentRender[1]

                # Adjust for horizontal wrapping
                if abs(dx) > GameConfig.SCREEN_WIDTH / 2:
                    if dx > 0:
                        dx -= GameConfig.SCREEN_WIDTH
                    else:
                        dx += GameConfig.SCREEN_WIDTH

                # Adjust for vertical wrapping
                if abs(dy) > GameConfig.SCREEN_HEIGHT / 2:
                    if dy > 0:
                        dy -= GameConfig.SCREEN_HEIGHT
                    else:
                        dy += GameConfig.SCREEN_HEIGHT

                newX = currentRender[0] + dx * easeProgress
                newY = currentRender[1] + dy * easeProgress
                self.renderPositions[i] = (newX, newY)
                if progress >= 1.0:
                    self.animationTypes[i] = 'idle'
                    # Ensure final position matches logical target exactly
                    self.renderPositions[i] = targetPos
                    
            elif animType == 'twitch' and stonePosition:
                # Twitch toward stone
                progress = min(1.0, self.animationTimers[i] / GameConfig.TWITCH_ANIMATION_DURATION)
                twitchAmount = (GameConfig.GRID_SIZE * 0.15) * (1.0 - abs(progress - 0.5) * 2.0)  # Peak at middle
                if self.twitchDirection:
                    twitchX = self.twitchDirection[0] * twitchAmount
                    twitchY = self.twitchDirection[1] * twitchAmount
                    self.renderPositions[i] = (
                        targetPos[0] + twitchX,
                        targetPos[1] + twitchY
                    )
                if progress >= 1.0:
                    self.animationTypes[i] = 'idle'
                    self.renderPositions[i] = targetPos
                    
                    
            elif animType == 'grow':
                # New segment grows from previous tail position
                progress = min(1.0, self.animationTimers[i] / GameConfig.GROW_ANIMATION_DURATION)
                easeProgress = 1.0 - (1.0 - progress) ** 2
                self.renderPositions[i] = (
                    currentRender[0] + (targetPos[0] - currentRender[0]) * easeProgress,
                    currentRender[1] + (targetPos[1] - currentRender[1]) * easeProgress
                )
                if progress >= 1.0:
                    self.animationTypes[i] = 'idle'
                    self.renderPositions[i] = targetPos
                    self.isGrowing = False
    
    def startTwitchAnimation(self, stonePosition: Tuple[int, int]) -> None:
        """
        Start twitch animation for all segments when hitting stone.
        
        Args:
            stonePosition: Position of the stone being hit
        """
        headPos = self.getHeadPosition()
        # Calculate direction from head to stone
        dx = stonePosition[0] - headPos[0]
        dy = stonePosition[1] - headPos[1]
        # Normalize
        length = (dx * dx + dy * dy) ** 0.5
        if length > 0:
            self.twitchDirection = (dx / length, dy / length)
        else:
            self.twitchDirection = (0, -1)
        
        # Start twitch for all segments
        for i in range(len(self.animationTimers)):
            self.animationTimers[i] = 0.0
            self.animationTypes[i] = 'twitch'
    
    def draw(self) -> None:
        """
        Draw the entire snake by drawing each segment with gradient colors.
        Uses interpolated positions for smooth animation.
        Draws eyes on the head.
        """
        # Draw body segments with gradient colors using render positions
        # Draw up to min of positions and renderPositions (in case of shrink animation)
        drawCount = min(len(self.positions), len(self.renderPositions))
        for index in range(drawCount):
            renderPos = (int(self.renderPositions[index][0]), int(self.renderPositions[index][1]))
            segmentColor: Tuple[int, int, int] = self.getSegmentColor(index)
            self.drawSingleTile(renderPos, segmentColor)
        
        # Draw shrinking tail segments
        for renderPos, timer, _ in self.shrinkingSegments:
            progress = min(1.0, timer / GameConfig.TAIL_SHRINK_ANIMATION_DURATION)
            fade = 1.0 - progress
            tailColor = self.getSegmentColor(len(self.positions) - 1) if len(self.positions) > 0 else GameConfig.SNAKE_COLOR
            fadedColor = tuple(int(c * fade) for c in tailColor)
            pos = (int(renderPos[0]), int(renderPos[1]))
            self.drawSingleTile(pos, fadedColor)
        
        # Draw eyes on the head
        self.drawEyes()
    
    def drawEyes(self) -> None:
        """
        Draw two black circles (eyes) on the front side of the snake's head.
        Eyes are positioned based on the snake's direction.
        Uses interpolated head position for animation.
        """
        if self.screen is None or len(self.positions) == 0 or len(self.renderPositions) == 0:
            return
        
        # Use render position for head
        headRenderPos = self.renderPositions[0]
        headCenterX: int = int(headRenderPos[0]) + GameConfig.GRID_SIZE // 2
        headCenterY: int = int(headRenderPos[1]) + GameConfig.GRID_SIZE // 2
        
        # Eye size and offset scale with grid size
        eyeRadius: int = max(1, GameConfig.GRID_SIZE // 6)
        eyeOffset: int = max(1, GameConfig.GRID_SIZE // 5)  # Distance from center
        
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
        # Sync animation data
        self.renderPositions = self.renderPositions[:collisionIndex]
        self.animationTimers = self.animationTimers[:collisionIndex]
        self.animationTypes = self.animationTypes[:collisionIndex]
    
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
        self.positions, self.direction = self.generateInitialBody(initialPosition, forbiddenPositions)
        self.nextDirection = None
        self.isAppleEaten = False
        self.isStopped = False
        # Reset animation data
        self.renderPositions = [(float(pos[0]), float(pos[1])) for pos in self.positions]
        self.animationTimers = [0.0] * len(self.positions)
        self.animationTypes = ['idle'] * len(self.positions)
        self.previousTailPosition = None
        self.isGrowing = False
        self.isShrinking = False
        self.twitchDirection = None
        self.shrinkingSegments = []
    
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

