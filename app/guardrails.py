"""
Deterministic & Semantic Safety Guardrail Engine for GSU CampusIT Copilot.
"""

import re
import uuid
from typing import Dict, Any, List
from app.config import settings

ESCALATION_RULES: List[Dict[str, Any]] = [
    {
        "rule_id": "ESC_MFA_HARD_LOCKOUT",
        "category": "Duo MFA Identity Verification Required",
        "priority": "P2 - High",
        "assignment_group": "GSU IIT Identity & Access Management (ServiceNow)",
        "reason": "Student cannot complete Duo self-service reactivation because they lack access to their old device, changed their phone number, or have no backup MFA passcodes.",
        "patterns": [
            r"(changed|new)\s+(my\s+)?(phone\s+)?number.*(duo|2fa|mfa|login|paws)",
            r"(duo|2fa|mfa).*(changed|new)\s+(my\s+)?(phone\s+)?number",
            r"(lost|stole|stolen|broke|broken|destroyed).*(phone|device).*(no\s+backup|can'?t\s+get\s+code|new\s+number|locked\s+out)",
            r"no\s+backup\s+(code|device|method)",
            r"need\s+a\s+(duo\s+)?bypass\s+code",
            r"duo\s+locked\s+me\s+out.*(can'?t|no)\s+(text|call|sms)"
        ]
    },
    {
        "rule_id": "ESC_SECURITY_COMPROMISE",
        "category": "Information Security / Compromised Account",
        "priority": "P1 - Critical",
        "assignment_group": "GSU CyberSecurity & Incident Response Team (CSIRT)",
        "reason": "Suspected account compromise, unauthorized login, or phishing link exposure.",
        "patterns": [
            r"\b(hacked|compromised|phishing|scammed|stole\s+my\s+password)\b",
            r"someone\s+(else\s+)?(logged\s+into|is\s+using|changed)\s+my\s+(account|email|paws|campusid)",
            r"clicked\s+a\s+(fake|suspicious|phishing|scam)\s+link",
            r"sending\s+spam\s+from\s+my\s+(panthermail|email)"
        ]
    },
    {
        "rule_id": "ESC_ADMIN_HOLD_OR_DISABLED",
        "category": "Administrative Account Hold / Disabled Status",
        "priority": "P2 - High",
        "assignment_group": "GSU IIT Tier-2 Account Provisioning / Registrar Liaison",
        "reason": "Account is administratively disabled, revoked, or blocked by an institutional hold.",
        "patterns": [
            r"account\s+(is\s+)?(disabled|suspended|revoked|terminated|deactivated)\s*(by\s+admin)?",
            r"(administrative|security|registrar|immunization|financial)\s+hold",
            r"mycampusid\s+says\s+(not\s+found|disabled|ineligible|contact\s+administrator)",
            r"reset\s+password\s+didn'?t\s+work\s+still\s+locked"
        ]
    }
]

def evaluate_escalation(user_query: str, top_similarity_score: float, conversation_history: List[Dict[str, str]] | None = None) -> Dict[str, Any]:
    normalized = user_query.lower().strip()
    combined_context = normalized
    if conversation_history:
        recent_user_msgs = [m.get("content", "").lower() for m in conversation_history[-2:] if m.get("role") == "user"]
        combined_context = " ".join(recent_user_msgs + [normalized])

    for rule in ESCALATION_RULES:
        for pattern in rule["patterns"]:
            if re.search(pattern, combined_context):
                ticket_id = f"INC-GSU-{uuid.uuid4().hex[:6].upper()}"
                return {
                    "should_escalate": True,
                    "rule_id": rule["rule_id"],
                    "trigger_type": "POLICY_GUARDRAIL",
                    "ticket": {
                        "ticket_id": ticket_id,
                        "portal_url": settings.GSU_PORTAL_URL,
                        "priority": rule["priority"],
                        "category": rule["category"],
                        "assignment_group": rule["assignment_group"],
                        "reason": rule["reason"],
                        "student_summary": user_query.strip(),
                        "contact_phone": settings.GSU_HELPDESK_PHONE,
                        "contact_email": settings.GSU_HELPDESK_EMAIL,
                        "walk_in_location": "Library North 2nd Floor (Atlanta)"
                    }
                }

    if top_similarity_score < settings.MIN_CONFIDENCE_THRESHOLD:
        ticket_id = f"INC-GSU-{uuid.uuid4().hex[:6].upper()}"
        return {
            "should_escalate": True,
            "rule_id": "ESC_LOW_CONFIDENCE_UNGROUNDED",
            "trigger_type": "LOW_RETRIEVAL_CONFIDENCE",
            "ticket": {
                "ticket_id": ticket_id,
                "portal_url": settings.GSU_PORTAL_URL,
                "priority": "P3 - Standard Triage",
                "category": "Unclassified / General IT Inquiry",
                "assignment_group": "GSU IIT Tier-1 Service Desk Triage",
                "reason": f"Query fell outside approved GSU self-service documentation thresholds (score {top_similarity_score:.2f}).",
                "student_summary": user_query.strip(),
                "contact_phone": settings.GSU_HELPDESK_PHONE,
                "contact_email": settings.GSU_HELPDESK_EMAIL,
                "walk_in_location": "Submit at https://gsutech.service-now.com/sp"
            }
        }

    return {"should_escalate": False, "rule_id": None, "trigger_type": None, "ticket": None}
