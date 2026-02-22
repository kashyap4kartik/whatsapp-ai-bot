import os
import threading
import time
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client as TwilioClient
from groq import Groq

app = Flask(__name__)

# Load environment variables correctly
TWILIO_SID = os.environ.get("TWILIO_SID")
TWILIO_TOKEN = os.environ.get("TWILIO_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Create clients
twilio_client = TwilioClient(TWILIO_SID, TWILIO_TOKEN)
client = Groq(api_key=GROQ_API_KEY)

BUSINESS_INFO = """
Business Name: Bright Future Coaching
Location: Near Bus Stand, Bhopal
Timing: 9 AM to 6 PM (Monday to Saturday)
Courses: Maths, Science, English
Fees: ₹1500 per month
Contact: 9876543210
"""

sent_followups = set()

def send_followup(phone):
    time.sleep(10) #wait for 10 sec

    twilio_client.messages.create(
        body="hi just checking,need any help?",
        from_ = "whatsapp:+14155238886",
        to = phone
    )


@app.route("/whatsapp",methods = ['POST'])

def whatsapp_reply():
    incoming_msg = request.form.get('Body')
    phone = request.form.get('From')
    print("Customer number:", phone)
    print("Customer",incoming_msg)

    import os
    file_path = os.path.join(os.path.dirname(__file__), "leads.txt")
    if phone:
        with open(file_path,'a') as f:
            f.write(phone + "\n")

    if phone not in sent_followups:
        sent_followups.add(phone)
        threading.Thread(target=send_followup, args=(phone,)).start()

    #AI thinking
    chat_completion = client.chat.completions.create(
    messages=[
        {"role": "system", "content": f"You are a helpful assistant for this business:\n{BUSINESS_INFO}\nOnly answer using this information. If not available, say you will connect human."},
    
        {"role": "user", "content": incoming_msg}
    ],
    model="llama-3.3-70b-versatile",
)

    reply_text = chat_completion.choices[0].message.content

    resp = MessagingResponse()
    msg = resp.message(reply_text)

    return str(resp)

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

    










