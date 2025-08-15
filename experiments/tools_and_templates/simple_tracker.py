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
        "status": "in_progress",
        "paused_time_minutes": 0,
        "pause_history": []
    }
    
    with open("experiment_status.json", "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"�� Started experiment: {exp_name}")
    print(f"⏰ Start time: {data['start_time']}")

def pause_experiment():
    """Pause experiment tracking"""
    if not os.path.exists("experiment_status.json"):
        print("❌ No active experiment found")
        return
    
    with open("experiment_status.json", "r") as f:
        data = json.load(f)
    
    if data["status"] == "paused":
        print("⚠️  Experiment is already paused")
        return
    
    pause_time = datetime.now().isoformat()
    data["status"] = "paused"
    data["pause_start"] = pause_time
    
    with open("experiment_status.json", "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"⏸️  Experiment paused at: {pause_time}")

def resume_experiment():
    """Resume experiment tracking"""
    if not os.path.exists("experiment_status.json"):
        print("❌ No active experiment found")
        return
    
    with open("experiment_status.json", "r") as f:
        data = json.load(f)
    
    if data["status"] != "paused":
        print("⚠️  Experiment is not paused")
        return
    
    if "pause_start" not in data:
        print("❌ No pause start time found")
        return
    
    resume_time = datetime.now().isoformat()
    pause_start = datetime.fromisoformat(data["pause_start"])
    resume_datetime = datetime.fromisoformat(resume_time)
    
    # Calculate pause duration
    pause_duration = (resume_datetime - pause_start).total_seconds() / 60
    
    # Add to pause history
    pause_record = {
        "pause_start": data["pause_start"],
        "pause_end": resume_time,
        "duration_minutes": round(pause_duration, 1)
    }
    data["pause_history"].append(pause_record)
    
    # Update total paused time
    data["paused_time_minutes"] += round(pause_duration, 1)
    
    # Resume experiment
    data["status"] = "in_progress"
    data.pop("pause_start", None)
    
    with open("experiment_status.json", "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"▶️  Experiment resumed at: {resume_time}")
    print(f"⏸️  Pause duration: {pause_duration:.1f} minutes")

def end_experiment(success: bool = True):
    """End experiment tracking"""
    if not os.path.exists("experiment_status.json"):
        print("❌ No active experiment found")
        return
    
    with open("experiment_status.json", "r") as f:
        data = json.load(f)
    
    # If experiment is paused, resume it first to get final pause time
    if data["status"] == "paused":
        print("⚠️  Experiment is paused, resuming to calculate final pause time...")
        resume_experiment()
        # Reload data after resume
        with open("experiment_status.json", "r") as f:
            data = json.load(f)
    
    data["end_time"] = datetime.now().isoformat()
    data["status"] = "completed" if success else "failed"
    
    # Calculate total duration (excluding paused time)
    start = datetime.fromisoformat(data["start_time"])
    end = datetime.fromisoformat(data["end_time"])
    total_duration = (end - start).total_seconds() / 60
    active_duration = total_duration - data["paused_time_minutes"]
    
    data["total_duration_minutes"] = round(total_duration, 1)
    data["active_duration_minutes"] = round(active_duration, 1)
    
    with open("results.json", "w") as f:
        json.dump(data, f, indent=2)
    
    os.remove("experiment_status.json")
    
    print(f"✅ Experiment completed!")
    print(f"⏱️  Total time: {total_duration:.1f} minutes")
    print(f"⏸️  Paused time: {data['paused_time_minutes']:.1f} minutes")
    print(f"🚀 Active time: {active_duration:.1f} minutes")

def show_status():
    """Show current experiment status"""
    if not os.path.exists("experiment_status.json"):
        print("❌ No active experiment found")
        return
    
    with open("experiment_status.json", "r") as f:
        data = json.load(f)
    
    print(f"🔬 Experiment: {data['experiment']}")
    print(f"📊 Status: {data['status']}")
    print(f"⏰ Start time: {data['start_time']}")
    
    if data["status"] == "paused" and "pause_start" in data:
        print(f"⏸️  Paused since: {data['pause_start']}")
    
    if data["paused_time_minutes"] > 0:
        print(f"⏸️  Total paused time: {data['paused_time_minutes']:.1f} minutes")
    
    if data["pause_history"]:
        print(f"📝 Pause history: {len(data['pause_history'])} pauses")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python simple_tracker.py <command> [args...]")
        print("Commands:")
        print("  start <exp_name>     - Start a new experiment")
        print("  pause                - Pause the current experiment")
        print("  resume               - Resume the paused experiment")
        print("  end [success/fail]   - End the current experiment")
        print("  status               - Show current experiment status")
    elif sys.argv[1] == "start":
        if len(sys.argv) < 3:
            print("❌ Please provide experiment name")
        else:
            start_experiment(sys.argv[2])
    elif sys.argv[1] == "pause":
        pause_experiment()
    elif sys.argv[1] == "resume":
        resume_experiment()
    elif sys.argv[1] == "end":
        success = len(sys.argv) < 3 or sys.argv[2] != "fail"
        end_experiment(success)
    elif sys.argv[1] == "status":
        show_status()
    else:
        print(f"❌ Unknown command: {sys.argv[1]}")