"""
Test Constants for NotASnake
============================

Simplified constants for unit testing without Pygame dependencies.
"""

# Screen dimensions
SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 768
CELL_SIZE = 20

# Movement constants
DIRECTIONS = {
    "UP": (0, -CELL_SIZE),
    "DOWN": (0, CELL_SIZE),
    "LEFT": (-CELL_SIZE, 0),
    "RIGHT": (CELL_SIZE, 0)
}

OPPOSITES = {
    "UP": "DOWN",
    "DOWN": "UP",
    "LEFT": "RIGHT",
    "RIGHT": "LEFT"
}

# Difficulty levels
DIFFICULTY_LEVELS = {
    "Story game": 6,
    "The Classic": 10,
    "Faster!": 16,
    "Whoosh!!!": 24,
}

# Score attack targets
SA_TARGETS = [15, 30, 50]
