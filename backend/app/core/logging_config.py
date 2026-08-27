"""
Structured Observability and Logging for CareerBridge AI.
Logs timestamps, agent names, request IDs, duration, and status without exposing sensitive credentials or keys.
"""
import logging
import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional

SENSITIVE_KEYS = {"password", "password_hash", "token", "access_token", "api_key", "secret", "authorization"}

class StructuredJSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage()
        }
        if hasattr(record, "agent_name"):
            log_obj["agent_name"] = record.agent_name
        if hasattr(record, "request_id"):
            log_obj["request_id"] = record.request_id
        if hasattr(record, "duration_ms"):
            log_obj["duration_ms"] = record.duration_ms
        if hasattr(record, "status"):
            log_obj["status"] = record.status
            
        return json.dumps(log_obj)

def mask_sensitive_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Masks passwords and tokens in logged payload dictionaries."""
    sanitized = {}
    for k, v in data.items():
        if any(sk in k.lower() for sk in SENSITIVE_KEYS):
            sanitized[k] = "******"
        elif isinstance(v, dict):
            sanitized[k] = mask_sensitive_dict(v)
        else:
            sanitized[k] = v
    return sanitized

def setup_logging():
    root = logging.getLogger()
    if not root.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(StructuredJSONFormatter())
        root.addHandler(handler)
        root.setLevel(logging.INFO)
