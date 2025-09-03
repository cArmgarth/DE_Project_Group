import os
from flask import Flask, render_template_string

app = Flask(__name__)


@app.route('/')
def home():
    return "GO TEAM TINFOIL!!"

@app.route('/api/status')
def api_status():
    return {"status": "ok", "message": "Flask app is running!"}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)