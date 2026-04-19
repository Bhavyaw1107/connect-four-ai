"""
ui.py - Pygame user interface for a playful Connect Four experience.

The UI is built around a light, cheerful visual language intended to feel
like a polished children's game while keeping the controls simple.
"""

import math
import sys

import pygame

from constants import (
    AI,
    COLS,
    EMPTY,
    HEIGHT,
    PLAYER,
    RADIUS,
    ROWS,
    SQUARE_SIZE,
    WIDTH,
)
from game_logic import get_next_open_row, is_valid_location


# Soft pastel palette
COLOR_SKY_TOP = (209, 236, 255)
COLOR_SKY_BOTTOM = (255, 244, 214)
COLOR_PANEL = (255, 255, 255)
COLOR_PANEL_BORDER = (205, 220, 242)
COLOR_PANEL_SHADOW = (178, 199, 227)
COLOR_BOARD = (137, 191, 255)
COLOR_BOARD_BORDER = (102, 155, 229)
COLOR_SLOT = (240, 247, 255)
COLOR_SLOT_SHADOW = (197, 215, 241)
COLOR_TEXT = (73, 88, 122)
COLOR_TEXT_SOFT = (111, 124, 154)
COLOR_ACCENT = (126, 212, 198)
COLOR_PLAYER = (255, 131, 165)
COLOR_PLAYER_GLOW = (255, 204, 220)
COLOR_AI = (255, 216, 102)
COLOR_AI_GLOW = (255, 239, 183)
COLOR_SUCCESS = (109, 207, 135)
COLOR_WARNING = (255, 166, 111)
COLOR_DRAW = (159, 181, 211)
COLOR_BUTTON = (255, 255, 255)
COLOR_BUTTON_HOVER = (255, 237, 247)
COLOR_BUTTON_ALT = (235, 250, 246)
COLOR_BUTTON_ALT_HOVER = (221, 246, 239)
COLOR_OVERLAY = (86, 106, 142, 132)


# Layout
HEADER_HEIGHT = 130
FOOTER_HEIGHT = 95
BOARD_WIDTH = COLS * SQUARE_SIZE
BOARD_HEIGHT = ROWS * SQUARE_SIZE
BOARD_X = (WIDTH - BOARD_WIDTH) // 2
BOARD_Y = HEADER_HEIGHT
BOARD_RECT = pygame.Rect(BOARD_X, BOARD_Y, BOARD_WIDTH, BOARD_HEIGHT)
FOOTER_RECT = pygame.Rect(32, HEIGHT - FOOTER_HEIGHT - 24, WIDTH - 64, FOOTER_HEIGHT)


BRAND_SIGNATURE_LABEL = "DESIGNED & ENGINEERED BY"
BRAND_SIGNATURE_NAMES = "Mit Parekh & Bhavya Parmar"
COPYRIGHT_TEXT = "© 2026 ConnectDots. All rights reserved."
WINDOW_FLAGS = pygame.RESIZABLE
MIN_WINDOW_WIDTH = 900
MIN_WINDOW_HEIGHT = 760


# Fonts are created lazily after pygame is initialized.
TITLE_FONT = None
SUBTITLE_FONT = None
BUTTON_FONT = None
LARGE_FONT = None
MEDIUM_FONT = None
SMALL_FONT = None
TINY_FONT = None

# Override to keep copyright text UTF-safe across editors.
COPYRIGHT_TEXT = "\u00A9 2026 ConnectDots. All rights reserved."


def ensure_pygame():
    """Initialize pygame and rebuild fonts if needed."""
    global TITLE_FONT, SUBTITLE_FONT, BUTTON_FONT, LARGE_FONT
    global MEDIUM_FONT, SMALL_FONT, TINY_FONT

    if not pygame.get_init():
        pygame.init()
    if not pygame.font.get_init():
        pygame.font.init()

    TITLE_FONT = pygame.font.SysFont("comicsansms", 60, bold=True)
    SUBTITLE_FONT = pygame.font.SysFont("comicsansms", 30, bold=True)
    BUTTON_FONT = pygame.font.SysFont("comicsansms", 28, bold=True)
    LARGE_FONT = pygame.font.SysFont("comicsansms", 42, bold=True)
    MEDIUM_FONT = pygame.font.SysFont("comicsansms", 28, bold=True)
    SMALL_FONT = pygame.font.SysFont("comicsansms", 22)
    TINY_FONT = pygame.font.SysFont("comicsansms", 18)


