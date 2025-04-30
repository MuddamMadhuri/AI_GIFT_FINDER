import os
from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Load environment variables
API_KEY = os.environ.get('OPENROUTER_API_KEY')  # ← Pulls from Render's config
API_URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",  # ← Now uses the env variable
    "Content-Type": "application/json"
}
MODEL = "mistralai/mistral-7b-instruct:free"
# MODEL = "gryphe/mythomax-l2-13b:free"

# def get_gift_suggestions(description, age, budget):
#     prompt = f"Suggest unique gift ideas for a {age}-year-old. Budget: ${budget}. Description: {description}"

#     payload = {
#         # "model": "openchat/openchat-7b:free",  # or another supported free model
#         "model": MODEL,
#         "messages": [{"role": "user", "content": prompt}]
#     }

#     response = requests.post(API_URL, headers=HEADERS, json=payload,verify=False)

#     # Check for errors
#     try:
#         data = response.json()
#         if "choices" in data:
#             return data["choices"][0]["message"]["content"]
#         elif "error" in data:
#             return f"❌ API Error: {data['error'].get('message', 'Unknown error')}"
#         else:
#             return "⚠️ Unexpected response from the AI API."
#     except Exception as e:
#         return f"❌ Failed to parse API response: {e}"

def get_gift_suggestions(description, age, budget):
    headers = {
        "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",  # Directly use env var
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-app-name.onrender.com",  # OpenRouter requires this
        "X-Title": "AI Gift Finder"  # Identify your app
    }
    
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": f"Suggest gifts for {age}-year-old. Budget: ${budget}. Interests: {description}"}]
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()  # Raise HTTP errors
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ API Error: {str(e)}"

def mock_product_links(suggestions_text):
    # Fake product links from keywords in the suggestion
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
@app.route("/form", methods=["GET", "POST"])
def form():
    suggestions = None
    if request.method == "POST":
        description = request.form["description"]
        age = request.form["age"]  # Note: You'll need to add this input to your form
        budget = request.form["budget"]
        suggestions_text = get_gift_suggestions(description, age, budget)
        suggestions = mock_product_links(suggestions_text)
    return render_template("form.html", suggestions=suggestions)

# ... (your existing routes like @app.route("/") and @app.route("/form")) ...

# ▼ Add this new debug route ▼
@app.route("/debug")
def debug():
    api_key = os.environ.get("OPENROUTER_API_KEY")
    return {
        "OPENROUTER_API_KEY_exists": bool(api_key),
        "key_length": len(api_key) if api_key else 0,
        "first_5_chars": api_key[:5] + "..." if api_key else None
    }

@app.route("/debug-full")
def debug_full():
    full_key = os.environ["OPENROUTER_API_KEY"]
    return f"Key (first/last 5 chars): {full_key[:5]}...{full_key[-5:]} | Length: {len(full_key)}"

if __name__ == "__main__":
    app.run(debug=True)
