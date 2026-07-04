import threading
import time
from flask import Flask, render_template_string, Response, request
import cv2
import serial.tools.list_ports
from arm import run_hand_tracking

app = Flask(__name__)

stop_event = None
thread = None
latest_frame = None
latest_status = "Ready"
latest_hand_found = False
selected_port = "COM10"

HTML_PAGE = """
<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>AI Robotic Hand</title>
  <style>
    body { font-family: Arial, sans-serif; background: #07111f; color: #f4f7fb; margin: 0; padding: 24px; }
    .card { max-width: 980px; margin: auto; background: #0f1d31; border-radius: 16px; padding: 24px; box-shadow: 0 12px 40px rgba(0,0,0,0.35); }
    h1 { margin-top: 0; }
    .controls { display: flex; gap: 12px; align-items: center; margin-bottom: 16px; flex-wrap: wrap; }
    select, button { border: 0; padding: 10px 16px; border-radius: 999px; cursor: pointer; font-weight: 700; }
    select { background: white; color: #07111f; }
    .start { background: #22c55e; color: white; }
    .stop { background: #ef4444; color: white; }
    .status { color: #93c5fd; font-weight: 600; }
    img { width: 100%; max-width: 100%; border-radius: 12px; background: #020617; border: 1px solid #22314d; }
    .hint { margin-top: 10px; color: #9fb3cb; }
  </style>
</head>
<body>
  <div class=\"card\">
    <h1>AI Robotic Hand Control</h1>
    <p class=\"status\" id=\"status\">Status: Ready</p>
    <div class=\"controls\">
      <label for=\"portSelect\">COM Port:</label>
      <select id=\"portSelect\"></select>
      <button class=\"start\" onclick=\"startStream()\">Start</button>
      <button class=\"stop\" onclick=\"stopStream()\">Stop</button>
    </div>
    <img id=\"feed\" src=\"/video_feed\" alt=\"Live camera feed\">
    <p class=\"hint\">The camera feed will appear here and the tracking will start when you press Start.</p>
  </div>

  <script>
    function updateStatus(text) {
      document.getElementById('status').textContent = 'Status: ' + text;
    }

    function populatePorts() {
      fetch('/ports')
        .then(r => r.json())
        .then(data => {
          const select = document.getElementById('portSelect');
          select.innerHTML = '';
          data.ports.forEach(port => {
            const option = document.createElement('option');
            option.value = port;
            option.textContent = port;
            select.appendChild(option);
          });
          if (!select.value && data.ports.length) {
            select.value = data.ports[0];
          }
        })
        .catch(() => {});
    }

    function startStream() {
      const port = document.getElementById('portSelect').value;
      fetch('/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ port: port })
      })
        .then(r => r.text())
        .then(() => updateStatus('Running'));
    }

    function stopStream() {
      fetch('/stop', { method: 'POST' })
        .then(r => r.text())
        .then(() => updateStatus('Stopped'));
    }

    populatePorts();
    setInterval(() => {
      populatePorts();
      fetch('/status').then(r => r.json()).then(data => {
        updateStatus(data.status);
      }).catch(() => {});
    }, 2000);
  </script>
</body>
</html>
"""


def generate_frames():
    global latest_frame
    while True:
        if latest_frame is None:
            time.sleep(0.1)
            continue

        frame = latest_frame
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.route('/')
def index():
    return render_template_string(HTML_PAGE)


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/ports')
def ports():
    detected_ports = [p.device for p in serial.tools.list_ports.comports()]
    return {'ports': detected_ports}


@app.route('/start', methods=['POST'])
def start_tracking():
    global stop_event, thread, latest_status, latest_hand_found, selected_port

    if thread is not None and thread.is_alive():
        latest_status = 'Running'
        return 'already running'

    payload = request.get_json(silent=True) or {}
    selected_port = payload.get('port', selected_port)

    latest_status = 'Starting...'
    stop_event = threading.Event()

    def worker():
        global latest_frame, latest_status, latest_hand_found
        def callback(frame, status, hand_found):
            global latest_frame, latest_status, latest_hand_found
            latest_frame = frame
            latest_status = status
            latest_hand_found = hand_found

        run_hand_tracking(stop_event=stop_event, frame_callback=callback, show_window=False, serial_port=selected_port)

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    return 'started'


@app.route('/stop', methods=['POST'])
def stop_tracking():
    global stop_event, thread, latest_status
    if stop_event is not None:
        stop_event.set()
    if thread is not None and thread.is_alive():
        thread.join(timeout=1.0)
    latest_status = 'Stopped'
    return 'stopped'


@app.route('/status')
def status():
    global latest_status
    return {'status': latest_status}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
