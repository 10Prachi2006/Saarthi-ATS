# webhook.py

from flask import Flask, request
from file_utils import update_candidate

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_vapi_result():
    data = request.json
    candidatename = data["metadata"]["candidate_name"]
    candidatephone = data["phoneNumber"]
    interviewresult = data.get("result", "")
    update_candidate(
        candidatename,
        candidatephone,
        {"call_status": "completed", "vapi_result": interviewresult}
    )
    return {"status": "ok"}, 200

if __name__ == "__main__":
    app.run(port=5000)
