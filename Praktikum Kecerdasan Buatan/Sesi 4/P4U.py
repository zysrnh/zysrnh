# ==============================================================================
# PRAKTIKUM KECERDASAN BUATAN - SESI 4
# FILE: P4U.py
# TOPIK: Tic-Tac-Toe AI Interaktif (UI/UX Flat, Anti-Slop, Minimal Emoji)
# - Mendukung Google Colab (UI Interaktif Flat Card & Grid)
# - Mendukung Terminal CLI (Fallback Box-Drawing Minimalis)
# - Fitur: 3 Tingkat Kesulitan, Giliran Acak, Undo, Restart, Early Draw, Match History
# ==============================================================================

import sys
import math
import random

# Menjaga kompatibilitas encoding terminal Windows & Colab
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
# 2. KOMPONEN UI/UX GOOGLE COLAB (HTML5, FLAT DESIGN, ZERO SLOP)
# ------------------------------------------------------------------------------
COLAB_UI_HTML = """
<div id="tictactoe-root" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: #0f172a; color: #f8fafc; padding: 24px; border-radius: 4px; border: 1px solid #334155; max-width: 580px; margin: 10px auto; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);">
  
  <!-- Header Minimalis -->
  <div style="border-bottom: 1px solid #334155; padding-bottom: 14px; margin-bottom: 18px; display: flex; justify-content: space-between; align-items: center;">
    <div>
      <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; color: #94a3b8; font-weight: 700;">Praktikum AI - Sesi 4</div>
      <div style="font-size: 20px; font-weight: 700; color: #f8fafc; margin-top: 2px;">TIC-TAC-TOE ENGINE</div>
    </div>
    <div id="status-pill" style="font-size: 11px; font-weight: 600; padding: 4px 10px; background: #1e293b; border: 1px solid #475569; border-radius: 2px; color: #38bdf8;">
      READY
    </div>
  </div>

  <!-- Kontrol Pengaturan: Flat & Presisi -->
  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 18px;">
    <div>
      <label style="font-size: 11px; font-weight: 600; text-transform: uppercase; color: #94a3b8; display: block; margin-bottom: 6px;">Tingkat Kesulitan</label>
      <select id="diff-select" style="width: 100%; background: #1e293b; color: #f8fafc; border: 1px solid #475569; padding: 8px 10px; border-radius: 2px; font-size: 13px; outline: none; cursor: pointer;">
        <option value="easy">Easy (Langkah Acak)</option>
        <option value="medium">Medium (Kedalaman Max 2)</option>
        <option value="hard" selected>Hard (Alpha-Beta / Unbeatable)</option>
      </select>
    </div>
    <div>
      <label style="font-size: 11px; font-weight: 600; text-transform: uppercase; color: #94a3b8; display: block; margin-bottom: 6px;">Giliran Pertama</label>
      <select id="turn-select" style="width: 100%; background: #1e293b; color: #f8fafc; border: 1px solid #475569; padding: 8px 10px; border-radius: 2px; font-size: 13px; outline: none; cursor: pointer;">
        <option value="human">Manusia (O)</option>
        <option value="bot">Bot (X)</option>
        <option value="random">Acak / Random (50:50)</option>
      </select>
    </div>
  </div>

  <!-- Papan 3x3: Solid, Flat, Tanpa Gradient -->
  <div style="display: flex; justify-content: center; margin: 18px 0;">
    <div style="display: grid; grid-template-columns: repeat(3, 90px); grid-template-rows: repeat(3, 90px); gap: 8px; background: #1e293b; padding: 8px; border: 1px solid #334155; border-radius: 4px;">
      <button class="cell-btn" data-idx="0" onclick="userMove(0)"></button>
      <button class="cell-btn" data-idx="1" onclick="userMove(1)"></button>
      <button class="cell-btn" data-idx="2" onclick="userMove(2)"></button>
      <button class="cell-btn" data-idx="3" onclick="userMove(3)"></button>
      <button class="cell-btn" data-idx="4" onclick="userMove(4)"></button>
      <button class="cell-btn" data-idx="5" onclick="userMove(5)"></button>
      <button class="cell-btn" data-idx="6" onclick="userMove(6)"></button>
      <button class="cell-btn" data-idx="7" onclick="userMove(7)"></button>
      <button class="cell-btn" data-idx="8" onclick="userMove(8)"></button>
    </div>
  </div>

  <!-- Status Bar Giliran -->
  <div id="game-message" style="text-align: center; font-size: 13px; font-weight: 600; min-height: 22px; color: #cbd5e1; margin-bottom: 16px;">
    Giliran Pemain: Klik salah satu kotak kosong
  </div>

  <!-- Action Buttons: Flat & Responsif -->
  <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-bottom: 20px;">
    <button onclick="undoMove()" style="background: #334155; color: #f8fafc; border: 1px solid #475569; padding: 10px; font-size: 12px; font-weight: 700; border-radius: 2px; cursor: pointer; text-transform: uppercase;">
      UNDO
    </button>
    <button onclick="restartRound()" style="background: #2563eb; color: #ffffff; border: 1px solid #1d4ed8; padding: 10px; font-size: 12px; font-weight: 700; border-radius: 2px; cursor: pointer; text-transform: uppercase;">
      RESTART
    </button>
    <button onclick="resetStats()" style="background: #1e293b; color: #94a3b8; border: 1px solid #334155; padding: 10px; font-size: 12px; font-weight: 700; border-radius: 2px; cursor: pointer; text-transform: uppercase;">
      RESET SKOR
    </button>
  </div>

  <!-- Rekap Skor -->
  <div style="background: #1e293b; border: 1px solid #334155; border-radius: 2px; padding: 12px; margin-bottom: 16px;">
    <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #94a3b8; font-weight: 700; margin-bottom: 8px;">Statistik Pertandingan</div>
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; text-align: center; font-size: 12px;">
      <div><span style="color: #94a3b8;">Menang</span><div id="score-win" style="font-size: 18px; font-weight: 700; color: #22c55e;">0</div></div>
      <div><span style="color: #94a3b8;">Kalah</span><div id="score-loss" style="font-size: 18px; font-weight: 700; color: #ef4444;">0</div></div>
      <div><span style="color: #94a3b8;">Seri</span><div id="score-draw" style="font-size: 18px; font-weight: 700; color: #f59e0b;">0</div></div>
      <div><span style="color: #94a3b8;">Total</span><div id="score-total" style="font-size: 18px; font-weight: 700; color: #f8fafc;">0</div></div>
    </div>
  </div>

  <!-- Tabel Riwayat Pertandingan -->
  <div style="background: #1e293b; border: 1px solid #334155; border-radius: 2px; padding: 12px;">
    <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #94a3b8; font-weight: 700; margin-bottom: 8px;">Riwayat Pertandingan Terakhir</div>
    <div style="max-height: 140px; overflow-y: auto;">
      <table style="width: 100%; border-collapse: collapse; font-size: 12px; text-align: left;">
        <thead>
          <tr style="border-bottom: 1px solid #334155; color: #94a3b8;">
            <th style="padding: 4px 6px;">Game</th>
            <th style="padding: 4px 6px;">Level</th>
            <th style="padding: 4px 6px;">Awal</th>
            <th style="padding: 4px 6px;">Hasil</th>
            <th style="padding: 4px 6px;">Langkah</th>
          </tr>
        </thead>
        <tbody id="history-body">
          <tr><td colspan="5" style="padding: 10px 6px; text-align: center; color: #64748b;">Belum ada riwayat permainan</td></tr>
        </tbody>
      </table>
    </div>
  </div>

</div>

<style>
  .cell-btn {
    width: 90px;
    height: 90px;
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 2px;
    font-size: 32px;
    font-weight: 700;
    color: #f8fafc;
    cursor: pointer;
    transition: background 0.15s ease, border-color 0.15s ease;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .cell-btn:hover:not(:disabled) {
    background: #1e293b;
    border-color: #64748b;
  }
  .cell-btn:disabled {
    cursor: default;
  }
  .cell-btn.mark-o {
    color: #38bdf8;
  }
  .cell-btn.mark-x {
    color: #f43f5e;
  }
</style>

<script>
(function() {
  let board = Array(9).fill(' ');
  let historyStack = [];
  let currentTurn = 'O';
  let isGameOver = false;
  let moveCount = 0;
  let stats = { win: 0, loss: 0, draw: 0, total: 0 };
  let matchHistory = [];

  const winConditions = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],
    [0, 3, 6], [1, 4, 7], [2, 5, 8],
    [0, 4, 8], [2, 4, 6]
  ];

  function checkWinnerState(b) {
    for (let c of winConditions) {
      if (b[c[0]] !== ' ' && b[c[0]] === b[c[1]] && b[c[1]] === b[c[2]]) {
        return b[c[0]];
      }
    }
    if (!b.includes(' ')) return 'DRAW';

    // Early Draw Detection
    let allBlocked = true;
    for (let c of winConditions) {
      let set = new Set([b[c[0]], b[c[1]], b[c[2]]]);
      if (!(set.has('X') && set.has('O'))) {
        allBlocked = false;
        break;
      }
    }
    if (allBlocked) return 'DRAW';

    return null;
  }

  function minimaxAB(b, depth, alpha, beta, isMax) {
    let w = checkWinnerState(b);
    if (w === 'X') return 10 - depth;
    if (w === 'O') return depth - 10;
    if (w === 'DRAW') return 0;

    let empty = [];
    for (let i = 0; i < 9; i++) if (b[i] === ' ') empty.push(i);

    if (isMax) {
      let maxEval = -Infinity;
      for (let m of empty) {
        b[m] = 'X';
        let ev = minimaxAB(b, depth + 1, alpha, beta, false);
        b[m] = ' ';
        maxEval = Math.max(maxEval, ev);
        alpha = Math.max(alpha, ev);
        if (beta <= alpha) break;
      }
      return maxEval;
    } else {
      let minEval = Infinity;
      for (let m of empty) {
        b[m] = 'O';
        let ev = minimaxAB(b, depth + 1, alpha, beta, true);
        b[m] = ' ';
        minEval = Math.min(minEval, ev);
        beta = Math.min(beta, ev);
        if (beta <= alpha) break;
      }
      return minEval;
    }
  }

  function getBestBotMove(diff) {
    let empty = [];
    for (let i = 0; i < 9; i++) if (board[i] === ' ') empty.push(i);
    if (empty.length === 0) return -1;

    if (diff === 'easy') {
      return empty[Math.floor(Math.random() * empty.length)];
    } else if (diff === 'medium') {
      // Kedalaman maks 2
      let bestS = -Infinity, bestM = empty[0];
      for (let m of empty) {
        board[m] = 'X';
        let s = minimaxAB(board, 2, -Infinity, Infinity, false);
        board[m] = ' ';
        if (s > bestS) { bestS = s; bestM = m; }
      }
      return bestM;
    } else {
      // Hard: Alpha-Beta Penuh
      let bestS = -Infinity, bestM = empty[0];
      for (let m of empty) {
        board[m] = 'X';
        let s = minimaxAB(board, 0, -Infinity, Infinity, false);
        board[m] = ' ';
        if (s > bestS) { bestS = s; bestM = m; }
      }
      return bestM;
    }
  }

  function updateDOM() {
    for (let i = 0; i < 9; i++) {
      let btn = document.querySelector(`.cell-btn[data-idx="${i}"]`);
      if (btn) {
        btn.textContent = board[i] === ' ' ? '' : board[i];
        btn.className = 'cell-btn ' + (board[i] === 'O' ? 'mark-o' : (board[i] === 'X' ? 'mark-x' : ''));
        btn.disabled = board[i] !== ' ' || isGameOver;
      }
    }
  }

  function finalizeGame(winner) {
    isGameOver = true;
    updateDOM();
    let resText = '';
    let pill = document.getElementById('status-pill');
    let msg = document.getElementById('game-message');

    if (winner === 'DRAW') {
      stats.draw++;
      resText = 'Seri (Draw)';
      pill.textContent = 'DRAW';
      pill.style.color = '#f59e0b';
      msg.textContent = 'Hasil Akhir: Seri (Semua garis kemenangan terblokir)';
    } else if (winner === 'X') {
      stats.loss++;
      resText = 'Bot Menang';
      pill.textContent = 'DEFEAT';
      pill.style.color = '#ef4444';
      msg.textContent = 'Hasil Akhir: Bot Menang!';
    } else {
      stats.win++;
      resText = 'Kamu Menang';
      pill.textContent = 'VICTORY';
      pill.style.color = '#22c55e';
      msg.textContent = 'Hasil Akhir: Kamu Menang!';
    }
    stats.total++;

    document.getElementById('score-win').textContent = stats.win;
    document.getElementById('score-loss').textContent = stats.loss;
    document.getElementById('score-draw').textContent = stats.draw;
    document.getElementById('score-total').textContent = stats.total;

    let diff = document.getElementById('diff-select').value.toUpperCase();
    let first = currentTurn === 'O' ? 'Manusia' : 'Bot';
    matchHistory.unshift({
      gameNo: stats.total,
      diff: diff,
      first: first,
      res: resText,
      moves: moveCount
    });

    renderHistory();
  }

  function renderHistory() {
    let tbody = document.getElementById('history-body');
    if (!tbody) return;
    if (matchHistory.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" style="padding: 10px 6px; text-align: center; color: #64748b;">Belum ada riwayat permainan</td></tr>';
      return;
    }
    tbody.innerHTML = matchHistory.slice(0, 5).map(m => `
      <tr style="border-bottom: 1px solid #334155; color: #e2e8f0;">
        <td style="padding: 5px 6px; font-weight: 600;">#${m.gameNo}</td>
        <td style="padding: 5px 6px; color: #94a3b8;">${m.diff}</td>
        <td style="padding: 5px 6px; color: #94a3b8;">${m.first}</td>
        <td style="padding: 5px 6px; font-weight: 600; color: ${m.res.includes('Kamu') ? '#22c55e' : (m.res.includes('Bot') ? '#ef4444' : '#f59e0b')};">${m.res}</td>
        <td style="padding: 5px 6px; color: #94a3b8;">${m.moves}</td>
      </tr>
    `).join('');
  }

  window.userMove = function(idx) {
    if (isGameOver || board[idx] !== ' ') return;

    historyStack.push([...board]);
    board[idx] = 'O';
    moveCount++;
    updateDOM();

    let w = checkWinnerState(board);
    if (w) { finalizeGame(w); return; }

    document.getElementById('game-message').textContent = 'Bot sedang berpikir...';
    document.getElementById('status-pill').textContent = 'BOT TURN';
    document.getElementById('status-pill').style.color = '#f43f5e';

    setTimeout(() => {
      let diff = document.getElementById('diff-select').value;
      let bMove = getBestBotMove(diff);
      if (bMove !== -1) {
        board[bMove] = 'X';
        moveCount++;
        updateDOM();
      }

      let w2 = checkWinnerState(board);
      if (w2) {
        finalizeGame(w2);
      } else {
        document.getElementById('game-message').textContent = 'Giliranmu: Pilih kotak kosong (O)';
        document.getElementById('status-pill').textContent = 'YOUR TURN';
        document.getElementById('status-pill').style.color = '#38bdf8';
      }
    }, 120);
  };

  window.undoMove = function() {
    if (historyStack.length === 0 || isGameOver) return;
    board = historyStack.pop();
    moveCount = Math.max(0, moveCount - 2);
    isGameOver = false;
    document.getElementById('status-pill').textContent = 'YOUR TURN';
    document.getElementById('status-pill').style.color = '#38bdf8';
    document.getElementById('game-message').textContent = 'Langkah terakhir dibatalkan (Undo)';
    updateDOM();
  };

  window.restartRound = function() {
    board = Array(9).fill(' ');
    historyStack = [];
    isGameOver = false;
    moveCount = 0;

    let turnChoice = document.getElementById('turn-select').value;
    let starter = 'O';
    if (turnChoice === 'bot') starter = 'X';
    else if (turnChoice === 'random') starter = Math.random() < 0.5 ? 'O' : 'X';

    updateDOM();

    if (starter === 'X') {
      document.getElementById('status-pill').textContent = 'BOT FIRST';
      document.getElementById('status-pill').style.color = '#f43f5e';
      document.getElementById('game-message').textContent = 'Bot melangkah pertama...';
      setTimeout(() => {
        let diff = document.getElementById('diff-select').value;
        let bMove = getBestBotMove(diff);
        if (bMove !== -1) {
          board[bMove] = 'X';
          moveCount++;
          updateDOM();
        }
        document.getElementById('status-pill').textContent = 'YOUR TURN';
        document.getElementById('status-pill').style.color = '#38bdf8';
        document.getElementById('game-message').textContent = 'Giliranmu: Pilih kotak kosong (O)';
      }, 150);
    } else {
      document.getElementById('status-pill').textContent = 'YOUR TURN';
      document.getElementById('status-pill').style.color = '#38bdf8';
      document.getElementById('game-message').textContent = 'Giliranmu jalan pertama: Pilih kotak (O)';
    }
  };

  window.resetStats = function() {
    stats = { win: 0, loss: 0, draw: 0, total: 0 };
    matchHistory = [];
    document.getElementById('score-win').textContent = '0';
    document.getElementById('score-loss').textContent = '0';
    document.getElementById('score-draw').textContent = '0';
    document.getElementById('score-total').textContent = '0';
    renderHistory();
  };

  // Mulai game awal
  window.restartRound();
})();
</script>
"""


# ------------------------------------------------------------------------------
# 3. RUNNER: DETEKSI OTOMATIS (GOOGLE COLAB vs TERMINAL CLI)
# ------------------------------------------------------------------------------
def display_ui():
    """Menampilkan UI Web Flat di Google Colab jika didukung, atau fallback ke CLI."""
    try:
        from IPython.display import HTML, display
        display(HTML(COLAB_UI_HTML))
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
    print("  1. Manusia (O)")
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
