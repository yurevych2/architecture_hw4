import os
from datetime import datetime

os.makedirs("error_reports", exist_ok=True)

def generate_alert(alert_type: str, description: str):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"error_reports/{timestamp}_{alert_type.replace(' ', '_')}.txt"
    with open(filename, "w") as f:
        f.write(f"Time: {timestamp}\n")
        f.write(f"Alert Type: {alert_type}\n")
        f.write(f"Description: {description}\n")
