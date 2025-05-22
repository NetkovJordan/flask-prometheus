import os
from flask import Flask, jsonify, Response
from prometheus_client import Gauge, generate_latest, CONTENT_TYPE_LATEST
import psutil
import random
import time
import threading

app = Flask(__name__)

# Metrics
cpu_usage_gauge = Gauge('app_cpu_usage_percent', 'CPU usage percentage of the application')
memory_usage = Gauge('app_memory_usage_mb', 'Memory usage in MB')
disk_usage = Gauge('app_disk_usage_percent', 'Disk usage percentage')
net_sent = Gauge('app_network_bytes_sent', 'Network bytes sent')
net_recv = Gauge('app_network_bytes_recv', 'Network bytes received')

# Background threads
def update_cpu_usage():
    while True:
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_usage_gauge.set(cpu_percent)
        time.sleep(4)

def update_system_metrics():
    while True:
        memory = psutil.virtual_memory().used / (1024 * 1024)
        disk = psutil.disk_usage('/').percent
        net = psutil.net_io_counters()
        memory_usage.set(memory)
        disk_usage.set(disk)
        net_sent.set(net.bytes_sent)
        net_recv.set(net.bytes_recv)
        time.sleep(5)

threading.Thread(target=update_cpu_usage, daemon=True).start()
threading.Thread(target=update_system_metrics, daemon=True).start()

# Routes
@app.route('/')
def index():
    return "Hello from Flask with Prometheus metrics!"

@app.route('/data')
def data():
    return jsonify({"value": random.randint(1, 100)})

@app.route('/metrics')
def metrics_endpoint():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

# Entry point
def main():
    host = os.getenv("FLASK_RUN_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_RUN_PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    print(f"Starting Flask app on {host}:{port} (debug={debug})")
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    main()
