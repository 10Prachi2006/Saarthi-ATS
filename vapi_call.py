import requests
import os

def call_candidate_with_vapi(name, phone, assistant_id, api_key, phone_number_id, callback_url):
    url = "https://api.vapi.ai/call"
    payload = {
        "phoneNumber": phone,
        "assistantId": assistant_id,
        "phoneNumberId": phone_number_id,
        "metadata": {"candidate_name": name},
        "webhookUrl": callback_url
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
