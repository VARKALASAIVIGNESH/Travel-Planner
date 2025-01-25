from flask import Flask, render_template, request, jsonify, send_file, session
import requests
import io

app = Flask(__name__)

# API Configuration
API_URL = "https://api.groq.com/openai/v1/chat/completions"
API_KEY = "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"  # Replace with your actual API key

# Home Route
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        destination = request.form.get('destination')
        budget = request.form.get('budget')
        duration = request.form.get('duration')
        preferences = request.form.get('preferences')

        prompt = (
            f"Create a detailed {duration}-day itinerary for a trip to {destination} with a {budget} budget. "
            f"Focus on activities, dining, and preferences: {preferences}."
        )
        payload = {
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}]
        }

        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        response = requests.post(API_URL, json=payload, headers=headers)

        if response.status_code == 200:
            itinerary = response.json().get("choices")[0].get("message").get("content")
            # Store the itinerary in the session to use later for downloading
            session['itinerary'] = itinerary
            return render_template('index.html', itinerary=itinerary, destination=destination)
        else:
            error_message = response.json().get("error", "An error occurred")
            return render_template('index.html', error=error_message)

    return render_template('index.html')

# Chatbot Route
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    destination = request.args.get('destination', 'your location')

    prompt = (
        f"You are a travel assistant. Answer specifically about {destination}. "
        f"User: {user_message}. Respond concisely."
    )

    payload = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt}]
    }

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    response = requests.post(API_URL, json=payload, headers=headers)

    if response.status_code == 200:
        bot_response = response.json().get("choices")[0].get("message").get("content").strip()
        return jsonify({"response": bot_response})
    else:
        return jsonify({"response": "Sorry, an error occurred."}), 500

# Download Itinerary Route
@app.route('/download_itinerary')
def download_itinerary():
    # Retrieve the generated itinerary from the session
    itinerary_content = session.get('itinerary', 'No itinerary available')

    # Create an in-memory file
    byte_io = io.BytesIO()
    byte_io.write(itinerary_content.encode())
    byte_io.seek(0)  # Rewind to the start of the file

    # Send the file to the user for download
    return send_file(byte_io, as_attachment=True, download_name="itinerary.txt", mimetype="text/plain")

if __name__ == "__main__":
    app.secret_key = 'your_secret_key'  # Set the secret key for session management
    app.run(debug=True)
