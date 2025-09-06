from flask import Flask, request, jsonify
from typing import List, Tuple

app = Flask(__name__)

def calculate_time(intel: List[List[int]], reserve: int, fronts: int, stamina: int) -> int:
    """
    Calculate the minimum time required for Klein to defeat all undeads and be in cooldown state.
    
    Args:
        intel: List of [front, mp_required] pairs
        reserve: Maximum mana reserve
        fronts: Total number of fronts
        stamina: Maximum number of spells before cooldown
    
    Returns:
        Total time in minutes
    """
    current_mana = reserve
    current_stamina = stamina
    total_time = 0
    last_front = None
    
    for i, (front, mp_required) in enumerate(intel):
        # Check if we can extend the previous attack on the same front
        if front == last_front and current_mana >= mp_required and current_stamina > 0:
            # Extend attack on same front (no time cost)
            current_mana -= mp_required
            current_stamina -= 1
        else:
            # Need to launch new attack (10 minutes)
            # First check if we need cooldown
            if current_mana < mp_required or current_stamina <= 0:
                # Cooldown needed (10 minutes)
                total_time += 10
                current_mana = reserve
                current_stamina = stamina
            
            # Launch attack (10 minutes)
            total_time += 10
            current_mana -= mp_required
            current_stamina -= 1
            last_front = front
    
    # Final cooldown to ensure Klein can immediately join expedition
    total_time += 10
    
    return total_time

@app.route('/the-mages-gambit', methods=['POST'])
def the_mages_gambit():
    try:
        data = request.get_json()
        
        if not isinstance(data, list):
            return jsonify({"error": "Expected a list of inputs"}), 400
        
        results = []
        
        for item in data:
            # Validate input
            if not all(key in item for key in ['intel', 'reserve', 'fronts', 'stamina']):
                return jsonify({"error": "Missing required fields"}), 400
            
            intel = item['intel']
            reserve = item['reserve']
            fronts = item['fronts']
            stamina = item['stamina']
            
            # Validate intel data
            for attack in intel:
                if len(attack) != 2:
                    return jsonify({"error": "Each intel item must have exactly 2 values"}), 400
                if not (1 <= attack[0] <= fronts):
                    return jsonify({"error": f"Front must be between 1 and {fronts}"}), 400
                if not (1 <= attack[1] <= reserve):
                    return jsonify({"error": f"MP consumption must be between 1 and {reserve}"}), 400
            
            time = calculate_time(intel, reserve, fronts, stamina)
            results.append({"time": time})
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
