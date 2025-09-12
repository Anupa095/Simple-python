import cv2
from ultralytics import YOLO
import easyocr
import numpy as np

# 🔹 Use pretrained YOLOv8 model (instead of missing best.pt)
MODEL_PATH = "yolov8n.pt"   # will auto-download first time
model = YOLO(MODEL_PATH)

# OCR reader
reader = easyocr.Reader(['en'])

# 0 = webcam (or replace with video path / image path)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Run YOLO detection
    results = model(frame)[0]

    if hasattr(results, "boxes") and len(results.boxes) > 0:
        boxes = results.boxes.xyxy.cpu().numpy()

        for box in boxes:
            x1, y1, x2, y2 = map(int, box)
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(frame.shape[1]-1, x2), min(frame.shape[0]-1, y2)

            roi = frame[y1:y2, x1:x2]
            if roi.size == 0:
                continue

            # Preprocess ROI for OCR
            roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            h, w = roi_gray.shape
            scale = max(1, 160 // max(h, w))
            if scale > 1:
                roi_gray = cv2.resize(roi_gray, (w*scale, h*scale), interpolation=cv2.INTER_LINEAR)

            # OCR
            ocr_results = reader.readtext(roi_gray)

            plate_text = ""
            if ocr_results:
                best = max(ocr_results, key=lambda r: r[2])
                plate_text = best[1]

            # Draw box + text
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
            if plate_text:
                cv2.putText(frame, plate_text, (x1, max(20, y1-10)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)

    cv2.imshow("Plate Detector + OCR", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
