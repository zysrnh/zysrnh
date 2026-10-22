# ==============================================================================
# PRAKTIKUM KECERDASAN BUATAN - SESI 4 (CHALLENGE / POST-TEST)
# FILE: P4C.py
# TOPIK: Bot Tic-Tac-Toe 3 Tingkat Kesulitan (Easy, Medium, Hard/Unbeatable)
#        + Perbandingan Jumlah Node (Minimax vs Alpha-Beta)
#        + Laporan Otomatis Uji Coba 5 Kali Permainan
# ==============================================================================

import sys
import math
import random

# Menjaga kompatibilitas output terminal Windows (CP1252) dan Google Colab (UTF-8)
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
    print("\n  Papan Tic-Tac-Toe       Panduan Nomor")
    for i in range(3):
        row_board = board[i * 3:(i + 1) * 3]
        row_guide = [str(n) for n in range(i * 3, (i + 1) * 3)]
        print(f"  | {' | '.join(row_board)} |       | {' | '.join(row_guide)} |")
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
    """
    Evaluasi heuristik sederhana jika kedalaman mencapai batas maksimum (depth = 2):
    Memberikan skor berdasarkan potensi garis kemenangan Bot (X) vs Manusia (O).
    """
    lines = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]
    score = 0
    for line in lines:
        values = [board[idx] for idx in line]
        if values.count('X') == 2 and values.count(' ') == 1:
            score += 2 # Peluang ancaman bagi X
        elif values.count('O') == 2 and values.count(' ') == 1:
            score -= 2 # Peluang ancaman bagi O
    return score

def minimax_depth_limited(board, depth, max_depth, is_maximizing):
    winner = check_winner(board)
    if winner == 'X':
        return 10 - depth
    if winner == 'O':
        return depth - 10
    if winner == 'DRAW':
        return 0

    # Batas kedalaman tercapai (Depth Limit)
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
# 4. ALGORITMA 3: ALPHA-BETA PRUNING PENUH (HARD LEVEL: UNBEATABLE)
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
                break # Pemangkasan cabang MIN
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
                break # Pemangkasan cabang MAX
        return min_eval


# ------------------------------------------------------------------------------
# 5. PEMILIHAN LANGKAH BOT BERDASARKAN 3 TINGKAT KESULITAN
# ------------------------------------------------------------------------------
def get_bot_move(board, difficulty):
    empty_cells = get_empty_cells(board)
    if not empty_cells:
        return -1, 0, 0

    # 1. LEVEL EASY: Langkah Acak Murni (Random Move)
    if difficulty.lower() == 'easy':
        return random.choice(empty_cells), 1, 1

    # 2. LEVEL MEDIUM: Depth-Limited Minimax (Kedalaman Maks = 2)
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
        return best_move, 0, 0

    # 3. LEVEL HARD / UNBEATABLE: Alpha-Beta Pruning Penuh hingga Terminal State
    else:
        global nodes_minimax_count, nodes_alphabeta_count
        nodes_minimax_count = 0
        nodes_alphabeta_count = 0

        # Hitung langkah terbaik sekaligus benchmark komparasi node
        best_score = -math.inf
        best_move = empty_cells[0]

        # Jalankan evaluasi Alpha-Beta
        for move in empty_cells:
            board[move] = 'X'
            score = alphabeta_counter(board, depth=0, alpha=-math.inf, beta=math.inf, is_maximizing=False)
            board[move] = ' '
            if score > best_score:
                best_score = score
                best_move = move

        # Evaluasi pembanding Minimax Murni pada giliran ini untuk statistik
        for move in empty_cells:
            board[move] = 'X'
            _ = minimax_counter(board, is_maximizing=False)
            board[move] = ' '

        return best_move, nodes_minimax_count, nodes_alphabeta_count


