# Snake Game

A classic Snake game implementation built with Python and Pygame, featuring modern object-oriented design, type annotations, and enhanced gameplay mechanics.

## Description

This Snake game is a fully object-oriented implementation that brings the classic arcade game to life with several enhancements:

### Core Features

- **Classic Snake Gameplay**: Control a snake that grows as it eats apples
- **Obstacle System**: Gray stone obstacles (2-3 randomly placed groups) that the snake must avoid
- **Visual Enhancements**:
  - Snake with animated eyes that follow the direction of movement
  - Gradient color system: snake body has a brightness gradient that cycles from head to tail
  - Circular apples instead of square tiles
  - Dynamic particle effects for stone crashes, tail cuts, and apple bites
- **Smart Spawning**: Snake and apples spawn in random positions, avoiding stone obstacles
- **High Score Tracking**: Persistent high score system that saves your best performance
- **Dual Controls**: Support for both arrow keys and WASD keys

### Game Mechanics

- **Snake Movement**: The snake moves at 3 cells per second with smooth rendering
- **Acceleration**: Hold `Ctrl` to ease into a 3× speed boost and release to decelerate smoothly
- **Initial Length**: Snake starts with 3 segments
- **Stone Collisions**: When the snake hits a stone, it stops, loses a tail segment each tick, spawns debris, and triggers a Game Over if its length drops below three segments
- **Self-Collision**: The snake cuts its tail exactly at the collision cell, shrinking without a full reset and spawning debris
- **Screen Wrapping**: Snake wraps around screen edges

### Technical Details

- **Object-Oriented Design**: Clean class hierarchy with `GameObject` as base class
- **Type Annotations**: Full type hints throughout the codebase
- **CamelCase Naming**: Consistent naming convention
- **English Documentation**: Comprehensive docstrings and comments

## Installation

1. Install Python 3.8 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Game

```bash
python the_snake.py
```

## Controls

- **Arrow Keys** or **WASD**: Change snake direction
- **Ctrl**: Hold to smoothly accelerate up to 3× speed
- **ESC**: Exit the game

## Game Data

The game saves your high score in `game_data.json` in the project directory.



## List of new game features

- **Improve the snake**
   - Come up with new ideas

- **Add particles**
   - Add tail disappearing particles

- **Add smooth animations and other visuals**
   - Jerky smooth snake movement animation
   - Twitch animation when colliding with stones
   - Animated tail shrinking when hitting stones
   - Animated tail growth when eating apples
   - Animated apple appearance/disappearance

   - Field edges wrap visibility to gain more control

### Game Features

- **Add game main menu**
   - Start screen with game title
   - Options menu for settings
   - High score display
   - Game instructions

- **Add ability to select different game modes or maps**
   - ...

### Advanced Features

- **Add textures maybe?**
   - Replace solid colors with sprite textures
   - Animated snake skin textures
   - Themed visual styles (nature, space, etc.)

- **Add multiplayer maybe?**
   - Local "multiplayer" with other snakes (bots)
   - Competitive mode
   - Cooperative mode
   - Online multiplayer support


## Recent Changes

- **Smoother Snake Animation**: The snake head and body now interpolate between grid cells for noticeably smoother movement (fixed jerky teleport). Implemented in `snake.py` by setting the new head render position to the previous render position and animating it toward the new cell.

- **Pause Menu**: Added a pause overlay that appears on game load and when pressing `Enter`. Resume by pressing any key. Implemented in `the_snake.py` with a new `isPaused` state and `drawPauseOverlay` method.

These changes improve visual polish and provide a simple pause/start screen for the player.
