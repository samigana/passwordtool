

from flask import Flask, jsonify, request
from flask_cors import CORS

from password_tool import GeneratorOptions, generate_password, rate_password

app = Flask(__name__)

CORS(app)


@app.route("/api/generate", methods=["POST"])
def api_generate():
   
    data = request.get_json(force=True) or {}

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
        return jsonify({"error": str(e)}), 400

 
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
    app.run(debug=True, port=5000)
