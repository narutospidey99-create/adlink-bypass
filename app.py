from flask import Flask, request, jsonify
from bypass import bypass_adlink    # Import function from bypass.py

app = Flask(__name__)

@app.route("/")
def home():
    return "Adlink Bypass API is running!"

@app.route("/bypass")
def api_bypass():
    url = request.args.get("url")
    if not url:
        return jsonify({"success": False, "error": "No URL provided"})
    
    result = bypass_adlink(url)
    return jsonify(result)

if __name__ == "__main__":
    app.run()
