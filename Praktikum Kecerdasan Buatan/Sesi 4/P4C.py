# ==============================================================================
# PRAKTIKUM KECERDASAN BUATAN - SESI 4 (CHALLENGE / POST-TEST)
# FILE: P4C.py
# TOPIK: Bot Tic-Tac-Toe 3 Tingkat Kesulitan (Easy, Medium, Hard/Unbeatable)
#        Langsung Muncul & Bisa Dimainkan di Terminal Maupun Google Colab!
# ==============================================================================

import sys
import time
import math
import random

# Menjaga kompatibilitas output terminal Windows dan Google Colab
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Variabel global untuk menghitung jumlah node yang dievaluasi
nodes_minimax_count = 0
nodes_alphabeta_count = 0


# ------------------------------------------------------------------------------
# 1. REPRESENTASI PAPAN & FUNGSI WASIT (TERMINAL STATE)
# ------------------------------------------------------------------------------
def print_board(board):
    print("\n  Papan Tic-Tac-Toe         Panduan Nomor Petak")
    print("  +---+---+---+             +---+---+---+")
    for i in range(3):
        row_board = [board[idx] if board[idx] != ' ' else ' ' for idx in range(i * 3, (i + 1) * 3)]
        row_guide = [str(n) for n in range(i * 3, (i + 1) * 3)]
        print(f"  | {row_board[0]} | {row_board[1]} | {row_board[2]} |             | {row_guide[0]} | {row_guide[1]} | {row_guide[2]} |")
        print("  +---+---+---+             +---+---+---+")
    print()

def check_winner(board):
    win_conditions = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8], # 3 Baris
        [0, 3, 6], [1, 4, 7], [2, 5, 8], # 3 Kolom
        [0, 4, 8], [2, 4, 6]             # 2 Diagonal
    ]
    for cond in win_conditions:
        if board[cond[0]] == board[cond[1]] == board[cond[2]] != ' ':
            return board[cond[0]]
    if ' ' not in board:
        return 'DRAW'
    return None

def get_empty_cells(board):
    return [i for i in range(9) if board[i] == ' ']


# ------------------------------------------------------------------------------
# 2. ALGORITMA 1: MINIMAX MURNI (DENGAN HITUNGAN JUMLAH NODE)
# ------------------------------------------------------------------------------
def minimax_counter(board, is_maximizing):
    global nodes_minimax_count
    nodes_minimax_count += 1

    winner = check_winner(board)
    if winner == 'X':
        return 10
    if winner == 'O':
        return -10
    if winner == 'DRAW':
        return 0

    if is_maximizing:
        best_score = -math.inf
        for move in get_empty_cells(board):
            board[move] = 'X'
            score = minimax_counter(board, False)
            board[move] = ' '
            best_score = max(score, best_score)
        return best_score
    else:
        best_score = math.inf
        for move in get_empty_cells(board):
            board[move] = 'O'
            score = minimax_counter(board, True)
            board[move] = ' '
            best_score = min(score, best_score)
        return best_score


# ------------------------------------------------------------------------------
# 3. ALGORITMA 2: MINIMAX DENGAN PEMBATASAN KEDALAMAN (MEDIUM LEVEL: MAX DEPTH = 2)
# ------------------------------------------------------------------------------
def evaluate_board_heuristic(board):
    lines = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]
    score = 0
    for line in lines:
        values = [board[idx] for idx in line]
        if values.count('X') == 2 and values.count(' ') == 1:
            score += 2
        elif values.count('O') == 2 and values.count(' ') == 1:
            score -= 2
    return score

def minimax_depth_limited(board, depth, max_depth, is_maximizing):
    winner = check_winner(board)
    if winner == 'X':
        return 10 - depth
    if winner == 'O':
        return depth - 10
    if winner == 'DRAW':
        return 0

    if depth >= max_depth:
        return evaluate_board_heuristic(board)

    if is_maximizing:
        best_score = -math.inf
        for move in get_empty_cells(board):
            board[move] = 'X'
            score = minimax_depth_limited(board, depth + 1, max_depth, False)
            board[move] = ' '
            best_score = max(score, best_score)
        return best_score
    else:
        best_score = math.inf
        for move in get_empty_cells(board):
            board[move] = 'O'
            score = minimax_depth_limited(board, depth + 1, max_depth, True)
            board[move] = ' '
            best_score = min(score, best_score)
        return best_score


