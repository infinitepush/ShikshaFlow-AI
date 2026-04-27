import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from config.config import GEMINI_API_KEY
import json
import traceback

# Initialize Gemini client
try:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_available = True
    print("Gemini API configured successfully")
except Exception as e:
    print(f"Gemini not configured: {e}")
    gemini_available = False

class AIQuotaError(Exception):
    pass

class AIServiceError(Exception):
    pass

def _clean_json_response(response):
    response = response.strip()
    if response.startswith('```json'):
        return response[7:-3].strip()
    if response.startswith('```'):
        return response[3:-3].strip()
    return response

def _generate_content(full_prompt, fallback_content):
    """Generic helper to generate content from a full prompt using Gemini."""
    if not gemini_available:
        print("Gemini not available, returning fallback content")
        return fallback_content

    preferred_models = [
        'models/gemini-2.5-flash',
        'models/gemini-pro-latest',
    ]
    quota_errors = []
    service_errors = []

    for model_name in preferred_models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(
                full_prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.8,
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=4096
                ),
                safety_settings=[
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"}
                ]
            )
            print(f"Successfully generated content with model: {model_name}")
            return response.text.strip()
        except ResourceExhausted as e:
            quota_errors.append(str(e))
            print(f"Gemini quota exhausted for {model_name}: {str(e)[:160]}...")
        except Exception as e:
            service_errors.append(f"{model_name}: {e}")
            print(f"Model {model_name} failed: {str(e)[:160]}...")

    if quota_errors:
        raise AIQuotaError("Gemini quota is exhausted. Please wait for quota reset or use a key/project with available quota.")

    print(f"Error during content generation: {service_errors}")
    traceback.print_exc()
    raise AIServiceError("Gemini could not generate content right now. Please try again.")

def generate_lecture(prompt):
    """Generates structured lecture JSON from prompt using Gemini."""
    system_prompt = """You are an educational content generator. 
Given a topic, produce structured lecture content.
Requirements:
1. Create 5-7 detailed slide outlines with a title, 2-3 content bullet points, and a CONCISE narration script (10-15 seconds).
2. Generate 3 multiple-choice quiz questions with 4 options and a correct answer.
3. Keep scripts SHORT and PUNCHY.
IMPORTANT: Output ONLY valid JSON with NO markdown formatting.
JSON Structure:
{
    "slides": [{"title": "...", "content": ["..."], "script": "..."}],
    "quiz": [{"question": "...", "options": ["..."], "answer": "..."}]
}"""
    full_prompt = f"{system_prompt}\n\nUSER REQUEST:\n{prompt}"
    fallback_content = '''{
        "slides":[{"title":"Error","content":["Error during content generation"],"script":"Please try again."}],
        "quiz": []
    }'''
    
    response = _generate_content(full_prompt, fallback_content)
    
    try:
        # Clean and validate response
        response = _clean_json_response(response)
        parsed = json.loads(response)
        print(f"Successfully generated lecture with {len(parsed.get('slides', []))} slides and {len(parsed.get('quiz', []))} quiz questions")
    except json.JSONDecodeError:
        print("Failed to parse lecture JSON response.")

    return response

def generate_study_plan(subjects, difficulty, deadline):
    """Generates a structured study plan using Gemini."""
    system_prompt = """You are an AI study planner.
Given subjects, a difficulty level, and a deadline, create a structured 7-day study plan.
IMPORTANT: Output ONLY valid JSON with NO markdown formatting.
JSON Structure:
{
    "subjects": ["..."],
    "difficulty": "...",
    "deadline": "...",
    "plan": [
        {"day": "Monday", "tasks": ["...", "..."]},
        {"day": "Tuesday", "tasks": ["...", "..."]},
        {"day": "Wednesday", "tasks": ["...", "..."]},
        {"day": "Thursday", "tasks": ["...", "..."]},
        {"day": "Friday", "tasks": ["...", "..."]},
        {"day": "Saturday", "tasks": ["...", "..."]},
        {"day": "Sunday", "tasks": ["...", "..."]}
    ]
}"""
    user_prompt = f"Subjects: {subjects}, Difficulty: {difficulty}, Deadline: {deadline}"
    full_prompt = f"{system_prompt}\n\nUSER REQUEST:\n{user_prompt}"
    fallback_content = '''{
        "subjects": [], "difficulty": "", "deadline": "",
        "plan": [{"day": "Error", "tasks": ["Could not generate study plan."]}]
    }'''
    
    response = _generate_content(full_prompt, fallback_content)

    try:
        # Clean and validate response
        response = _clean_json_response(response)
        json.loads(response)
        print("Successfully generated study plan.")
    except json.JSONDecodeError:
        print("Failed to parse study plan JSON response.")
        
    return response

