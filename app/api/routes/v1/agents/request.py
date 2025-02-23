from typing import Optional, Dict

from pydantic import BaseModel


class UpdateMonitoringConfigRequest(BaseModel):
    check_interval: Optional[int] = None
    risk_threshold: Optional[str] = None
    notification_settings: Optional[Dict] = None