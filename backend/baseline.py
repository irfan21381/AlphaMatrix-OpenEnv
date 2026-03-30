# baseline.py

import requests

BASE_URL = "http://127.0.0.1:8000"

def run_baseline():
    try:
        print("🚀 Starting Baseline Test...\n")

        # Step 1: Initialize
        init_data = {
            "issue": "overheating",
            "cpu": 90,
            "battery": 10,
            "context": "user_call",
            "apps_running": 15
        }

        r = requests.post(f"{BASE_URL}/initialize", json=init_data)
        print("Initialize Response:", r.json(), "\n")

        # Step 2: Actions
        actions = [
            {"action_type": "analyze"},
            {"action_type": "close_apps"}
        ]

        for action in actions:
            r = requests.post(f"{BASE_URL}/step", json=action)
            print("Step Response:", r.json(), "\n")

        # Step 3: Grader
        r = requests.get(f"{BASE_URL}/grader")
        print("Final Score:", r.json())

    except Exception as e:
        print("Error:", str(e))


if __name__ == "__main__":
    run_baseline()