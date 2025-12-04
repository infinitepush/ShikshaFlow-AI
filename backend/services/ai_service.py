import google.generativeai as genai
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

def _generate_content(full_prompt, fallback_content):
    """Generic helper to generate content from a full prompt using Gemini."""
    if not gemini_available:
        print("Gemini not available, returning fallback content")
        return fallback_content

    try:
        # Try models in order of preference based on confirmed availability
        model = None
        preferred_models = [
            'models/gemini-pro-latest',    # Confirmed available
            'models/gemini-2.5-flash',     # Confirmed available
            'models/gemini-1.5-flash-latest' # A good fallback
        ]
        
        for model_name in preferred_models:
            try:
                model = genai.GenerativeModel(model_name)
                # Quick test to see if model is available
                model.generate_content("test", generation_config=genai.GenerationConfig(max_output_tokens=1))
                print(f"Successfully initialized model: {model_name}")
                break
            except Exception as e:
                print(f"Model {model_name} not available: {str(e)[:100]}...")
                continue
        
        if model is None:
            print("No working model found, returning fallback content")
            return fallback_content

        # Generate content with appropriate settings
        response = model.generate_content(
            full_prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.8, # Slightly more creative for chat
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

        # For chat, we don't need to parse JSON, just return the text
        response_text = response.text.strip()
        return response_text

    except Exception as e:
        print(f"Error during content generation: {e}")
        traceback.print_exc()
        return fallback_content

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
        if response.startswith('```json'):
            response = response[7:-3].strip()
        elif response.startswith('```'):
            response = response[3:-3].strip()
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
        if response.startswith('```json'):
            response = response[7:-3].strip()
        elif response.startswith('```'):
            response = response[3:-3].strip()
        json.loads(response)
        print("Successfully generated study plan.")
    except json.JSONDecodeError:
        print("Failed to parse study plan JSON response.")
        
    return response

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