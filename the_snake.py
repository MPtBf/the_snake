"""
Snake Game - Main game file.
A classic snake game implementation using Pygame.
"""

from random import randint
from typing import Tuple, Optional, List, Dict, Set

import pygame as pg

from config import GameConfig
from game_data import GameDataManager
from game_objects import Apple, Stone
from particles import ParticleOptions, ParticleSystem
from snake import Snake


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
        self.particles: ParticleSystem = ParticleSystem()
        self.isAccelerating: bool = False
        self.speedMultiplier: float = 1.0
        self.timeAccumulator: float = 0.0
        self.isGameOver: bool = False
        # Pause state: start paused so main menu/overlay is shown on load
        self.isPaused: bool = True
        self.gameOverReason: str = ""
        self.gameOverFont: pg.font.Font = pg.font.SysFont("arial", 42)
        self.subTextFont: pg.font.Font = pg.font.SysFont("arial", 24)
    
    def generateStones(self) -> List[Stone]:
        """
        Generate 2-3 random stone groups on the game board.
        Ensures stones are at least MIN_STONE_DISTANCE cells apart.
        
        Returns:
            List of Stone objects
        """
        stones: List[Stone] = []
        forbiddenPositions: Set[Tuple[int, int]] = set()
        numStones: int = randint(GameConfig.MIN_STONES, GameConfig.MAX_STONES)
        
        for _ in range(numStones):
            stonePositions: List[Tuple[int, int]] = Stone.generateStoneGroup(
                forbiddenPositions,
                stones
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
                # Open pause menu with ENTER
                if event.key == pg.K_RETURN:
                    self.isPaused = True
                    continue

                # If paused, any key (except ESC) resumes the game
                if self.isPaused:
                    if event.key == pg.K_ESCAPE:
                        return False
                    # Resume on any other key
                    self.isPaused = False
                    # Reset accumulator so movement timing is consistent
                    self.timeAccumulator = 0.0
                    continue

                if event.key in (pg.K_LCTRL, pg.K_RCTRL):
                    self.isAccelerating = True
                    continue

                # Handle escape key
                if event.key == pg.K_ESCAPE:
                    return False

                # Handle direction keys
                if self.isGameOver:
                    continue
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

            elif event.type == pg.KEYUP:
                if event.key in (pg.K_LCTRL, pg.K_RCTRL):
                    self.isAccelerating = False
        
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

    def updateSpeed(self, deltaTime: float) -> None:
        """
        Smoothly adjust the snake movement speed based on acceleration state.
        """

        target = (
            GameConfig.MAX_SPEED_MULTIPLIER
            if self.isAccelerating
            else 1.0
        )
        rate = (
            GameConfig.SPEED_ACCELERATION
            if self.isAccelerating
            else GameConfig.SPEED_DECELERATION
        )
        if self.speedMultiplier < target:
            self.speedMultiplier = min(
                target, self.speedMultiplier + rate * deltaTime
            )
        else:
            self.speedMultiplier = max(
                target, self.speedMultiplier - rate * deltaTime
            )

    def triggerGameOver(self, reason: str) -> None:
        """
        Stop the game loop and show the Game Over message.
        """

        if self.isGameOver:
            return
        self.isGameOver = True
        self.gameOverReason = reason
        pg.display.set_caption(
            f"{GameConfig.GAME_TITLE} - Game Over"
        )

    @staticmethod
    def getCellCenter(position: Tuple[int, int]) -> Tuple[float, float]:
        """
        Calculate the pixel coordinates at the center of a grid cell.
        """

        return (
            position[0] + GameConfig.GRID_SIZE / 2,
            position[1] + GameConfig.GRID_SIZE / 2,
        )

    @staticmethod
    def normalizeDirection(direction: Tuple[int, int]) -> Tuple[float, float]:
        """
        Convert a grid direction tuple into a normalized vector.
        """

        vector = pg.Vector2(direction)
        if vector.length_squared() == 0:
            vector = pg.Vector2(0, -1)
        else:
            vector = vector.normalize()
        return vector.x, vector.y

    def spawnStoneCollisionParticles(
        self,
        stonePosition: Tuple[int, int],
        snakeHeadPosition: Tuple[int, int],
    ) -> None:
        """
        Emit gray particles when the snake collides with a stone.
        Particles fly from stone to snake head.
        """

        # Calculate direction from stone to snake head
        direction = self.calculateDirection(stonePosition, snakeHeadPosition)
        
        options = ParticleOptions(
            position=self.getCellCenter(stonePosition),
            amount=10,
            color=GameConfig.STONE_COLOR,
            sizeRange=(3, 6),
            lifetimeRange=(0.35, 0.6),
            speedRange=(90.0, 170.0),
            direction=direction,
            directionSpread=0.3,
            spawnSpread=4.0,
            shape="square",
        )
        self.particles.emit(options)
    
    def calculateDirection(
        self,
        fromPos: Tuple[int, int],
        toPos: Tuple[int, int]
    ) -> Tuple[float, float]:
        """
        Calculate normalized direction vector from one position to another.
        """
        dx = toPos[0] - fromPos[0]
        dy = toPos[1] - fromPos[1]
        # Handle wrapping
        if abs(dx) > GameConfig.SCREEN_WIDTH // 2:
            dx = dx - GameConfig.SCREEN_WIDTH if dx > 0 else dx + GameConfig.SCREEN_WIDTH
        if abs(dy) > GameConfig.SCREEN_HEIGHT // 2:
            dy = dy - GameConfig.SCREEN_HEIGHT if dy > 0 else dy + GameConfig.SCREEN_HEIGHT
        
        length = (dx * dx + dy * dy) ** 0.5
        if length > 0:
            return (dx / length, dy / length)
        return (0.0, -1.0)

    def spawnTailCollisionParticles(
        self,
        position: Tuple[int, int],
        direction: Tuple[int, int],
    ) -> None:
        """
        Emit dark green particles when the snake collides with itself.
        """

        options = ParticleOptions(
            position=self.getCellCenter(position),
            amount=12,
            color=(0, 120, 0),
            sizeRange=(2, 5),
            lifetimeRange=(0.25, 0.55),
            speedRange=(80.0, 150.0),
            direction=self.normalizeDirection(direction),
            directionSpread=0.4,
            spawnSpread=3.0,
            shape="circle",
        )
        self.particles.emit(options)

    def spawnAppleParticles(
        self,
        position: Tuple[int, int],
        direction: Tuple[int, int],
    ) -> None:
        """
        Emit red particles when the snake eats an apple.
        Particles fly out faster than snake speed.
        """
        # Calculate base speed relative to snake speed (faster)
        baseSpeed = GameConfig.SPEED * GameConfig.GRID_SIZE * self.speedMultiplier
        particleSpeed = baseSpeed * 1.5  # 1.5x faster than snake

        options = ParticleOptions(
            position=self.getCellCenter(position),
            amount=14,
            color=GameConfig.APPLE_COLOR,
            sizeRange=(2, 4),
            lifetimeRange=(0.2, 0.45),
            speedRange=(particleSpeed * 0.7, particleSpeed * 1.3),
            direction=self.normalizeDirection(direction),
            directionSpread=0.35,
            spawnSpread=2.0,
            shape="circle",
        )
        self.particles.emit(options)
    
    def spawnTrailParticles(
        self,
        tailPosition: Tuple[int, int],
    ) -> None:
        """
        Emit yellow trail particles behind the snake tail.
        Only spawns when tail moves (not when growing).
        """
        from random import uniform
        
        options = ParticleOptions(
            position=self.getCellCenter(tailPosition),
            amount=8,
            color=(255, 255, 0),  # Yellow
            sizeRange=(1, 3),
            lifetimeRange=(0.8, 1.2),  # Long lifetime
            speedRange=(10.0, 20.0),  # Small random speed
            direction=(0.0, 0.0),  # Random direction
            directionSpread=2.0,  # Full random spread
            spawnSpread=6.0,  # Randomized position
            shape="circle",
        )
        self.particles.emit(options)
    
    def updateGameState(self) -> None:
        """
        Update all game objects and check for collisions.
        Handles apple eating, snake self-collision, and stone collisions.
        """
        if self.isGameOver:
            return

        # Update snake direction (pass stone positions to prevent 180 rotation)
        self.snake.updateDirection(self.stonePositions)
        
        # Check for stone collision before moving
        # Calculate where the head would be after moving
        headX, headY = self.snake.getHeadPosition()
        dx, dy = self.snake.direction
        nextHead: Tuple[int, int] = (
            (headX + dx * GameConfig.GRID_SIZE) % GameConfig.SCREEN_WIDTH,
            (headY + dy * GameConfig.GRID_SIZE) % GameConfig.SCREEN_HEIGHT
        )
        
        # Check if next position is a stone
        hitStone: bool = nextHead in self.stonePositions
        wasStopped: bool = self.snake.isStopped
        self.snake.isStopped = hitStone
        
        # Spawn particles and trigger animation when hitting stone
        if hitStone:
            if not wasStopped:
                # First collision - start twitch animation
                self.snake.startTwitchAnimation(nextHead)
            # Spawn particles every move when colliding
            self.spawnStoneCollisionParticles(nextHead, self.snake.getHeadPosition())
        
        # Track tail position before move for trail particles
        oldTailPos: Optional[Tuple[int, int]] = None
        wasGrowing: bool = self.snake.isAppleEaten
        if len(self.snake.positions) > 0:
            oldTailPos = self.snake.positions[-1]
        
        # Move snake (will handle stopping internally)
        self.snake.move()
        
        # Spawn trail particles if tail moved (not when growing)
        if (not wasGrowing and 
            not self.snake.isStopped and
            oldTailPos and 
            len(self.snake.positions) > 0 and
            self.snake.previousTailPosition):
            self.spawnTrailParticles(self.snake.previousTailPosition)

        if self.snake.isStopped and len(self.snake.positions) < GameConfig.INITIAL_SNAKE_LENGTH:
            self.triggerGameOver("Stone collision")
            return
        
        # Check if snake ate the apple
        if self.snake.getHeadPosition() == self.apple.position:
            self.spawnAppleParticles(self.snake.getHeadPosition(), self.snake.direction)
            self.snake.eatApple()
            self.apple.randomizePosition(
                forbiddenPositions=self.snake.positions,
                stonePositions=self.stonePositions
            )
        
        # Check for self-collision and cut tail instead of resetting
        collisionIndex: Optional[int] = self.snake.checkSelfCollision()
        if collisionIndex is not None:
            self.spawnTailCollisionParticles(
                self.snake.getHeadPosition(),
                self.snake.direction,
            )
            self.snake.cutTail(collisionIndex)
        
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
        self.particles.draw(self.screen)

        if self.isGameOver:
            self.drawGameOverOverlay()
        
        # Update display
        pg.display.update()

    def drawGameOverOverlay(self) -> None:
        """
        Render the Game Over text overlay.
        """

        overlay = pg.Surface(
            (GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT), pg.SRCALPHA
        )
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        title = self.gameOverFont.render("Game Over", True, (255, 255, 255))
        reasonText = self.subTextFont.render(
            self.gameOverReason or "Try again!",
            True,
            (200, 200, 200),
        )
        infoText = self.subTextFont.render(
            "Close the game to restart.",
            True,
            (200, 200, 200),
        )
        centerX = GameConfig.SCREEN_WIDTH // 2
        centerY = GameConfig.SCREEN_HEIGHT // 2
        self.screen.blit(title, title.get_rect(center=(centerX, centerY - 20)))
        self.screen.blit(
            reasonText, reasonText.get_rect(center=(centerX, centerY + 20))
        )
        self.screen.blit(
            infoText, infoText.get_rect(center=(centerX, centerY + 50))
        )

    def drawPauseOverlay(self) -> None:
        """
        Render the Pause overlay. Shown at startup and when the player presses Enter.
        Press any key to resume.
        """

        overlay = pg.Surface(
            (GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT), pg.SRCALPHA
        )
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        title = self.gameOverFont.render(GameConfig.GAME_TITLE, True, (255, 255, 255))
        infoText = self.subTextFont.render(
            "Press any key to start / resume",
            True,
            (220, 220, 220),
        )
        centerX = GameConfig.SCREEN_WIDTH // 2
        centerY = GameConfig.SCREEN_HEIGHT // 2
        self.screen.blit(title, title.get_rect(center=(centerX, centerY - 20)))
        self.screen.blit(infoText, infoText.get_rect(center=(centerX, centerY + 20)))
    
    def run(self) -> None:
        """
        Main game loop.
        Runs until the player exits the game.
        Speed is controlled to 3 cells per second with acceleration support.
        """
        running: bool = True
        while running:
            deltaTime: float = self.clock.tick(60) / 1000.0

            # Handle input
            running = self.handleInput()

            # Update speed multiplier
            # Only update speed while not paused
            if not self.isPaused:
                self.updateSpeed(deltaTime)

            if not self.isGameOver and not self.isPaused:
                self.timeAccumulator += deltaTime
                movementInterval = 1.0 / (
                    GameConfig.SPEED * self.speedMultiplier
                )
                while (
                    self.timeAccumulator >= movementInterval
                    and not self.isGameOver
                ):
                    self.timeAccumulator -= movementInterval
                    self.updateGameState()
            else:
                # When paused or game over, stop accumulating movement
                if self.isPaused:
                    self.timeAccumulator = 0.0
            

            # Update snake animation (don't animate while paused or game over)
            if not self.isGameOver and not self.isPaused:
                stonePos = None
                if self.snake.isStopped and len(self.snake.positions) > 0:
                    # Find stone position for twitch animation
                    headX, headY = self.snake.getHeadPosition()
                    dx, dy = self.snake.direction
                    nextHead = (
                        (headX + dx * GameConfig.GRID_SIZE) % GameConfig.SCREEN_WIDTH,
                        (headY + dy * GameConfig.GRID_SIZE) % GameConfig.SCREEN_HEIGHT
                    )
                    if nextHead in self.stonePositions:
                        stonePos = nextHead
                self.snake.updateAnimation(deltaTime, stonePos)
            
            # Update particles only while not paused (pause freezes visuals)
            if not self.isPaused:
                self.particles.update(deltaTime)

            # Render everything every frame for smooth visuals
            self.render()

            # If paused, draw pause overlay on top and update display
            if self.isPaused and not self.isGameOver:
                self.drawPauseOverlay()
                pg.display.update()
        
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
