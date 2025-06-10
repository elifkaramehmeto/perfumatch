from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

app = Flask(__name__, static_folder='.')
CORS(app)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/search-results.html')
def search_results():
    return send_from_directory('.', 'search-results.html')

@app.route('/perfume-detail.html')
def perfume_detail():
    return send_from_directory('.', 'perfume-detail.html')

@app.route('/src/<path:filename>')
def src_files(filename):
    return send_from_directory('src', filename)

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'message': 'Simple app working'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 