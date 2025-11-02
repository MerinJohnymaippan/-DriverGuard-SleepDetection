from twilio.rest import Client
from dotenv import load_dotenv
import os

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
EMERGENCY_CONTACT = os.getenv("EMERGENCY_CONTACT")


# Initialize Twilio Client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Send test SMS
try:
    message = client.messages.create(
        body="🚨 Test Alert: Twilio SMS is working!",
        from_=TWILIO_PHONE_NUMBER,
        to=EMERGENCY_CONTACT
    )
    print(f"✅ SMS Sent! SID: {message.sid}")

    # Make test call
    call = client.calls.create(
        twiml='<Response><Say>Test Alert! Twilio call is working.</Say></Response>',
        from_=TWILIO_PHONE_NUMBER,
        to=EMERGENCY_CONTACT
    )
    print(f"✅ Call Initiated! SID: {call.sid}")

except Exception as e:
    print(f"❌ Error: {e}")
