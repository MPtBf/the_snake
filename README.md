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
   - Fix snake spawn directions bug (head should be rotated in the save direction as a tail, but now it seems like tail and head directions are chosen independently of each other)
   - Come up with new ideas

- **Add smooth animations and other visuals**
   - Last tail segment is getting darker on move, but it should not
   - Last tail segment is flying through the entire fiend, but it should not. It should move on edges like head segment.
   - Snake looses its eyes when wrapping around edges.

   - Snake tail segments are drawn on top of the head segment, but snake head should have bigger z-index. Also snake movement particles should have smaller z-index than the snake.
   - Twitch animation when colliding with stones
   - Animated tail shrinking when hitting stones
   - Animated tail growth when eating apples
   - Field edges wrap visibility to gain more control

- **Add particles**
   - Add tail disappearing particles

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


## New Features and recent changes (window resize, apple hints, improved animation)

- **Resizable / Fullscreen Window**: The game now supports window resizing and fullscreen (F11). Internally the game renders to a fixed logical surface sized to the game's grid and then scales that surface to the window while preserving aspect ratio. If the window aspect doesn't match the game field, dark letterbox bars remain visible so the entire field is always shown.

- **Apple Hint & Appearance Animation**: When the player gets close to the apple (within 5 cells), the apple decides a new spawn location and subtle particles spawn at that location as a hint. If the player moves away (more than 5 cells) the hint stops. If the player eats the apple, the apple reappears at the decided position with a smooth grow animation. The apple is drawn at 0.8 of a tile size.

- **Full-Body Smooth Movement**: All snake segments now animate smoothly between logical cells, including correct wrapping behavior (segments use the shortest wrapped path across edges). This fixes abrupt teleporting or segments flying across the entire field when crossing edges.
