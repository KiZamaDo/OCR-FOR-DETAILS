from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pytesseract
from PIL import Image
import os
import re
import pandas as pd

# pytesseract.pytesseract.tesseract_cmd = r'Tesseract-OCR\tesseract.exe'
# pytesseract.pytesseract.tesseract_cmd = os.path.join(os.getcwd(), 'Tesseract-OCR', 'tesseract.exe')
pytesseract.pytesseract.tesseract_cmd = "tesseract"

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Define entity unit map and abbreviation map
entity_unit_map = {
    'width': ['kilometer', 'metre', 'yard', 'foot', 'inch', 'centimetre', 'millimetre'],
    'depth': ['kilometer', 'metre', 'yard', 'foot', 'inch', 'centimetre', 'millimetre'],
    'height': ['kilometer', 'metre', 'yard', 'foot', 'inch', 'centimetre', 'millimetre'],
    'item_weight': ['ton', 'kilogram', 'pound', 'ounce', 'gram', 'milligram', 'microgram'],
    'maximum_weight_recommendation': ['ton', 'kilogram', 'pound', 'ounce', 'gram', 'milligram', 'microgram'],
    'voltage': ['kilovolt', 'volt', 'millivolt'],
    'wattage': ['kilowatt', 'watt'],
    'item_volume': ['gallon', 'imperial gallon', 'quart', 'pint', 'cup', 'fluid ounce', 'litre', 'decilitre', 'centilitre',
                    'millilitre', 'microlitre', 'cubic foot', 'cubic inch']
}

abbreviation_map = {
    'cm': 'centimetre',
    'mm': 'millimetre',
    'm': 'metre',
    'ft': 'foot',
    'in': 'inch',
    'kg': 'kilogram',
    'g': 'gram',
    'mg': 'milligram',
    'ug': 'microgram',
    'lb': 'pound',
    'oz': 'ounce',
    'ml': 'millilitre',
    'l': 'litre',
    'cl': 'centilitre',
    'kw': 'kilowatt',
    'v': 'volt',
    'kv': 'kilovolt',
    'mv': 'millivolt',
    'w': 'watt',
    "'": 'foot',   # Single apostrophe for feet
    '"': 'inch'    # Double apostrophe for inches
}

def replace_abbreviations(text):
    if pd.isna(text):
        return text

    # Substitute abbreviations attached to numbers (e.g., "250g" or "10kg")
    for abbr, full_word in abbreviation_map.items():
        text = re.sub(rf'(\d+){abbr}\b', rf'\1 {full_word}', text)

    # Handle standalone abbreviations
    for abbr, full_word in abbreviation_map.items():
        if abbr in ["'", '"']:
            text = text.replace(abbr, full_word)
        else:
            text = re.sub(rf'\b{abbr}\b', full_word, text)

    return text

def extract_value_with_unit(content, entity):
    units = entity_unit_map.get(entity, [])
    for unit in units:
        matches = re.findall(rf'(\d+(?:\.\d+)?)\s*{unit}', content, re.IGNORECASE)
        if matches:
            max_value = max(float(match) for match in matches)
            return f"{max_value} {unit}"
    return None

