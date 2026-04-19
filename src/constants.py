"""
Constants and Configuration for Connect Four Game
"""

# Grid dimensions
ROWS = 6
COLS = 7

# Player identifiers
PLAYER = 1  # Human player (red pieces)
AI = 2      # Computer player (yellow pieces)
EMPTY = 0   # Empty cell

# Game settings
WINDOW_LENGTH = 4  # Length needed to win
DEPTH = 4          # Minimax search depth

# Piece colors (RGB)
COLOR_PLAYER = (255, 0, 0)      # Red
COLOR_AI = (255, 255, 0)        # Yellow
COLOR_BOARD = (0, 0, 255)       # Blue
COLOR_EMPTY = (0, 0, 0)         # Black (background)
COLOR_HOVER = (200, 200, 200)   # Light gray for hover effect

# UI Dimensions
SQUARE_SIZE = 100
RADIUS = SQUARE_SIZE // 2 - 12
WIDTH = 900
HEIGHT = 860
