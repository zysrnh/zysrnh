# ==============================================================================
# PRAKTIKUM KECERDASAN BUATAN - SESI 4
# FILE: P4U.py
# TOPIK: Tic-Tac-Toe AI Engine (Monokrom Hitam-Putih, Proporsional, Micro-Animation)
# - Mendukung Google Colab (UI Interaktif) & Terminal CLI (Fallback)
# - 3 Tingkat Kesulitan, Giliran Acak, Undo, Restart, Early Draw, Match History
# ==============================================================================

import sys
import math
import random
import os

# Menjaga kompatibilitas output encoding di Windows Terminal & Google Colab
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


# ------------------------------------------------------------------------------
# 1. LOGIKA INTI PERMAINAN (PYTHON ENGINE)
# ------------------------------------------------------------------------------
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

    # Deteksi Dini Hasil Seri (Semua 8 garis kemenangan sudah terblokir)
    all_blocked = True
    for cond in win_conditions:
        symbols = {board[cond[0]], board[cond[1]], board[cond[2]]}
        if not ('X' in symbols and 'O' in symbols):
            all_blocked = False
            break

    if all_blocked:
        return 'DRAW'

    return None

def get_empty_cells(board):
    return [i for i in range(9) if board[i] == ' ']

def evaluate_heuristic(board):
    lines = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]
    score = 0
    for l in lines:
        vals = [board[idx] for idx in l]
        if vals.count('X') == 2 and vals.count(' ') == 1:
            score += 2
        elif vals.count('O') == 2 and vals.count(' ') == 1:
            score -= 2
    return score

def minimax_depth_limited(board, depth, max_depth, is_maximizing):
    w = check_winner(board)
    if w == 'X':
        return 10 - depth
    if w == 'O':
        return depth - 10
    if w == 'DRAW':
        return 0

    if depth >= max_depth:
        return evaluate_heuristic(board)

    if is_maximizing:
        best = -math.inf
        for m in get_empty_cells(board):
            board[m] = 'X'
            s = minimax_depth_limited(board, depth + 1, max_depth, False)
            board[m] = ' '
            best = max(s, best)
        return best
    else:
        best = math.inf
        for m in get_empty_cells(board):
            board[m] = 'O'
            s = minimax_depth_limited(board, depth + 1, max_depth, True)
            board[m] = ' '
            best = min(s, best)
        return best

def minimax_alpha_beta(board, depth, alpha, beta, is_maximizing):
    w = check_winner(board)
    if w == 'X':
        return 10 - depth
    if w == 'O':
        return depth - 10
    if w == 'DRAW':
        return 0

    if is_maximizing:
        max_eval = -math.inf
        for m in get_empty_cells(board):
            board[m] = 'X'
            ev = minimax_alpha_beta(board, depth + 1, alpha, beta, False)
            board[m] = ' '
            max_eval = max(max_eval, ev)
            alpha = max(alpha, ev)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = math.inf
        for m in get_empty_cells(board):
            board[m] = 'O'
            ev = minimax_alpha_beta(board, depth + 1, alpha, beta, True)
            board[m] = ' '
            min_eval = min(min_eval, ev)
            beta = min(beta, ev)
            if beta <= alpha:
                break
        return min_eval

def get_bot_move(board, difficulty):
    empty = get_empty_cells(board)
    if not empty:
        return -1

    if difficulty == 'easy':
        return random.choice(empty)
    elif difficulty == 'medium':
        best_s, best_m = -math.inf, empty[0]
        for m in empty:
            board[m] = 'X'
            s = minimax_depth_limited(board, 0, max_depth=2, is_maximizing=False)
            board[m] = ' '
            if s > best_s:
                best_s = s
                best_m = m
        return best_m
    else: # hard
        best_s, best_m = -math.inf, empty[0]
        for m in empty:
            board[m] = 'X'
            s = minimax_alpha_beta(board, 0, -math.inf, math.inf, False)
            board[m] = ' '
            if s > best_s:
                best_s = s
                best_m = m
        return best_m


# ------------------------------------------------------------------------------
# 2. RUNNER: DETEKSI OTOMATIS (GOOGLE COLAB vs TERMINAL CLI)
# ------------------------------------------------------------------------------
def display_ui():
    """Menampilkan UI Web Monokrom di Google Colab jika didukung, atau fallback ke CLI."""
    try:
        from IPython.display import HTML, display
        html_file = os.path.join(os.path.dirname(__file__), 'P4U.html')
        if os.path.exists(html_file):
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            display(HTML(content))
        else:
            main_cli()
    except Exception:
        main_cli()

def main_cli():
    """Fallback ke mode terminal bersih (Clean Box-Drawing, Zero Emoji)."""
    print("=" * 60)
    print("[PRAKTIKUM AI - SESI 4] TIC-TAC-TOE ENGINE")
    print("=" * 60)

    print("\n[PILIHAN TINGKAT KESULITAN]")
    print("  1. Easy   (Langkah Acak)")
    print("  2. Medium (Kedalaman Max 2)")
    print("  3. Hard   (Alpha-Beta / Unbeatable)")
    d_inp = input("Pilih level (1/2/3) [default: 3]: ").strip()
    levels = {'1': 'easy', '2': 'medium', '3': 'hard'}
    diff = levels.get(d_inp, 'hard')

    print("\n[PILIHAN GILIRAN PERTAMA]")
    print("  1. User (O)")
    print("  2. Bot (X)")
    print("  3. Acak (50:50)")
    f_inp = input("Pilih giliran (1/2/3) [default: 1]: ").strip()

    board = [' '] * 9
    first = 'O'
    if f_inp == '2': first = 'X'
    elif f_inp == '3': first = random.choice(['O', 'X'])

    curr = first
    history = []

    print("\n" + "-" * 60)
    print(f"Permainan Dimulai | Level: [{diff.upper()}] | Awal: [{first}]")
    print("Perintah: [0-8] Petak | [u] Undo | [r] Restart | [q] Keluar")
    print("-" * 60)

    while True:
        w = check_winner(board)
        if w:
            print("\n  Papan Akhir:")
            for i in range(3):
                row = board[i*3:(i+1)*3]
                print(f"  | {' | '.join(row)} |")
            print("-" * 40)
            if w == 'DRAW': print("[HASIL] Permainan Berakhir Seri (Draw)")
            elif w == 'X': print(f"[HASIL] Bot [{diff.upper()}] Menang")
            else: print("[HASIL] Selamat, Kamu Menang")
            print("-" * 40)
            break

        if curr == 'O':
            print("\n  Papan Saat Ini:        Nomor Petak:")
            for i in range(3):
                row = board[i*3:(i+1)*3]
                guide = [str(n) for n in range(i*3, (i+1)*3)]
                print(f"  | {' | '.join(row)} |        | {' | '.join(guide)} |")

            inp = input("\nGiliranmu (O) [0-8/u/r/q]: ").strip().lower()
            if inp in ['q', 'exit', 'quit']: break
            if inp in ['r', 'reset']:
                board = [' '] * 9; history.clear(); curr = first; continue
            if inp in ['u', 'undo']:
                if history: board = history.pop(); continue
                else: print("[INFO] Tidak ada langkah untuk di-undo"); continue

            try:
                m = int(inp)
                if m not in range(9) or board[m] != ' ': continue
                history.append(list(board))
                board[m] = 'O'
                curr = 'X'
            except ValueError:
                continue
        else:
            bm = get_bot_move(board, diff)
            if bm != -1: board[bm] = 'X'
            curr = 'O'


# ------------------------------------------------------------------------------
# ENTRY POINT
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    display_ui()
