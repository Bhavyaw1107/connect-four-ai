"""
evaluation.py - Position evaluation for Connect Four AI

Evaluates board positions to guide the AI's decision-making.
Higher scores indicate better positions for the AI.
"""

from constants import ROWS, COLS, EMPTY, PLAYER, AI, WINDOW_LENGTH


def evaluate_window(window, piece):
    """
    Evaluate a window of 4 cells for scoring purposes.

    A window is a sequence of 4 adjacent cells that can be
    horizontal, vertical, or diagonal.

    Scoring system:
    - 4 in a row (win): +100000 (AI) or -100000 (Player)
    - 3 in a row: +100
    - 2 in a row: +10
    - Blocking opponent 3: -80 penalty

    Args:
        window: List of 4 cell values
        piece: Player identifier (AI or PLAYER)

    Returns:
        int: Score for this window
    """
    score = 0
    opp_piece = PLAYER if piece == AI else AI

    # AI scoring (positive values for AI advantage)
    if window.count(piece) == 4:
        score += 100000  # Winning move
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 100     # Three in a row
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 10      # Two in a row

    # Opponent blocking scoring (negative values)
    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 80      # Must block opponent's three

    return score


def score_position(board, piece):
    """
    Calculate the overall score for the current board position.

    Evaluates all possible windows for the given piece and returns
    a total score. Higher scores favor the AI.

    Args:
        board: The game board
        piece: Player identifier to evaluate for

    Returns:
        int: Total score for the position
    """
    score = 0

    # Center column preference - controlling center is strategically advantageous
    center_array = list(board[:, COLS // 2])
    score += center_array.count(piece) * 6

    # Horizontal windows evaluation
    for r in range(ROWS):
        row_array = list(board[r, :])
        for c in range(COLS - 3):
            window = row_array[c:c + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Vertical windows evaluation
    for c in range(COLS):
        col_array = list(board[:, c])
        for r in range(ROWS - 3):
            window = col_array[r:r + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Positive slope diagonal (\) evaluation
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r + i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    # Negative slope diagonal (/) evaluation
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            window = [board[r - i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score
