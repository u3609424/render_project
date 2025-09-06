from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import random
import os

app = Flask(__name__)
CORS(app)

@app.route('/2048.html')
def serve_2048():
    return send_from_directory('.', '2048.html')

class Game2048:
    def __init__(self):
        self.grid = [[0 for _ in range(4)] for _ in range(4)]
        self.score = 0
        self.add_tile()
        self.add_tile()
    
    def add_tile(self):
        empty_cells = [(i, j) for i in range(4) for j in range(4) if self.grid[i][j] == 0]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.grid[i][j] = 2 if random.random() < 0.9 else 4
    
    def move(self, direction):
        moved = False
        
        if direction == 0:  # up
            for j in range(4):
                for i in range(1, 4):
                    if self.grid[i][j] != 0:
                        row = i
                        while row > 0 and self.grid[row-1][j] == 0:
                            self.grid[row-1][j] = self.grid[row][j]
                            self.grid[row][j] = 0
                            row -= 1
                            moved = True
                        if row > 0 and self.grid[row-1][j] == self.grid[row][j]:
                            self.grid[row-1][j] *= 2
                            self.score += self.grid[row-1][j]
                            self.grid[row][j] = 0
                            moved = True
        
        elif direction == 1:  # right
            for i in range(4):
                for j in range(2, -1, -1):
                    if self.grid[i][j] != 0:
                        col = j
                        while col < 3 and self.grid[i][col+1] == 0:
                            self.grid[i][col+1] = self.grid[i][col]
                            self.grid[i][col] = 0
                            col += 1
                            moved = True
                        if col < 3 and self.grid[i][col+1] == self.grid[i][col]:
                            self.grid[i][col+1] *= 2
                            self.score += self.grid[i][col+1]
                            self.grid[i][col] = 0
                            moved = True
        
        elif direction == 2:  # down
            for j in range(4):
                for i in range(2, -1, -1):
                    if self.grid[i][j] != 0:
                        row = i
                        while row < 3 and self.grid[row+1][j] == 0:
                            self.grid[row+1][j] = self.grid[row][j]
                            self.grid[row][j] = 0
                            row += 1
                            moved = True
                        if row < 3 and self.grid[row+1][j] == self.grid[row][j]:
                            self.grid[row+1][j] *= 2
                            self.score += self.grid[row+1][j]
                            self.grid[row][j] = 0
                            moved = True
        
        elif direction == 3:  # left
            for i in range(4):
                for j in range(1, 4):
                    if self.grid[i][j] != 0:
                        col = j
                        while col > 0 and self.grid[i][col-1] == 0:
                            self.grid[i][col-1] = self.grid[i][col]
                            self.grid[i][col] = 0
                            col -= 1
                            moved = True
                        if col > 0 and self.grid[i][col-1] == self.grid[i][col]:
                            self.grid[i][col-1] *= 2
                            self.score += self.grid[i][col-1]
                            self.grid[i][col] = 0
                            moved = True
        
        if moved:
            self.add_tile()
        
        return moved

games = {}

@app.route('/new', methods=['POST'])
def new_game():
    game_id = str(random.randint(100000, 999999))
    games[game_id] = Game2048()
    return jsonify({
        'id': game_id,
        'grid': games[game_id].grid,
        'score': games[game_id].score
    })

@app.route('/move', methods=['POST'])
def move():
    data = request.get_json()
    game_id = data['id']
    direction = data['direction']
    
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]
    moved = game.move(direction)
    
    return jsonify({
        'moved': moved,
        'grid': game.grid,
        'score': game.score
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
