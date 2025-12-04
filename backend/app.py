from flask import Flask, jsonify, request, send_from_directory
from controllers.generate_controller import generate_assets
from services.ai_service import generate_study_plan, generate_chat_response
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

@app.route("/summarize", methods=["POST"])
def summarize():
    summarizer_url = "https://pdf-summarizer-service-1.onrender.com/summarize_notes"
    
    try:
        if 'file' in request.files:
            files = {'file': (request.files['file'].filename, request.files['file'].stream, request.files['file'].mimetype)}
            response = requests.post(summarizer_url, files=files)
            response.raise_for_status()
            return jsonify(response.json()), response.status_code

        elif request.is_json:
            data = request.get_json()
            # The external service expects multipart/form-data for both file and text
            files = {'notes_text': (None, data.get('notes_text'))}
            response = requests.post(summarizer_url, files=files)
            response.raise_for_status()
            return jsonify(response.json()), response.status_code
            
        return jsonify({"error": "Invalid request"}), 400
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error contacting summarizer service: {e}"}), 500

@app.route("/generate-study-plan", methods=['POST'])
def generate_plan_route():
    data = request.get_json()
    subjects = data.get('subjects')
    difficulty = data.get('difficulty')
    deadline = data.get('deadline')
    
    if not all([subjects, difficulty, deadline]):
        return jsonify({"error": "Missing required fields: subjects, difficulty, deadline"}), 400
        
    plan_json_string = generate_study_plan(subjects, difficulty, deadline)
    # The service already returns a stringified JSON, so we can return it directly
    # with the correct content type.
    return app.response_class(response=plan_json_string, status=200, mimetype='application/json')

@app.route('/chat', methods=['POST'])
def chat_route():
    data = request.get_json()
    history = data.get('history', [])
    question = data.get('question')

    if not question:
        return jsonify({"error": "Missing 'question' field"}), 400

    chat_response = generate_chat_response(history, question)
    return jsonify({"response": chat_response})

@app.route("/generate", methods=["OPTIONS"])
@app.route("/generate-study-plan", methods=["OPTIONS"])
@app.route("/chat", methods=["OPTIONS"])
def handle_options():
    return '', 200

@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    return send_from_directory('output', filename, as_attachment=True)

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "message": "Server is running"})

@app.route("/generate", methods=["POST"])
def generate():
    return generate_assets()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)