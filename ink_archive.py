from flask import Flask, request, jsonify
import math
import os

app = Flask(__name__)

def find_cycle(goods, rates):
    n = len(goods)
    graph = [[0] * n for _ in range(n)]
    
    for i in range(n):
        for j in range(n):
            if i != j and rates[i][j] > 0:
                graph[i][j] = -math.log(rates[i][j])
    
    distance = [float('inf')] * n
    predecessor = [-1] * n
    distance[0] = 0
    
    for _ in range(n - 1):
        for u in range(n):
            for v in range(n):
                if graph[u][v] != 0 and distance[u] + graph[u][v] < distance[v]:
                    distance[v] = distance[u] + graph[u][v]
                    predecessor[v] = u
    
    for u in range(n):
        for v in range(n):
            if graph[u][v] != 0 and distance[u] + graph[u][v] < distance[v]:
                cur = u
                for _ in range(n):
                    cur = predecessor[cur]
                
                start = cur
                cycle_nodes = []
                while True:
                    cycle_nodes.append(cur)
                    cur = predecessor[cur]
                    if cur == start and len(cycle_nodes) > 1:
                        break
                
                cycle_nodes.reverse()
                cycle = [goods[i] for i in cycle_nodes]
                product = 1.0
                for i in range(len(cycle_nodes)):
                    u_idx = goods.index(cycle[i])
                    v_idx = goods.index(cycle[(i + 1) % len(cycle_nodes)])
                    product *= rates[u_idx][v_idx]
                
                return cycle, product - 1.0
    
    return None, 0.0

def find_best_cycle(goods, rates):
    n = len(goods)
    best_cycle = None
    best_gain = 0.0
    
    for start in range(n):
        log_rates = [[0.0] * n for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                if rates[i][j] > 0:
                    log_rates[i][j] = -math.log(rates[i][j])
                else:
                    log_rates[i][j] = float('inf')
        
        dist = [[0.0] * n for _ in range(n)]
        next_node = [[-1] * n for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                dist[i][j] = log_rates[i][j]
                if log_rates[i][j] < float('inf'):
                    next_node[i][j] = j
        
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if dist[i][k] + dist[k][j] < dist[i][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
                        next_node[i][j] = next_node[i][k]
        
        for i in range(n):
            if dist[i][i] < 0:
                cycle = []
                cur = i
                visited = set()
                while cur not in visited:
                    visited.add(cur)
                    cur = next_node[cur][i]
                
                start = cur
                cycle_nodes = [start]
                next_val = next_node[start][i]
                
                while next_val != start:
                    cycle_nodes.append(next_val)
                    next_val = next_node[next_val][i]
                
                cycle_nodes.append(start)
                
                product = 1.0
                for j in range(len(cycle_nodes) - 1):
                    u = cycle_nodes[j]
                    v = cycle_nodes[j + 1]
                    product *= rates[u][v]
                
                gain = product - 1.0
                if gain > best_gain:
                    best_gain = gain
                    best_cycle = [goods[idx] for idx in cycle_nodes]
    
    return best_cycle, best_gain

@app.route('/The-Ink-Archive', methods=['POST'])
def solve():
    data = request.get_json()
    challenges = data.get('challenges', [])
    
    results = []
    
    for challenge in challenges:
        goods = challenge.get('goods', [])
        rates = challenge.get('rates', [])
        
        if len(challenges) == 1:
            cycle, gain = find_cycle(goods, rates)
        else:
            cycle, gain = find_best_cycle(goods, rates)
        
        if cycle:
            results.append({
                'path': cycle,
                'gain': gain * 100
            })
        else:
            results.append({
                'path': [],
                'gain': 0.0
            })
    
    return jsonify(results)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
