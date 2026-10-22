# ==============================================================================
# PRAKTIKUM KECERDASAN BUATAN - SESI 4
# FILE: P4.py
# GAME TIC-TAC-TOE LENGKAP & SMART DRAW DETECTION:
# 1. Early Draw Detection: Otomatis DRAW jika semua garis sudah terblokir
# 2. Pemilihan Mode Kesulitan (Easy, Medium, Hard)
# 3. Pemilihan Siapa Duluan: Manusia, Bot, atau RANDOM (50:50)
# 4. Fitur In-Game: Undo ('u'), Restart ('r'), History ('h'), Stop ('q')
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

# Riwayat seluruh pertandingan yang dimainkan selama sesi
match_history = []


# ------------------------------------------------------------------------------
# 1. INISIALISASI PAPAN & CEK KEMENANGAN (DENGAN DETEKSI OTOMATIS DRAW)
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

    # 1. Cek apakah ada pemain yang menang (3 simbol sama beruntun)
    for cond in win_conditions:
        if board[cond[0]] == board[cond[1]] == board[cond[2]] != ' ':
            return board[cond[0]]

    # 2. Cek apakah seluruh petak papan sudah terisi penuh
    if ' ' not in board:
        return 'DRAW'

    # 3. FITUR EARLY DRAW (OTOMATIS DRAW):
    # Jika ke-8 garis kemenangan sudah terblokir (masing-masing garis memiliki 'X' dan 'O'),
    # maka secara matematis mustahil ada yang bisa menang meskipun masih ada sisa petak kosong.
    all_lines_blocked = True
    for cond in win_conditions:
        line_symbols = {board[cond[0]], board[cond[1]], board[cond[2]]}
        # Jika suatu garis belum mengandung kedua simbol ('X' dan 'O'), maka masih bisa dimenangkan
        if not ('X' in line_symbols and 'O' in line_symbols):
            all_lines_blocked = False
            break

    if all_lines_blocked:
        return 'DRAW'

    return None

def get_empty_cells(board):
    return [i for i in range(9) if board[i] == ' ']


# ------------------------------------------------------------------------------
# 2. LOGIKA AI BOT (EASY, MEDIUM, HARD)
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
# 3. FUNGSI RIWAYAT PERMAINAN (MATCH HISTORY & REKAP SKOR)
# ------------------------------------------------------------------------------
def print_history():
    print("\n" + "=" * 70)
    print("📜 RIWAYAT PERTANDINGAN (MATCH HISTORY) 📜")
    print("=" * 70)
    if not match_history:
        print("  Belum ada pertandingan yang selesai dicatat.")
        print("=" * 70 + "\n")
        return

    print(f"{'Game #':<8} | {'Level':<8} | {'Jalan Awal':<12} | {'Hasil Akhir':<18} | {'Total Langkah'}")
    print("-" * 70)
    menang_kamu = 0
    menang_bot = 0
    seri = 0

    for match in match_history:
        print(f"Game {match['game_no']:<3} | {match['difficulty']:<8} | {match['first']:<12} | {match['result']:<18} | {match['steps']} langkah")
        if match['result'] == 'Kamu Menang':
            menang_kamu += 1
        elif match['result'] == 'Bot Menang':
            menang_bot += 1
        elif 'Seri' in match['result']:
            seri += 1

    print("=" * 70)
    print(f"📊 REKAP SKOR: Menang (Kamu): {menang_kamu} | Menang (Bot): {menang_bot} | Seri: {seri} | Total Game: {len(match_history)}")
    print("=" * 70 + "\n")


