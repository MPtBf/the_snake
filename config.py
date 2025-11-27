"""
Game configuration constants and settings.
"""

from typing import Tuple, Dict
import pygame as pg


class GameConfig:
    """
    Configuration class containing all game constants and settings.
    Centralizes all configuration values for easy modification.
    """
    
    # Grid settings
    # `GRID_SIZE` is the pixel size of one tile. The number of tiles
    # horizontally and vertically remains constant (GRID_WIDTH/GRID_HEIGHT).
    GRID_SIZE: int = 20
    GRID_WIDTH: int = 32  # number of tiles horizontally (fixed)
    GRID_HEIGHT: int = 24  # number of tiles vertically (fixed)

    # Screen dimensions derived from grid size and tile counts
    SCREEN_WIDTH: int = GRID_SIZE * GRID_WIDTH
    SCREEN_HEIGHT: int = GRID_SIZE * GRID_HEIGHT
    
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
    MAX_SPEED_MULTIPLIER: float = 3.0
    SPEED_ACCELERATION: float = 2.0  # multiplier per second while accelerating
    SPEED_DECELERATION: float = 1.5  # multiplier per second while slowing down
    
    # Snake initial length
    INITIAL_SNAKE_LENGTH: int = 3
    
    # Stone configuration
    MIN_STONES: int = 3
    MAX_STONES: int = 7
    MIN_STONE_SIZE: int = 2  # Minimum width/height
    MAX_STONE_SIZE: int = 4  # Maximum width/height
    MIN_STONE_DISTANCE: int = 5  # Minimum distance between stones in cells
    
    # Animation settings (durations are in seconds)
    MOVE_ANIMATION_DURATION: float = 1.5  # Duration of quick movement animation
    TWITCH_ANIMATION_DURATION: float = 0.4  # Duration of stone collision twitch
    TAIL_SHRINK_ANIMATION_DURATION: float = 0.8  # Duration of tail shrinking animation
    GROW_ANIMATION_DURATION: float = 0.8  # Duration of growth animation
    
    # Game title
    GAME_TITLE: str = 'Snake!'
    
    # Data file for saving high scores
    DATA_FILE: str = 'game_data.json'
    
    # Z-index layer settings for rendering priority (lower = drawn first)
    PARTICLE_Z_INDEX: int = 0
    STONE_Z_INDEX: int = 1
    APPLE_Z_INDEX: int = 2
    SNAKE_BODY_Z_INDEX: int = 3
    SNAKE_HEAD_Z_INDEX: int = 4
    
    @staticmethod
    def getBorderColor(color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """
        Calculate a darker border color for a given color.
        Used to create visual depth for game objects.
        
        Args:
            color: RGB tuple representing the base color
            
        Returns:
            RGB tuple representing a darker version of the color
        """
        return tuple(int(c * 0.8) for c in color)
    
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


class RenderDebug:
    """
    Debug flags to toggle rendering features on/off for debugging purposes.
    Set any flag to False to disable that feature's rendering.
    """
    # Core gameplay features
    ENABLE_PARTICLES: bool = False
    ENABLE_SNAKE_BODY: bool = True
    ENABLE_SNAKE_EYES: bool = True
    ENABLE_SNAKE_ANIMATION: bool = False
    ENABLE_BODY_GRADIENT: bool = False  # If False, all segments use same color
    ENABLE_STONES: bool = True
    ENABLE_APPLE: bool = True
    ENABLE_APPLE_HINT: bool = True
    
    # Visual effects
    ENABLE_SHRINKING_ANIMATION: bool = True
    ENABLE_GROWTH_ANIMATION: bool = True
