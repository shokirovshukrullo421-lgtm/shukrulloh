class Graph:
    def __init__(self, graph):
        self.graph = graph
        self.n = len(graph)

    # 1) Yo‘l topish (DFS ishlatamiz)
    def dfs(self, s, t, parent, visited):
        visited[s] = True
        if s == t:
            return True

        for v in range(self.n):
            if not visited[v] and self.graph[s][v] > 0:
                parent[v] = s
                if self.dfs(v, t, parent, visited):
                    return True
        return False

    # Ford–Fulkerson, har bir qadamni print qiladi
    def ford_fulkerson(self, source, sink):
        parent = [-1] * self.n
        max_flow = 0
        step = 1

        while True:
            visited = [False] * self.n

            # 1) Yo‘l top
            if not self.dfs(source, sink, parent, visited):
                break  # Yo‘l qolmadi

            # 2) Yo‘ldagi sonlarni yoz va 3) Eng kichigini ol
            path_flow = float('inf')
            v = sink
            path = []
            while v != source:
                u = parent[v]
                path_flow = min(path_flow, self.graph[u][v])  # minimal sig‘im
                path.append(v)
                v = u
            path.append(source)
            path.reverse()

            print(f"\n{step}-qadam")
            print("Topilgan yo‘l:", path)          # 2) Yo‘lni chiqar
            print("Minimal sig‘im:", path_flow)     # 3) Eng kichigi

            # 4) Oldinga AYIR va 5) Orqaga QO‘SH
            v = sink
            while v != source:
                u = parent[v]
                self.graph[u][v] -= path_flow  # oldinga ayir
                self.graph[v][u] += path_flow  # orqaga qo‘sh
                v = u

            max_flow += path_flow
            step += 1  # keyingi qadamga o‘t

        print("\nMaksimal oqim topildi!")
        return max_flow


# === TEST GRAF ===
graph = [
    [0, 16, 13, 0, 0],
    [0, 0, 10, 12, 0],
    [0, 4, 0, 0, 14],
    [0, 0, 9, 0, 0],
    [0, 0, 0, 7, 0]
]

g = Graph(graph)
print("Maksimal oqim =", g.ford_fulkerson(0, 5))