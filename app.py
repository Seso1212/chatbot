from flask import Flask, request, jsonify, render_template
from difflib import get_close_matches
import json
import re

app = Flask(__name__)

# Load predefined questions and answers from a file
def load_qa():
    try:
        with open('qa_dict.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {
            "What is your name?": "I am a chatbot_.",
            "How are you?": "I am just a bunch of code, but I'm here to help!",
            "What is the capital of France?": "The capital of France is Paris.",
            # Add more question-answer pairs as needed
        }

# Save the question-answer pairs to a file
def save_qa(qa_dict):
    with open('qa_dict.json', 'w') as file:
        json.dump(qa_dict, file, indent=4)

qa_dict = load_qa()

# Abbreviation dictionary
abbreviation_dict = {
    "u": "you",
    "r": "are",
    "y": "why",
    "k": "okay",
    # Add more abbreviations as needed
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    original_message = user_message  # Store the original message before abbreviation replacement

    # Replace abbreviations with full forms
    for abbr, full in abbreviation_dict.items():
        user_message = re.sub(r'\b' + re.escape(abbr) + r'\b', full, user_message, flags=re.IGNORECASE)

    matched_question = get_close_matches(user_message, qa_dict.keys(), n=1, cutoff=0.6)
    if matched_question:
        answer = qa_dict.get(matched_question[0])
    else:
        answer = "Sorry, I don't understand that question."

    return jsonify({"response": answer, "matched_question": matched_question[0] if matched_question else "", "original_message": original_message})

@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.json
    matched_question = data.get('matched_question')
    feedback = data.get('feedback')
    user_message = data.get('user_message')
    original_message = data.get('original_message')

    if feedback == 'bad' and user_message:
        qa_dict[original_message] = user_message
    elif feedback == 'bad':
        qa_dict[original_message] = "I'm sorry, I didn't know that before. Can you provide the correct answer?"

    save_qa(qa_dict)
    return jsonify({"status": "feedback received"})

if __name__ == '__main__':
    app.run(debug=True)



