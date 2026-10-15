import heapq

# --- LANGKAH 1: Inisialisasi Graf Berbobot & Tabel Heuristik ---
graph_weighted = {
    'A': {'B': 4, 'C': 2},
    'B': {'A': 4, 'D': 5, 'E': 10},
    'C': {'A': 2, 'E': 3, 'F': 8},
    'D': {'B': 5, 'G': 6},
    'E': {'B': 10, 'C': 3, 'G': 2},
    'F': {'C': 8, 'G': 4},
    'G': {}
}

heuristic = {
    'A': 10,
    'B': 8,
    'C': 5,
    'D': 6,
    'E': 2,
    'F': 3,
    'G': 0
}

print('--- INISIALISASI GRAF BERBOBOT DAN HEURISTIK SELESAI ---\n')


# --- LANGKAH 2: Algoritma Greedy Best-First Search (GBFS) ---
def greedy_bfs(graph, heuristic, start, goal):
    # Priority Queue menyimpan pasangan (h(n), node, path)
    pq = [(heuristic[start], start, [start])]
    visited = set()

    while pq:
        h_val, current, path = heapq.heappop(pq)
        if current in visited:
            continue
        visited.add(current)
        print(f'[Greedy BFS] Eksplorasi Node: {current} | Nilai h(n): {h_val}')

        if current == goal:
            return path, h_val

        for neighbor in graph[current]:
            if neighbor not in visited:
                heapq.heappush(pq, (heuristic[neighbor], neighbor, path + [neighbor]))
    return None, 0

print('=== PENCARIAN GREEDY BFS ===')
path_gbfs, _ = greedy_bfs(graph_weighted, heuristic, 'A', 'G')
print('Jalur Greedy BFS:', ' -> '.join(path_gbfs))
print()


# --- LANGKAH 3: Algoritma A* (A-Star) Search ---
def a_star_search(graph, heuristic, start, goal):
    # Priority Queue menyimpan (f(n), g(n), current_node, path)
    pq = [(heuristic[start], 0, start, [start])]
    visited = {}

    while pq:
        f_val, g_val, current, path = heapq.heappop(pq)
        if current in visited and visited[current] <= g_val:
            continue
        visited[current] = g_val
        print(f'[A* Search] Node: {current} | g(n): {g_val} | h(n): {heuristic[current]} | f(n): {f_val}')

        if current == goal:
            return path, g_val

        for neighbor, weight in graph[current].items():
            new_g = g_val + weight
            new_f = new_g + heuristic[neighbor]
            heapq.heappush(pq, (new_f, new_g, neighbor, path + [neighbor]))
    return None, float('inf')

print('=== PENCARIAN A* SEARCH ===')
path_astar, total_cost = a_star_search(graph_weighted, heuristic, 'A', 'G')
print('Jalur A* Search :', ' -> '.join(path_astar))
print('Total Biaya g(n) :', total_cost)