def draw_gradient_background(screen):
    """Paint a soft sky gradient across the entire window."""
    for y in range(HEIGHT):
        ratio = y / max(HEIGHT - 1, 1)
        color = (
            int(COLOR_SKY_TOP[0] * (1 - ratio) + COLOR_SKY_BOTTOM[0] * ratio),
            int(COLOR_SKY_TOP[1] * (1 - ratio) + COLOR_SKY_BOTTOM[1] * ratio),
            int(COLOR_SKY_TOP[2] * (1 - ratio) + COLOR_SKY_BOTTOM[2] * ratio),
        )
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))


def draw_cloud(screen, x, y, scale=1.0):
    """Draw a rounded cartoon cloud."""
    color = (255, 255, 255)
    shadow = (226, 236, 252)
    circles = [
        (x, y, 20),
        (x + 24 * scale, y - 8 * scale, 24),
        (x + 54 * scale, y, 22),
        (x + 76 * scale, y - 4 * scale, 18),
    ]
    for cx, cy, radius in circles:
        pygame.draw.circle(screen, shadow, (int(cx), int(cy + 6 * scale)), int(radius * scale))
    for cx, cy, radius in circles:
        pygame.draw.circle(screen, color, (int(cx), int(cy)), int(radius * scale))
    pygame.draw.rect(
        screen,
        color,
        pygame.Rect(int(x - 6 * scale), int(y), int(92 * scale), int(28 * scale)),
        border_radius=int(14 * scale),
    )


