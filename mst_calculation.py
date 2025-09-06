from flask import Flask, request, jsonify
import cv2
import numpy as np
import base64
from PIL import Image
import io
import os 

app = Flask(__name__)

def preprocess_image(image_data):
    image_bytes = base64.b64decode(image_data.split(',')[-1])
    image = Image.open(io.BytesIO(image_bytes))
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

def detect_nodes(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=10, maxRadius=50)
    return [(int(c[0]), int(c[1])) for c in circles[0]] if circles is not None else []

def extract_weight(region):
    gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if 5 < w < 20 and 10 < h < 25:
            return 1
    return None

def get_edges(image, nodes):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=30, maxLineGap=10)
    graph_edges = []
    
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            dists1 = [np.sqrt((n[0]-x1)*2 + (n[1]-y1)*2) for n in nodes]
            dists2 = [np.sqrt((n[0]-x2)*2 + (n[1]-y2)*2) for n in nodes]
            u, v = np.argmin(dists1), np.argmin(dists2)
            if u != v:
                mx, my = (x1+x2)//2, (y1+y2)//2
                crop = image[max(0,my-20):min(image.shape[0],my+20), max(0,mx-20):min(image.shape[1],mx+20)]
                weight = extract_weight(crop)
                if weight: graph_edges.append((u, v, weight))
    return graph_edges

def kruskal(n, edges):
    edges.sort(key=lambda x: x[2])
    parent = list(range(n))
    def find(x):
        if parent[x] != x: parent[x] = find(parent[x])
        return parent[x]
    weight, count = 0, 0
    for u, v, w in edges:
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[rv] = ru
            weight += w
            count += 1
            if count == n-1: break
    return weight

@app.route('/mst-calculation', methods=['POST'])
def handle_request():
    data = request.get_json()
    results = []
    for case in data['test_cases']:
        img = preprocess_image(case['image'])
        nodes = detect_nodes(img)
        edges = get_edges(img, nodes)
        mst_weight = kruskal(len(nodes), edges)
        results.append({'value': mst_weight})
    return jsonify(results)

if __name__ == '__main__':  
    port = int(os.environ.get('PORT', 5000))  
    app.run(host='0.0.0.0', port=port)
