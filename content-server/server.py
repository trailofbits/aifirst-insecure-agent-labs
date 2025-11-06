"""
Simple Flask server for serving test content pages
"""
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import os
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PAGES_DIR = os.path.join(os.path.dirname(__file__), 'pages')


@app.route('/')
def index():
    """List available pages"""
    pages = []
    if os.path.exists(PAGES_DIR):
        for filename in os.listdir(PAGES_DIR):
            if filename.endswith('.html'):
                pages.append(filename.replace('.html', ''))

    return jsonify({
        'message': 'Content Server',
        'pages': pages,
        'endpoints': {
            'page': '/page/<name>',
            'health': '/health'
        }
    })


@app.route('/page/<page_name>')
def serve_page(page_name):
    """Serve a specific page"""
    try:
        logger.info(f"Serving page: {page_name}")
        return send_from_directory(PAGES_DIR, f'{page_name}.html')
    except FileNotFoundError:
        return jsonify({'error': 'Page not found'}), 404


@app.route('/health')
def health():
    """Health check"""
    return jsonify({'status': 'healthy'})


@app.route('/api/page/<page_name>', methods=['GET'])
def get_page_content(page_name):
    """Get raw HTML content of a page"""
    try:
        file_path = os.path.join(PAGES_DIR, f'{page_name}.html')

        # Security: prevent directory traversal
        if '..' in page_name or '/' in page_name:
            return jsonify({'error': 'Invalid page name'}), 400

        if not os.path.exists(file_path):
            return jsonify({'error': 'Page not found'}), 404

        with open(file_path, 'r') as f:
            content = f.read()

        return jsonify({'content': content})
    except Exception as e:
        logger.error(f"Error reading page {page_name}: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/page/<page_name>', methods=['PUT'])
def update_page_content(page_name):
    """Update page content"""
    try:
        # Security: prevent directory traversal
        if '..' in page_name or '/' in page_name:
            return jsonify({'error': 'Invalid page name'}), 400

        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({'error': 'Content is required'}), 400

        file_path = os.path.join(PAGES_DIR, f'{page_name}.html')

        with open(file_path, 'w') as f:
            f.write(data['content'])

        logger.info(f"Updated page: {page_name}")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error updating page {page_name}: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('CONTENT_SERVER_PORT', 8181))
    app.run(host='0.0.0.0', port=port, debug=False)
