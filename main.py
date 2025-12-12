
#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__, static_folder='static', template_folder='templates')

LIBRE_URL = 'https://libretranslate.de/translate'


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/translate', methods=['POST'])
def translate():
	data = request.json or {}
	text = data.get('text', '').strip()
	target = data.get('target', 'fr')
	if not text:
		return jsonify({'error': 'no text provided'}), 400
	try:
		resp = requests.post(LIBRE_URL, data={
			'q': text,
			'source': 'auto',
			'target': target,
			'format': 'text'
		}, timeout=6)
		resp.raise_for_status()
		result = resp.json()
		translated = result.get('translatedText') or result.get('translated_text') or ''
	except Exception:
		# fallback simple transformation when external service fails
		translated = '[fallback] ' + text[::-1]
	return jsonify({'text': translated})


if __name__ == '__main__':
	app.run(debug=True, host='127.0.0.1', port=5000)
