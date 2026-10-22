# ==============================================================================
# PRAKTIKUM KECERDASAN BUATAN - SESI 4
# FILE: P4.py
# GAME TIC-TAC-TOE LENGKAP:
# - Pemilihan Mode Kesulitan (Easy, Medium, Hard)
# - Pemilihan Siapa Jalan Duluan (Manusia atau Bot)
# - Fitur In-Game Undo ('u') & Ulangi ('r') Kapan Saja
# ==============================================================================
import sys
import math
import random

# Menjaga kompatibilitas output encoding
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


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
# 2. LOGIKA AI: EASY, MEDIUM (DEPTH-LIMITED), HARD (ALPHA-BETA)
# ------------------------------------------------------------------------------
def evaluate_board_heuristic(board):
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
        return evaluate_board_heuristic(board)

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

    # Level 1: Easy (Acak)
    if difficulty == 'easy':
        return random.choice(empty)

    # Level 2: Medium (Kedalaman Maksimal 2)
    elif difficulty == 'medium':
        best_s = -math.inf
        best_m = empty[0]
        for m in empty:
            board[m] = 'X'
            s = minimax_depth_limited(board, 0, max_depth=2, is_maximizing=False)
            board[m] = ' '
            if s > best_s:
                best_s = s
                best_m = m
        return best_m

    # Level 3: Hard (Alpha-Beta Pruning Penuh / Unbeatable)
    else:
        best_s = -math.inf
        best_m = empty[0]
        for m in empty:
            board[m] = 'X'
            s = minimax_alpha_beta(board, 0, -math.inf, math.inf, False)
            board[m] = ' '
            if s > best_s:
                best_s = s
                best_m = m
        return best_m


# ------------------------------------------------------------------------------
# 3. GAME LOOP INTERAKTIF: PILIH MODE, PILIH DULUAN, UNDO & RESTART
# ------------------------------------------------------------------------------
def main_game():
    print("=" * 60)
    print("🎮 GAME TIC-TAC-TOE: MANUSIA vs AI BOT 🎮")
    print("=" * 60)

    # 1. Pemilihan Tingkat Kesulitan
    print("\n[1] PILIH TINGKAT KESULITAN:")
    print("  1. Easy   (Langkah Acak)")
    print("  2. Medium (Minimax Kedalaman Max 2)")
    print("  3. Hard   (Alpha-Beta Pruning / Unbeatable)")
    diff_inp = input("👉 Pilih level (1/2/3) [default: 3]: ").strip()
    levels = {'1': 'easy', '2': 'medium', '3': 'hard'}
    difficulty = levels.get(diff_inp, 'hard')

    # 2. Pemilihan Siapa Jalan Duluan
    print("\n[2] PILIH SIAPA YANG JALAN DULUAN:")
    print("  1. Manusia duluan ('O')")
    print("  2. Bot duluan ('X')")
    first_inp = input("👉 Pilih giliran pertama (1/2) [default: 1]: ").strip()
    first_player = 'X' if first_inp == '2' else 'O'

    while True:
        board = [' '] * 9
        history = []  # Menyimpan riwayat papan untuk fitur UNDO ('u')
        current_player = first_player

        print("\n" + "=" * 60)
        print(f"✨ PERMAINAN DIMULAI! LEVEL: [{difficulty.upper()}] ✨")
        print(f"Pemain Pertama: {'BOT (X)' if first_player == 'X' else 'KAMU (O)'}")
        print("Kontrol In-Game:")
        print("  • Ketik 0 - 8 : Memilih petak langkah")
        print("  • Ketik 'u'   : UNDO (Batalkan langkah terakhir)")
        print("  • Ketik 'r'   : RESTART (Ulangi game dari awal)")
        print("=" * 60)

        # Loop Ronde Permainan
        while True:
            # Jika giliran Manusia: Tampilkan papan dan simpan snapshot untuk Undo
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

                # Simpan keadaan papan sebelum manusia melangkah agar bisa di-undo
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
                    print("\n[🔄 RESTART] Game diulang kembali dari awal!\n")
                    break

                try:
                    move = int(user_input)
                    if move not in range(9):
                        print("⚠️ Pilihan harus angka 0 sampai 8!")
                        continue
                    if board[move] != ' ':
                        print("⚠️ Petak tersebut sudah terisi, pilih petak yang kosong!")
                        continue

                    # Simpan snapshot sebelum menaruh 'O'
                    history.append(list(board))
                    board[move] = 'O'
                    current_player = 'X'

                except ValueError:
                    print("⚠️ Harap masukkan angka 0-8, 'u' untuk undo, atau 'r' untuk ulangi!")

            # Jika giliran Bot ('X')
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
                bot_move = get_bot_move(board, difficulty)
                if bot_move != -1:
                    board[bot_move] = 'X'
                    print(f"✅ Bot meletakkan 'X' di petak nomor: {bot_move}")
                current_player = 'O'

        # Setelah satu game berakhir: Opsi main lagi
        tanya = input("\n🔄 Mau main lagi? (y = Ya / n = Keluar / g = Ganti Pengaturan): ").strip().lower()
        if tanya == 'g':
            main_game()
            break
        elif tanya != 'y':
            print("\n👋 Terima kasih sudah bermain! Sampai jumpa lagi.\n")
            break


# ------------------------------------------------------------------------------
# ENTRY POINT
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    main_game()
