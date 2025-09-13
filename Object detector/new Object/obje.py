from ultralytics import YOLO
import imageio
from PIL import Image, ImageTk
import tkinter as tk

# =========================
# Load YOLOv8 model
# =========================
MODEL_PATH = "yolov8n.pt"
model = YOLO(MODEL_PATH)

# =========================
# Webcam Detector Class
# =========================
class WebcamDetector:
    def __init__(self, window):
        self.window = window
        self.window.title("YOLOv8 Webcam Detection (No OpenCV)")
        self.label = tk.Label(window)
        self.label.pack()

        # Open webcam using imageio
        self.cap = imageio.get_reader("<video0>")  # Linux/Mac: "<video0>", Windows: "<video0>" usually works
        self.running = True
        self.update_frame()

    def update_frame(self):
        if not self.running:
            return

        try:
            frame = self.cap.get_next_data()
            # YOLO detection
            results = model(frame)
            annotated_frame = results[0].plot()

            # Convert to PIL Image for Tkinter
            img = Image.fromarray(annotated_frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.label.imgtk = imgtk
            self.label.configure(image=imgtk)

        except Exception as e:
            print("Error capturing frame:", e)

        self.window.after(10, self.update_frame)

    def stop(self):
        self.running = False
        self.cap.close()
        self.window.destroy()


# =========================
# Run Tkinter Window
# =========================
root = tk.Tk()
detector = WebcamDetector(root)
root.protocol("WM_DELETE_WINDOW", detector.stop)
root.mainloop()
