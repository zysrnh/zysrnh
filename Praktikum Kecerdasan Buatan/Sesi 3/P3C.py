import heapq

# ==============================================================================
# STUDI KASUS: Navigasi Rute Logistik Pintar Kota Bandung
# Titik Awal: 'S' (Gudang Utama)
# Titik Tujuan: 'GOAL' (Pusat Distribusi)
# ==============================================================================

# 1. Definisi Graf Berbobot Riil g(n)
graph_weighted = {
    'S': {'A': 3, 'B': 2},
    'A': {'C': 4, 'D': 1},
    'B': {'D': 2, 'E': 3},
    'C': {'GOAL': 2},
    'D': {'GOAL': 5},
    'E': {'GOAL': 2},
    'GOAL': {}
}

# 2. Tabel Estimasi Jarak Garis Lurus h(n)
heuristic = {
    'S': 7,
    'A': 5,
    'B': 4,
    'C': 2,
    'D': 4,
    'E': 2,
    'GOAL': 0
}


# --- ALGORITMA 1: Greedy Best-First Search (GBFS) ---
def greedy_bfs(graph, heuristic, start, goal):
    # Priority Queue menyimpan (h(n), g(n), current_node, path)
    pq = [(heuristic[start], 0, start, [start])]
    visited = set()

    print("--- Proses Eksplorasi Greedy BFS ---")
    while pq:
        h_val, g_val, current, path = heapq.heappop(pq)
        if current in visited:
            continue
        visited.add(current)
        print(f"[Greedy BFS] Eksplorasi Node: {current:<4} | Nilai h(n): {h_val}")

        if current == goal:
            return path, g_val

        for neighbor, weight in graph[current].items():
            if neighbor not in visited:
                heapq.heappush(pq, (heuristic[neighbor], g_val + weight, neighbor, path + [neighbor]))
    return None, 0


# --- ALGORITMA 2: A* (A-Star) Search ---
def a_star_search(graph, heuristic, start, goal):
    # Priority Queue menyimpan (f(n), g(n), current_node, path)
    pq = [(heuristic[start], 0, start, [start])]
    visited = {}

    print("--- Proses Eksplorasi A* Search ---")
    while pq:
        f_val, g_val, current, path = heapq.heappop(pq)
        if current in visited and visited[current] <= g_val:
            continue
        visited[current] = g_val
        print(f"[A* Search]  Node: {current:<4} | g(n): {g_val} | h(n): {heuristic[current]} | f(n): {f_val}")

        if current == goal:
            return path, g_val

        for neighbor, weight in graph[current].items():
            new_g = g_val + weight
            new_f = new_g + heuristic[neighbor]
            heapq.heappush(pq, (new_f, new_g, neighbor, path + [neighbor]))
    return None, float('inf')


# ==============================================================================
# EKSEKUSI & PERHITUNGAN BIAYA RIIL g(n)
# ==============================================================================
print("=" * 55)
print("HASIL PENCARIAN RUTE LOGISTIK PINTAR KOTA BANDUNG")
print("=" * 55)

# Eksekusi Greedy BFS
path_gbfs, cost_gbfs = greedy_bfs(graph_weighted, heuristic, 'S', 'GOAL')
print("\n> Hasil Akhir Greedy BFS:")
print(f"  Rute Terbentuk        : {' -> '.join(path_gbfs)}")
print(f"  Total Biaya Riil g(n) : {cost_gbfs}")
print("-" * 55)

# Eksekusi A* Search
path_astar, cost_astar = a_star_search(graph_weighted, heuristic, 'S', 'GOAL')
print("\n> Hasil Akhir A* Search:")
print(f"  Rute Terbentuk        : {' -> '.join(path_astar)}")
print(f"  Total Biaya Riil g(n) : {cost_astar}")
print("=" * 55)