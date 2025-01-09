import yaml
from flask import Flask, render_template, request
from openai import OpenAI

import yaml
from flask import Flask, render_template, request
from openai import OpenAI

app = Flask(__name__)

# Load configuration from YAML file
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

api_key = config["openai"]["api_key"]
base_url = config["openai"]["base_url"]
model = config["openai"]["model"]

# Initialize OpenAI client
openai_client = OpenAI(base_url=base_url, api_key=api_key)

@app.route("/", methods=["GET", "POST"])
def index():
    checked_text = None
    original_text = None
    errors = []

    if request.method == "POST":
        original_text = request.form.get("text")
        if not original_text:
            return "No text provided!"

        try:
            # Prepare the prompt for OpenAI API
            prompt = (
                "You are an expert proofreader. Analyze the following text, "
                "identify spelling and grammar mistakes, and suggest corrections. "
                "Provide the output in JSON format with the following structure: \n"
                "{\n"
                "  'corrected_text': 'Corrected version of the text',\n"
                "  'errors': [\n"
                "    {\n"
                "      'error_before': 'original word or phrase',\n"
                "      'error_after': 'corrected word or phrase',\n"
                "      'error_type': 'type of error (e.g., spelling, grammar)',\n"
                "      'error_analysis': 'brief explanation of the error'\n"
                "    }\n"
                "  ]\n"
                "}\n\n"
                f"Text to analyze: {original_text}"
            )

            # Send the request to OpenAI
            response = openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a spelling and grammar correction assistant."},
                    {"role": "user", "content": prompt},
                ],
            )

        # Parse the response
            import json
            response_message = response.choices[0].message.content.strip()
            response_message = response_message.strip('```json').strip('```')  # Remove code block markers
            response_json = json.loads(response_message)  # Use strict JSON parsing

            checked_text = response_json.get("corrected_text", "")
            errors = response_json.get("errors", [])


        except Exception as e:
            checked_text = f"Error: {e}"

    # Render the HTML template with the original text, corrected text, and errors
    return render_template("index.html", checked_text=checked_text, original_text=original_text, errors=errors)

if __name__ == "__main__":
    app.run(debug=True)
