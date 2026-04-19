"""
main.py - Main entry point for the Connect Four AI game.

This module coordinates the landing page, guide page, game loop, and
end-of-round transitions.
"""

import time
import threading

import numpy as np
import pygame

from constants import AI, DEPTH, PLAYER
from game_logic import (
    create_board,
    drop_piece,
    get_winning_cells_from_move,
    get_next_open_row,
    get_valid_locations,
    is_valid_location,
)
from minimax import minimax
from ui import ConnectFourUI, GuidePage, LandingPage


PLAYER_STATUS = "Your turn! Pick a column."
AI_STATUS = "AI is thinking..."


def build_overlay(title, subtext, color):
    """Create a UI overlay payload."""
    return {"title": title, "subtext": subtext, "color": color}


def run_game(ui):
    """
    Run a single game loop.

    Returns:
        str: "restart" to immediately replay or "menu" to return home.
    """
    board = create_board()
    turn = PLAYER
    game_over = False
    current_status = PLAYER_STATUS
    current_overlay = None
    winning_cells = []

    ui.draw_state(board, current_status, is_player_turn=True, winning_cells=winning_cells)

    while True:
        ai_thinking = turn == AI and not game_over
        col_to_play, action = ui.handle_events(board, game_over, ai_thinking)

        if action == "restart":
            return "restart"
        if action == "menu":
            return "menu"

        if turn == PLAYER and not game_over and col_to_play is not None:
            if is_valid_location(board, col_to_play):
                row = ui.animate_drop(
                    board,
                    col_to_play,
                    PLAYER,
                    status_text=current_status,
                    is_player_turn=True,
                )
                if row is None:
                    row = get_next_open_row(board, col_to_play)

                drop_piece(board, row, col_to_play, PLAYER)

                winning_cells = get_winning_cells_from_move(board, row, col_to_play, PLAYER)
                if winning_cells:
                    game_over = True
                    current_status = "You connected four!"
                    current_overlay = build_overlay(
                        "You Win!",
                        "Fantastic job! You connected four.",
                        (109, 207, 135),
                    )
                    ui.draw_state(
                        board,
                        current_status,
                        is_player_turn=True,
                        overlay=current_overlay,
                        winning_cells=winning_cells,
                    )
                else:
                    turn = AI
                    current_status = AI_STATUS
                    current_overlay = None
                    winning_cells = []
                    ui.draw_state(board, current_status, is_player_turn=False, winning_cells=winning_cells)

        if turn == AI and not game_over:
            ui.draw_state(board, AI_STATUS, is_player_turn=False)

            ai_result = {"col": None, "done": False}

            def ai_turn():
                col, _ = minimax(board, DEPTH, -np.inf, np.inf, True)
                ai_result["col"] = col
                ai_result["done"] = True

            thread = threading.Thread(target=ai_turn, daemon=True)
            thread.start()

            while not ai_result["done"]:
                pygame.event.pump()
                pygame.time.wait(10)

            thread.join()
            col = ai_result["col"]

            time.sleep(0.25)
            if col is not None and is_valid_location(board, col):
                row = ui.animate_drop(
                    board,
                    col,
                    AI,
                    status_text=AI_STATUS,
                    is_player_turn=False,
                )
                if row is None:
                    row = get_next_open_row(board, col)

                drop_piece(board, row, col, AI)

                winning_cells = get_winning_cells_from_move(board, row, col, AI)
                if winning_cells:
                    game_over = True
                    current_status = "The AI found a winning line."
                    current_overlay = build_overlay(
                        "AI Wins!",
                        "Nice try! Jump back in for another round.",
                        (255, 166, 111),
                    )
                    ui.draw_state(
                        board,
                        current_status,
                        is_player_turn=False,
                        overlay=current_overlay,
                        winning_cells=winning_cells,
                    )
                else:
                    turn = PLAYER
                    current_status = PLAYER_STATUS
                    current_overlay = None
                    winning_cells = []
                    ui.draw_state(board, current_status, is_player_turn=True, winning_cells=winning_cells)

        if not game_over and len(get_valid_locations(board)) == 0:
            game_over = True
            current_status = "No more moves. The board is full."
            current_overlay = build_overlay(
                "It's a Draw!",
                "No worries. Try another colorful round.",
                (159, 181, 211),
            )
            winning_cells = []
            ui.draw_state(
                board,
                current_status,
                is_player_turn=True,
                overlay=current_overlay,
                winning_cells=winning_cells,
            )

        ui.clock.tick(60)


def main():
    """Run the full application."""
    print("Starting Connect Dots...")

    while True:
        landing = LandingPage()
        result = landing.run()
        landing.cleanup()

        if result == "play":
            while True:
                ui = ConnectFourUI()
                outcome = run_game(ui)
                ui.cleanup()

                if outcome == "restart":
                    continue
                break

        elif result == "guide":
            guide = GuidePage()
            guide.run()
            guide.cleanup()


if __name__ == "__main__":
    main()