@app.route('/')
def upload_page():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return jsonify({"error": "No image file found"}), 400

    file = request.files['image']
    entity_name = request.form.get('entity_name')

    if not entity_name or entity_name not in entity_unit_map:
        return jsonify({"error": f"Invalid or missing entity name. Choose from {list(entity_unit_map.keys())}"}), 400

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
     image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
     file.save(image_path)

    try:
        img = Image.open(image_path)
        extracted_text = pytesseract.image_to_string(img)

        # Process the extracted text
        modified_text = replace_abbreviations(extracted_text)
        entity_value = extract_value_with_unit(modified_text, entity_name)

        result = {
            "entity_name": entity_name,
            "entity_value": entity_value or "Not found"
        }

        # Render the result table
        return render_template('result.html', result=result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        os.remove(image_path)  # Cleanup uploaded file


if __name__ == '__main__':
    app.run()


# from flask import Flask, request, render_template, jsonify
# from flask_cors import CORS
# import pytesseract
# from PIL import Image
# import os
# import re
# import pandas as pd

# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


# app = Flask(__name__)
# CORS(app)

# UPLOAD_FOLDER = 'uploads'
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# # Define entity unit map and abbreviation map
# entity_unit_map = {
#     'width': ['kilometer', 'metre', 'yard', 'foot', 'inch', 'centimetre', 'millimetre'],
#     'depth': ['kilometer', 'metre', 'yard', 'foot', 'inch', 'centimetre', 'millimetre'],
#     'height': ['kilometer', 'metre', 'yard', 'foot', 'inch', 'centimetre', 'millimetre'],
#     'item_weight': ['ton', 'kilogram', 'pound', 'ounce', 'gram', 'milligram', 'microgram'],
#     'maximum_weight_recommendation': ['ton', 'kilogram', 'pound', 'ounce', 'gram', 'milligram', 'microgram'],
#     'voltage': ['kilovolt', 'volt', 'millivolt'],
#     'wattage': ['kilowatt', 'watt'],
#     'item_volume': ['gallon', 'imperial gallon', 'quart', 'pint', 'cup', 'fluid ounce', 'litre', 'decilitre', 'centilitre',
#                     'millilitre', 'microlitre', 'cubic foot', 'cubic inch']
# }

# abbreviation_map = {
#     'cm': 'centimetre',
#     'mm': 'millimetre',
#     'm': 'metre',
#     'ft': 'foot',
#     'in': 'inch',
#     'kg': 'kilogram',
#     'g': 'gram',
#     'mg': 'milligram',
#     'ug': 'microgram',
#     'lb': 'pound',
#     'oz': 'ounce',
#     'ml': 'millilitre',
#     'l': 'litre',
#     'cl': 'centilitre',
#     'kw': 'kilowatt',
#     'v': 'volt',
#     'kv': 'kilovolt',
#     'mv': 'millivolt',
#     'w': 'watt',
#     "'": 'foot',
#     '"': 'inch'
# }

# def replace_abbreviations(text):
#     if pd.isna(text):
#         return text

#     for abbr, full_word in abbreviation_map.items():
#         text = re.sub(rf'(\d+){abbr}\b', rf'\1 {full_word}', text)

#     for abbr, full_word in abbreviation_map.items():
#         if abbr in ["'", '"']:
#             text = text.replace(abbr, full_word)
#         else:
#             text = re.sub(rf'\b{abbr}\b', full_word, text)

#     return text

# def extract_value_with_unit(content, entity):
#     units = entity_unit_map.get(entity, [])
#     for unit in units:
#         matches = re.findall(rf'(\d+(?:\.\d+)?)\s*{unit}', content, re.IGNORECASE)
#         if matches:
#             max_value = max(float(match) for match in matches)
#             return f"{max_value} {unit}"
#     return None

# @app.route('/')
# def upload_page():
#     return render_template('index.html')

# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if 'image' not in request.files:
#         return jsonify({"error": "No image file found"}), 400

#     file = request.files['image']
#     entity_name = request.form.get('entity_name')

#     if not entity_name or entity_name not in entity_unit_map:
#         return jsonify({"error": f"Invalid or missing entity name. Choose from {list(entity_unit_map.keys())}"}), 400

#     if file.filename == '':
#         return jsonify({"error": "No selected file"}), 400

#     if file:
#         image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
#         file.save(image_path)

#         try:
#             img = Image.open(image_path)
#             extracted_text = pytesseract.image_to_string(img)

#             # Process the extracted text
#             modified_text = replace_abbreviations(extracted_text)
#             entity_value = extract_value_with_unit(modified_text, entity_name)

#             result = {
#                 "entity_name": entity_name,
#                 "entity_value": entity_value or "Not found"
#             }

#             return render_template('result.html', result=result)
#         except Exception as e:
#             return jsonify({"error": str(e)}), 500
#         finally:
#             os.remove(image_path)  # Cleanup uploaded file

# if __name__ == '__main__':
#     app.run(debug=True)
