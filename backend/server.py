from flow import analyze
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/analyze', methods=['POST'])
def analyze_project():
    try:
        return jsonify(analyze(request.files["project_zip_folder"].read()))
    except Exception as exception:
        return jsonify({"error": str(exception)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)