# ------------------------------------------------------------------------------
# 6. FUNGSI UTAMA: play_game(difficulty) INTERAKTIF (TUGAS MAHASISWA)
# ------------------------------------------------------------------------------
def play_game(difficulty=None):
    """
    Fungsi interaksi manusia (pemain 'O') vs Bot (pemain 'X')
    Mendukung 3 level: 'easy', 'medium', 'hard'.
    Dilengkapi fitur in-game restart ('r') dan analisis node secara realtime.
    """
    valid_levels = {'1': 'easy', '2': 'medium', '3': 'hard', 'easy': 'easy', 'medium': 'medium', 'hard': 'hard'}
    
    # Menu pilihan jika difficulty belum diset
    if not difficulty or str(difficulty).lower() not in valid_levels:
        print("\n" + "=" * 55)
        print("[PILIHAN] TINGKAT KESULITAN BOT TIC-TAC-TOE:")
        print("  [1] Easy   : Langkah Acak (Random Move)")
        print("  [2] Medium : Minimax Terbatas (Depth-Limited, Max Depth = 2)")
        print("  [3] Hard   : Alpha-Beta Pruning Penuh (Unbeatable AI)")
        print("=" * 55)
        choice = input("Pilih level (1/2/3) [default: 3]: ").strip().lower()
        difficulty = valid_levels.get(choice, 'hard')
    else:
        difficulty = valid_levels[str(difficulty).lower()]

    while True:
        board = [' '] * 9
        print("\n" + "=" * 55)
        print(f"[GAME START] LEVEL: [{difficulty.upper()}]")
        print("Kamu = 'O' (Manusia) | Bot = 'X' (AI)")
        print("TIPS: Ketik 'r' kapan saja saat giliranmu untuk ULANGI GAME")
        print("=" * 55)

        current_player = 'O'
        ingame_restart = False

        while True:
            print_board(board)
            winner = check_winner(board)
            if winner:
                print("=" * 45)
                if winner == 'DRAW':
                    print(">> HASIL PERMAINAN: SERI (DRAW)!")
                elif winner == 'X':
                    print(f">> HASIL PERMAINAN: BOT [{difficulty.upper()}] MENANG!")
                else:
                    print(f">> HASIL PERMAINAN: HEBAT, KAMU MENGALAHKAN BOT [{difficulty.upper()}]!")
                print("=" * 45)
                break

            # --- GILIRAN MANUSIA ('O') ---
            if current_player == 'O':
                user_input = input(">> Giliranmu (O)! Masukkan petak (0-8) [r = Ulangi]: ").strip().lower()
                
                # Fitur In-Game Restart
                if user_input in ['r', 'reset', 'ulang']:
                    print("\n[RESTART] Permainan diulang dari awal oleh pemain!\n")
                    ingame_restart = True
                    break

                try:
                    move = int(user_input)
                    if move not in range(9):
                        print("[PERINGATAN] Masukkan angka antara 0 sampai 8!")
                        continue
                    if board[move] != ' ':
                        print("[PERINGATAN] Petak tersebut sudah terisi, pilih petak kosong!")
                        continue
                    board[move] = 'O'
                    current_player = 'X'
                except ValueError:
                    print("[PERINGATAN] Input tidak valid! Ketik angka 0-8 atau 'r'.")

            # --- GILIRAN BOT ('X') ---
            else:
                print(f"[BOT] Bot [{difficulty.upper()}] sedang berpikir...")
                bot_move, nodes_mm, nodes_ab = get_bot_move(board, difficulty)
                board[bot_move] = 'X'
                print(f"[BOT] Meletakkan 'X' di petak nomor: {bot_move}")

                # Tampilkan perbandingan node jika bermain di level Hard
                if difficulty == 'hard' and nodes_mm > 0:
                    pangkas = nodes_mm - nodes_ab
                    hemat = (pangkas / nodes_mm) * 100 if nodes_mm > 0 else 0
                    print(f"   [ANALISIS NODE] Langkah Ini:")
                    print(f"      - Minimax Murni     : {nodes_mm} nodes")
                    print(f"      - Alpha-Beta Pruning: {nodes_ab} nodes")
                    print(f"      - Node Terpangkas   : {pangkas} nodes (Hemat {hemat:.1f}%!)")

                current_player = 'O'

        if ingame_restart:
            continue

        # Tanya ulangi game atau ganti level
        tanya = input("\n[PILIHAN] Mau main lagi? (y = main lagi / n = keluar / g = ganti level): ").strip().lower()
        if tanya == 'g':
            play_game()
            break
        elif tanya != 'y':
            print("\nTerima kasih sudah bermain! Sampai jumpa.\n")
            break


