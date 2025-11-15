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
        
        # Check for self-collision and cut tail instead of resetting
        collisionIndex: Optional[int] = self.snake.checkSelfCollision()
        if collisionIndex is not None:
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