# ------------------------------------------------------------------------------
# 4. ALGORITMA 3: ALPHA-BETA PRUNING PENUH (HARD LEVEL: UNBEATABLE CEPAT)
# ------------------------------------------------------------------------------
def alphabeta_counter(board, depth, alpha, beta, is_maximizing):
    global nodes_alphabeta_count
    nodes_alphabeta_count += 1

    winner = check_winner(board)
    if winner == 'X':
        return 10 - depth
    if winner == 'O':
        return depth - 10
    if winner == 'DRAW':
        return 0

    if is_maximizing:
        max_eval = -math.inf
        for move in get_empty_cells(board):
            board[move] = 'X'
            eval_score = alphabeta_counter(board, depth + 1, alpha, beta, False)
            board[move] = ' '
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = math.inf
        for move in get_empty_cells(board):
            board[move] = 'O'
            eval_score = alphabeta_counter(board, depth + 1, alpha, beta, True)
            board[move] = ' '
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval


# ------------------------------------------------------------------------------
# 5. PEMILIHAN LANGKAH BOT (OPTIMAL & CEPAT)
# ------------------------------------------------------------------------------
def get_bot_move(board, difficulty):
    empty_cells = get_empty_cells(board)
    if not empty_cells:
        return -1, 0

    if difficulty.lower() == 'easy':
        return random.choice(empty_cells), 1

    elif difficulty.lower() == 'medium':
        best_score = -math.inf
        best_move = empty_cells[0]
        for move in empty_cells:
            board[move] = 'X'
            score = minimax_depth_limited(board, 0, max_depth=2, is_maximizing=False)
            board[move] = ' '
            if score > best_score:
                best_score = score
                best_move = move
        return best_move, 0

    else: # HARD
        global nodes_alphabeta_count
        nodes_alphabeta_count = 0

        best_score = -math.inf
        best_move = empty_cells[0]

        for move in empty_cells:
            board[move] = 'X'
            score = alphabeta_counter(board, depth=0, alpha=-math.inf, beta=math.inf, is_maximizing=False)
            board[move] = ' '
            if score > best_score:
                best_score = score
                best_move = move

        return best_move, nodes_alphabeta_count


# ------------------------------------------------------------------------------
# 6. FUNGSI UTAMA: play_game(difficulty) LANGSUNG MUNCUL & BISA DIMAINKAN
# ------------------------------------------------------------------------------
def play_game(difficulty='hard'):
    """
    Fungsi interaksi manusia (pemain 'O') vs Bot (pemain 'X').
    Default langsung membuka level 'hard' agar papan LANGSUNG MUNCUL di layar tanpa tertahan menu!
    """
    valid_levels = {'1': 'easy', '2': 'medium', '3': 'hard', 'easy': 'easy', 'medium': 'medium', 'hard': 'hard'}
    curr_diff = valid_levels.get(str(difficulty).lower(), 'hard')

    while True:
        board = [' '] * 9
        print("\n" + "=" * 55)
        print(f"🎮 PERMAINAN DIMULAI! LEVEL BOT: [{curr_diff.upper()}] 🎮")
        print("Kamu = 'O' (Manusia) | Bot = 'X' (AI)")
        print("Ketik nomor (0-8) untuk melangkah, atau ketik 'r' untuk Ulangi")
        print("=" * 55)

        current_player = 'O'
        ingame_restart = False

        while True:
            # Papan langsung tercetak di layar
            print_board(board)
            winner = check_winner(board)
            if winner:
                print("=" * 45)
                if winner == 'DRAW':
                    print("🤝 HASIL PERMAINAN: SERI (DRAW)!")
                elif winner == 'X':
                    print(f"🤖 HASIL PERMAINAN: BOT [{curr_diff.upper()}] MENANG!")
                else:
                    print(f"🎉 HASIL PERMAINAN: HEBAT, KAMU MENGALAHKAN BOT [{curr_diff.upper()}]!")
                print("=" * 45)
                break

            # --- GILIRAN MANUSIA ('O') ---
            if current_player == 'O':
                user_input = input("👉 Giliranmu (O)! Masukkan petak (0-8) [r = Ulangi]: ").strip().lower()
                
                # Fitur In-Game Restart
                if user_input in ['r', 'reset', 'ulang']:
                    print("\n[🔄 RESTART] Permainan diulang dari awal oleh pemain!\n")
                    ingame_restart = True
                    break

                try:
                    move = int(user_input)
                    if move not in range(9):
                        print("⚠️ Masukkan angka antara 0 sampai 8!")
                        continue
                    if board[move] != ' ':
                        print("⚠️ Petak tersebut sudah terisi, pilih petak kosong!")
                        continue
                    board[move] = 'O'
                    current_player = 'X'
                except ValueError:
                    print("⚠️ Input tidak valid! Ketik angka 0-8 atau 'r'.")

            # --- GILIRAN BOT ('X') ---
            else:
                print(f"🤖 Bot [{curr_diff.upper()}] berpikir...")
                bot_move, nodes_ab = get_bot_move(board, curr_diff)
                board[bot_move] = 'X'
                print(f"✅ Bot meletakkan 'X' di petak: {bot_move}")
                if curr_diff == 'hard':
                    print(f"   (Alpha-Beta mengevaluasi {nodes_ab} nodes)")

                current_player = 'O'

        if ingame_restart:
            continue

        # Tanya ulangi game atau ganti level
        tanya = input("\n🔄 Mau main lagi? (y = main lagi / n = keluar / 1 = Easy / 2 = Medium / 3 = Hard): ").strip().lower()
        if tanya in ['1', 'easy']:
            curr_diff = 'easy'
            continue
        elif tanya in ['2', 'medium']:
            curr_diff = 'medium'
            continue
        elif tanya in ['3', 'hard']:
            curr_diff = 'hard'
            continue
        elif tanya != 'y':
            print("\n👋 Terima kasih sudah bermain! Sampai jumpa.\n")
            break