def generate_notes_summary(notes_text):
    """Summarizes notes and creates study aids using Gemini."""
    system_prompt = """You are an expert educational note summarizer.
Given notes text, create concise study material for a student.
IMPORTANT: Output ONLY valid JSON with NO markdown formatting.
JSON Structure:
{
    "summary": ["...", "..."],
    "flashcards": [{"question": "...", "answer": "..."}],
    "glossary": [{"term": "...", "definition": "..."}],
    "concept_map": [{"parent": "...", "children": ["...", "..."]}]
}
Requirements:
1. Summary: 5-8 clear bullet points.
2. Flashcards: 5-8 useful Q&A cards.
3. Glossary: 5-10 key terms with simple definitions.
4. Concept map: 3-6 parent concepts with related children.
5. Keep language student-friendly and accurate."""

    trimmed_notes = notes_text[:18000]
    full_prompt = f"{system_prompt}\n\nNOTES TEXT:\n{trimmed_notes}"
    fallback_content = '''{
        "summary": ["Could not generate a summary. Please try again."],
        "flashcards": [],
        "glossary": [],
        "concept_map": []
    }'''

    response = _generate_content(full_prompt, fallback_content)

    try:
        response = _clean_json_response(response)
        parsed = json.loads(response)
        print("Successfully generated notes summary.")
        return parsed
    except json.JSONDecodeError:
        print("Failed to parse notes summary JSON response.")
        return json.loads(fallback_content)

def generate_chat_response(history, question):
    """Generates a conversational response using Gemini."""
    system_prompt = """You are Shikshak, a friendly and helpful AI tutor. 
Your goal is to help students understand concepts, clarify doubts, and stay motivated.
Keep your answers concise, encouraging, and easy to understand.
Do not generate JSON, just provide a conversational response as a string."""

    # Format the history for the prompt
    formatted_history = "\n".join([f"{msg['sender']}: {msg['text']}" for msg in history])
    
    full_prompt = f"{system_prompt}\n\nCONVERSATION HISTORY:\n{formatted_history}\n\nUSER ASKS:\n{question}"
    fallback_content = "I'm sorry, I'm having a little trouble thinking right now. Please try asking again in a moment."
    
    response = _generate_content(full_prompt, fallback_content)
    print(f"Successfully generated chat response for question: {question}")
    return response

def generate_doubt_response(history, question):
    """Generates a focused tutoring answer for doubt sessions using Gemini."""
    system_prompt = """You are Shikshak, an expert AI doubt-solving tutor.
Help the student understand the concept behind their doubt.
Use clear, friendly explanations.
If useful, include a short example or step-by-step reasoning.
Keep the answer focused and avoid unnecessary length."""

    formatted_history = "\n".join([
        f"{msg.get('sender', 'user')}: {msg.get('text', '')}"
        for msg in history[-8:]
    ])

    full_prompt = f"{system_prompt}\n\nSESSION HISTORY:\n{formatted_history}\n\nSTUDENT DOUBT:\n{question}"
    fallback_content = "I could not generate an answer right now. Please try asking your doubt again."

    response = _generate_content(full_prompt, fallback_content)
    print(f"Successfully generated doubt response for question: {question}")
    return response
