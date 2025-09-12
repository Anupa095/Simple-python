from ultralytics import YOLO
import cv2

# Load pre-trained YOLOv8 model (detects 80 COCO classes)
model = YOLO("yolov8n.pt")  # yolov8n.pt is small and fast

# Open webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture frame")
        break

    # YOLO expects images in RGB format
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Run YOLO detection
    results = model(rgb_frame)

    # Annotate frame with bounding boxes and labels
    annotated_frame = results[0].plot()

    # Convert back to BGR for OpenCV display (optional)
    annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR)

    # Show the frame
    cv2.imshow("YOLOv8 Object Detection", annotated_frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
