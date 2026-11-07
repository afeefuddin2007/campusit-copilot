"""
Centralized configuration for CampusIT Copilot.
Manages environment variables, GSU ServiceNow portal references, and RAG thresholds.
"""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    APP_NAME: str = "GSU CampusIT Copilot"
    APP_VERSION: str = "1.0.0"
    GSU_PORTAL_URL: str = "https://gsutech.service-now.com/sp"
    GSU_CAMPUSID_URL: str = "https://mycampusid.gsu.edu"
    GSU_DUO_PORTAL_URL: str = "https://duo.gsu.edu"
    GSU_HELPDESK_PHONE: str = "404-413-HELP (404-413-4357)"
    GSU_HELPDESK_EMAIL: str = "help@gsu.edu"

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip()
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    CHROMA_PERSIST_DIR: str = os.getenv(
        "CHROMA_PERSIST_DIR",
        str(Path(__file__).resolve().parent.parent / "chroma_db"),
    )
    COLLECTION_NAME: str = "gsu_servicenow_kb_vector_v1"
    TOP_K_RESULTS: int = 3
    MIN_CONFIDENCE_THRESHOLD: float = 0.22


settings = Settings()
