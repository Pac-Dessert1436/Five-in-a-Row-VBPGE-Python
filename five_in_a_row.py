import pygame
from random import randint, uniform
from enum import IntEnum, unique

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Five-in-a-Row")

# Colors
BACKGROUND = (15, 56, 15)
GRID_COLOR = (100, 100, 100)
BLACK = (20, 20, 20)
WHITE = (245, 245, 245)
HIGHLIGHT = (255, 215, 0)
TEXT_COLOR = (240, 240, 240)
SHADOW = (10, 40, 10)
HIGHLIGHT_GREEN = (50, 205, 50)

# Game constants
GRID_SIZE = 15
WIN_COUNT = 5
BOARD_PADDING = 40
CELL_SIZE = min((SCREEN_WIDTH - 2 * BOARD_PADDING) // GRID_SIZE,
                (SCREEN_HEIGHT - 2 * BOARD_PADDING - 80) // GRID_SIZE)
BOARD_START_X = (SCREEN_WIDTH - GRID_SIZE * CELL_SIZE) // 2
BOARD_START_Y = (SCREEN_HEIGHT - GRID_SIZE * CELL_SIZE) // 2 - 20


@unique
class Piece(IntEnum):
    EMPTY = 0
    BLACK = 1
    WHITE = 2


# Create game board
board = [[Piece.EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
current_player = Piece.BLACK
game_over = False
winner = Piece.EMPTY
hover_pos = (-1, -1)
particles = []
black_has_violation = False


class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = randint(2, 5)
        self.speed_x = uniform(-2, 2)
        self.speed_y = uniform(-2, 2)
        self.lifespan = randint(20, 40)

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.lifespan -= 1
        self.size = max(0, self.size - 0.1)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color,
                           (int(self.x), int(self.y)), int(self.size))


# Font setup
try:
    title_font = pygame.font.Font(None, 48)
    status_font = pygame.font.Font(None, 36)
    message_font = pygame.font.Font(None, 60)
    small_font = pygame.font.Font(None, 28)
except:
    # Fallback if font loading fails
    title_font = pygame.font.SysFont(None, 48)
    status_font = pygame.font.SysFont(None, 36)
    message_font = pygame.font.SysFont(None, 60)
    small_font = pygame.font.SysFont(None, 28)


def reset_game():
    """Function to reset the game."""
    global board, current_player, game_over, winner, particles, black_has_violation
    board = [[Piece.EMPTY for _ in range(
        GRID_SIZE)] for _ in range(GRID_SIZE)]
    current_player = Piece.BLACK
    game_over = False
    winner = Piece.EMPTY
    particles = []
    black_has_violation = False


def draw_board():
    """Function to draw the game board."""

    # Draw grid lines
    for i in range(GRID_SIZE):
        x = BOARD_START_X + i * CELL_SIZE + CELL_SIZE // 2
        y = BOARD_START_Y + i * CELL_SIZE + CELL_SIZE // 2

        # Draw horizontal lines
        x1 = BOARD_START_X + CELL_SIZE // 2
        x2 = BOARD_START_X + GRID_SIZE * CELL_SIZE - CELL_SIZE // 2
        pygame.draw.line(screen, GRID_COLOR, (x1, y), (x2, y), 2)

        # Draw vertical lines
        y1 = BOARD_START_Y + CELL_SIZE // 2
        y2 = BOARD_START_Y + GRID_SIZE * CELL_SIZE - CELL_SIZE // 2
        pygame.draw.line(screen, GRID_COLOR, (x, y1), (x, y2), 2)

    # Draw star points (traditional Gomoku markers)
    star_points = [(3, 3), (3, 11), (7, 7), (11, 3), (11, 11)]
    for point in star_points:
        x = BOARD_START_X + point[0] * CELL_SIZE + CELL_SIZE // 2
        y = BOARD_START_Y + point[1] * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(screen, GRID_COLOR, (x, y), 4)

    # Draw pieces
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            pos_x = BOARD_START_X + x * CELL_SIZE + CELL_SIZE // 2
            pos_y = BOARD_START_Y + y * CELL_SIZE + CELL_SIZE // 2

            if board[x][y] == Piece.BLACK:
                # Draw black piece with highlight
                pygame.draw.circle(
                    screen, BLACK, (pos_x, pos_y), CELL_SIZE // 2 - 2)
                pygame.draw.circle(screen, (60, 60, 60),
                                   (pos_x, pos_y), CELL_SIZE // 2 - 2, 2)
                pygame.draw.circle(screen, (80, 80, 80),
                                   (pos_x - 4, pos_y - 4), 4)
            elif board[x][y] == Piece.WHITE:
                # Draw white piece with shadow
                pygame.draw.circle(
                    screen, WHITE, (pos_x, pos_y), CELL_SIZE // 2 - 2)
                pygame.draw.circle(screen, (180, 180, 180),
                                   (pos_x, pos_y), CELL_SIZE // 2 - 2, 2)
                pygame.draw.circle(screen, (200, 200, 200),
                                   (pos_x + 3, pos_y + 3), 3)

    # Draw hover indicator
    if not game_over and 0 <= hover_pos[0] < GRID_SIZE and 0 <= hover_pos[1] < GRID_SIZE:
        if board[hover_pos[0]][hover_pos[1]] == Piece.EMPTY:
            pos_x = BOARD_START_X + hover_pos[0] * CELL_SIZE + CELL_SIZE // 2
            pos_y = BOARD_START_Y + hover_pos[1] * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.circle(screen, HIGHLIGHT,
                               (pos_x, pos_y), CELL_SIZE // 4, 2)


def handle_player_turn(mouse_pos):
    """Function to handle player moves."""
    global current_player, game_over, winner, black_has_violation

    # Convert mouse position to grid coordinates
    grid_x = (mouse_pos[0] - BOARD_START_X) // CELL_SIZE
    grid_y = (mouse_pos[1] - BOARD_START_Y) // CELL_SIZE

    # Validate move
    if (0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE and
            board[grid_x][grid_y] == Piece.EMPTY):

        # Check professional rules for black pieces
        if current_player == Piece.BLACK:
            # Temporarily place the piece to check for violations
            board[grid_x][grid_y] = current_player
            has_violation = check_black_violations(grid_x, grid_y)
            board[grid_x][grid_y] = Piece.EMPTY

            if has_violation:
                # Skip black's turn due to violation
                black_has_violation = True
                current_player = Piece.WHITE
                return
            black_has_violation = False

        # Place piece
        board[grid_x][grid_y] = current_player

        # Create particles for visual effect
        pos_x = BOARD_START_X + grid_x * CELL_SIZE + CELL_SIZE // 2
        pos_y = BOARD_START_Y + grid_y * CELL_SIZE + CELL_SIZE // 2
        color = (100, 100, 100) if current_player == Piece.BLACK else (
            200, 200, 200)
        for _ in range(20):
            particles.append(Particle(pos_x, pos_y, color))

        # Check win condition
        if check_win(grid_x, grid_y):
            game_over = True
            winner = current_player
            # Create win particles
            for _ in range(100):
                win_color = (50, 50, 50) if winner == Piece.BLACK else (
                    220, 220, 220)
                particles.append(Particle(pos_x, pos_y, win_color))

        # Switch player and reset violation state in time
        if current_player == Piece.BLACK:
            current_player = Piece.WHITE
        else:
            black_has_violation = False
            current_player = Piece.BLACK


def check_black_violations(x, y):
    """Check for black piece violations (professional rules)."""
    return check_overline(x, y) or check_double_three(x, y) or check_double_four(x, y)


def check_overline(x, y):
    """Check for overline (more than 5 in a row)."""
    directions = [
        (1, 0),   # Horizontal
        (0, 1),   # Vertical
        (1, 1),   # Diagonal /
        (1, -1)   # Diagonal \
    ]
    player = board[x][y]

    for dx, dy in directions:
        count = 1  # Current piece

        # Check positive direction
        for i in range(1, 6):  # Check up to 5 pieces beyond win condition
            nx, ny = x + dx * i, y + dy * i
            if not (0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE):
                break
            if board[nx][ny] != player:
                break
            count += 1

        # Check negative direction
        for i in range(1, 6):  # Check up to 5 pieces beyond win condition
            nx, ny = x - dx * i, y - dy * i
            if not (0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE):
                break
            if board[nx][ny] != player:
                break
            count += 1

        if count > 5:
            return True

    return False


def check_double_three(x, y):
    """Check for double three violation."""
    directions = [
        (1, 0),   # Horizontal
        (0, 1),   # Vertical
        (1, 1),   # Diagonal /
        (1, -1)   # Diagonal \
    ]
    player = board[x][y]
    three_count = 0

    for dx, dy in directions:
        # Check for open three in this direction
        if is_open_three(x, y, dx, dy, player):
            three_count += 1
            if three_count >= 2:
                return True

    return False


def check_double_four(x, y):
    """Check for double four violation."""
    directions = [
        (1, 0),   # Horizontal
        (0, 1),   # Vertical
        (1, 1),   # Diagonal /
        (1, -1)   # Diagonal \
    ]
    player = board[x][y]
    four_count = 0

    for dx, dy in directions:
        # Check for open four in this direction
        if is_open_four(x, y, dx, dy, player):
            four_count += 1
            if four_count >= 2:
                return True

    return False


def is_open_three(x, y, dx, dy, player):
    """Check if the current position forms an open three in the given direction."""
    count = 1
    open_ends = 0

    # Check positive direction
    for i in range(1, 4):
        nx, ny = x + dx * i, y + dy * i
        if not (0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE):
            break
        if board[nx][ny] == player:
            count += 1
        elif board[nx][ny] == Piece.EMPTY:
            open_ends += 1
            break
        else:
            break

    # Check negative direction
    for i in range(1, 4):
        nx, ny = x - dx * i, y - dy * i
        if not (0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE):
            break
        if board[nx][ny] == player:
            count += 1
        elif board[nx][ny] == Piece.EMPTY:
            open_ends += 1
            break
        else:
            break

    # Open three has exactly 3 pieces and 2 open ends
    return count == 3 and open_ends == 2


def is_open_four(x, y, dx, dy, player):
    """Check if the current position forms an open four in the given direction."""
    count = 1
    open_ends = 0

    # Check positive direction
    for i in range(1, 5):
        nx, ny = x + dx * i, y + dy * i
        if not (0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE):
            break
        if board[nx][ny] == player:
            count += 1
        elif board[nx][ny] == Piece.EMPTY:
            open_ends += 1
            break
        else:
            break

    # Check negative direction
    for i in range(1, 5):
        nx, ny = x - dx * i, y - dy * i
        if not (0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE):
            break
        if board[nx][ny] == player:
            count += 1
        elif board[nx][ny] == Piece.EMPTY:
            open_ends += 1
            break
        else:
            break

    # Open four has exactly 4 pieces and 2 open ends
    return count == 4 and open_ends == 2


def check_win(x, y):
    """Function to check for a win."""
    player = board[x][y]
    directions = [
        (1, 0),   # Horizontal
        (0, 1),   # Vertical
        (1, 1),   # Diagonal /
        (1, -1)   # Diagonal \
    ]

    for dx, dy in directions:
        count = 1  # Current piece

        # Check positive direction
        for i in range(1, WIN_COUNT):
            nx, ny = x + dx * i, y + dy * i
            if not (0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE) or board[nx][ny] != player:
                break
            count += 1

        # Check negative direction
        for i in range(1, WIN_COUNT):
            nx, ny = x - dx * i, y - dy * i
            if not (0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE) or board[nx][ny] != player:
                break
            count += 1

        if count >= WIN_COUNT:
            return True

    return False


def draw_ui():
    """Function to draw UI elements."""
    # Draw title
    title_shadow = title_font.render("FIVE-IN-A-ROW", True, SHADOW)
    title_text = title_font.render("FIVE-IN-A-ROW", True, HIGHLIGHT_GREEN)
    screen.blit(title_shadow, (SCREEN_WIDTH//2 -
                title_shadow.get_width()//2 + 2, 22))
    screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 20))

    color = (10, 10, 10) if current_player == Piece.BLACK else (220, 220, 220)

    # Display violation message if black has a violation
    if black_has_violation:
        violation_text = small_font.render(
            "BLACK VIOLATION! WHITE'S TURN", True, (255, 0, 0))
        screen.blit(violation_text, (10, 70))

    # Draw game status
    if not game_over:
        status_text = "BLACK'S TURN" if current_player == Piece.BLACK else "WHITE'S TURN"

        # Draw status background
        pygame.draw.rect(screen, (30, 80, 30),
                         (SCREEN_WIDTH//2 - 120, BOARD_START_Y +
                          GRID_SIZE * CELL_SIZE + 15, 240, 40),
                         border_radius=10)
        pygame.draw.rect(screen, (40, 100, 40),
                         (SCREEN_WIDTH//2 - 120, BOARD_START_Y +
                          GRID_SIZE * CELL_SIZE + 15, 240, 40),
                         3, border_radius=10)

        # Draw status text
        text = status_font.render(status_text, True, color)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2,
                           BOARD_START_Y + GRID_SIZE * CELL_SIZE + 25))
    else:
        # Draw winner message
        win_text = "BLACK WINS!" if winner == Piece.BLACK else "WHITE WINS!"

        # Draw message background
        pygame.draw.rect(screen, (30, 80, 30),
                         (SCREEN_WIDTH//2 - 150, BOARD_START_Y +
                          GRID_SIZE * CELL_SIZE + 15, 300, 40),
                         border_radius=10)
        pygame.draw.rect(screen, (40, 100, 40),
                         (SCREEN_WIDTH//2 - 150, BOARD_START_Y +
                          GRID_SIZE * CELL_SIZE + 15, 300, 40),
                         3, border_radius=10)

        # Draw winner text
        text = message_font.render(win_text, True, color)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2,
                           BOARD_START_Y + GRID_SIZE * CELL_SIZE + 15))

        # Draw restart prompt
        restart_shadow = small_font.render("Press R to restart", True, SHADOW)
        restart_text = small_font.render("Press R to restart", True, HIGHLIGHT)
        screen.blit(restart_shadow, (SCREEN_WIDTH//2 - restart_shadow.get_width()//2 + 2,
                                     BOARD_START_Y + GRID_SIZE * CELL_SIZE + 72))
        screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2,
                                   BOARD_START_Y + GRID_SIZE * CELL_SIZE + 70))

    # Draw instructions
    instr = "Click on the board to place your piece"
    if not game_over:
        instr_text = small_font.render(instr, True, (180, 180, 180))
        screen.blit(instr_text, (SCREEN_WIDTH//2 - instr_text.get_width()//2,
                                 BOARD_START_Y + GRID_SIZE * CELL_SIZE + 70))

    # Draw player indicators
    pygame.draw.circle(screen, (40, 100, 40), (50, 40), 20)
    pygame.draw.circle(screen, (40, 100, 40), (SCREEN_WIDTH - 50, 40), 20)

    pygame.draw.circle(screen, BLACK, (50, 40), 15)
    pygame.draw.circle(screen, WHITE, (SCREEN_WIDTH - 50, 40), 15)

    # Draw current player highlight
    if current_player == Piece.BLACK and not game_over:
        pygame.draw.circle(screen, HIGHLIGHT, (50, 40), 20, 3)
    elif current_player == Piece.WHITE and not game_over:
        pygame.draw.circle(screen, HIGHLIGHT, (SCREEN_WIDTH - 50, 40), 20, 3)


# Main game loop
clock = pygame.time.Clock()
running = True

while running:
    mouse_pos = pygame.mouse.get_pos()

    # Update hover position
    hover_x = (mouse_pos[0] - BOARD_START_X) // CELL_SIZE
    hover_y = (mouse_pos[1] - BOARD_START_Y) // CELL_SIZE
    if (0 <= hover_x < GRID_SIZE and 0 <= hover_y < GRID_SIZE):
        hover_pos = (hover_x, hover_y)
    else:
        hover_pos = (-1, -1)

    # Process events
    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                running = False
            case pygame.MOUSEBUTTONDOWN if event.button == 1 and not game_over:
                handle_player_turn(mouse_pos)
            case pygame.KEYDOWN if event.key == pygame.K_r:
                reset_game()
            case pygame.KEYDOWN if event.key == pygame.K_ESCAPE:
                running = False

    # Update particles
    for particle in particles[:]:
        particle.update()
        if particle.lifespan <= 0:
            particles.remove(particle)

    # Draw everything
    screen.fill(BACKGROUND)

    # Draw board background
    pygame.draw.rect(screen, (25, 80, 25),
                     (BOARD_START_X - 10, BOARD_START_Y - 10,
                     GRID_SIZE * CELL_SIZE + 20, GRID_SIZE * CELL_SIZE + 20),
                     border_radius=8)
    pygame.draw.rect(screen, (40, 100, 40),
                     (BOARD_START_X - 10, BOARD_START_Y - 10,
                     GRID_SIZE * CELL_SIZE + 20, GRID_SIZE * CELL_SIZE + 20),
                     3, border_radius=8)

    # Draw the board
    draw_board()

    # Draw particles
    for particle in particles:
        particle.draw(screen)

    # Draw UI
    draw_ui()

    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
