from ultralytics import YOLO
import cv2

# Load YOLO model
model = YOLO("models/yolo_model.pt")

# Get class labels from the model
class_labels = model.names  
print("Model Class Labels:", class_labels)

# Find the correct Class ID for "phone"
PHONE_CLASS_ID = None
for class_id, name in class_labels.items():
    if "phone" in name.lower() or "cellphone" in name.lower():
        PHONE_CLASS_ID = class_id
        break

if PHONE_CLASS_ID is None:
    print("⚠ WARNING: No 'phone' class found in the model!")
else:
    print(f"✅ Detected 'phone' class ID: {PHONE_CLASS_ID}")

def detect_phone(frame, confidence_threshold=0.5):
    results = model(frame)
    phone_detected = False
    phone_confidence = 0.0  

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])  
            cls = int(box.cls[0])  

            print(f"Detected Class ID: {cls}, Label: {class_labels.get(cls, 'Unknown')}, Confidence: {conf:.2f}")

            # Improve phone detection accuracy
            if cls == PHONE_CLASS_ID and conf > confidence_threshold:
                phone_detected = True
                phone_confidence = conf

                # Draw a wider bounding box to detect side views
                padding = 10  
                cv2.rectangle(frame, (x1 - padding, y1), (x2 + padding, y2), (0, 255, 0), 2)

                label = f"Phone {conf:.2f}"
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    if phone_detected:
        cv2.putText(frame, "WARNING: Phone detected!", 
                    (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    return frame, phone_detected, phone_confidence