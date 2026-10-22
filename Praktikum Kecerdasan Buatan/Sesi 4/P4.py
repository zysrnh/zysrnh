# Langkah 1: Inisialisasi Papan & Cek Kemenangan Tic-Tac-Toe
import math

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

# Test Papan Sederhana
board_sample = ['X', 'O', 'X', ' ', 'O', ' ', ' ', ' ', 'X']
print_board(board_sample)
print("Status Game:", check_winner(board_sample))
