
#!/usr/bin/env python3
import hashlib
import json
import os
import random

import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__, static_folder='static', template_folder='templates')

# Baidu Translate settings
# You must set the following environment variables before running the app:
# - BAIDU_APPID : your Baidu Translate App ID
# - BAIDU_SECRET : your Baidu Translate Secret Key
BAIDU_APPID = os.environ.get('BAIDU_APPID')
BAIDU_SECRET = os.environ.get('BAIDU_SECRET')
BAIDU_URL = 'https://fanyi-api.baidu.com/api/trans/vip/translate'


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
    from_lang = 'auto'

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
        result = r.json()

        # Log API response
        print(f"Baidu API response: {json.dumps(result, indent=4, ensure_ascii=False)}")

        if 'trans_result' in result:
            dst = '\n'.join([item['dst'] for item in result['trans_result']])
            return jsonify({'text': dst})
        else:
            return jsonify(result), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
