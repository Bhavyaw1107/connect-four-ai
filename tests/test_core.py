import sys
import unittest
from pathlib import Path

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from constants import AI, PLAYER
from evaluation import evaluate_window
from game_logic import (
    create_board,
    drop_piece,
    get_next_open_row,
    get_winning_cells,
    get_winning_cells_from_move,
    winning_move,
)
from minimax import minimax


class ConnectFourCoreTests(unittest.TestCase):
    def test_create_board_uses_expected_shape(self):
        board = create_board()
        self.assertEqual(board.shape, (6, 7))
        self.assertTrue((board == 0).all())

    def test_get_next_open_row_fills_from_bottom_up(self):
        board = create_board()
        self.assertEqual(get_next_open_row(board, 2), 0)
        drop_piece(board, 0, 2, PLAYER)
        self.assertEqual(get_next_open_row(board, 2), 1)

    def test_winning_move_detects_horizontal_vertical_and_diagonal(self):
        horizontal = create_board()
        for col in range(4):
            drop_piece(horizontal, get_next_open_row(horizontal, col), col, PLAYER)
        self.assertTrue(winning_move(horizontal, PLAYER))

        vertical = create_board()
        for _ in range(4):
            row = get_next_open_row(vertical, 3)
            drop_piece(vertical, row, 3, AI)
        self.assertTrue(winning_move(vertical, AI))

        diagonal = create_board()
        diagonal_moves = [
            (0, PLAYER),
            (1, AI),
            (1, PLAYER),
            (2, AI),
            (2, AI),
            (2, PLAYER),
            (3, AI),
            (3, AI),
            (3, AI),
            (3, PLAYER),
        ]
        for col, piece in diagonal_moves:
            drop_piece(diagonal, get_next_open_row(diagonal, col), col, piece)
        self.assertTrue(winning_move(diagonal, PLAYER))

        reverse_diagonal = create_board()
        reverse_moves = [
            (3, PLAYER),
            (2, AI),
            (2, PLAYER),
            (1, AI),
            (1, AI),
            (1, PLAYER),
            (0, AI),
            (0, AI),
            (0, AI),
            (0, PLAYER),
        ]
        for col, piece in reverse_moves:
            drop_piece(reverse_diagonal, get_next_open_row(reverse_diagonal, col), col, piece)
        self.assertTrue(winning_move(reverse_diagonal, PLAYER))
        self.assertEqual(len(get_winning_cells(reverse_diagonal, PLAYER)), 4)

    def test_winning_move_does_not_trigger_on_scattered_pieces(self):
        board = create_board()
        scattered_moves = [
            (0, AI),
            (1, AI),
            (3, AI),
            (4, AI),
            (6, AI),
        ]
        for col, piece in scattered_moves:
            drop_piece(board, get_next_open_row(board, col), col, piece)

        self.assertFalse(winning_move(board, AI))
        self.assertEqual(get_winning_cells(board, AI), [])

    def test_get_winning_cells_from_move_requires_last_move_to_complete_line(self):
        board = create_board()
        for col in range(3):
            drop_piece(board, get_next_open_row(board, col), col, AI)

        row = get_next_open_row(board, 4)
        drop_piece(board, row, 4, AI)

        self.assertEqual(get_winning_cells_from_move(board, row, 4, AI), [])

        winning_row = get_next_open_row(board, 3)
        drop_piece(board, winning_row, 3, AI)
        self.assertEqual(len(get_winning_cells_from_move(board, winning_row, 3, AI)), 4)

    def test_evaluate_window_rewards_threats_and_blocks(self):
        self.assertGreater(evaluate_window([AI, AI, AI, 0], AI), 0)
        self.assertLess(evaluate_window([PLAYER, PLAYER, PLAYER, 0], AI), 0)

    def test_minimax_takes_immediate_winning_move(self):
        board = create_board()
        for col in range(3):
            drop_piece(board, get_next_open_row(board, col), col, AI)

        col, _ = minimax(board, 4, -np.inf, np.inf, True)
        self.assertEqual(col, 3)


if __name__ == "__main__":
    unittest.main()
