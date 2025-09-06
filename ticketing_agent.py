from flask import Flask, request, jsonify
import math

app = Flask(__name__)

def calculate_distance(customer_loc, concert_loc):
    x1, y1 = customer_loc
    x2, y2 = concert_loc
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def get_latency_points(distance):
    if distance <= 1:
        return 30
    elif distance <= 2:
        return 20
    else:
        return 0

@app.route('/ticketing-agent', methods=['POST'])
def ticketing_agent():
    if request.headers.get('Content-Type') != 'application/json':
        return jsonify({"error": "Content-Type must be application/json"}), 400
    
    data = request.get_json()
    customers = data.get('customers', [])
    concerts = data.get('concerts', [])
    priority = data.get('priority', {})
    
    result = {}
    
    for customer in customers:
        customer_name = customer['name']
        vip_status = customer['vip_status']
        customer_loc = customer['location']
        credit_card = customer['credit_card']
        
        max_points = -1
        best_concert = None
        
        for concert in concerts:
            concert_name = concert['name']
            concert_loc = concert['booking_center_location']
            
            # Calculate points
            points = 0
            if vip_status:
                points += 100
            if credit_card in priority and priority[credit_card] == concert_name:
                points += 50
            distance = calculate_distance(customer_loc, concert_loc)
            points += get_latency_points(distance)
            
            if points > max_points:
                max_points = points
                best_concert = concert_name
        
        result[customer_name] = best_concert
    
    return jsonify(result), 200, {'Content-Type': 'application/json'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)