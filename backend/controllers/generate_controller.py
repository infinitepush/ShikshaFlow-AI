from flask import request, jsonify
from config.config import GENERATE_VIDEO, MAX_SLIDE_SECONDS, MAX_VIDEO_SLIDES
from services.ai_service import AIQuotaError, generate_lecture
from services.slide_service import generate_slides
from services.voice_service import generate_voiceover, combine_audio
from services.video_service import create_video, get_media_duration
from services.quiz_service import generate_quiz
from services.cloud_service import upload_file
from services.database_service import save_lecture_record
from utils.file_utils import convert_pptx_to_images
import json

def generate_assets():
    try:
        print("Received request to generate assets")
        
        # Check if request has JSON data
        if not request.is_json:
            print("Request is not JSON")
            return jsonify({"error": "Request must be JSON"}), 400
            
        data = request.get_json()
        print(f"Request data: {data}")
        
        if data is None:
            print("Invalid JSON data")
            return jsonify({"error": "Invalid JSON data"}), 400
            
        prompt = data.get("prompt")
        theme = data.get("theme", "Minimalist")
        user_email = data.get("user_email")
        print(f"Prompt: {prompt}, Theme: {theme}")

        if not prompt:
            print("Prompt is required")
            return jsonify({"error": "Prompt is required"}), 400

        # 1. Generate AI content
        print("Generating AI content...")
        ai_output_str = generate_lecture(prompt)
        print(f"AI output string: {ai_output_str}")
        
        if not ai_output_str:
            print("Failed to generate AI content")
            return jsonify({"error": "Failed to generate AI content"}), 500
            
        # Clean the AI output string to ensure it's valid JSON
        # Remove any markdown code block markers if present
        ai_output_str = ai_output_str.strip()
        if ai_output_str.startswith("```json"):
            ai_output_str = ai_output_str[7:]
        if ai_output_str.startswith("```"):
            ai_output_str = ai_output_str[3:]
        if ai_output_str.endswith("```"):
            ai_output_str = ai_output_str[:-3]
        ai_output_str = ai_output_str.strip()
        
        print(f"Cleaned AI output string: {ai_output_str}")
        
        ai_output = json.loads(ai_output_str)
        print(f"Parsed AI output: {ai_output}")
        
        # Ensure required keys exist
        if "slides" not in ai_output:
            print("Missing 'slides' in AI output")
            return jsonify({"error": "Missing 'slides' in AI output"}), 500
            
        if "quiz" not in ai_output:
            print("Missing 'quiz' in AI output")
            return jsonify({"error": "Missing 'quiz' in AI output"}), 500
            
        slides = ai_output["slides"]
        quiz = ai_output["quiz"]

        # 2. Generate slides
        print("Generating slides...")
        slides_path = generate_slides(slides, theme)
        print(f"Slides path: {slides_path}")

        # 3. Generate voiceover for each slide
        print("Generating voiceovers...")
        voice_paths = []
        durations = []
        for i, s in enumerate(slides):
            slide_script = s["script"]
            voice_path = f"output/voiceover_{i}.mp3"
            generate_voiceover(slide_script, voice_path)
            voice_paths.append(voice_path)
            duration = get_media_duration(voice_path)
            if duration:
                capped_duration = min(duration, MAX_SLIDE_SECONDS) if GENERATE_VIDEO else duration
                durations.append(capped_duration)
            else:
                durations.append(MAX_SLIDE_SECONDS)

        # Combine voiceovers into a single file
        full_voice_path = "output/voiceover.mp3"
        combine_audio(voice_paths, full_voice_path)
        print(f"Combined voice path: {full_voice_path}")

        slides_upload = upload_file(slides_path, resource_type="raw")
        slides_url = slides_upload["secure_url"] if slides_upload else slides_path

        voice_upload = upload_file(full_voice_path, resource_type="video")
        voice_url = voice_upload["secure_url"] if voice_upload else full_voice_path

        # 4. Convert slides to images for video creation
        print("Converting slides to images...")
        slide_images_result = convert_pptx_to_images(slides_path)
        slide_images_local = slide_images_result["local_paths"]
        slide_images_cloud = slide_images_result["cloud_urls"]
        print(f"Slide images (local): {slide_images_local}")
        print(f"Slide images (cloud): {slide_images_cloud}")

        video_path = None
        video_local_path = None
        if GENERATE_VIDEO:
            print("Creating video with custom durations...")
            video_result = create_video(slide_images_local[:MAX_VIDEO_SLIDES], full_voice_path, durations=durations)

            if isinstance(video_result, dict):
                video_path = video_result["cloud_url"]
                video_local_path = video_result["local_path"]
            else:
                video_path = video_result
                video_local_path = video_result
        else:
            print("Video generation disabled; returning slides, voiceover, and quiz only.")

        # 6. Generate quiz
        print("Generating quiz...")
        quiz_data = generate_quiz(quiz)
        print(f"Quiz data: {quiz_data}")

        # 7. Return final result
        result = {
            "lecture_id": None,
            "user_email": user_email,
            "prompt": prompt,
            "theme": theme,
            "slides_path": slides_path,
            "slides_url": slides_url,
            "voice_path": full_voice_path,
            "voice_url": voice_url,
            "video_path": video_path,
            "video_local_path": video_local_path if 'video_local_path' in locals() else video_path,
            "slide_images": slide_images_cloud,
            "slide_durations": durations,
            "quiz": quiz_data
        }

        lecture_record = save_lecture_record({
            "user_email": user_email,
            "prompt": prompt,
            "theme": theme,
            "slides": slides,
            "quiz": quiz_data,
            "assets": {
                "slides_local_path": slides_path,
                "slides_url": slides_url,
                "voice_local_path": full_voice_path,
                "voice_url": voice_url,
                "video_local_path": video_local_path if 'video_local_path' in locals() else video_path,
                "video_url": video_path,
                "slide_images": slide_images_cloud,
                "slide_durations": durations,
            },
        })
        result["lecture_id"] = lecture_record["id"]

        print(f"Returning result: {result}")
        return jsonify(result)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return jsonify({"error": f"Invalid JSON from AI service: {str(e)}"}), 500
    except AIQuotaError as e:
        print(f"AI quota error: {e}")
        return jsonify({"error": str(e)}), 429
    except Exception as e:
        print(f"Error in generate_assets: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
