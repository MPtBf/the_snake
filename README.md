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
- **Smart Spawning**: Snake and apples spawn in random positions, avoiding stone obstacles
- **High Score Tracking**: Persistent high score system that saves your best performance
- **Dual Controls**: Support for both arrow keys and WASD keys

### Game Mechanics

- **Snake Movement**: The snake moves at 3 cells per second with smooth rendering
- **Initial Length**: Snake starts with 3 segments
- **Stone Collisions**: When the snake hits a stone, it stops moving and loses one tail segment per game tick until the player changes direction
- **Self-Collision**: Snake resets when it collides with its own body (requires at least 5 segments)
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
- **ESC**: Exit the game

## Game Data

The game saves your high score in `game_data.json` in the project directory.

## Future Plans

### Bug Fixes & Improvements

0. **Snake tail cutting on collision**
    - On collision with its tail Snake should not respawn, but lose the tail part that it collided with

1. **Fix bugs with stone collision**
   - Ensure proper stopping and resuming behavior
   - Fix edge cases with stone positioning
   - Fix snake 180 rotation possibility while colliding with stone

2. **Improve stone generation algorithm**
   - Better distribution of stones across the game board
   - Prevent stones from blocking too much of the playable area
   - Fully randomize stone shape generation without hardcoding every state
   - Make possible to easily change size of stone to generate

### Visual Enhancements

3. **Add particles**
   - Particle effects when snake eats apples
   - Particle trails for snake movement
   - Effect on collision with stone
   - Snake tail disappearing effect when the snake collides with it

4. **Add smooth animations and other visuals**
   - Smooth snake movement transitions
   - Animated apple appearance/disappearance

### Game Features

5. **Add game main menu**
   - Start screen with game title
   - Options menu for settings
   - High score display
   - Game instructions

6. **Add ability to select different game modes or maps**
   - ...

### Advanced Features

7. **Add textures maybe?**
   - Replace solid colors with sprite textures
   - Animated snake skin textures
   - Themed visual styles (nature, space, etc.)

8. **Add multiplayer maybe?**
   - Local "multiplayer" with other snakes (bots)
   - Competitive mode
   - Cooperative mode
   - Online multiplayer support
