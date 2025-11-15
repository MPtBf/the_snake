"""
Game data management for saving and loading high scores.
"""

import json
from typing import Dict, Optional
from config import GameConfig


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

