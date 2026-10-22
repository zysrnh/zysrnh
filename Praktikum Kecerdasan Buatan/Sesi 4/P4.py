# ==============================================================================
# PRAKTIKUM KECERDASAN BUATAN - SESI 4
# LANGKAH 1, 2, & 3: TIC-TAC-TOE DENGAN MINIMAX & ALPHA-BETA PRUNING
# ==============================================================================
import math

# ------------------------------------------------------------------------------
# LANGKAH 1: Inisialisasi Papan & Cek Kemenangan
# ------------------------------------------------------------------------------
def print_board(board):
    for row in [board[i*3:(i+1)*3] for i in range(3)]:
        print('| ' + ' | '.join(row) + ' |')

def check_winner(board):
    win_conditions = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8], # Baris
        [0, 3, 6], [1, 4, 7], [2, 5, 8], # Kolom
        [0, 4, 8], [2, 4, 6]             # Diagonal
    ]
    for cond in win_conditions:
        if board[cond[0]] == board[cond[1]] == board[cond[2]] != ' ':
            return board[cond[0]]
    if ' ' not in board:
        return 'DRAW'
    return None


# ------------------------------------------------------------------------------
# LANGKAH 2: Fungsi Rekursif Minimax Standar
# ------------------------------------------------------------------------------
def minimax(board, is_maximizing):
    winner = check_winner(board)
    if winner == 'X':
        return 10  # Bot (MAX) Menang
    if winner == 'O':
        return -10 # Manusia (MIN) Menang
    if winner == 'DRAW':
        return 0

    if is_maximizing:
        best_score = -math.inf
        for i in range(9):
            if board[i] == ' ':
                board[i] = 'X'
                score = minimax(board, False)
                board[i] = ' '
                best_score = max(score, best_score)
        return best_score
    else:
        best_score = math.inf
        for i in range(9):
            if board[i] == ' ':
                board[i] = 'O'
                score = minimax(board, True)
                board[i] = ' '
                best_score = min(score, best_score)
        return best_score

def find_best_move(board):
    best_score = -math.inf
    best_move = -1
    for i in range(9):
        if board[i] == ' ':
            board[i] = 'X'
            score = minimax(board, False)
            board[i] = ' '
            if score > best_score:
                best_score = score
                best_move = i
    return best_move


# ------------------------------------------------------------------------------
# LANGKAH 3: Minimax dengan Alpha-Beta Pruning (Optimalisasi Pencarian)
# ------------------------------------------------------------------------------
def minimax_alpha_beta(board, depth, alpha, beta, is_maximizing):
    winner = check_winner(board)
    if winner == 'X':
        return 10 - depth  # Penalti kedalaman
    if winner == 'O':
        return depth - 10
    if winner == 'DRAW':
        return 0

    if is_maximizing:
        max_eval = -math.inf
        for i in range(9):
            if board[i] == ' ':
                board[i] = 'X'
                eval_score = minimax_alpha_beta(board, depth + 1, alpha, beta, False)
                board[i] = ' '
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Pemangkasan cabang MIN
        return max_eval
    else:
        min_eval = math.inf
        for i in range(9):
            if board[i] == ' ':
                board[i] = 'O'
                eval_score = minimax_alpha_beta(board, depth + 1, alpha, beta, True)
                board[i] = ' '
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Pemangkasan cabang MAX
        return min_eval

def find_best_move_ab(board):
    best_score = -math.inf
    best_move = -1
    for i in range(9):
        if board[i] == ' ':
            board[i] = 'X'
            score = minimax_alpha_beta(board, 0, -math.inf, math.inf, False)
            board[i] = ' '
            if score > best_score:
                best_score = score
                best_move = i
    return best_move


# ------------------------------------------------------------------------------
# Test Papan Sederhana & Perbandingan
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    board_sample = ['X', 'O', 'X', ' ', 'O', ' ', ' ', ' ', 'X']
    print("--- Kondisi Papan Saat Ini ---")
    print_board(board_sample)
    print("Status Game:", check_winner(board_sample))

    # Uji Langkah 2 (Minimax Standar)
    move_standard = find_best_move(board_sample)
    print(f"\n[Langkah 2 - Minimax Standar] Langkah Terbaik Bot (X): Indeks {move_standard}")

    # Uji Langkah 3 (Minimax + Alpha-Beta Pruning)
    move_ab = find_best_move_ab(board_sample)
    print(f"[Langkah 3 - Alpha-Beta Pruning] Langkah Terbaik Bot (X): Indeks {move_ab}")
