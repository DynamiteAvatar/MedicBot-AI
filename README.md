🩺 **MedicBotAI – Detailed Project Explanation**
🎙️ **Frontend (Client-Side)**
The frontend handles everything the user sees and interacts with.

🌐** Language Selection**
Users can select their preferred language for speech input using a dropdown.

The chatbot updates its speech recognition model dynamically based on this choice.

🎤 **Capturing Voice Input**
Uses the Web Speech API to listen to the user’s speech.

Automatically adapts to the selected language.

🎛️ **Mic Button Control**
Start recognition when the user clicks the mic button.

Stop recognition when the user stops speaking or clicks again.

🔗 **Sending Data to Backend**
The function sendSymptomsToBackend() sends the text version of the user’s symptoms to the backend server.

The backend processes the symptoms and returns an AI-generated response.

🔊 **Text-to-Speech (TTS) Output**
Converts the bot’s text replies into spoken audio.

Can be triggered automatically after the bot replies or manually via a speaker icon.

👋 **Greeting the User**
On load, the chatbot greets the user with a TTS welcome message.

🖥️ **Backend (Server-Side)**
The backend is the brain of the application, processing input and generating intelligent responses.

📦 **Importing Flask & Gemini API**
Flask runs the backend server.

Google Gemini API is used to generate AI-based responses.

⚙️ **App Initialization**
Flask app is set up.

Gemini API is configured using a secure API key.

💬 **Calling the Gemini API**
User’s symptom text is sent as a prompt to Gemini.

Gemini returns a structured AI response.

The response is parsed from raw text into usable JSON and sent back to the frontend.

🚨 **Error Handling**
If there’s an error in the code or the Gemini API fails, the system sends an error message back to the user.

📌 **Summary**
MedicBotAI:

🎧 Listens to your voice.

📝 Understands your symptoms.

🧠 Processes them using AI (Gemini API).

💬 Responds in text.

🔊 Speaks the reply back to you.


**THANKS FOR READING**

