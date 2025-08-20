import language_tool_python
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Initialize the language tool. It's good practice to do this once.
tool = language_tool_python.LanguageTool('en-US')

@app.route('/')
def index():
    """Renders the main page."""
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check():
    """
    Receives text from the frontend, checks it for grammar errors,
    and returns the corrections.
    """
    text = request.json.get('text', '')

    matches = tool.check(text)

    issues = []
    for rule in matches:
        issues.append({
            'message': rule.message,
            'replacements': rule.replacements,
            'offset': rule.offset,
            'length': rule.errorLength,
            'type': rule.ruleId,
            'context': {
                'text': rule.context,
                'offset': rule.offsetInContext,
                'length': rule.errorLength
            }
        })

    corrected_text = language_tool_python.utils.correct(text, matches)

    return jsonify({
        'issues': issues,
        'corrected_text': corrected_text
    })

if __name__ == '__main__':
    # It's recommended to run the app using the 'flask run' command.
    # The 'debug=True' mode is useful for development.
    app.run(debug=True)
