from flask import Flask, render_template, Response
import cv2
from utils.detection import detect_phone
from utils.drowsiness import detect_drowsiness
from utils.alert import play_alert_sound, stop_alert_sound
from twilio.rest import Client
import threading
import time
from dotenv import load_dotenv
import os

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
EMERGENCY_CONTACT = os.getenv("EMERGENCY_CONTACT")


app = Flask(__name__)
camera = cv2.VideoCapture(0)  # Open webcam

# Alert state variables
previous_phone_state = False
previous_drowsy_state = False
alert_sound_count = 0  # To count consecutive alert sounds
alert_threshold = 4  # Trigger after 4 consecutive alert sounds
cooldown_period = 30  # Cooldown period in seconds
last_alert_time = 0  # Track last alert time
alert_in_progress = False  # Prevent multiple alerts simultaneously

# Function to send SMS and make a call
def send_alert():
    """Send SMS and make a call to the emergency contact."""
    global alert_in_progress

    if alert_in_progress:
        return

    alert_in_progress = True

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        # Send SMS
        message = client.messages.create(
            body="🚨 Emergency Alert: The driver is showing prolonged drowsiness. Immediate action is required!",
            from_=TWILIO_PHONE_NUMBER,
            to=EMERGENCY_CONTACT
        )
        print(f"SMS sent: {message.sid}")

        # Make a call and use the hosted TwiML XML response
        call = client.calls.create(
    url="http://demo.twilio.com/docs/voice.xml",  # Replace with your actual public URL (using `ngrok`)
    from_=TWILIO_PHONE_NUMBER,
    to=EMERGENCY_CONTACT
)

        print(f"Call initiated: {call.sid}")

    except Exception as e:
        print(f"Error sending alert: {e}")

    finally:
        alert_in_progress = False

# Function to generate video frames with detection and alert logic
def generate_frames():
    """Generate video frames with detection and alert logic."""
    global previous_phone_state, previous_drowsy_state, alert_sound_count
    global last_alert_time, alert_in_progress

    while True:
        success, frame = camera.read()
        if not success:
            break

        # Phone detection
        frame, phone_detected, phone_confidence = detect_phone(frame)

        # Drowsiness detection
        frame, drowsy, drowsiness_confidence = detect_drowsiness(frame)

        current_time = time.time()

        # Drowsiness alert logic
        if drowsy:
            play_alert_sound("drowsiness")

            # Increment counter only when the alert sound plays
            alert_sound_count += 1
            print(f"Alert Sound Count: {alert_sound_count}")

            # Trigger emergency alert only after 4 consecutive alert sounds
            if alert_sound_count >= alert_threshold and (current_time - last_alert_time >= cooldown_period):
                print("🚨 Triggering Emergency Alert!")
                threading.Thread(target=send_alert).start()
                last_alert_time = current_time
                alert_sound_count = 0  # Reset the counter after alert

            previous_drowsy_state = True

        else:
            stop_alert_sound("drowsiness")

            # Reset alert sound counter if no drowsiness is detected
            alert_sound_count = 0
            previous_drowsy_state = False

        # Phone detection logic
        if phone_detected:
            play_alert_sound("phone")
            previous_phone_state = True
        elif previous_phone_state:
            stop_alert_sound("phone")
            previous_phone_state = False

        # Frame processing
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
@app.route("/twilio-voice")
def twilio_voice():
    """Twilio XML Response for Calls"""
    response = """<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Say voice="alice">Emergency Alert! The driver has been detected as drowsy multiple times. Immediate action is required.</Say>
    </Response>"""
    return Response(response, mimetype="text/xml")

@app.route('/')
def index():
    """Render the HTML page."""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Provide the video stream."""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