def draw_copyright(screen, y):
    """Render the copyright line."""
    copyright_label = TINY_FONT.render(COPYRIGHT_TEXT, True, COLOR_TEXT_SOFT)
    screen.blit(copyright_label, copyright_label.get_rect(center=(WIDTH // 2, y)))


def draw_brand_signature(screen, y):
    """Render the landing-page creator signature."""
    label = TINY_FONT.render(BRAND_SIGNATURE_LABEL, True, COLOR_TEXT_SOFT)
    screen.blit(label, label.get_rect(center=(WIDTH // 2, y)))

    name_font = pygame.font.SysFont("comicsansms", 26, bold=True)
    draw_centered_wrapped_text(screen, BRAND_SIGNATURE_NAMES, name_font, COLOR_ACCENT, WIDTH // 2, y + 30, 520, 28, max_lines=2)


def wrap_text(text, font, max_width):
    """Split text into lines that fit within a maximum width."""
    words = text.split()
    if not words:
        return [""]

    lines = []
    current_line = words[0]
    for word in words[1:]:
        trial_line = f"{current_line} {word}"
        if font.size(trial_line)[0] <= max_width:
            current_line = trial_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    return lines


def truncate_text(text, font, max_width):
    """Truncate text with ellipsis if it exceeds max width."""
    if font.size(text)[0] <= max_width:
        return text
    ellipsis = "..."
    truncated = text
    while font.size(truncated + ellipsis)[0] > max_width and len(truncated) > 0:
        truncated = truncated[:-1]
    return truncated + ellipsis if truncated else ellipsis


def clamp_wrapped_lines(text, font, max_width, max_lines):
    """Wrap text and clamp it to a maximum number of lines."""
    lines = wrap_text(text, font, max_width)
    if len(lines) <= max_lines:
        return lines

    kept_lines = lines[: max_lines - 1]
    remainder = " ".join(lines[max_lines - 1 :])
    kept_lines.append(truncate_text(remainder, font, max_width))
    return kept_lines


def draw_wrapped_lines(screen, lines, font, color, left, top, line_height):
    """Draw wrapped lines and return the next y position."""
    current_y = top
    for line in lines:
        label = font.render(line, True, color)
        screen.blit(label, (left, current_y))
        current_y += line_height
    return current_y


def draw_centered_wrapped_text(screen, text, font, color, center_x, top, max_width, line_height, max_lines=None):
    """Draw centered wrapped text within a bounded width."""
    lines = wrap_text(text, font, max_width) if max_lines is None else clamp_wrapped_lines(text, font, max_width, max_lines)
    current_y = top
    for line in lines:
        label = font.render(line, True, color)
        rect = label.get_rect(center=(center_x, current_y))
        screen.blit(label, rect)
        current_y += line_height
    return current_y


def get_viewport(window_size):
    """Return the centered viewport for the fixed-size virtual canvas."""
    window_width, window_height = window_size
    scale = min(window_width / WIDTH, window_height / HEIGHT)
    render_width = max(1, int(WIDTH * scale))
    render_height = max(1, int(HEIGHT * scale))
    offset_x = (window_width - render_width) // 2
    offset_y = (window_height - render_height) // 2
    return pygame.Rect(offset_x, offset_y, render_width, render_height)


def get_desktop_size():
    """Return the current desktop resolution."""
    desktop_sizes = pygame.display.get_desktop_sizes()
    if desktop_sizes:
        return desktop_sizes[0]

    display_info = pygame.display.Info()
    return display_info.current_w, display_info.current_h


def create_window(size, fullscreen=False):
    """Create a responsive window; fullscreen uses a maximized windowed view."""
    if fullscreen:
        desktop_w, desktop_h = get_desktop_size()
        screen = pygame.display.set_mode((desktop_w, desktop_h), WINDOW_FLAGS)
        return screen

    width = max(MIN_WINDOW_WIDTH, size[0])
    height = max(MIN_WINDOW_HEIGHT, size[1])

    desktop_w, desktop_h = get_desktop_size()
    width = min(width, desktop_w)
    height = min(height, desktop_h)
    screen = pygame.display.set_mode((width, height), WINDOW_FLAGS)
    return screen


def toggle_fullscreen(screen, is_fullscreen, windowed_size):
    """Toggle between maximized windowed mode and the last windowed size."""
    if is_fullscreen:
        new_screen = create_window(windowed_size, fullscreen=False)
        return new_screen, False, new_screen.get_size()

    current_size = screen.get_size()
    new_screen = create_window(get_desktop_size(), fullscreen=True)
    return new_screen, True, current_size


def handle_resize_event(event_size, windowed_size):
    """Apply resize safely and preserve a reliable logical window state."""
    new_screen = create_window(event_size, fullscreen=False)
    actual_size = new_screen.get_size()
    desktop_size = get_desktop_size()
    is_fullscreen = actual_size[0] >= desktop_size[0] and actual_size[1] >= desktop_size[1] - 2
    if is_fullscreen:
        return new_screen, True, windowed_size
    return new_screen, False, actual_size


def present_canvas(window, canvas):
    """Scale the fixed-size canvas to the active window without distortion."""
    viewport = get_viewport(window.get_size())
    window.fill(COLOR_SKY_BOTTOM)
    if viewport.size == (WIDTH, HEIGHT):
        window.blit(canvas, viewport.topleft)
    else:
        scaled = pygame.transform.smoothscale(canvas, viewport.size)
        window.blit(scaled, viewport.topleft)
    pygame.display.flip()


def to_virtual_pos(pos, window_size):
    """Map a real window position back to the fixed virtual canvas."""
    viewport = get_viewport(window_size)
    if not viewport.collidepoint(pos):
        return -1, -1

    relative_x = pos[0] - viewport.left
    relative_y = pos[1] - viewport.top
    virtual_x = int(relative_x * WIDTH / viewport.width)
    virtual_y = int(relative_y * HEIGHT / viewport.height)
    return virtual_x, virtual_y


def wrapped_text_block(screen, text, font, color, left, top, max_width, line_height):
    """Render wrapped multi-line text and return the final y position."""
    return draw_wrapped_lines(screen, wrap_text(text, font, max_width), font, color, left, top, line_height)


def draw_panel(screen, rect, fill, border=COLOR_PANEL_BORDER, radius=28, shadow_offset=7):
    """Draw a rounded panel with a soft shadow."""
    shadow_rect = rect.move(0, shadow_offset)
    pygame.draw.rect(screen, COLOR_PANEL_SHADOW, shadow_rect, border_radius=radius)
    pygame.draw.rect(screen, fill, rect, border_radius=radius)
    pygame.draw.rect(screen, border, rect, width=2, border_radius=radius)


def draw_text_with_shadow(screen, text, font, color, center, shadow_color=(255, 255, 255)):
    """Draw text with a subtle highlight shadow."""
    label = font.render(text, True, color)
    shadow = font.render(text, True, shadow_color)
    rect = label.get_rect(center=center)
    screen.blit(shadow, rect.move(0, 3))
    screen.blit(label, rect)


def draw_button(
    screen,
    rect,
    text,
    hovered=False,
    fill=COLOR_BUTTON,
    hover_fill=COLOR_BUTTON_HOVER,
    border=COLOR_PANEL_BORDER,
):
    """Draw a pill-shaped button."""
    active_fill = hover_fill if hovered else fill
    lift = -3 if hovered else 0
    button_rect = rect.move(0, lift)
    draw_panel(screen, button_rect, active_fill, border=border, radius=22, shadow_offset=6)
    draw_text_with_shadow(
        screen,
        text,
        BUTTON_FONT,
        COLOR_TEXT,
        button_rect.center,
        shadow_color=(255, 255, 255),
    )


def draw_piece(screen, center, piece, radius=RADIUS):
    """Draw a glossy piece."""
    if piece == PLAYER:
        base_color = COLOR_PLAYER
        glow_color = COLOR_PLAYER_GLOW
    else:
        base_color = COLOR_AI
        glow_color = COLOR_AI_GLOW

    pygame.draw.circle(screen, glow_color, center, radius + 7)
    pygame.draw.circle(screen, base_color, center, radius)
    highlight_center = (center[0] - radius // 3, center[1] - radius // 3)
    pygame.draw.circle(screen, (255, 255, 255), highlight_center, max(6, radius // 4))


def draw_header(screen, status_text, is_player_turn, hovered_home=False, banner=None):
    """Draw the title and status strip above the board."""
    title_rect = pygame.Rect(24, 26, 290, 84)
    status_rect = pygame.Rect(324, 26, 370, 84)
    home_rect = pygame.Rect(WIDTH - 148, 28, 122, 56)

    draw_panel(screen, title_rect, COLOR_PANEL)
    draw_panel(screen, status_rect, COLOR_PANEL)

    draw_text_with_shadow(
        screen,
        "Connect Dots",
        MEDIUM_FONT,
        COLOR_TEXT,
        (title_rect.centerx, title_rect.centery - 8),
    )
    draw_centered_wrapped_text(
        screen,
        "Drop dots and challenge the clever AI!",
        TINY_FONT,
        COLOR_TEXT_SOFT,
        title_rect.centerx,
        title_rect.centery + 18,
        title_rect.width - 24,
        18,
        max_lines=1,
    )

    if banner:
        status_color = banner["color"]
        pygame.draw.circle(screen, status_color, (status_rect.left + 30, status_rect.top + 28), 12)
        # Truncate title if too long
        title_text = truncate_text(banner["title"], SMALL_FONT, status_rect.width - 68)
        title_label = SMALL_FONT.render(title_text, True, status_color)
        screen.blit(title_label, (status_rect.left + 52, status_rect.top + 14))

        wrapped_lines = clamp_wrapped_lines(banner["subtext"], TINY_FONT, status_rect.width - 42, 2)
        draw_wrapped_lines(screen, wrapped_lines, TINY_FONT, COLOR_TEXT_SOFT, status_rect.left + 20, status_rect.top + 38, 18)
    else:
        status_color = COLOR_PLAYER if is_player_turn else COLOR_AI
        pygame.draw.circle(screen, status_color, (status_rect.left + 34, status_rect.centery), 16)
        wrapped_lines = clamp_wrapped_lines(status_text, TINY_FONT, status_rect.width - 84, 2)
        draw_wrapped_lines(screen, wrapped_lines, TINY_FONT, COLOR_TEXT, status_rect.left + 62, status_rect.top + 22, 20)

    draw_button(
        screen,
        home_rect,
        "Menu",
        hovered=hovered_home,
        fill=COLOR_BUTTON_ALT,
        hover_fill=COLOR_BUTTON_ALT_HOVER,
        border=COLOR_ACCENT,
    )


def draw_footer(screen, text_left, text_right, show_actions=False, hovered_restart=False, hovered_menu=False):
    """Draw footer hints under the board."""
    draw_panel(screen, FOOTER_RECT, COLOR_PANEL)
    content_width = 350 if show_actions else FOOTER_RECT.width - 48
    left_lines = clamp_wrapped_lines(text_left, TINY_FONT, content_width, 2)
    right_lines = clamp_wrapped_lines(text_right, TINY_FONT, content_width, 2)
    draw_wrapped_lines(screen, left_lines, TINY_FONT, COLOR_TEXT, FOOTER_RECT.left + 24, FOOTER_RECT.top + 18, 18)
    draw_wrapped_lines(screen, right_lines, TINY_FONT, COLOR_TEXT_SOFT, FOOTER_RECT.left + 24, FOOTER_RECT.top + 50, 16)

    if show_actions:
        restart_rect = pygame.Rect(FOOTER_RECT.right - 320, FOOTER_RECT.top + 20, 140, 52)
        menu_rect = pygame.Rect(FOOTER_RECT.right - 168, FOOTER_RECT.top + 20, 140, 52)
        draw_button(screen, restart_rect, "Play Again", hovered=hovered_restart)
        draw_button(
            screen,
            menu_rect,
            "Main Menu",
            hovered=hovered_menu,
            fill=COLOR_BUTTON_ALT,
            hover_fill=COLOR_BUTTON_ALT_HOVER,
            border=COLOR_ACCENT,
        )


def draw_board_frame(screen):
    """Draw the board container and empty slots."""
    board_shadow = BOARD_RECT.inflate(32, 32)
    draw_panel(screen, board_shadow, COLOR_PANEL, border=COLOR_PANEL_BORDER, radius=34, shadow_offset=10)

    inner_board = BOARD_RECT.inflate(16, 16)
    pygame.draw.rect(screen, COLOR_BOARD, inner_board, border_radius=32)
    pygame.draw.rect(screen, COLOR_BOARD_BORDER, inner_board, width=4, border_radius=32)

    for col in range(COLS):
        for row in range(ROWS):
            center_x = BOARD_RECT.left + col * SQUARE_SIZE + SQUARE_SIZE // 2
            center_y = BOARD_RECT.top + row * SQUARE_SIZE + SQUARE_SIZE // 2
            pygame.draw.circle(screen, COLOR_SLOT_SHADOW, (center_x, center_y + 4), RADIUS + 7)
            pygame.draw.circle(screen, COLOR_SLOT, (center_x, center_y), RADIUS + 4)


def draw_hover_piece(screen, hover_col):
    """Draw a hovering preview piece above the chosen column."""
    if hover_col < 0 or hover_col >= COLS:
        return
    center_x = BOARD_RECT.left + hover_col * SQUARE_SIZE + SQUARE_SIZE // 2
    center_y = BOARD_RECT.top - 24
    draw_piece(screen, (center_x, center_y), PLAYER, radius=max(20, RADIUS - 6))


def draw_board_state(screen, board):
    """Draw all placed pieces using board coordinates."""
    for col in range(COLS):
        for row in range(ROWS):
            if board[row][col] == EMPTY:
                continue
            visual_row = ROWS - 1 - row
            center_x = BOARD_RECT.left + col * SQUARE_SIZE + SQUARE_SIZE // 2
            center_y = BOARD_RECT.top + visual_row * SQUARE_SIZE + SQUARE_SIZE // 2
            draw_piece(screen, (center_x, center_y), board[row][col])


def draw_winning_highlights(screen, winning_cells):
    """Highlight the exact winning four cells."""
    for row, col in winning_cells:
        visual_row = ROWS - 1 - row
        center_x = BOARD_RECT.left + col * SQUARE_SIZE + SQUARE_SIZE // 2
        center_y = BOARD_RECT.top + visual_row * SQUARE_SIZE + SQUARE_SIZE // 2
        pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), RADIUS + 12, width=5)
        pygame.draw.circle(screen, COLOR_ACCENT, (center_x, center_y), RADIUS + 18, width=4)


def render_game_scene(
    screen,
    board,
    status_text,
    is_player_turn=True,
    hover_col=-1,
    floating_piece=None,
    overlay=None,
    winning_cells=None,
    hovered_home=False,
    hovered_restart=False,
    hovered_menu=False,
):
    """Render the entire game scene."""
    ensure_pygame()
    draw_gradient_background(screen)
    draw_cloud(screen, 74, 88, 1.1)
    draw_cloud(screen, 710, 102, 0.9)
    draw_header(screen, status_text, is_player_turn, hovered_home=hovered_home, banner=overlay)
    draw_board_frame(screen)
    draw_board_state(screen, board)
    if winning_cells:
        draw_winning_highlights(screen, winning_cells)

    if hover_col >= 0 and overlay is None:
        draw_hover_piece(screen, hover_col)

    if floating_piece is not None:
        draw_piece(screen, floating_piece["center"], floating_piece["piece"])

    if overlay:
        footer_left = "Winning four is highlighted on the board."
        footer_right = "Press R or Enter to replay. Esc or M for menu. F11 toggles fullscreen."
    else:
        footer_left = "Click a column to drop your dot." if is_player_turn else "Watch the AI plan its next move."
        footer_right = "Use Menu anytime. Press F11 to toggle fullscreen."
    draw_footer(
        screen,
        footer_left,
        footer_right,
        show_actions=overlay is not None,
        hovered_restart=hovered_restart,
        hovered_menu=hovered_menu,
    )
    draw_copyright(screen, HEIGHT - 18)

class LandingPage:
    """Landing page with playful presentation and button hover feedback."""

    def __init__(self):
        ensure_pygame()
        pygame.display.set_caption("Connect Dots")
        self.windowed_size = (WIDTH, HEIGHT)
        self.is_fullscreen = True
        self.screen = create_window(get_desktop_size(), fullscreen=True)
        self.canvas = pygame.Surface((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.play_button = pygame.Rect(WIDTH // 2 - 170, HEIGHT // 2 + 22, 340, 70)
        self.guide_button = pygame.Rect(WIDTH // 2 - 170, HEIGHT // 2 + 112, 340, 70)
        self.hover_target = None

    def handle_events(self):
        """Return the selected landing-page action."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.VIDEORESIZE:
                self.screen, self.is_fullscreen, self.windowed_size = handle_resize_event(
                    (event.w, event.h),
                    self.windowed_size,
                )

            if event.type == pygame.MOUSEMOTION:
                mouse_pos = to_virtual_pos(event.pos, self.screen.get_size())
                self.hover_target = None
                if self.play_button.collidepoint(mouse_pos):
                    self.hover_target = "play"
                elif self.guide_button.collidepoint(mouse_pos):
                    self.hover_target = "guide"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = to_virtual_pos(event.pos, self.screen.get_size())
                if self.play_button.collidepoint(mouse_pos):
                    return "play"
                if self.guide_button.collidepoint(mouse_pos):
                    return "guide"

            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                self.screen, self.is_fullscreen, self.windowed_size = toggle_fullscreen(
                    self.screen,
                    self.is_fullscreen,
                    self.windowed_size,
                )

        return None

    def draw(self):
        """Draw the landing page."""
        draw_gradient_background(self.canvas)
        draw_cloud(self.canvas, 92, 120, 1.3)
        draw_cloud(self.canvas, 642, 148, 1.0)

        hero_rect = pygame.Rect(95, 120, WIDTH - 190, 460)
        draw_panel(self.canvas, hero_rect, COLOR_PANEL, radius=34, shadow_offset=10)

        draw_text_with_shadow(
            self.canvas,
            "Connect Dots",
            TITLE_FONT,
            COLOR_TEXT,
            (hero_rect.centerx, hero_rect.top + 95),
        )
        draw_centered_wrapped_text(
            self.canvas,
            "A bright, bubbly battle of four-in-a-row!",
            SUBTITLE_FONT,
            COLOR_ACCENT,
            hero_rect.centerx,
            hero_rect.top + 155,
            hero_rect.width - 80,
            30,
            max_lines=2,
        )

        draw_centered_wrapped_text(
            self.canvas,
            "Take turns dropping candy-colored dots. Beat the clever AI or jump into the guide first.",
            SMALL_FONT,
            COLOR_TEXT_SOFT,
            hero_rect.centerx,
            hero_rect.top + 235,
            hero_rect.width - 140,
            28,
            max_lines=3,
        )

        draw_button(self.canvas, self.play_button, "Play Game", hovered=self.hover_target == "play")
        draw_button(
            self.canvas,
            self.guide_button,
            "How To Play",
            hovered=self.hover_target == "guide",
            fill=COLOR_BUTTON_ALT,
            hover_fill=COLOR_BUTTON_ALT_HOVER,
            border=COLOR_ACCENT,
        )

        draw_centered_wrapped_text(
            self.canvas,
            "Playful visuals. Smart AI. Friendly challenge.",
            TINY_FONT,
            COLOR_TEXT_SOFT,
            WIDTH // 2,
            HEIGHT - 118,
            460,
            18,
            max_lines=1,
        )
        draw_brand_signature(self.canvas, HEIGHT - 92)
        draw_copyright(self.canvas, HEIGHT - 38)

        present_canvas(self.screen, self.canvas)
        self.clock.tick(60)

    def run(self):
        """Run the landing-page loop."""
        while True:
            result = self.handle_events()
            if result is not None:
                return result
            self.draw()

    def cleanup(self):
        """Release pygame resources for this screen."""
        return


class GuidePage:
    """Guide page with colorful cards and clear rules."""

    def __init__(self):
        ensure_pygame()
        pygame.display.set_caption("Connect Dots - Guide")
        self.windowed_size = (WIDTH, HEIGHT)
        self.is_fullscreen = True
        self.screen = create_window(get_desktop_size(), fullscreen=True)
        self.canvas = pygame.Surface((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.back_button = pygame.Rect(48, HEIGHT - 98, 140, 58)
        self.hover_back = False

    def handle_events(self):
        """Handle guide page interactions."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.VIDEORESIZE:
                self.screen, self.is_fullscreen, self.windowed_size = handle_resize_event(
                    (event.w, event.h),
                    self.windowed_size,
                )

            if event.type == pygame.MOUSEMOTION:
                mouse_pos = to_virtual_pos(event.pos, self.screen.get_size())
                self.hover_back = self.back_button.collidepoint(mouse_pos)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = to_virtual_pos(event.pos, self.screen.get_size())
                if self.back_button.collidepoint(mouse_pos):
                    return "back"

            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                self.screen, self.is_fullscreen, self.windowed_size = toggle_fullscreen(
                    self.screen,
                    self.is_fullscreen,
                    self.windowed_size,
                )

        return None

    def draw_rule_card(self, rect, title, lines, accent):
        """Draw a single rule card."""
        draw_panel(self.canvas, rect, COLOR_PANEL, border=accent, radius=26, shadow_offset=8)
        draw_text_with_shadow(self.canvas, truncate_text(title, MEDIUM_FONT, rect.width - 44), MEDIUM_FONT, accent, (rect.centerx, rect.top + 32))
        y = rect.top + 68
        max_width = rect.width - 48
        for line in lines:
            for wrapped_line in clamp_wrapped_lines(line, TINY_FONT, max_width, 2):
                label = TINY_FONT.render(wrapped_line, True, COLOR_TEXT)
                self.canvas.blit(label, (rect.left + 24, y))
                y += 24
            y += 6

    def draw(self):
        """Draw the guide page."""
        draw_gradient_background(self.canvas)
        draw_cloud(self.canvas, 64, 92, 1.0)
        draw_cloud(self.canvas, 730, 110, 0.85)

        heading_rect = pygame.Rect(92, 54, WIDTH - 184, 94)
        draw_panel(self.canvas, heading_rect, COLOR_PANEL)
        draw_text_with_shadow(
            self.canvas,
            "How To Play",
            LARGE_FONT,
            COLOR_TEXT,
            (heading_rect.centerx, heading_rect.centery - 10),
        )
        draw_centered_wrapped_text(
            self.canvas,
            "Simple rules, bright dots, and a clever little AI.",
            TINY_FONT,
            COLOR_TEXT_SOFT,
            heading_rect.centerx,
            heading_rect.centery + 18,
            heading_rect.width - 40,
            18,
            max_lines=2,
        )

        cards = [
            (
                pygame.Rect(120, 180, 340, 180),
                "Goal",
                [
                    "Line up four matching dots. You can win across, up, or diagonally. Look for sneaky setups in two directions.",
                ],
                COLOR_PLAYER,
            ),
            (
                pygame.Rect(480, 180, 340, 180),
                "Your Turn",
                [
                    "Click any open column on the board. Your pink dot drops to the lowest space. Pick spots that create two threats at once.",
                ],
                COLOR_ACCENT,
            ),
            (
                pygame.Rect(80, 390, 740, 120),
                "AI Turn",
                [
                    "The yellow AI studies the board next. It tries to win and block your plans. Stay alert after every move it makes.",
                ],
                COLOR_AI,
            ),
        ]
        for rect, title, lines, accent in cards:
            self.draw_rule_card(rect, title, lines, accent)

        tips_rect = pygame.Rect(80, 520, 740, 200)
        draw_panel(self.canvas, tips_rect, COLOR_PANEL, border=COLOR_ACCENT, radius=28, shadow_offset=8)
        draw_text_with_shadow(self.canvas, "Winning Tips", MEDIUM_FONT, COLOR_TEXT, (tips_rect.centerx, tips_rect.top + 34))
        tips = [
            "Start near the center to build more possible lines. Watch the top preview dot so you always know where a move will drop. Diagonal connections count too, and a winning four will glow on the board. After a round, use Play Again or Main Menu from the end card.",
        ]
        bullet_y = tips_rect.top + 68
        for tip in tips:
            pygame.draw.circle(self.canvas, COLOR_ACCENT, (tips_rect.left + 32, bullet_y + 10), 7)
            wrapped_lines = clamp_wrapped_lines(tip, TINY_FONT, tips_rect.width - 88, 2)
            for line_index, wrapped_line in enumerate(wrapped_lines):
                label = TINY_FONT.render(wrapped_line, True, COLOR_TEXT) # type: ignore
                self.canvas.blit(label, (tips_rect.left + 54, bullet_y + line_index * 21))
            bullet_y += max(30, len(wrapped_lines) * 21 + 6)

        draw_centered_wrapped_text(
            self.canvas,
            "Four connected dots always decide the winner.",
            TINY_FONT,
            COLOR_TEXT_SOFT,
            tips_rect.centerx,
            tips_rect.bottom - 28,
            tips_rect.width - 40,
            18,
            max_lines=1,
        )

        draw_button(self.canvas, self.back_button, "Back", hovered=self.hover_back)
        draw_copyright(self.canvas, HEIGHT - 18)
        present_canvas(self.screen, self.canvas)
        self.clock.tick(60)

    def run(self):
        """Run the guide loop."""
        while True:
            result = self.handle_events()
            if result == "back":
                return
            self.draw()

    def cleanup(self):
        """Release pygame resources for this screen."""
        return


class ConnectFourUI:
    """Main gameplay UI with hover previews and endgame action cards."""

    def __init__(self):
        ensure_pygame()
        pygame.display.set_caption("Connect Dots")
        self.windowed_size = (WIDTH, HEIGHT)
        self.is_fullscreen = True
        self.screen = create_window(get_desktop_size(), fullscreen=True)
        self.canvas = pygame.Surface((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.home_button = pygame.Rect(WIDTH - 154, 28, 122, 56)
        self.restart_button = pygame.Rect(FOOTER_RECT.right - 330, FOOTER_RECT.top + 20, 150, 52)
        self.menu_button = pygame.Rect(FOOTER_RECT.right - 168, FOOTER_RECT.top + 20, 150, 52)
        self.hover_col = -1
        self.hover_target = None
        self.current_overlay = None
        self.current_status = "Your turn!"
        self.current_is_player_turn = True

    def _column_from_pos(self, pos):
        """Translate a mouse position into a board column."""
        if not BOARD_RECT.collidepoint(pos):
            return -1
        relative_x = pos[0] - BOARD_RECT.left
        col = relative_x // SQUARE_SIZE
        return col if 0 <= col < COLS else -1

    def handle_events(self, board, game_over, ai_thinking):
        """Handle gameplay events and return a selected column plus optional action."""
        col_to_play = None
        action = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.VIDEORESIZE:
                self.screen, self.is_fullscreen, self.windowed_size = handle_resize_event(
                    (event.w, event.h),
                    self.windowed_size,
                )

            if event.type == pygame.MOUSEMOTION:
                mouse_pos = to_virtual_pos(event.pos, self.screen.get_size())
                self.hover_target = None
                if self.home_button.collidepoint(mouse_pos):
                    self.hover_target = "home"
                elif game_over and self.restart_button.collidepoint(mouse_pos):
                    self.hover_target = "restart"
                elif game_over and self.menu_button.collidepoint(mouse_pos):
                    self.hover_target = "menu"

                if not game_over and not ai_thinking:
                    col = self._column_from_pos(mouse_pos)
                    self.hover_col = col if col >= 0 and is_valid_location(board, col) else -1
                else:
                    self.hover_col = -1

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = to_virtual_pos(event.pos, self.screen.get_size())
                if self.home_button.collidepoint(mouse_pos):
                    action = "menu"
                    continue

                if game_over:
                    if self.restart_button.collidepoint(mouse_pos):
                        action = "restart"
                    elif self.menu_button.collidepoint(mouse_pos):
                        action = "menu"
                    continue

                if not ai_thinking:
                    col = self._column_from_pos(mouse_pos)
                    if col >= 0 and is_valid_location(board, col):
                        col_to_play = col

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    self.screen, self.is_fullscreen, self.windowed_size = toggle_fullscreen(
                        self.screen,
                        self.is_fullscreen,
                        self.windowed_size,
                    )
                elif event.key in (pygame.K_ESCAPE, pygame.K_m):
                    action = "menu"
                elif game_over and event.key in (pygame.K_r, pygame.K_RETURN):
                    action = "restart"

        return col_to_play, action

    def draw_state(self, board, status_text, is_player_turn=True, overlay=None, winning_cells=None):
        """Draw and remember the current gameplay scene."""
        self.current_status = status_text
        self.current_is_player_turn = is_player_turn
        self.current_overlay = overlay

        render_game_scene(
            self.canvas,
            board,
            status_text,
            is_player_turn=is_player_turn,
            hover_col=self.hover_col,
            overlay=overlay,
            winning_cells=winning_cells,
            hovered_home=self.hover_target == "home",
            hovered_restart=self.hover_target == "restart",
            hovered_menu=self.hover_target == "menu",
        )
        present_canvas(self.screen, self.canvas)

    def animate_drop(self, board, col, piece, status_text, is_player_turn):
        """Animate a piece dropping down the board."""
        row = get_next_open_row(board, col)
        if row is None:
            return None

        center_x = BOARD_RECT.left + col * SQUARE_SIZE + SQUARE_SIZE // 2
        start_y = BOARD_RECT.top - 26
        final_visual_row = ROWS - 1 - row
        final_y = BOARD_RECT.top + final_visual_row * SQUARE_SIZE + SQUARE_SIZE // 2

        frames = 18
        for frame in range(frames):
            progress = (frame + 1) / frames
            eased = 1 - math.pow(1 - progress, 3)
            current_y = int(start_y + (final_y - start_y) * eased)
            floating_piece = {"center": (center_x, current_y), "piece": piece}
            render_game_scene(
                self.canvas,
                board,
                status_text,
                is_player_turn=is_player_turn,
                hover_col=-1,
                floating_piece=floating_piece,
                hovered_home=self.hover_target == "home",
            )
            present_canvas(self.screen, self.canvas)
            pygame.event.pump()
            self.clock.tick(60)

        return row

    def cleanup(self):
        """Release pygame resources for this screen."""
        return


def draw_board(board, screen):
    """Backward-compatible board renderer."""
    render_game_scene(screen, board, "Your turn!", is_player_turn=True)


def show_message(screen, text, subtext="", color=COLOR_SUCCESS):
    """Backward-compatible overlay renderer."""
    render_game_scene(
        screen,
        [[EMPTY for _ in range(COLS)] for _ in range(ROWS)],
        "Round finished",
        is_player_turn=True,
        overlay={"title": text, "subtext": subtext, "color": color},
    )


def draw_turn_indicator(screen, text, is_player_turn=True):
    """Backward-compatible status renderer."""
    render_game_scene(
        screen,
        [[EMPTY for _ in range(COLS)] for _ in range(ROWS)],
        text,
        is_player_turn=is_player_turn,
    )
