# app.py
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import time
import os
import google.generativeai as genai
# from dotenv import load_dotenv # Uncomment if you want to load API key from .env file

app = Flask(__name__)
CORS(app)

# --- Configure Gemini API ---
# load_dotenv() # Uncomment if loading from .env
# API_KEY = os.getenv("GEMINI_API_KEY", "") # Load from .env or set a default empty string

# IMPORTANT: Replace "" with your actual Google Gemini API Key.
# If running in a Canvas environment, leave it as "" as it might be auto-injected.
# Otherwise, for local development, you MUST put your key here.
API_KEY = "AIzaSyAICHnXWXTxBgxjoR7vz-MBHQAtMpriKYI" 

if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("Warning: GEMINI_API_KEY not set. Ensure it's provided by the environment or set explicitly in app.py.")
    # Attempt to configure without key for Canvas auto-injection behavior if left empty
    # This might still fail if the environment doesn't provide it and the key is truly missing.
    genai.configure(api_key="")


# --- Gemini Model Configuration ---
GEMINI_MODEL_NAME = "gemini-2.0-flash"

# Define the expected JSON schema for the LLM's response
# This guides the LLM to give structured output for easier parsing
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "diagnosis": {"type": "string", "description": "Likely health condition(s) based on symptoms."},
        "advice": {"type": "string", "description": "General home care tips, common OTC remedies, and disclaimers."},
        "follow_up_questions": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of concise follow-up questions to gather more information."
        },
        "critical_alert": {"type": "boolean", "description": "True if symptoms are critical, false otherwise."},
        "critical_message_en": {"type": "string", "description": "English critical alert message if applicable."},
        "critical_message_hi": {"type": "string", "description": "Hindi critical alert message if applicable."}
    },
    "required": ["diagnosis", "advice", "follow_up_questions", "critical_alert"]
}


# --- Function to interact with Gemini LLM ---
def get_llm_response(symptom_text):
    """
    Sends symptom text to Gemini LLM and gets a structured response.
    """
    try:
        model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        
        # The prompt guides the LLM on what kind of information to provide and in what format.
        prompt = f"""
        You are VoiceDoc AI, a multilingual healthcare assistant for Bharat.
        Analyze the user's symptoms. Drawing upon comprehensive medical knowledge and information typically found on reputable health websites (like WHO, CDC, or national health services), provide a likely diagnosis, comprehensive home care advice (including common, safe over-the-counter remedies and general care tips), and intelligent follow-up questions.
        
        If the symptoms sound critical (e.g., severe breathing difficulty, sudden severe pain, loss of consciousness, persistent high fever in infants, bleeding that won't stop, signs of stroke/heart attack), explicitly set 'critical_alert' to true and provide an emergency message in both English and Hindi. Otherwise, set it to false.

        Strictly adhere to the following JSON schema for your response. Ensure all string values are in plain text, suitable for display. Do NOT include Markdown formatting (like **bold** or *italics*) within the JSON string values, as the frontend will apply it. However, you can use Markdown within the 'response_text' if you generate that separately (but for this structured output, keep it plain).
        
        User Symptoms: "{symptom_text}"
        """
        
        # Configure generation to enforce the JSON schema
        generation_config = genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=RESPONSE_SCHEMA
        )

        response = model.generate_content(prompt, generation_config=generation_config)
        
        # Access the text part of the candidate, which will be a JSON string
        raw_json_string = response.candidates[0].content.parts[0].text
        
        # Parse the JSON string into a Python dictionary
        import json
        parsed_response = json.loads(raw_json_string)
        
        return parsed_response

    except Exception as e:
        # This print statement is crucial for debugging API errors in your terminal
        print(f"Error calling Gemini API: {e}") 
        # Provide a fallback generic error response
        return {
            "diagnosis": "Unable to provide a detailed diagnosis at this moment.",
            "advice": "There was an issue processing your request with the AI. Please try again or consult a doctor. Remember, this AI provides general information and is not a substitute for professional medical advice.",
            "follow_up_questions": [],
            "critical_alert": False,
            "critical_message_en": "",
            "critical_message_hi": ""
        }

# --- Flask Routes ---
@app.route('/')
def index():
    """Serves the main HTML page for the chatbot."""
    # Flask will look for 'index.html' inside the 'templates' folder by default
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """
    API endpoint to receive symptom text, analyze it using LLM, and return a response.
    """
    data = request.get_json()
    symptom_text = data.get('symptom_text', '')

    if not symptom_text:
        return jsonify({
            "response_text": "No symptoms provided. Please tell me how you are feeling.",
            "follow_up_questions": []
        }), 400

    # Simulate processing time for better user experience
    time.sleep(1.5) 
    
    llm_output = get_llm_response(symptom_text)

    # Construct the bot's display message from the LLM's structured output
    bot_response_text = ""
    if llm_output.get("critical_alert"):
        bot_response_text += f"**{llm_output.get('critical_message_en', 'EMERGENCY ALERT')}**\n\n"
        bot_response_text += f"**{llm_output.get('critical_message_hi', 'आपातकालीन चेतावनी')}**\n\n"
        bot_response_text += "Please share your location (e.g., 'My PIN code is 123456') so we can attempt to alert the nearest ASHA worker/PHC if configured."
    else:
        bot_response_text += f"🩺 **Diagnosis:** {llm_output.get('diagnosis', 'Not available.')}\n\n"
        bot_response_text += f"• **Advice:** {llm_output.get('advice', 'No specific advice available.')}\n\n"
        
        # Add general multilingual closing
        bot_response_text += "हम आपको जल्द स्वस्थ होने की कामना करते हैं। (We wish you a speedy recovery.)\n\n"
        bot_response_text += "**Important Disclaimer:** This AI provides general health information and *suggests common over-the-counter remedies only*. It is **not a substitute for professional medical advice, diagnosis, or treatment**. Always consult a qualified healthcare professional before taking any medication or making decisions about your health. If symptoms persist or worsen, seek immediate medical attention."

    return jsonify({
        "response_text": bot_response_text.strip(),
        "follow_up_questions": llm_output.get("follow_up_questions", [])
    })

if __name__ == '__main__':
    app.run(debug=True)