# ------------------------------------------------------------------------------
# 7. FITUR BENCHMARK & KOMPARASI
# ------------------------------------------------------------------------------
def compare_minimax_vs_alphabeta():
    global nodes_minimax_count, nodes_alphabeta_count
    test_board = ['X', 'O', ' ', ' ', 'X', ' ', ' ', ' ', 'O']
    print("\n" + "=" * 65)
    print("📊 KOMPARASI: MINIMAX MURNI vs ALPHA-BETA PRUNING")
    print("=" * 65)
    print_board(test_board)

    nodes_minimax_count = 0
    t0 = time.perf_counter()
    for move in get_empty_cells(test_board):
        test_board[move] = 'X'
        _ = minimax_counter(test_board, False)
        test_board[move] = ' '
    t_minimax = (time.perf_counter() - t0) * 1000

    nodes_alphabeta_count = 0
    t1 = time.perf_counter()
    for move in get_empty_cells(test_board):
        test_board[move] = 'X'
        _ = alphabeta_counter(test_board, 0, -math.inf, math.inf, False)
        test_board[move] = ' '
    t_ab = (time.perf_counter() - t1) * 1000

    hemat_node = nodes_minimax_count - nodes_alphabeta_count
    persen_hemat = (hemat_node / nodes_minimax_count) * 100 if nodes_minimax_count > 0 else 0

    print(f"• Node Minimax Murni : {nodes_minimax_count} nodes ({t_minimax:.2f} ms)")
    print(f"• Node Alpha-Beta    : {nodes_alphabeta_count} nodes ({t_ab:.2f} ms)")
    print(f"• Efisiensi          : Hemat {persen_hemat:.1f}% node evaluasi!")
    print("=" * 65 + "\n")


def run_benchmark_trials(num_games=5):
    print("\n" + "=" * 70)
    print(f"🚀 MENJALANKAN BENCHMARK OTOMATIS ({num_games}x PER LEVEL)")
    print("=" * 70)
    for lvl in ['easy', 'medium', 'hard']:
        hasil = {'MENANG_X': 0, 'MENANG_O': 0, 'DRAW': 0}
        for _ in range(num_games):
            board = [' '] * 9
            curr = 'O'
            while True:
                w = check_winner(board)
                if w:
                    hasil['MENANG_X' if w == 'X' else ('MENANG_O' if w == 'O' else 'DRAW')] += 1
                    break
                empty = get_empty_cells(board)
                if not empty: break
                if curr == 'O':
                    board[random.choice(empty)] = 'O'
                    curr = 'X'
                else:
                    move, _ = get_bot_move(board, lvl)
                    board[move] = 'X'
                    curr = 'O'
        print(f"• Level {lvl.upper():<7}: Bot Menang = {hasil['MENANG_X']}, Manusia = {hasil['MENANG_O']}, Seri = {hasil['DRAW']}")
    print("=" * 70 + "\n")


# ------------------------------------------------------------------------------
# ENTRY POINT: LANGSUNG MULAI MAIN SECARA OTOMATIS!
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    play_game('hard')
