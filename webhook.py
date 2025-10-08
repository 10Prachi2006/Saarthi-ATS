from flask import Flask, request
from file_utils import update_candidate

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def handle_vapi_result():
    data = request.json
    candidate_name = data["metadata"]["candidate_name"]
    candidate_phone = data["phoneNumber"]
    interview_result = data.get("result", "")
    update_candidate(candidate_name, candidate_phone, {
        "call_status": "completed",
        "vapi_result": interview_result
    })
    return {"status": "ok"}, 200

if __name__ == "__main__":
    app.run(port=5000)
