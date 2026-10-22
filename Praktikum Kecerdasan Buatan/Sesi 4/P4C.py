# ==============================================================================
# PRAKTIKUM KECERDASAN BUATAN - SESI 4 (CHALLENGE / POST-TEST)
# FILE: P4C.py
# FITUR LENGKAP:
# 1. Tiga Tingkat Kesulitan: Easy (Acak), Medium (Depth-Limited), Hard (Alpha-Beta)
# 2. Pemilihan Siapa Jalan Duluan: Manusia ('O') atau Bot ('X')
# 3. Fitur In-Game: UNDO ('u') & RESTART ('r')
# 4. Analisis & Perbandingan Node (Minimax vs Alpha-Beta)
# 5. Benchmark Otomatis 5x Pertandingan per Level
# ==============================================================================

import sys
import time
import math
import random

# Menjaga kompatibilitas output encoding di Windows Terminal & Google Colab
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Variabel global untuk penghitungan node evaluasi
nodes_minimax_count = 0
nodes_alphabeta_count = 0


# ------------------------------------------------------------------------------
# 1. INISIALISASI PAPAN & CEK KEMENANGAN
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

def get_empty_cells(board):
    return [i for i in range(9) if board[i] == ' ']


# ------------------------------------------------------------------------------
# 2. ALGORITMA MINIMAX MURNI (DENGAN HITUNGAN NODE)
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
# 3. ALGORITMA MINIMAX DEPTH-LIMITED (MEDIUM LEVEL: MAX DEPTH = 2)
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
# 4. ALGORITMA ALPHA-BETA PRUNING (HARD LEVEL: UNBEATABLE CEPAT)
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
# 5. PEMILIHAN LANGKAH BOT BERDASARKAN LEVEL
# ------------------------------------------------------------------------------
def get_bot_move(board, difficulty):
    empty_cells = get_empty_cells(board)
    if not empty_cells:
        return -1, 0

    # 1. Easy: Acak Murni
    if difficulty.lower() == 'easy':
        return random.choice(empty_cells), 1

    # 2. Medium: Minimax Kedalaman Max 2
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

    # 3. Hard: Alpha-Beta Pruning (Unbeatable)
    else:
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
# 6. FUNGSI UTAMA: play_game() INTERAKTIF (PILIH MODE, GILIRAN, UNDO, RESTART)
# ------------------------------------------------------------------------------
def play_game(difficulty=None, first_player=None):
    valid_levels = {'1': 'easy', '2': 'medium', '3': 'hard', 'easy': 'easy', 'medium': 'medium', 'hard': 'hard'}
    
    # 1. Pilih Tingkat Kesulitan jika belum diset
    if not difficulty or str(difficulty).lower() not in valid_levels:
        print("\n" + "=" * 55)
        print("[PILIHAN] TINGKAT KESULITAN BOT TIC-TAC-TOE:")
        print("  [1] Easy   : Langkah Acak (Random Move)")
        print("  [2] Medium : Minimax Terbatas (Depth-Limited, Max Depth = 2)")
        print("  [3] Hard   : Alpha-Beta Pruning Penuh (Unbeatable AI)")
        print("=" * 55)
        diff_choice = input("Pilih level (1/2/3) [default: 3]: ").strip().lower()
        difficulty = valid_levels.get(diff_choice, 'hard')
    else:
        difficulty = valid_levels[str(difficulty).lower()]

    # 2. Pilih Siapa yang Jalan Duluan jika belum diset
    if not first_player:
        print("\n[PILIHAN] SIAPA YANG JALAN DULUAN:")
        print("  [1] Manusia duluan ('O')")
        print("  [2] Bot duluan ('X')")
        fp_choice = input("Pilih giliran pertama (1/2) [default: 1]: ").strip()
        first_player = 'X' if fp_choice == '2' else 'O'

    while True:
        board = [' '] * 9
        history = []  # Menyimpan snapshot board untuk fitur UNDO ('u')
        current_player = first_player

        print("\n" + "=" * 60)
        print(f"🎮 MULAI PERMAINAN - LEVEL: [{difficulty.upper()}] 🎮")
        print(f"Pemain Pertama : {'BOT (X)' if first_player == 'X' else 'KAMU (O)'}")
        print("Petunjuk Kontrol:")
        print("  • Masukkan 0-8 : Memilih kotak langkah")
        print("  • Ketik 'u'    : UNDO (Batalkan langkah terakhir)")
        print("  • Ketik 'r'    : RESTART (Ulangi game dari awal)")
        print("=" * 60)

        # Loop Ronde Permainan
        while True:
            # --- GILIRAN MANUSIA ('O') ---
            if current_player == 'O':
                print_board(board)
                winner = check_winner(board)
                if winner:
                    print("=" * 45)
                    if winner == 'DRAW':
                        print("🤝 HASIL AKHIR: GAME SERI (DRAW)!")
                    elif winner == 'X':
                        print(f"🤖 HASIL AKHIR: BOT [{difficulty.upper()}] MENANG!")
                    else:
                        print("🎉 HASIL AKHIR: SELAMAT, KAMU (O) MENANG!")
                    print("=" * 45)
                    break

                user_input = input("👉 Giliranmu (O)! Masukkan petak (0-8) [u = Undo, r = Ulangi]: ").strip().lower()

                # --- FITUR UNDO ---
                if user_input in ['u', 'undo']:
                    if len(history) > 0:
                        board = history.pop()
                        print("\n[⏪ UNDO BERHASIL] Langkah terakhir dibatalkan!")
                        continue
                    else:
                        print("\n⚠️ Belum ada langkah yang bisa di-undo!")
                        continue

                # --- FITUR RESTART IN-GAME ---
                if user_input in ['r', 'reset', 'ulang']:
                    print("\n[🔄 RESTART] Game diulang dari awal oleh pemain!\n")
                    break

                try:
                    move = int(user_input)
                    if move not in range(9):
                        print("⚠️ Pilihan harus angka 0 sampai 8!")
                        continue
                    if board[move] != ' ':
                        print("⚠️ Petak tersebut sudah terisi, pilih petak kosong!")
                        continue

                    # Simpan snapshot sebelum melangkah
                    history.append(list(board))
                    board[move] = 'O'
                    current_player = 'X'

                except ValueError:
                    print("⚠️ Harap masukkan angka 0-8, 'u' untuk undo, atau 'r' untuk ulangi!")

            # --- GILIRAN BOT ('X') ---
            else:
                winner = check_winner(board)
                if winner:
                    print_board(board)
                    print("=" * 45)
                    if winner == 'DRAW':
                        print("🤝 HASIL AKHIR: GAME SERI (DRAW)!")
                    elif winner == 'X':
                        print(f"🤖 HASIL AKHIR: BOT [{difficulty.upper()}] MENANG!")
                    else:
                        print("🎉 HASIL AKHIR: SELAMAT, KAMU (O) MENANG!")
                    print("=" * 45)
                    break

                print(f"🤖 Bot [{difficulty.upper()}] sedang berpikir...")
                bot_move, nodes_count = get_bot_move(board, difficulty)
                if bot_move != -1:
                    board[bot_move] = 'X'
                    print(f"✅ Bot meletakkan 'X' di petak nomor: {bot_move}")
                    if difficulty == 'hard':
                        print(f"   (Alpha-Beta mengevaluasi {nodes_count} nodes)")

                current_player = 'O'

        # Opsi setelah game usai
        tanya = input("\n🔄 Mau main lagi? (y = Ya / n = Keluar / g = Ganti Pengaturan Level): ").strip().lower()
        if tanya == 'g':
            play_game()
            break
        elif tanya != 'y':
            print("\n👋 Terima kasih sudah bermain! Sampai jumpa lagi.\n")
            break


# ------------------------------------------------------------------------------
# 7. FITUR KOMPARASI & BENCHMARK OTOMATIS (POST-TEST)
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

    print("-" * 65)
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
                if not empty:
                    break
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
# ENTRY POINT PROGRAM
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("      STUDI KASUS & POST-TEST PRAKTIKUM AI: TIC-TAC-TOE      ")
    print("=" * 60)
    print("Pilihan Menu:")
    print("  [1] Main Game Interaktif (Pilih Mode, Duluan, Undo, Restart)")
    print("  [2] Jalankan Benchmark Otomatis 5x Permainan (Laporan)")
    print("  [3] Bandingkan Efisiensi Node (Minimax vs Alpha-Beta)")
    print("=" * 60)
    menu_choice = input("Pilih menu (1/2/3) [default: 1]: ").strip()

    if menu_choice == '2':
        run_benchmark_trials(num_games=5)
    elif menu_choice == '3':
        compare_minimax_vs_alphabeta()
    else:
        play_game()
