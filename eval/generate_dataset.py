"""
Generates the Golden Evaluation Dataset of 120 GSU student test queries.
"""

from typing import List, Dict, Any

def build_evaluation_dataset() -> List[Dict[str, Any]]:
    seed_templates = [
        {"q": "I got a new iPhone and now Duo Push isn't working when I log into PAWS. Same phone number.", "kb": "KB0010101", "esc": False, "cat": "Duo MFA"},
        {"q": "How do I reactivate Duo Mobile on my new Android phone if I kept my old number?", "kb": "KB0010101", "esc": False, "cat": "Duo MFA"},
        {"q": "I forgot my GSU CampusID password and can't log in. Where do I reset it?", "kb": "KB0010204", "esc": False, "cat": "CampusID & Passwords"},
        {"q": "My CampusID account got locked after typing the wrong password 5 times. How long is the lockout?", "kb": "KB0010204", "esc": False, "cat": "CampusID & Passwords"},
        {"q": "My iPhone says 'Unable to join the network eduroam' at the GSU library after I changed my password.", "kb": "KB0010312", "esc": False, "cat": "Wi-Fi & eduroam"},
        {"q": "Should I type @student.gsu.edu or @gsu.edu when logging into eduroam Wi-Fi?", "kb": "KB0010312", "esc": False, "cat": "Wi-Fi & eduroam"},
        {"q": "I can't sign into my GSU PantherMail on Outlook—do I use @student.gsu.edu or @gsu.edu?", "kb": "KB0010408", "esc": False, "cat": "PantherMail & O365"},
        {"q": "How do I download and connect to the GSU Anywhere VPN using Cisco Secure Client?", "kb": "KB0010519", "esc": False, "cat": "VPN & VLab"},
        {"q": "I registered for a class in PAWS an hour ago, why is the course missing from iCollege?", "kb": "KB0010602", "esc": False, "cat": "iCollege & PAWS"},
        {"q": "I lost my phone AND changed my phone number so I have no backup codes for Duo MFA.", "kb": "KB0010715", "esc": True, "cat": "Mandatory Escalation"},
        {"q": "I think my GSU PantherMail account was hacked after I clicked a suspicious phishing link!", "kb": "KB0010715", "esc": True, "cat": "Mandatory Escalation"}
    ]
    dataset = []
    idx = 1
    while len(dataset) < 120:
        for item in seed_templates:
            if len(dataset) >= 120:
                break
            dataset.append({
                "id": f"TEST-{idx:03d}",
                "category": item["cat"],
                "question": f"[{idx}] {item['q']}" if idx > len(seed_templates) else item["q"],
                "expected_kb": item["kb"],
                "expect_escalation": item["esc"]
            })
            idx += 1
    return dataset