# ------------------------------------------------------------------------------
# 4. GAME LOOP INTERAKTIF LENGKAP
# ------------------------------------------------------------------------------
def main_game():
    global match_history
    print("=" * 65)
    print("🎮 GAME TIC-TAC-TOE: MANUSIA vs AI BOT 🎮")
    print("=" * 65)

    # 1. Pemilihan Tingkat Kesulitan
    print("\n[1] PILIH TINGKAT KESULITAN:")
    print("  1. Easy   (Langkah Acak)")
    print("  2. Medium (Minimax Kedalaman Max 2)")
    print("  3. Hard   (Alpha-Beta Pruning / Unbeatable)")
    diff_inp = input("👉 Pilih level (1/2/3) [default: 3]: ").strip()
    levels = {'1': 'easy', '2': 'medium', '3': 'hard'}
    difficulty = levels.get(diff_inp, 'hard')

    # 2. Pemilihan Siapa Jalan Duluan (Manusia, Bot, atau RANDOM)
    print("\n[2] PILIH SIAPA YANG JALAN DULUAN:")
    print("  1. Manusia duluan ('O')")
    print("  2. Bot duluan ('X')")
    print("  3. Random / Acak (Kocok otomatis 50:50)")
    first_inp = input("👉 Pilih giliran pertama (1/2/3) [default: 1]: ").strip()
    turn_choice_mode = first_inp if first_inp in ['1', '2', '3'] else '1'

    while True:
        # Tentukan giliran pertama ronde ini
        if turn_choice_mode == '3':
            first_player = random.choice(['O', 'X'])
            print(f"\n🎲 Hasil Undian Acak: {'KAMU (O)' if first_player == 'O' else 'BOT (X)'} jalan duluan!")
        elif turn_choice_mode == '2':
            first_player = 'X'
        else:
            first_player = 'O'

        board = [' '] * 9
        history = []  # Riwayat snapshot papan untuk fitur UNDO ('u')
        current_player = first_player
        total_steps = 0

        print("\n" + "=" * 65)
        print(f"✨ RONDE DIMULAI! LEVEL: [{difficulty.upper()}] ✨")
        print(f"Pemain Pertama : {'BOT (X)' if first_player == 'X' else 'KAMU (O)'}")
        print("Kontrol In-Game:")
        print("  • Ketik 0 - 8 : Memilih petak langkah")
        print("  • Ketik 'u'   : UNDO (Batalkan langkah terakhir)")
        print("  • Ketik 'r'   : RESTART (Ulangi ronde ini dari awal)")
        print("  • Ketik 'h'   : HISTORY (Lihat riwayat pertandingan)")
        print("  • Ketik 'q'   : HENTIKAN PERMAINAN (Keluar dari game)")
        print("=" * 65)

        # Loop Pergerakan dalam Satu Ronde
        while True:
            # Cek status sebelum giliran jalan
            winner = check_winner(board)
            if winner:
                print_board(board)
                print("=" * 45)
                if winner == 'DRAW':
                    result_text = 'Seri (Draw)'
                    print("🤝 HASIL AKHIR: GAME SERI (DRAW)!")
                    print("💡 Info: Semua garis kemenangan sudah terblokir (Otomatis Seri).")
                elif winner == 'X':
                    result_text = 'Bot Menang'
                    print(f"🤖 HASIL AKHIR: BOT [{difficulty.upper()}] MENANG!")
                else:
                    result_text = 'Kamu Menang'
                    print("🎉 HASIL AKHIR: SELAMAT, KAMU (O) MENANG!")
                print("=" * 45)

                match_history.append({
                    'game_no': len(match_history) + 1,
                    'difficulty': difficulty.upper(),
                    'first': 'Manusia (O)' if first_player == 'O' else 'Bot (X)',
                    'result': result_text,
                    'steps': total_steps
                })
                break

            # --- GILIRAN MANUSIA ('O') ---
            if current_player == 'O':
                print_board(board)
                user_input = input("👉 Giliranmu (O)! Masukkan petak (0-8) [u=Undo, r=Reset, h=Hist, q=Stop]: ").strip().lower()

                # 1. Hentikan Permainan
                if user_input in ['q', 'quit', 'exit', 'stop', 'hentikan']:
                    print("\n🛑 Permainan dihentikan oleh pemain.")
                    print_history()
                    return

                # 2. Lihat History In-Game
                if user_input in ['h', 'hist', 'history']:
                    print_history()
                    continue

                # 3. Fitur Undo
                if user_input in ['u', 'undo']:
                    if len(history) > 0:
                        board = history.pop()
                        total_steps = max(0, total_steps - 1)
                        print("\n[⏪ UNDO BERHASIL] Langkah terakhir dibatalkan!")
                        continue
                    else:
                        print("\n⚠️ Belum ada langkah yang bisa di-undo!")
                        continue

                # 4. Fitur Restart
                if user_input in ['r', 'reset', 'ulang']:
                    print("\n[🔄 RESTART] Game ronde ini diulang kembali dari awal!\n")
                    break

                try:
                    move = int(user_input)
                    if move not in range(9):
                        print("⚠️ Pilihan harus angka 0 sampai 8!")
                        continue
                    if board[move] != ' ':
                        print("⚠️ Petak tersebut sudah terisi, pilih petak yang kosong!")
                        continue

                    # Simpan snapshot sebelum melangkah
                    history.append(list(board))
                    board[move] = 'O'
                    total_steps += 1
                    current_player = 'X'

                except ValueError:
                    print("⚠️ Ketik angka 0-8, 'u' (undo), 'r' (reset), 'h' (history), atau 'q' (stop)!")

            # --- GILIRAN BOT ('X') ---
            else:
                print(f"\n🤖 Bot [{difficulty.upper()}] sedang berpikir...")
                bot_move = get_bot_move(board, difficulty)
                if bot_move != -1:
                    board[bot_move] = 'X'
                    total_steps += 1
                    print(f"✅ Bot meletakkan 'X' di petak nomor: {bot_move}")
                current_player = 'O'

        # Tanya opsi setelah satu ronde berakhir
        tanya = input("\n🔄 Mau main lagi? (y = Ya / g = Ganti Setting / h = History / q = Keluar): ").strip().lower()
        if tanya == 'g':
            main_game()
            break
        elif tanya == 'h':
            print_history()
            lanjut = input("Mau lanjut main lagi? (y/n): ").strip().lower()
            if lanjut != 'y':
                print("\n👋 Terima kasih sudah bermain! Sampai jumpa lagi.\n")
                break
        elif tanya in ['q', 'n', 'exit', 'quit', 'stop']:
            print_history()
            print("👋 Terima kasih sudah bermain! Sampai jumpa lagi.\n")
            break


# ------------------------------------------------------------------------------
# ENTRY POINT
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    main_game()
