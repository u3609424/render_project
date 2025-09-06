from flask import Flask, request, jsonify, Response
from typing import List
import json

app = Flask(__name__)

def merge_intervals(intervals: List[List[int]]) -> List[List[int]]:
    """
    Part 1: Merge overlapping intervals to find busy periods
    """
    if not intervals:
        return []
    
    # Sort intervals by start time
    intervals.sort(key=lambda x: x[0])
    
    merged = []
    current_start, current_end = intervals[0]
    
    for i in range(1, len(intervals)):
        if intervals[i][0] <= current_end:
            # Overlapping intervals, merge them
            current_end = max(current_end, intervals[i][1])
        else:
            # No overlap, add current interval and start new one
            merged.append([current_start, current_end])
            current_start, current_end = intervals[i]
    
    merged.append([current_start, current_end])
    return merged

def min_boats_needed(intervals: List[List[int]]) -> int:
    """
    Part 2: Find minimum number of boats needed using sweep-line algorithm
    """
    if not intervals:
        return 0
    
    # Create events: (time, +1 for start, -1 for end)
    events = []
    for start, end in intervals:
        events.append((start, 1))
        events.append((end, -1))
    
    # Sort events by time, and for same time, process ends first
    events.sort(key=lambda x: (x[0], x[1]))
    
    max_boats = 0
    current_boats = 0
    
    for time, event_type in events:
        current_boats += event_type
        max_boats = max(max_boats, current_boats)
    
    return max_boats

@app.route('/sailing-club/submission', methods=['POST'])
def sailing_club():
    try:
        data = request.get_json()
        test_cases = data.get('testCases', [])
        
        solutions = []
        
        for test_case in test_cases:
            case_id = test_case['id']
            intervals = test_case['input']
            
            # Part 1: Merge intervals
            merged_slots = merge_intervals(intervals)
            
            # Part 2: Find minimum boats needed
            min_boats = min_boats_needed(intervals)
            
            # Create solution dictionary with ordered entries
            solution = [
                ("id", case_id),
                ("sortedMergedSlots", merged_slots),
                ("minBoatsNeeded", min_boats)
            ]
            
            solutions.append(dict(solution))
        
        # Create the response with ordered keys
        response_data = [("solutions", solutions)]
        
        # Use json.dumps with ensure_ascii=False to maintain order
        response_json = json.dumps(dict(response_data), ensure_ascii=False, indent=2)
        
        return Response(response_json, mimetype='application/json')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
