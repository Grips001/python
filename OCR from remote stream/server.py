# screen_stream_service.py
from flask import Flask, Response
import cv2
import mss
import numpy as np
import threading
import time

app = Flask(__name__)

def generate_frames():
    import mss  # re-import inside thread
    sct = mss.mss()  # thread-safe: create new instance per connection

    try:
        monitor = sct.monitors[1]  # Primary monitor
    except Exception as e:
        print(f"❌ Failed to access monitor: {e}")
        return

    while True:
        try:
            sct_img = sct.grab(monitor)
            frame = np.array(sct_img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            ret, jpeg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
            if not ret:
                print("❌ JPEG encode failed.")
                continue

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
        except Exception as e:
            print(f"❌ Frame generation error: {e}")
            break


@app.route('/stream')
def stream():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def start_server():
    app.run(host='0.0.0.0', port=8080, threaded=True)

if __name__ == '__main__':
    threading.Thread(target=start_server).start()
    while True:
        time.sleep(60)
