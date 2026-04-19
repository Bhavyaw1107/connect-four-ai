"""
game_logic.py - Core game logic for Connect Four

Handles board creation, piece dropping, move validation,
and win detection for Connect Four game.
"""

import numpy as np
from constants import ROWS, COLS, EMPTY, PLAYER, AI, WINDOW_LENGTH


def create_board():
    """
    Create a new empty Connect Four board.

    Returns:
        numpy.ndarray: A 6x7 array filled with zeros (EMPTY cells)
    """
    return np.zeros((ROWS, COLS), dtype=int)


def drop_piece(board, row, col, piece):
    """
    Drop a piece into the board at the specified position.

    Args:
        board: The game board
        row: Row index where to place the piece
        col: Column index where to place the piece
        piece: Player identifier (PLAYER or AI)
    """
    board[row][col] = piece


def is_valid_location(board, col):
    """
    Check if a column has available space for a new piece.

    Args:
        board: The game board
        col: Column index to check

    Returns:
        bool: True if the top row of the column is empty
    """
    return board[ROWS - 1][col] == EMPTY


def get_next_open_row(board, col):
    """
    Find the lowest available row in a given column.
    This determines where a piece will land when dropped.

    Args:
        board: The game board
        col: Column index to check

    Returns:
        int: Row index where the piece will land, or None if column is full
    """
    for r in range(ROWS):
        if board[r][col] == EMPTY:
            return r
    return None


def get_valid_locations(board):
    """
    Get a list of all columns that have available space.

    Args:
        board: The game board

    Returns:
        list: List of column indices that are not full
    """
    return [c for c in range(COLS) if is_valid_location(board, c)]


def get_winning_cells(board, piece):
    """
    Return the exact four connected cells for a winning move.

    Args:
        board: The game board
        piece: Player identifier to check win for

    Returns:
        list[tuple[int, int]]: The winning cells, or an empty list if none
    """
    # Horizontal win check
    for c in range(COLS - 3):
        for r in range(ROWS):
            if all(board[r][c + i] == piece for i in range(WINDOW_LENGTH)):
                return [(r, c + i) for i in range(WINDOW_LENGTH)]

    # Vertical win check
    for c in range(COLS):
        for r in range(ROWS - 3):
            if all(board[r + i][c] == piece for i in range(WINDOW_LENGTH)):
                return [(r + i, c) for i in range(WINDOW_LENGTH)]

    # Positive slope diagonal (\) win check
    for c in range(COLS - 3):
        for r in range(ROWS - 3):
            if all(board[r + i][c + i] == piece for i in range(WINDOW_LENGTH)):
                return [(r + i, c + i) for i in range(WINDOW_LENGTH)]

    # Negative slope diagonal (/) win check
    for c in range(COLS - 3):
        for r in range(3, ROWS):
            if all(board[r - i][c + i] == piece for i in range(WINDOW_LENGTH)):
                return [(r - i, c + i) for i in range(WINDOW_LENGTH)]

    return []


def get_winning_cells_from_move(board, row, col, piece):
    """
    Return the winning four cells created by the most recent move.

    Args:
        board: The game board
        row: Row index of the newly placed piece
        col: Column index of the newly placed piece
        piece: Player identifier to check win for

    Returns:
        list[tuple[int, int]]: The winning cells, or an empty list if none
    """
    directions = ((1, 0), (0, 1), (1, 1), (1, -1))

    for delta_row, delta_col in directions:
        connected = [(row, col)]

        for step in (1, -1):
            current_row = row + delta_row * step
            current_col = col + delta_col * step

            while 0 <= current_row < ROWS and 0 <= current_col < COLS:
                if board[current_row][current_col] != piece:
                    break
                connected.append((current_row, current_col))
                current_row += delta_row * step
                current_col += delta_col * step

        if len(connected) >= WINDOW_LENGTH:
            connected.sort()
            return connected[:WINDOW_LENGTH]

    return []


def winning_move(board, piece):
    """
    Check if the specified player has won the game.

    Args:
        board: The game board
        piece: Player identifier to check win for

    Returns:
        bool: True if the player has 4 connected pieces
    """
    return bool(get_winning_cells(board, piece))


def is_terminal_node(board):
    """
    Check if the game has ended (win or draw).

    Args:
        board: The game board

    Returns:
        bool: True if the game is over (win or draw)
    """
    return (
        winning_move(board, PLAYER) or
        winning_move(board, AI) or
        len(get_valid_locations(board)) == 0
    )
