from flask import Flask, request, jsonify
import re
import os  

app = Flask(__name__)

class DuolingoSorter:
    def __init__(self):
        self.roman_map = {'I':1,'V':5,'X':10,'L':50,'C':100,'D':500,'M':1000}
        self.english_words = {'zero':0,'one':1,'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,'eight':8,'nine':9,'ten':10,'eleven':11,'twelve':12,'thirteen':13,'fourteen':14,'fifteen':15,'sixteen':16,'seventeen':17,'eighteen':18,'nineteen':19,'twenty':20,'thirty':30,'forty':40,'fifty':50,'sixty':60,'seventy':70,'eighty':80,'ninety':90,'hundred':100,'thousand':1000,'million':1000000}
        self.german_words = {'null':0,'eins':1,'zwei':2,'drei':3,'vier':4,'fünf':5,'sechs':6,'sieben':7,'acht':8,'neun':9,'zehn':10,'elf':11,'zwölf':12,'dreizehn':13,'vierzehn':14,'fünfzehn':15,'sechzehn':16,'siebzehn':17,'achtzehn':18,'neunzehn':19,'zwanzig':20,'dreißig':30,'vierzig':40,'fünfzig':50,'sechzig':60,'siebzig':70,'achtzig':80,'neunzig':90,'hundert':100,'tausend':1000,'million':1000000}
        self.chinese_digits = {'零':0,'〇':0,'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10,'百':100,'千':1000,'万':10000,'億':100000000,'亿':100000000}
        self.language_order = ['roman','english','traditional_chinese','simplified_chinese','german','arabic']

    def roman_to_int(self, s):
        total, prev = 0, 0
        for char in reversed(s):
            val = self.roman_map[char]
            total += -val if val < prev else val
            prev = val
        return total

    def parse_word_number(self, text, word_map):
        total = current = 0
        for word in text.lower().replace('-',' ').replace('und',' ').split():
            if word in word_map:
                val = word_map[word]
                if val in [100,1000,1000000]:
                    total += (current or 1) * val
                    current = 0
                else:
                    current += val
        return total + current

    def parse_chinese_number(self, text):
        total = current = last_mult = 1
        for char in reversed(text):
            if char in self.chinese_digits:
                val = self.chinese_digits[char]
                if val >= 10:
                    if val in [10000,100000000]:
                        total += current * last_mult
                        current, last_mult = 0, val
                    else:
                        last_mult = val
                        if current == 0: current = 1
                else:
                    current += val * last_mult
                    last_mult = 1
        return total + current * last_mult

    def detect_language(self, text):
        if re.match(r'^\d+$', text): return 'arabic'
        if re.match(r'^[IVXLCDM]+$', text.upper()): return 'roman'
        if any(word in text.lower() for word in self.english_words): return 'english'
        if any(word in text.lower() for word in self.german_words): return 'german'
        if any(char in text for char in self.chinese_digits):
            return 'traditional_chinese' if '億' in text else 'simplified_chinese'
        return 'unknown'

    def convert_to_number(self, text):
        lang = self.detect_language(text)
        if lang == 'arabic': return int(text)
        if lang == 'roman': return self.roman_to_int(text.upper())
        if lang == 'english': return self.parse_word_number(text, self.english_words)
        if lang == 'german': return self.parse_word_number(text, self.german_words)
        if lang in ['traditional_chinese','simplified_chinese']: return self.parse_chinese_number(text)
        return int(text) if text.isdigit() else 0

    def sort_part_one(self, lst):
        return [str(self.roman_to_int(x) if x.isalpha() else int(x)) for x in sorted(lst, key=lambda x: self.roman_to_int(x) if x.isalpha() else int(x))]

    def sort_part_two(self, lst):
        items = []
        for item in lst:
            num_val = self.convert_to_number(item)
            lang = self.detect_language(item)
            lang_prio = self.language_order.index(lang) if lang in self.language_order else 999
            items.append((num_val, lang_prio, item))
        return [x[2] for x in sorted(items, key=lambda x: (x[0], x[1]))]

@app.route('/duolingo-sort', methods=['POST'])
def handle_request():
    data = request.get_json()
    part = data.get('part')
    unsorted_list = data.get('challengeInput', {}).get('unsortedList', [])
    sorter = DuolingoSorter()
    
    if part == "ONE":
        sorted_list = sorter.sort_part_one(unsorted_list)
    elif part == "TWO":
        sorted_list = sorter.sort_part_two(unsorted_list)
    else:
        return jsonify({'error': 'Invalid part'}), 400
        
    return jsonify({'sortedList': sorted_list})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  
    app.run(host='0.0.0.0', port=port)  
