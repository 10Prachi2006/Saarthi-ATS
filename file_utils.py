import csv
import os

CANDIDATES_FILE = "candidates.csv"
FIELDNAMES = ["name", "phone", "resume_summary", "AI_score", "shortlist_status", "call_status", "vapi_result"]

def load_candidates():
    if not os.path.exists(CANDIDATES_FILE):
        with open(CANDIDATES_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
        return []
    with open(CANDIDATES_FILE, "r") as f:
        return list(csv.DictReader(f))

def save_candidate(candidate):
    with open(CANDIDATES_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow(candidate)

def update_candidate(name, phone, updates):
    candidates = load_candidates()
    for c in candidates:
        if c["name"] == name and c["phone"] == phone:
            c.update(updates)
            break
    with open(CANDIDATES_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(candidates)
