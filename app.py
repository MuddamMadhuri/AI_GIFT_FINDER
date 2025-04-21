from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file

app = Flask(__name__)

API_KEY = os.getenv("OPENROUTER_API_KEY")

print(f"🔑 API Key Loaded: {API_KEY}")

API_URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
MODEL = "mistralai/mistral-7b-instruct:free"
  # Switched to a safe, free model

def get_gift_suggestions(description, age, budget):
    prompt = f"Suggest unique gift ideas for a {age}-year-old. Budget: ${budget}. Description: {description}"

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    try:
        print("📡 Sending request to AI API...")
        print("Payload:", payload)

        response = requests.post(API_URL, headers=HEADERS, json=payload)

        print("🔁 Response status:", response.status_code)
        print("🔁 Response text:", response.text)

        data = response.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        elif "error" in data:
            return f"❌ API Error: {data['error'].get('message', 'Unknown error')}"
        else:
            return "⚠️ Unexpected response from the AI API."
    except Exception as e:
        return f"❌ Failed to reach API: {e}"

def mock_product_links(suggestions_text):
    lines = suggestions_text.split("\n")
    output = []
    for line in lines:
        if line.strip():
            keywords = line.strip().split(":")[0]
            query = "+".join(keywords.strip().split())
            link = f"https://www.amazon.com/s?k={query}"
            output.append(f"{line} — <a href='{link}' target='_blank'>View on Amazon</a>")
    return output

@app.route("/", methods=["GET", "POST"])
def index():
    suggestions = None
    links = None
    if request.method == "POST":
        description = request.form["description"]
        age = request.form["age"]
        budget = request.form["budget"]
        suggestions = get_gift_suggestions(description, age, budget)
        links = mock_product_links(suggestions)
    return render_template("index.html", suggestions=links)

if __name__ == "__main__":
    app.run(debug=True)