# ------------------------------------------------------------------------------
# 7. FITUR OTOMATIS: SIMULASI 5 KALI PERMAINAN (TUGAS MAHASISWA POIN 3)
# ------------------------------------------------------------------------------
def run_benchmark_trials(num_games=5):
    """
    Menjalankan simulasi otomatis 5 kali permainan per level kesulitan
    dan menghasilkan tabel laporan pengujian node untuk laporan praktikum.
    """
    print("\n" + "=" * 75)
    print(f"[BENCHMARK] MENJALANKAN SIMULASI OTOMATIS ({num_games}x UJI COBA PER LEVEL)")
    print("=" * 75)

    levels = ['easy', 'medium', 'hard']
    laporan = []

    for lvl in levels:
        print(f"\n[+] Menguji Level: {lvl.upper()} ({num_games} pertandingan)...")
        hasil = {'MENANG_X': 0, 'MENANG_O': 0, 'DRAW': 0}
        total_nodes_mm = 0
        total_nodes_ab = 0
        total_bot_moves = 0

        for game_idx in range(num_games):
            board = [' '] * 9
            # Simulasi: Pemain Manusia bermain acak untuk menguji responsivitas Bot
            curr = 'O'
            while True:
                winner = check_winner(board)
                if winner:
                    if winner == 'X':
                        hasil['MENANG_X'] += 1
                    elif winner == 'O':
                        hasil['MENANG_O'] += 1
                    else:
                        hasil['DRAW'] += 1
                    break

                empty = get_empty_cells(board)
                if not empty:
                    break

                if curr == 'O':
                    board[random.choice(empty)] = 'O'
                    curr = 'X'
                else:
                    move, n_mm, n_ab = get_bot_move(board, lvl)
                    board[move] = 'X'
                    if lvl == 'hard':
                        total_nodes_mm += n_mm
                        total_nodes_ab += n_ab
                        total_bot_moves += 1
                    curr = 'O'

        avg_mm = total_nodes_mm / total_bot_moves if total_bot_moves > 0 else 0
        avg_ab = total_nodes_ab / total_bot_moves if total_bot_moves > 0 else 0
        laporan.append({
            'level': lvl.upper(),
            'bot_win': hasil['MENANG_X'],
            'human_win': hasil['MENANG_O'],
            'draw': hasil['DRAW'],
            'avg_mm_nodes': avg_mm,
            'avg_ab_nodes': avg_ab
        })

    # Tampilkan Tabel Laporan Hasil Uji Coba
    print("\n" + "=" * 80)
    print("TABEL LAPORAN HASIL UJI COBA 5 KALI PERMAINAN (POST-TEST CHALLENGE)")
    print("=" * 80)
    print(f"{'Tingkat Kesulitan':<18} | {'Bot (X)':<8} | {'Pemain (O)':<10} | {'Seri':<6} | {'Rata-rata Node (MM vs AB)':<28}")
    print("-" * 80)
    for row in laporan:
        if row['level'] == 'HARD':
            node_info = f"{row['avg_mm_nodes']:.1f} vs {row['avg_ab_nodes']:.1f} (Hemat!)"
        elif row['level'] == 'MEDIUM':
            node_info = "Depth-Limited (Max Depth 2)"
        else:
            node_info = "1 node (Random Move)"
        print(f"{row['level']:<18} | {row['bot_win']:<8} | {row['human_win']:<10} | {row['draw']:<6} | {node_info:<28}")
    print("=" * 80)
    print("Kesimpulan Laporan:")
    print("1. Level Hard tidak terkalahkan (Unbeatable) dengan Alpha-Beta Pruning.")
    print("2. Alpha-Beta Pruning memangkas node evaluasi secara signifikan dibanding Minimax murni.")
    print("=" * 80 + "\n")


# ------------------------------------------------------------------------------
# ENTRY POINT PROGRAM
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("      STUDI KASUS & POST-TEST PRAKTIKUM AI: TIC-TAC-TOE      ")
    print("=" * 60)
    print("Menu Utama:")
    print("  [1] Main Game Interaktif Manusia vs Bot (3 Tingkat Kesulitan)")
    print("  [2] Jalankan Benchmark Otomatis 5x Permainan (Laporan Praktikum)")
    print("=" * 60)
    menu_choice = input("Pilih menu (1/2) [default: 1]: ").strip()

    if menu_choice == '2':
        run_benchmark_trials(num_games=5)
    else:
        play_game()
