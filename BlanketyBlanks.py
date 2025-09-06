from flask import Flask, request, jsonify
import numpy as np
from scipy.interpolate import UnivariateSpline
from scipy.signal import savgol_filter
import json

app = Flask(__name__)

def impute_series(series):
    """
    Impute missing values in a single series using spline interpolation and Savitzky-Golay
    filtering to handle trends, periodic components, and noise (per rules). Round to 2 decimal
    places. Clip values to prevent exploding predictions and ensure no NaNs/Infs.
    """
    n = len(series)
    x = np.arange(n)
    y = np.array(series, dtype=float)
    mask = ~np.isnan(y)  # Non-null values
    
    # Handle case with fewer than 2 non-null points
    if np.sum(mask) < 2:
        mean_val = np.nanmean(y) if np.sum(mask) > 0 else 0.0
        imputed = [round(mean_val, 2) for _ in range(n)]
        return imputed if not np.any(np.isnan(imputed) | np.isinf(imputed)) else [0.0] * n
    
    x_known = x[mask]
    y_known = y[mask]
    
    # Robust imputation: spline interpolation for smooth trends and periodic patterns
    try:
        spline = UnivariateSpline(x_known, y_known, s=0.5, k=3)
        y_imputed = spline(x)
    except Exception:
        # Fallback to linear interpolation if spline fails
        y_imputed = np.interp(x, x_known, y_known)
    
    # Apply Savitzky-Golay filter for additional smoothing (handles short-memory dependencies)
    try:
        window = min(51, n // 10 * 2 + 1)  # Adaptive window size
        y_imputed = savgol_filter(y_imputed, window_length=window, polyorder=2)
    except Exception:
        pass  # Fallback to spline/linear interpolation if filter fails
    
    # Preserve known values
    y_imputed[mask] = y[mask]
    
    # Stability: clip values to prevent exploding predictions (per rules)
    y_min, y_max = np.min(y_known), np.max(y_known)
    y_range = y_max - y_min if y_max != y_min else 1.0
    y_imputed = np.clip(y_imputed, y_min - 0.5 * y_range, y_max + 0.5 * y_range)
    
    # Ensure no NaNs/Infs and round to 2 decimal places
    y_imputed = np.where(np.isnan(y_imputed) | np.isinf(y_imputed), np.nanmean(y_known) or 0.0, y_imputed)
    return [round(val, 2) for val in y_imputed]

def validate_input(data):
    """
    Validate input: 100 series, 1000 elements each, elements are float or null (per rules).
    """
    try:
        if not data or 'series' not in data:
            return False, "Invalid input: 'series' key missing"
        series_list = data['series']
        if len(series_list) != 100:
            return False, f"Expected 100 series, got {len(series_list)}"
        for i, series in enumerate(series_list):
            if len(series) != 1000:
                return False, f"Series {i}: Expected 1000 elements, got {len(series)}"
            if not all(x is None or isinstance(x, (int, float)) for x in series):
                return False, f"Series {i}: Contains non-numeric or non-null values"
        return True, "Input validation passed"
    except Exception as e:
        return False, f"Input validation error: {str(e)}"

def validate_output(result):
    """
    Validate output: 100 series, 1000 elements each, no nulls, all numeric, no NaNs/Infs (per rules).
    """
    try:
        if "answer" not in result:
            return False, "Missing 'answer' key"
        if len(result["answer"]) != 100:
            return False, f"Expected 100 series, got {len(result['answer'])}"
        for i, series in enumerate(result["answer"]):
            if len(series) != 1000:
                return False, f"Series {i}: Expected 1000 elements, got {len(series)}"
            if any(x is None for x in series):
                return False, f"Series {i}: Contains null values"
            if not all(isinstance(x, (int, float)) for x in series):
                return False, f"Series {i}: Contains non-numeric values"
            if any(np.isnan(x) or np.isinf(x) for x in series):
                return False, f"Series {i}: Contains NaNs or Infs"
        return True, "Output validation passed"
    except Exception as e:
        return False, f"Output validation error: {str(e)}"

def generate_test_input(filename):
    """
    Generate test input with 100 series of 1000 elements, 20% nulls, with trends, periodic
    components, and noise (per rules). Save to filename.
    """
    np.random.seed(42)
    series = []
    for _ in range(100):
        t = np.arange(1000)
        # Linear trend + sinusoidal component + noise
        s = 0.5 * t / 1000 + 0.2 * np.sin(2 * np.pi * t / 50) + np.random.normal(0, 0.05, 1000)
        s = np.round(s, 2)  # Round to 2 decimal places
        # Set 20% of elements to null
        null_indices = np.random.choice(1000, 200, replace=False)
        s[null_indices] = np.nan
        # Convert nans to None for JSON
        s = [None if np.isnan(x) else x for x in s]
        series.append(s)
    
    test_input = {"series": series}
    with open(filename, 'w') as f:
        json.dump(test_input, f, indent=2)
    print(f"Generated test input saved to {filename}")

def test_endpoint(test_input_file):
    """
    Test imputation with user-provided or generated JSON file.
    Input: {"series": [[float or null, ...], ...]} (100 series, 1000 elements each).
    Output: {"answer": [[float, ...], ...]} (100 series, 1000 elements, no nulls).
    Saves output to imputed_output.json. Prints samples per rules.
    """
    try:
        print(f"Loading test data from {test_input_file}...")
        with open(test_input_file, 'r') as f:
            test_input = json.load(f)
        
        # Validate input
        is_valid_input, input_message = validate_input(test_input)
        if not is_valid_input:
            print(f"Input error: {input_message}")
            return False
        
        # Print sample input (first 2 series, first 6 elements each)
        print("\nSample input (first 2 series, first 6 elements each):")
        sample_input = {
            "series": [s[:6] + ["... 1000 elements ..."] for s in test_input["series"][:2]] + ["// 98 more lists"]
        }
        print(json.dumps(sample_input, indent=2))
        
        print("\nRunning imputation...")
        result = []
        for series in test_input["series"]:
            series_np = [np.nan if x is None else x for x in series]
            imputed_series = impute_series(series_np)
            result.append(imputed_series)
        
        output = {"answer": result}
        
        # Validate output
        is_valid_output, output_message = validate_output(output)
        print(f"Output validation: {output_message}")
        
        if is_valid_output:
            # Print sample output (first 2 series, first 6 elements each)
            print("\nSample output (first 2 series, first 6 elements each):")
            sample_output = {
                "answer": [s[:6] + ["... 1000 elements ..."] for s in output["answer"][:2]] + ["// 98 more lists"]
            }
            print(json.dumps(sample_output, indent=2))
            
            # Save full output
            output_file = "imputed_output.json"
            with open(output_file, 'w') as f:
                json.dump(output, f, indent=2)
            print(f"\nFull imputed output saved to {output_file}")
        
        return is_valid_output
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

@app.route('/blankety', methods=['POST'])
def blankety():
    """
    Flask endpoint to process JSON input and return imputed series.
    Input: {"series": [[float or null, ...], ...]} (100 series, 1000 elements each).
    Output: {"answer": [[float, ...], ...]} (100 series, 1000 elements, no nulls).
    """
    try:
        data = request.get_json()
        is_valid_input, input_message = validate_input(data)
        if not is_valid_input:
            return jsonify({'error': input_message}), 400
        
        result = []
        for series in data['series']:
            series_np = [np.nan if x is None else x for x in series]
            imputed_series = impute_series(series_np)
            result.append(imputed_series)
        
        output = {"answer": result}
        is_valid_output, output_message = validate_output(output)
        if not is_valid_output:
            return jsonify({'error': output_message}), 500
        
        return jsonify(output)
    
    except Exception as e:
        return jsonify({'error': f'Processing error: {str(e)}'}), 500

if __name__ == '__main__':
    print("Starting Blankety Blanks server...")
    input_file = "test_input.json"
    generate_test_input(input_file)  # Generate sample input
    test_endpoint(input_file)  # Run test with generated input
    # app.run(debug=False)  # Commented out; use Gunicorn for production
