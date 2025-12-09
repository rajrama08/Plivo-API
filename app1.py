import os
from flask import Flask, request, Response
from plivo import RestClient

app = Flask(__name__)

# 
AUTH_ID = "auth_id"
AUTH_TOKEN = "auth_toke"
FROM_NUMBER = "14692463987"  
ASSOCIATE_NUMBER = "+917042335375"  
AUDIO_FILE_URL = "https://raw.githubusercontent.com/rajrama08/Plivo-API/main/ttsMP3.com_VoiceText_2025-12-9_9-3-55.mp3" 
####

BASE_URL = "https://bookish-trout-p7p97gr79r63jxg-5000.app.github.dev"  # we'll fix this in STEP 6

client = RestClient(AUTH_ID, AUTH_TOKEN)


@app.route("/")
def index():
    return "Plivo IVR app is running"



@app.route("/make_call")
def make_call():
    """
    Call this URL in browser to start a call:
    http://localhost:5000/make_call?to=+91XXXXXXXXXX
    """
    to_number = request.args.get("to")
    if not to_number:
        return "Please provide ?to=PHONE_NUMBER in the URL"

    answer_url = f"{BASE_URL}/ivr/language"

    try:
        response = client.calls.create(
            from_=FROM_NUMBER,
            to_=to_number,
            answer_url=answer_url,
            answer_method="GET",
        )
        
        return f"Call initiated to {to_number}. Check your phone."
    except Exception as e:
        return f"Error initiating call: {e}"



@app.route("/ivr/language", methods=["GET", "POST"])
def ivr_language():
    """
    Level 1 IVR:
    Ask caller to choose language:
    1 - English
    2 - Spanish
    Then send the digit to /ivr/menu
    """
    next_url = f"{BASE_URL}/ivr/menu"

    xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <GetDigits action="{next_url}" method="POST" timeout="5" numDigits="1">
        <Speak>Press 1 for English. Press 2 for Spanish.</Speak>
    </GetDigits>
    <Speak>No input received. Goodbye.</Speak>
    <Hangup/>
</Response>
"""
    return Response(xml_response, mimetype="text/xml")



@app.route("/ivr/menu", methods=["GET", "POST"])
def ivr_menu():
    """
    Second IVR menu:
    After language, ask:
    "Press 1 to hear a message. Press 2 to talk to an associate."
    """
    language_digit = request.values.get("Digits")  # what user pressed in language menu

    if language_digit not in ("1", "2"):
        # Invalid input, repeat language menu
        repeat_url = f"{BASE_URL}/ivr/language"
        xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Speak>Invalid input.</Speak>
    <Redirect>{repeat_url}</Redirect>
</Response>
"""
        return Response(xml_response, mimetype="text/xml")

    # Build the next step URL with language info passed as query param
    action_url = f"{BASE_URL}/ivr/action?lang={language_digit}"

    xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <GetDigits action="{action_url}" method="POST" timeout="5" numDigits="1">
        <Speak>Press 1 to hear a message. Press 2 to talk to an associate.</Speak>
    </GetDigits>
    <Speak>No input received. Goodbye.</Speak>
    <Hangup/>
</Response>
"""
    return Response(xml_response, mimetype="text/xml")



@app.route("/ivr/action", methods=["GET", "POST"])
def ivr_action():
    """
    If user presses:
    1 -> Play audio
    2 -> Dial associate
    """
    lang = request.args.get("lang")  
    choice = request.values.get("Digits")

    if choice == "1":
       
        xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>{AUDIO_FILE_URL}</Play>
    <Speak>Thank you for calling. Goodbye.</Speak>
    <Hangup/>
</Response>
"""
    elif choice == "2":
       
        xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Speak>Connecting you to an associate now.</Speak>
    <Dial callerId="{FROM_NUMBER}">
        <Number>{ASSOCIATE_NUMBER}</Number>
    </Dial>
</Response>
"""
    else:
        
        menu_url = f"{BASE_URL}/ivr/menu"
        xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Speak>Invalid input.</Speak>
    <Redirect>{menu_url}</Redirect>
</Response>
"""

    return Response(xml_response, mimetype="text/xml")


if __name__ == "__main__":
   
    app.run(host="0.0.0.0", port=5000, debug=True)
