import requests
import cv2
import numpy as np
from PIL import Image
import pytesseract
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from io import BytesIO

# IP of the source streaming machine
STREAM_URL = 'http://192.168.1.112:8080/stream'

def grab_single_frame_mjpeg():
    print("🔄 Connecting to MJPEG stream...")
    response = requests.get(STREAM_URL, stream=True)
    bytes_data = b''

    for chunk in response.iter_content(chunk_size=1024):
        bytes_data += chunk
        start = bytes_data.find(b'\xff\xd8')
        end = bytes_data.find(b'\xff\xd9')

        if start != -1 and end != -1:
            jpg_data = bytes_data[start:end+2]
            bytes_data = bytes_data[end+2:]  # remove processed bytes

            print("✅ Frame captured.")
            np_arr = np.frombuffer(jpg_data, dtype=np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            return frame

    print("❌ Failed to get a valid frame.")
    return None

def preprocess_for_ocr(frame):
    print("🎨 Preprocessing image for OCR...")
    
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        gray,
        maxValue=255,
        adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        thresholdType=cv2.THRESH_BINARY,
        blockSize=31,
        C=10
    )

    # Optional: Resize to improve OCR accuracy (especially for small text)
    # thresh = cv2.resize(thresh, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)

    # Debugging: Uncomment to preview the preprocessed frame
    # cv2.imshow("Preprocessed", thresh)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return thresh

def capture_and_ocr():
    frame = grab_single_frame_mjpeg()
    if frame is None:
        text_box.delete(1.0, tk.END)
        text_box.insert(tk.END, "Failed to capture frame.")
        return

    # Preprocess image
    processed_image = preprocess_for_ocr(frame)

    # Convert to PIL format for pytesseract
    image = Image.fromarray(processed_image)

    try:
        raw_text = pytesseract.image_to_string(image)
        raw_text = raw_text.replace("$3", "S3")
    except Exception as e:
        raw_text = f"OCR error: {e}"

    text_box.delete(1.0, tk.END)
    text_box.insert(tk.END, raw_text)

# GUI
root = tk.Tk()
root.title("Capture & OCR from Stream")

btn = tk.Button(root, text="Capture & OCR", command=capture_and_ocr)
btn.pack(pady=10)

text_box = ScrolledText(root, wrap=tk.WORD, width=100, height=40)
text_box.pack(padx=10, pady=10, fill='both', expand=True)

root.mainloop()
