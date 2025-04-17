from flask import Flask, jsonify
import os

# Create a very simple Flask app for testing
app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "message": "Hello from minimal-app!",
        "service": "Sloane AI Phone Service Backend"
    })

@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "healthy"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)