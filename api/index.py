import json
import os
from flask import Flask, jsonify, request

app = Flask(__name__)

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "courses.json")

def load_courses():
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

@app.route("/api/courses", methods=["GET"])
def get_courses():
    keyword = request.args.get("q", "").lower()
    courses = load_courses()
    if keyword:
        courses = [
            c for c in courses
            if keyword in c.get("title", "").lower()
            or keyword in c.get("description", "").lower()
            or keyword in c.get("department", "").lower()
        ]
    return jsonify({"total": len(courses), "courses": courses})

if __name__ == "__main__":
    app.run(debug=True, port=5000)