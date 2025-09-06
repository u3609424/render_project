from flask import Flask, request, jsonify
import re
import os

app = Flask(__name__)

def reverse_mirror_words(x):
    words = x.split()
    return ' '.join(word[::-1] for word in words)

def reverse_encode_mirror_alphabet(x):
    result = []
    for char in x:
        if 'a' <= char <= 'z':
            result.append(chr(219 - ord(char)))
        elif 'A' <= char <= 'Z':
            result.append(chr(155 - ord(char)))
        else:
            result.append(char)
    return ''.join(result)

def reverse_toggle_case(x):
    return x.swapcase()

def reverse_swap_pairs(x):
    words = x.split()
    result = []
    for word in words:
        chars = list(word)
        for i in range(0, len(chars)-1, 2):
            chars[i], chars[i+1] = chars[i+1], chars[i]
        result.append(''.join(chars))
    return ' '.join(result)

def reverse_encode_index_parity(x):
    words = x.split()
    result = []
    for word in words:
        n = len(word)
        mid = (n + 1) // 2
        original = [''] * n
        even_idx = 0
        odd_idx = mid
        for i in range(n):
            if i % 2 == 0:
                original[i] = word[even_idx]
                even_idx += 1
            else:
                original[i] = word[odd_idx]
                odd_idx += 1
        result.append(''.join(original))
    return ' '.join(result)

def reverse_double_consonants(x):
    result = []
    i = 0
    while i < len(x):
        result.append(x[i])
        if x[i].lower() not in 'aeiou' and x[i].isalpha():
            if i+1 < len(x) and x[i] == x[i+1]:
                i += 1
        i += 1
    return ''.join(result)

def solve_challenge_one(transformations, transformed_word):
    reverse_funcs = {
        'mirror_words(x)': reverse_mirror_words,
        'encode_mirror_alphabet(x)': reverse_encode_mirror_alphabet,
        'toggle_case(x)': reverse_toggle_case,
        'swap_pairs(x)': reverse_swap_pairs,
        'encode_index_parity(x)': reverse_encode_index_parity,
        'double_consonants(x)': reverse_double_consonants
    }
    
    current = transformed_word
    for func in reversed(transformations):
        current = reverse_funcs[func](current)
    return current

def solve_challenge_two(coordinates):
    coords = [(float(lat), float(lon)) for lat, lon in coordinates]
    center_lat = sum(lat for lat, lon in coords) / len(coords)
    center_lon = sum(lon for lat, lon in coords) / len(coords)
    distances = [((lat - center_lat)**2 + (lon - center_lon)**2) for lat, lon in coords]
    avg_dist = sum(distances) / len(distances)
    filtered = [i for i, d in enumerate(distances) if d <= avg_dist]
    pattern_coords = [coords[i] for i in filtered]
    pattern_value = int(len(pattern_coords) * 100)
    return str(pattern_value)

def solve_challenge_three(log_entry):
    cipher_type = re.search(r'CIPHER_TYPE: (\w+)', log_entry).group(1)
    payload = re.search(r'ENCRYPTED_PAYLOAD: (\w+)', log_entry).group(1)
    
    if cipher_type == 'RAILFENCE':
        n = len(payload)
        rail = [[None] * n for _ in range(3)]
        dir_down = None
        row, col = 0, 0
        for i in range(n):
            if row == 0:
                dir_down = True
            if row == 2:
                dir_down = False
            rail[row][col] = True
            col += 1
            row += 1 if dir_down else -1
        
        index = 0
        for i in range(3):
            for j in range(n):
                if rail[i][j] and index < n:
                    rail[i][j] = payload[index]
                    index += 1
        
        result = []
        row, col = 0, 0
        for i in range(n):
            if row == 0:
                dir_down = True
            if row == 2:
                dir_down = False
            result.append(rail[row][col])
            col += 1
            row += 1 if dir_down else -1
        return ''.join(result)
    
    elif cipher_type == 'KEYWORD':
        keyword = "SHADOW"
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        key = ''.join(sorted(set(keyword.upper() + alphabet), key=(keyword.upper() + alphabet).index))
        decrypted = []
        for char in payload.upper():
            if char in key:
                idx = key.index(char)
                decrypted.append(alphabet[idx])
            else:
                decrypted.append(char)
        return ''.join(decrypted)
    
    elif cipher_type == 'POLYBIUS':
        polybius = {
            'A': '11', 'B': '12', 'C': '13', 'D': '14', 'E': '15',
            'F': '21', 'G': '22', 'H': '23', 'I': '24', 'J': '24', 'K': '25',
            'L': '31', 'M': '32', 'N': '33', 'O': '34', 'P': '35',
            'Q': '41', 'R': '42', 'S': '43', 'T': '44', 'U': '45',
            'V': '51', 'W': '52', 'X': '53', 'Y': '54', 'Z': '55'
        }
        reverse_polybius = {v: k for k, v in polybius.items()}
        chunks = [payload[i:i+2] for i in range(0, len(payload), 2)]
        return ''.join(reverse_polybius[chunk] for chunk in chunks)
    
    return payload

def solve_challenge_four(ch1, ch2, ch3):
    return f"{ch1}_{ch2}_{ch3}"

@app.route('/operation-safeguard', methods=['POST'])
def operation_safeguard():
    data = request.get_json()
    
    ch1 = solve_challenge_one(
        data['challenge_one']['transformations'],
        data['challenge_one']['transformed_encrypted_word']
    )
    
    ch2 = solve_challenge_two(data['challenge_two'])
    ch3 = solve_challenge_three(data['challenge_three'])
    ch4 = solve_challenge_four(ch1, ch2, ch3)
    
    return jsonify({
        'challenge_one': ch1,
        'challenge_two': ch2,
        'challenge_three': ch3,
        'challenge_four': ch4
    })

if __name__ == '__main__':  
    port = int(os.environ.get('PORT', 5000))  
    app.run(host='0.0.0.0', port=port) 
