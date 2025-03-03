from datetime import datetime
from typing import Optional


def parse_date(date_string: Optional[str]) -> Optional[datetime]:
    """
    Parse date strings from HubSpot API into datetime objects.

    Args:
        date_string: ISO format date string from HubSpot API

    Returns:
        Parsed datetime object or None if input is None/empty
    """
    if not date_string:
        return None

    try:
        # HubSpot typically uses ISO 8601 format
        return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
    except (ValueError, TypeError):
        # Fallback parsing if the format is different
        try:
            return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ")
        except (ValueError, TypeError):
            try:
                return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
            except (ValueError, TypeError):
                # Log the error and return None if all parsing attempts fail
                print(f"Failed to parse date: {date_string}")
                return None
