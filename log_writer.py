import json, os, datetime

def log_event(data, folder="logs"):
    """Appends a JSON entry to a file in the logs folder."""
    os.makedirs(folder, exist_ok=True)
    date_str = datetime.date.today().isoformat()
    path = os.path.join(folder, f"nexa_log_{date_str}.json")

    # Load existing logs if file exists
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            logs = []
    else:
        logs = []

    logs.append(data)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
