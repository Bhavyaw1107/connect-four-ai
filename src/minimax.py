"""
minimax.py - AI Minimax algorithm with Alpha-Beta pruning

Implements the Minimax algorithm with Alpha-Beta pruning to find
the best move for the AI player in Connect Four.
"""

import numpy as np
import random
from constants import PLAYER, AI
from game_logic import (
    get_valid_locations,
    is_terminal_node,
    winning_move,
    get_next_open_row,
    drop_piece
)
from evaluation import score_position


def minimax(board, depth, alpha, beta, maximizing_player):
    """
    Minimax algorithm with Alpha-Beta pruning to find the best move.

    The algorithm recursively evaluates all possible moves to a given
    depth, alternating between maximizing (AI) and minimizing (Player)
    perspectives. Alpha-Beta pruning eliminates branches that cannot
    affect the final decision.

    Args:
        board: The current game board
        depth: How many moves ahead to search
        alpha: Best value the maximizer can guarantee (for pruning)
        beta: Best value the minimizer can guarantee (for pruning)
        maximizing_player: True if AI is evaluating, False for Player

    Returns:
        tuple: (best_column, score) - The best column to play and its score
    """
    # Get valid moves and check for terminal state
    valid_locations = get_valid_locations(board)
    terminal = is_terminal_node(board)

    # Base case: depth limit reached or game ended
    if depth == 0 or terminal:
        if terminal:
            # Game over - evaluate based on outcome
            if winning_move(board, AI):
                return (None, 100000)   # AI wins
            elif winning_move(board, PLAYER):
                return (None, -100000)  # Player wins
            else:
                return (None, 0)        # Draw
        else:
            # Depth limit reached - use heuristic evaluation
            return (None, score_position(board, AI))

    # AI's turn - maximizing player
    if maximizing_player:
        value = -np.inf
        best_col = random.choice(valid_locations)

        for col in valid_locations:
            # Get the row where the piece will land
            row = get_next_open_row(board, col)
            if row is None:
                continue

            # Copy board and simulate the move
            temp_board = board.copy()
            drop_piece(temp_board, row, col, AI)

            # Recursively evaluate this move
            new_score = minimax(temp_board, depth - 1, alpha, beta, False)[1]

            if new_score > value:
                value = new_score
                best_col = col

            # Alpha-Beta pruning
            alpha = max(alpha, value)
            if alpha >= beta:
                break  # Beta cut-off

        return best_col, value

    # Player's turn - minimizing player
    else:
        value = np.inf
        best_col = random.choice(valid_locations)

        for col in valid_locations:
            # Get the row where the piece will land
            row = get_next_open_row(board, col)
            if row is None:
                continue

            # Copy board and simulate the move
            temp_board = board.copy()
            drop_piece(temp_board, row, col, PLAYER)

            # Recursively evaluate this move
            new_score = minimax(temp_board, depth - 1, alpha, beta, True)[1]

            if new_score < value:
                value = new_score
                best_col = col

            # Alpha-Beta pruning
            beta = min(beta, value)
            if alpha >= beta:
                break  # Alpha cut-off

        return best_col, value
