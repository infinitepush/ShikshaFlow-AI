from io import BytesIO

from flask import Flask, jsonify, request, send_from_directory
from controllers.generate_controller import generate_assets
from services.auth_service import login_user, signup_user, verify_token
from services.ai_service import (
    generate_chat_response,
    generate_doubt_response,
    generate_notes_summary,
    generate_study_plan,
)
from services.database_service import (
    add_doubt_messages,
    create_doubt_session,
    get_doubt_session,
    list_lecture_records,
    list_doubt_sessions,
)
from config.config import FRONTEND_ORIGINS
from flask_cors import CORS
from pypdf import PdfReader

app = Flask(__name__)
CORS(
    app,
    resources={r"/*": {"origins": FRONTEND_ORIGINS}},
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "OPTIONS"],
)

def get_request_user():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    try:
        return verify_token(auth_header.split(" ", 1)[1])
    except Exception:
        return None

@app.route("/auth/signup", methods=["POST"])
def signup_route():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    if not all([name, email, password]):
        return jsonify({"error": "Missing name, email, or password"}), 400

    try:
        user, token = signup_user(name, email, password)
        return jsonify({"user": user, "token": token}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 409

@app.route("/auth/login", methods=["POST"])
def login_route():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    if not all([email, password]):
        return jsonify({"error": "Missing email or password"}), 400

    try:
        user, token = login_user(email, password)
        return jsonify({"user": user, "token": token})
    except ValueError as e:
        return jsonify({"error": str(e)}), 401

@app.route("/auth/me", methods=["GET"])
def me_route():
    user = get_request_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"user": user})

@app.route("/summarize", methods=["POST"])
def summarize():
    try:
        notes_text = ""

        if 'file' in request.files:
            uploaded_file = request.files['file']
            if uploaded_file.mimetype != "application/pdf":
                return jsonify({"error": "Only PDF files are supported for upload"}), 400

            reader = PdfReader(BytesIO(uploaded_file.read()))
            page_text = [page.extract_text() or "" for page in reader.pages]
            notes_text = "\n\n".join(page_text).strip()

        elif request.is_json:
            data = request.get_json()
            notes_text = (data.get('notes_text') or "").strip()
        else:
            return jsonify({"error": "Invalid request"}), 400

        if not notes_text:
            return jsonify({"error": "No readable notes text found"}), 400

        summary = generate_notes_summary(notes_text)
        return jsonify({"result": {"raw_output": summary}})
    except Exception as e:
        return jsonify({"error": f"Error summarizing notes: {e}"}), 500

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

@app.route("/doubt-sessions", methods=["GET"])
def list_doubts_route():
    request_user = get_request_user()
    user_email = request.args.get("user_email") or (request_user or {}).get("email")
    return jsonify({"sessions": list_doubt_sessions(user_email)})

@app.route("/doubt-sessions", methods=["POST"])
def create_doubt_route():
    data = request.get_json() or {}
    request_user = get_request_user()
    session = create_doubt_session(
        title=data.get("title", "New Doubt Session"),
        user_email=data.get("user_email") or (request_user or {}).get("email"),
    )
    return jsonify({"session": session}), 201

@app.route("/doubt-sessions/<session_id>/messages", methods=["POST"])
def add_doubt_message_route(session_id):
    data = request.get_json() or {}
    question = (data.get("question") or "").strip()

    if not question:
        return jsonify({"error": "Missing question"}), 400

    session = get_doubt_session(session_id)
    if not session:
        return jsonify({"error": "Doubt session not found"}), 404

    mentor_response = generate_doubt_response(session.get("messages", []), question)
    updated_session = add_doubt_messages(session_id, question, mentor_response)
    return jsonify({"session": updated_session, "response": mentor_response})

@app.route("/generate", methods=["OPTIONS"])
@app.route("/generate-study-plan", methods=["OPTIONS"])
@app.route("/chat", methods=["OPTIONS"])
@app.route("/summarize", methods=["OPTIONS"])
@app.route("/doubt-sessions", methods=["OPTIONS"])
@app.route("/doubt-sessions/<session_id>/messages", methods=["OPTIONS"])
@app.route("/auth/signup", methods=["OPTIONS"])
@app.route("/auth/login", methods=["OPTIONS"])
@app.route("/auth/me", methods=["OPTIONS"])
@app.route("/lectures", methods=["OPTIONS"])
def handle_options():
    return '', 200

@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    return send_from_directory('output', filename, as_attachment=True)

@app.route("/media/<filename>", methods=["GET"])
def media_file(filename):
    return send_from_directory('output', filename)

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "message": "Server is running"})

@app.route("/lectures", methods=["GET"])
def list_lectures_route():
    request_user = get_request_user()
    user_email = request.args.get("user_email") or (request_user or {}).get("email")
    return jsonify({"lectures": list_lecture_records(user_email)})

@app.route("/generate", methods=["POST"])
def generate():
    return generate_assets()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
