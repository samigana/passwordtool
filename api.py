"""
api.py
======

A thin HTTP wrapper around the EXISTING password_tool.py.

This file does not change password_tool.py in any way — it only
imports the functions/classes already defined there and exposes
them as two JSON API endpoints so a web frontend can call them:

    POST /api/generate  -> uses generate_password()
    POST /api/rate       -> uses rate_password()

Run this instead of password_tool.py when you want the web UI.
password_tool.py itself still works exactly as before from the
command line — this file is purely additive.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS

# Import the existing, unmodified backend functions/classes.
from password_tool import GeneratorOptions, generate_password, rate_password

app = Flask(__name__)

# CORS lets the frontend (served from a different port/file, e.g.
# opened directly in the browser or via Live Server) call this API.
# For a beginner/local project we allow all origins ("*").
# If you deploy this publicly later, restrict this to your real
# frontend URL instead of "*".
CORS(app)


@app.route("/api/generate", methods=["POST"])
def api_generate():
    """
    Generate a password from user-selected options.

    Expected JSON body:
    {
        "length": 16,
        "use_lower": true,
        "use_upper": true,
        "use_digits": true,
        "use_special": true,
        "exclude_ambiguous": false
    }
    """
    data = request.get_json(force=True) or {}

    # Build the same GeneratorOptions object the CLI version uses.
    opts = GeneratorOptions(
        length=int(data.get("length", 16)),
        use_lower=bool(data.get("use_lower", True)),
        use_upper=bool(data.get("use_upper", True)),
        use_digits=bool(data.get("use_digits", True)),
        use_special=bool(data.get("use_special", True)),
        exclude_ambiguous=bool(data.get("exclude_ambiguous", False)),
    )

    try:
        password = generate_password(opts)
    except ValueError as e:
        # e.g. length too short for the selected character sets
        return jsonify({"error": str(e)}), 400

    # Reuse the existing rate_password() function to also return
    # strength info for the password we just generated.
    result = rate_password(password)

    return jsonify({
        "password": password,
        "score": result.score,
        "label": result.label,
        "entropy_bits": round(result.entropy_bits, 1),
    })


@app.route("/api/rate", methods=["POST"])
def api_rate():
    """
    Rate a password the user typed in.

    Expected JSON body:
    {
        "password": "some-password-here"
    }
    """
    data = request.get_json(force=True) or {}
    password = data.get("password", "")

    result = rate_password(password)

    return jsonify({
        "score": result.score,
        "label": result.label,
        "entropy_bits": round(result.entropy_bits, 1),
        "feedback": result.feedback,
    })


if __name__ == "__main__":
    # Runs on http://127.0.0.1:5000 by default.
    app.run(debug=True, port=5000)