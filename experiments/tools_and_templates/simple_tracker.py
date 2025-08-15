#!/usr/bin/env python3
"""Simple experiment tracking for SpecPlane experiments"""

import json
import os
from datetime import datetime
from pathlib import Path

def start_experiment(exp_name: str):
    """Start tracking an experiment"""
    data = {
        "experiment": exp_name,
        "start_time": datetime.now().isoformat(),
        "status": "in_progress"
    }
    
    with open("experiment_status.json", "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"🔬 Started experiment: {exp_name}")
    print(f"⏰ Start time: {data['start_time']}")

def end_experiment(success: bool = True):
    """End experiment tracking"""
    if not os.path.exists("experiment_status.json"):
        print("❌ No active experiment found")
        return
    
    with open("experiment_status.json", "r") as f:
        data = json.load(f)
    
    data["end_time"] = datetime.now().isoformat()
    data["status"] = "completed" if success else "failed"
    
    # Calculate duration
    start = datetime.fromisoformat(data["start_time"])
    end = datetime.fromisoformat(data["end_time"])
    duration = (end - start).total_seconds() / 60
    data["duration_minutes"] = round(duration, 1)
    
    with open("results.json", "w") as f:
        json.dump(data, f, indent=2)
    
    os.remove("experiment_status.json")
    
    print(f"✅ Experiment completed in {duration:.1f} minutes")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python simple_tracker.py start <exp_name> | end [success/fail]")
    elif sys.argv[1] == "start":
        start_experiment(sys.argv[2])
    elif sys.argv[1] == "end":
        success = len(sys.argv) < 3 or sys.argv[2] != "fail"
        end_experiment(success)