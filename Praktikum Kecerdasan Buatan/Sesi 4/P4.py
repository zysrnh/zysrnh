# ==============================================================================
# PRAKTIKUM KECERDASAN BUATAN - SESI 4
# GAME TIC-TAC-TOE: ALGORITMA MINIMAX & ALPHA-BETA PRUNING
# Lengkap: Langkah 1, 2, 3, dan Langkah 4 (Game Interaktif + In-Game Restart 'r')
# ==============================================================================
import math

# ------------------------------------------------------------------------------
# LANGKAH 1: INISIALISASI PAPAN & CEK KEMENANGAN
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
# LANGKAH 2: FUNGSI REKURSIF MINIMAX STANDAR
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
                board[i] = ' ' # Backtrack
                best_score = max(score, best_score)
        return best_score
    else:
        best_score = math.inf
        for i in range(9):
            if board[i] == ' ':
                board[i] = 'O'
                score = minimax(board, True)
                board[i] = ' ' # Backtrack
                best_score = min(score, best_score)
        return best_score

def find_best_move(board):
    best_score = -math.inf
    best_move = -1
    for i in range(9):
        if board[i] == ' ':
            board[i] = 'X'
            score = minimax(board, False)
            board[i] = ' ' # Backtrack
            if score > best_score:
                best_score = score
                best_move = i
    return best_move


# ------------------------------------------------------------------------------
# LANGKAH 3: MINIMAX DENGAN ALPHA-BETA PRUNING
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
                board[i] = ' ' # Backtrack
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
                board[i] = ' ' # Backtrack
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
            board[i] = ' ' # Backtrack
            if score > best_score:
                best_score = score
                best_move = i
    return best_move


# ------------------------------------------------------------------------------
# LANGKAH 4: GAME LOOP INTERAKTIF (DENGAN OPSI ULANGI IN-GAME 'r')
# ------------------------------------------------------------------------------
def main_game():
    while True:
        board = [' '] * 9
        print("=" * 55)
        print("🎮 GAME TIC-TAC-TOE: MANUSIA vs AI BOT 🎮")
        print("=" * 55)
        print("Panduan Indeks Petak (0 - 8):")
        print("| 0 | 1 | 2 |")
        print("| 3 | 4 | 5 |")
        print("| 6 | 7 | 8 |")
        print("\nKamu = 'O' (Manusia) | Bot = 'X' (AI Alpha-Beta)")
        print("💡 TIPS: Ketik 'r' kapan saja saat giliranmu untuk ULANGI GAME")
        print("=" * 55 + "\n")

        current_player = 'O' # Manusia mulai duluan
        restart_ingame = False

        while True:
            print_board(board)
            
            # Cek kondisi kemenangan
            winner = check_winner(board)
            if winner:
                print("\n" + "=" * 35)
                if winner == 'DRAW':
                    print("🤝 HASIL AKHIR: GAME SERI (DRAW)!")
                elif winner == 'X':
                    print("🤖 HASIL AKHIR: BOT (X) MENANG!")
                else:
                    print("🎉 HASIL AKHIR: KAMU (O) MENANG!")
                print("=" * 35)
                break

            # Giliran Manusia
            if current_player == 'O':
                user_input = input("\n👉 Giliranmu! Masukkan petak (0-8) atau [r = Ulangi]: ").strip().lower()
                
                # Fitur In-Game Restart: Ulangi kapan saja
                if user_input in ['r', 'reset', 'ulang']:
                    print("\n" + "🔄" * 15)
                    print("🔄 Permainan diulang dari awal oleh pemain!")
                    print("🔄" * 15 + "\n")
                    restart_ingame = True
                    break

                try:
                    move = int(user_input)
                    if move < 0 or move > 8:
                        print("⚠️ Pilihan harus angka 0 sampai 8!")
                        continue
                    if board[move] != ' ':
                        print("⚠️ Petak tersebut sudah terisi, pilih yang kosong!")
                        continue
                    board[move] = 'O'
                    current_player = 'X'
                except ValueError:
                    print("⚠️ Harap masukkan angka 0-8 atau ketik 'r' untuk mengulang!")
            else:
                # Giliran Bot AI
                print("\n🤖 Bot (X) sedang menghitung langkah terbaik...")
                move = find_best_move_ab(board)
                board[move] = 'X'
                print(f"✅ Bot memilih petak indeks: {move}\n")
                current_player = 'O'

        # Jika diulang saat game masih jalan (in-game restart)
        if restart_ingame:
            continue

        # Opsi ulangi setelah game selesai normal
        ulang = input("\n🔄 Mau main lagi? (y/n): ").strip().lower()
        if ulang != 'y':
            print("\n👋 Terima kasih sudah bermain! Sampai jumpa lagi.\n")
            break
        print("\n" + "~" * 55 + "\n")


# Jalankan game interaktif jika dieksekusi langsung
if __name__ == "__main__":
    main_game()
