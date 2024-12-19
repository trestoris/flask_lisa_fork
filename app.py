import yaml
from flask import Flask, render_template, request
from openai import OpenAI

app = Flask(__name__)

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

api_key = config["openai"]["api_key"]
base_url = config["openai"]["base_url"]
model = config["openai"]["model"]

openai_client = OpenAI(base_url=base_url, api_key=api_key)


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    original_text = None

    if request.method == "POST":
        original_text = request.form.get("text")
        if not original_text:
            return "No text provided!"

        try:
            prompt = (
                "You are an expert proofreader. Analyze the following text, "
                "identify spelling and grammar mistakes, and suggest corrections. "
                "Provide the output in JSON format with the following structure:\n"
                "As addition provide a final text with correction"
                "give me a joke"
                "{\n"
                "  'errors': [\n"
                "    {'word': 'incorrect_word', 'suggestions': ['suggestion1', 'suggestion2']}\n"
                "       {'word': 'final_text': ['finaltext']}\n"
                "       {'joke': 'joke': ['joke']}\n"
                "  ]\n"
                "}\n\n"
                f"Text to analyze: {original_text}"
            )

            response = openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a spelling and grammar correction assistant."},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
            )

            result = response.choices[0].message.content.strip()
        except Exception as e:
            result = f"Error: {e}"

    return render_template("index.html", result=result, original_text=original_text)


if __name__ == "__main__":
    app.run(debug=True)