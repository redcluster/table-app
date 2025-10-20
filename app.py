from flask import Flask, render_template, request, jsonify
import json
import os
import re
from datetime import datetime

app = Flask(__name__)

DATA_DIR = './data/'
DATA_FILE = 'table.json'

default_data = [
    {"row1": "Wert 1", "row2": "Wert 2", "row3": "Wert 3"}
]

ROW_LABEL_MAPPING = {"row1":"Spalte \"Was\"", "row2":"Spalte \"Wer\"", "row3":"Spalte \"Kommentar\""}
MAX_LENGTH = 200

# 0-0, a-z, A-Z, äöüßÄÖÜ, ., -, Whitespace Zeichen (Leerzeichen, Tab & Zeilenumbrüche)
VALID_CHARACTERS_REGEX = re.compile(r'^[0-9a-zA-ZäöüÄÖÜß.,\s-]*$')

@app.route('/favicon.ico')
def favicon():
    return '', 204  # 204 No Content

def load_data():
    if os.path.exists(DATA_DIR + DATA_FILE):
        with open(DATA_DIR + DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # use default file
        with open(DATA_DIR + DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, ensure_ascii=False, indent=4)
        return default_data

def save_data(data):
    with open(DATA_DIR + DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    # save a copy
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    bak_filename = f"{DATA_DIR}{timestamp}_{DATA_FILE}"
    with open(bak_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def validate_data(data):
    for row in data:
        for key, value in row.items():
            if len(value) > MAX_LENGTH:
                return False, f"Fehler: Der Wert in '{key}' darf maximal {MAX_LENGTH} Zeichen enthalten."
            if not VALID_CHARACTERS_REGEX.match(value):
                return False, f"Fehler: Der Wert in {ROW_LABEL_MAPPING[key]} enthält ungültige Zeichen. Nur 0-9, a-z, A-Z, äöüßÄÖÜ, ., -, Leerzeichen und ein Zeilenumbruch sind erlaubt."
    return True, "Daten sind gültig."

@app.route('/')
def index():
    data = load_data()
    return render_template('index.html', data=data)

@app.route('/save', methods=['POST'])
def save():
    new_data = request.json
    
    is_valid, message = validate_data(new_data)
    
    if not is_valid:
        return jsonify({"message": message}), 400

    save_data(new_data)
    return jsonify({"message": "Daten gespeichert!"}), 200

if __name__ == '__main__':
    app.run(debug=False)

