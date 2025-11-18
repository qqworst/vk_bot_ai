import vk_api
from flask import Flask, request
from google import genai
import os

VK_API_TOKEN = os.getenv("VK_API_TOKEN", "vk1.a.QZ1duBjzU0FQ5-jsyplneOTqnGHPx3YpTz0Hat19FWQSu4Zp0s1bGnWveeZnSQ9Lr0_uXhwLkn8Hf7wZR_yKmipTkOPikIN0R40N4h55RD3HmE6STUbq-piLrz5BuPmxC0Vuo9x82aJzPwoDX-n4Ic4cy5WZfEIOqsHBxC01pdGvoos9MeQhfwszNl7qoSw3EorZ7f3dpW5jaKvxRg4VEw")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBEKiO012rhv7YplIDVIf61bnEF8qVaFxo")
GROUP_ID = int(os.getenv("GROUP_ID", "233981911"))
CONFIRMATION_STRING = os.getenv("CONFIRMATION_STRING", "a6517b79")
MODEL_NAME = "gemini-2.5-flash"

app = Flask(__name__)
vk_session = vk_api.VkApi(token=VK_API_TOKEN)
vk = vk_session.get_api()

try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    print("Gemini init error:", e)
    client = None

def send_message(peer_id, text):
    try:
        vk.messages.send(
            peer_id=peer_id,
            message=text,
            random_id=int.from_bytes(os.urandom(4), "big")
        )
    except Exception as e:
        print("Send error:", e)

def get_gemini_response(text):
    if not client:
        return "Gemini init error"
    try:
        r = client.models.generate_content(model=MODEL_NAME, contents=text)
        return r.text or "Empty response"
    except Exception as e:
        print("Gemini error:", e)
        return "Gemini request failed"

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data:
        return "ok"

    if data.get("type") == "confirmation":
        return CONFIRMATION_STRING

    if data.get("type") == "message_new":
        try:
            msg = data["object"]["message"]
            peer_id = msg["peer_id"]
            text = msg.get("text", "").strip()
            if text:
                send_message(peer_id, get_gemini_response(text))
        except Exception as e:
            print("Process error:", e)
        return "ok"

    return "ok"
