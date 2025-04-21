from flask import Flask, render_template, request
import requests

app = Flask(__name__)

API_KEY = "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"  # Get it from https://openrouter.ai
API_URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
MODEL = "mistralai/mistral-7b-instruct:free"
def get_gift_suggestions(description, age, budget):
    prompt = f"Suggest unique gift ideas for a {age}-year-old. Budget: ${budget}. Description: {description}"

    payload = {
        # "model": "openchat/openchat-7b:free",  # or another supported free model
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload,verify=False)

    # Check for errors
    try:
        data = response.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        elif "error" in data:
            return f"❌ API Error: {data['error'].get('message', 'Unknown error')}"
        else:
            return "⚠️ Unexpected response from the AI API."
    except Exception as e:
        return f"❌ Failed to parse API response: {e}"


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

# if __name__ == "__main__":
#     app.run(debug=True)
import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Render sets this automatically
    app.run(host='0.0.0.0', port=port)

