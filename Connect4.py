import numpy as np
import pygame
import sys
import math
import random

# Game constants
ROWS = 6
COLS = 7

PLAYER_TURN = 0
AI_TURN = 1

PLAYER_PIECE = 1
AI_PIECE = 2

Orange = (255, 165, 0)
White = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

def create_board():
    board = np.zeros((ROWS, COLS))
    return board

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[0][col] == 0

def get_next_open_row(board, col):
    for r in range(ROWS-1, -1, -1):
        if board[r][col] == 0:
            return r

def winning_move(board, piece):
    # Check horizontally
    for c in range(COLS-3):
        for r in range(ROWS):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True
    # Check vertically
    for c in range(COLS):
        for r in range(ROWS-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True
    # Check positive diagonal
    for c in range(COLS-3):
        for r in range(3, ROWS):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True
    # Check negative diagonal
    for c in range(3, COLS):
        for r in range(3, ROWS):
            if board[r][c] == piece and board[r-1][c-1] == piece and board[r-2][c-2] == piece and board[r-3][c-3] == piece:
                return True

def draw_board(board):
    for c in range(COLS):
        for r in range(ROWS):
            pygame.draw.rect(screen, Orange, (c * sq_size, r * sq_size + sq_size, sq_size, sq_size))
            if board[r][c] == 0:
                pygame.draw.circle(screen, White, (int(c * sq_size + sq_size/2), int(r * sq_size + sq_size + sq_size/2)), circle_radius)
            elif board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(screen, RED, (int(c * sq_size + sq_size/2), int(r * sq_size + sq_size + sq_size/2)), circle_radius)
            else:
                pygame.draw.circle(screen, YELLOW, (int(c * sq_size + sq_size/2), int(r * sq_size + sq_size + sq_size/2)), circle_radius)
    pygame.display.update()

def evaluate_window(window, piece):
    opponent_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opponent_piece = AI_PIECE

    score = 0
    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(0) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(0) == 2:
        score += 2

    if window.count(opponent_piece) == 3 and window.count(0) == 1:
        score -= 4

    return score

def score_position(board, piece):
    score = 0
    center_array = [int(i) for i in list(board[:, COLS//2])]
    center_count = center_array.count(piece)
    score += center_count * 6

    for r in range(ROWS):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLS - 3):
            window = row_array[c:c + 4]
            score += evaluate_window(window, piece)

    for c in range(COLS):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROWS - 3):
            window = col_array[r:r + 4]
            score += evaluate_window(window, piece)

    for r in range(3, ROWS):
        for c in range(COLS - 3):
            window = [board[r - i][c + i] for i in range(4)]
            score += evaluate_window(window, piece)

    for r in range(3, ROWS):
        for c in range(3, COLS):
            window = [board[r - i][c - i] for i in range(4)]
            score += evaluate_window(window, piece)

    return score

def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

def alpha_beta(board, depth, alpha, beta, maximizing_player):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)

    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, 10000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -10000000)
            else:
                return (None, 0)
        else:
            return (None, score_position(board, AI_PIECE))

    if maximizing_player:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            if row is None:
                continue

            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = alpha_beta(b_copy, depth - 1, alpha, beta, False)[1]

            if new_score > value:
                value = new_score
                column = col

            alpha = max(alpha, value)
            if alpha >= beta:
                break

        return column, value

    else:
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            if row is None:
                continue

            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = alpha_beta(b_copy, depth - 1, alpha, beta, True)[1]

            if new_score < value:
                value = new_score
                column = col

            beta = min(beta, value)
            if alpha >= beta:
                break

        return column, value

def get_valid_locations(board):
    valid_locations = []
    for col in range(COLS):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

def pick_best_move(board, piece):
    valid_locations = get_valid_locations(board)
    best_score = -10000
    best_col = random.choice(valid_locations)
    for col in valid_locations:
        row = get_next_open_row(board, col)
        temp_board = board.copy()
        drop_piece(temp_board, row, col, piece)
        score = score_position(temp_board, piece)
        if score > best_score:
            best_score = score
            best_col = col

    return best_col

# Initialize pygame
pygame.init()

# Screen size
sq_size = 100
width = COLS * sq_size
height = (ROWS + 1) * sq_size

size = (width, height)
circle_radius = int(sq_size / 2 - 5)

screen = pygame.display.set_mode(size)
draw_board(create_board())
pygame.display.update()

myfont = pygame.font.SysFont("monospace", 75)

board = create_board()
game_over = False
turn = random.randint(PLAYER_TURN, AI_TURN)

# Game loop
while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, White, (0, 0, width, sq_size))
            posx = event.pos[0]
            if turn == PLAYER_TURN:
                pygame.draw.circle(screen, RED, (posx, int(sq_size / 2)), circle_radius)

        pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.draw.rect(screen, White, (0, 0, width, sq_size))
            if turn == PLAYER_TURN:
                posx = event.pos[0]
                col = int(math.floor(posx / sq_size))

                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, PLAYER_PIECE)

                    if winning_move(board, PLAYER_PIECE):
                        label = myfont.render("Player 1 wins!!", 1, RED)
                        screen.blit(label, (40, 10))
                        game_over = True

                    turn += 1
                    turn = turn % 2

                    draw_board(board)

    if turn == AI_TURN and not game_over:
        col = random.choice(get_valid_locations(board))

        if is_valid_location(board, col):
            pygame.time.wait(500)
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, AI_PIECE)

            if winning_move(board, AI_PIECE):
                label = myfont.render("Player 2 wins!!", 1, YELLOW)
                screen.blit(label, (40, 10))
                game_over = True

            turn += 1
            turn = turn % 2

            draw_board(board)

    if game_over:
        pygame.time.wait(3000)
        pygame.quit()
