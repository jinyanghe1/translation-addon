
#!/usr/bin/env python3
import hashlib
import json
import os
import random
import re
from collections import Counter

import requests
from flask import Flask, jsonify, render_template, request

from common_words import COMMON_EN, COMMON_FR

app = Flask(__name__, static_folder='static', template_folder='templates')

# Baidu Translate settings
BAIDU_APPID = os.environ.get('BAIDU_APPID')
BAIDU_SECRET = os.environ.get('BAIDU_SECRET')
BAIDU_URL = 'https://fanyi-api.baidu.com/api/trans/vip/translate'


def call_baidu_api(query, to_lang='zh', from_lang='auto'):
    appid = BAIDU_APPID or '20251212002517999'
    secret = BAIDU_SECRET or 'F7GviUYKor4WV9NkJiKV'

    salt = random.randint(32768, 65536)
    sign = hashlib.md5((appid + query + str(salt) + secret).encode('utf-8')).hexdigest()

    params = {
        'appid': appid,
        'q': query,
        'from': from_lang,
        'to': to_lang,
        'salt': salt,
        'sign': sign
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    try:
        r = requests.post(BAIDU_URL, params=params, headers=headers)
        return r.json()
    except Exception as e:
        return {'error': str(e)}


def is_rare(word):
    # Basic filtering: length > 3, alphabetical
    if len(word) <= 3:
        return False
    if not re.match(r'^[a-zA-Zà-ÿÀ-ß]+$', word):
        return False
    
    w_lower = word.lower()
    # Check against common lists
    if w_lower in COMMON_EN or w_lower in COMMON_FR:
        return False
        
    return True


@app.route('/')
def index():
    return render_template('index.html')


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


@app.route('/translate', methods=['POST', 'OPTIONS'])
def translate():
    if request.method == 'OPTIONS':
        return jsonify({})

    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400

    query = data['text']
    to_lang = data.get('target', 'zh')
    
    result = call_baidu_api(query, to_lang)

    # Log API response
    print(f"Baidu API response: {json.dumps(result, indent=4, ensure_ascii=False)}")

    if 'trans_result' in result:
        dst = '\n'.join([item['dst'] for item in result['trans_result']])
        return jsonify({'text': dst})
    else:
        return jsonify(result), 400


@app.route('/detect', methods=['POST', 'OPTIONS'])
def detect_rare_words():
    if request.method == 'OPTIONS':
        return jsonify({})

    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400

    text = data['text']
    # Simple tokenization
    words = re.findall(r'\b[a-zA-Zà-ÿÀ-ß]+\b', text)
    
    # Filter unique rare words
    unique_words = set()
    rare_candidates = []
    
    for w in words:
        if w.lower() not in unique_words and is_rare(w):
            unique_words.add(w.lower())
            rare_candidates.append(w)
            
    # Limit to top 20 to avoid heavy API usage
    rare_candidates = rare_candidates[:20]
    
    if not rare_candidates:
        return jsonify({'results': []})

    # Batch translate
    # Join with newlines to translate multiple words at once
    query = '\n'.join(rare_candidates)
    res = call_baidu_api(query, to_lang='zh')
    
    results = []
    if 'trans_result' in res:
        for src_res, item in zip(rare_candidates, res['trans_result']):
            # Verify alignment (Baidu usually preserves order but best to be safe)
            # Actually Baidu returns src and dst in items.
            src = item['src']
            dst = item['dst']
            
            # Logic: If translation is same as source (unrecognized), skip
            if src.lower() == dst.lower():
                continue
                
            results.append({'word': src, 'translation': dst})
            
    return jsonify({'results': results})

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
