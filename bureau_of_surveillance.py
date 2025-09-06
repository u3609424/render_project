from collections import defaultdict
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

def find_extra_channels(network):
    graph = defaultdict(list)
    edges = []
    spy_set = set()
    
    for connection in network:
        spy1, spy2 = connection['spy1'], connection['spy2']
        graph[spy1].append(spy2)
        graph[spy2].append(spy1)
        edges.append((spy1, spy2))
        spy_set.update([spy1, spy2])
    
    visited = set()
    parent = {}
    cycle_edges = set()
    
    def dfs(node, par):
        visited.add(node)
        parent[node] = par
        
        for neighbor in graph[node]:
            if neighbor == par:
                continue
            if neighbor in visited:
                cycle_nodes = set()
                current = node
                while current != neighbor:
                    cycle_nodes.add(current)
                    current = parent[current]
                cycle_nodes.add(neighbor)
                
                for edge in edges:
                    u, v = edge
                    if u in cycle_nodes and v in cycle_nodes:
                        cycle_edges.add((min(u, v), max(u, v)))
            else:
                dfs(neighbor, node)
    
    for spy in spy_set:
        if spy not in visited:
            dfs(spy, None)
    
    extra_channels = []
    for edge in cycle_edges:
        u, v = edge
        extra_channels.append({"spy1": u, "spy2": v})
    
    return extra_channels

@app.route('/investigate', methods=['POST'])
def investigate():
    data = request.get_json()
    networks = data.get('networks', [])
    
    result_networks = []
    
    for network_data in networks:
        network_id = network_data['networkId']
        network_connections = network_data['network']
        
        extra_channels = find_extra_channels(network_connections)
        
        result_networks.append({
            "networkId": network_id,
            "extraChannels": extra_channels
        })
    
    return jsonify({"networks": result_networks})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
