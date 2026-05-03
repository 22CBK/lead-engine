import os
import json

def get_status_path():
    return os.path.join(os.path.dirname(__file__), '..', 'data', 'engine_status.json')

def update_status(state="idle", message="Waiting to start", progress=0):
    """
    state: idle | running | error | done
    message: String describing current action
    progress: Integer 0-100
    """
    path = get_status_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    status_data = {
        "state": state,
        "message": message,
        "progress": progress
    }
    
    with open(path, 'w') as f:
        json.dump(status_data, f)

def get_status():
    path = get_status_path()
    if not os.path.exists(path):
        return {"state": "idle", "message": "Waiting to start", "progress": 0}
        
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except:
        return {"state": "idle", "message": "Waiting to start", "progress": 0}
