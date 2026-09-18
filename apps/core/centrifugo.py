import time
import jwt
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class CentrifugoService:
    def __init__(self):
        self.api_url = settings.CENTRIFUGO_API_URL
        self.api_key = settings.CENTRIFUGO_API_KEY
        self.secret = settings.CENTRIFUGO_SECRET

    def generate_connection_token(self, user_id: str, exp_seconds: int = 86400) -> str:
        """Generate a client connection JWT for Centrifugo WebSocket connection."""
        claims = {
            "sub": str(user_id),
            "exp": int(time.time()) + exp_seconds,
        }
        return jwt.encode(claims, self.secret, algorithm="HS256")

    def publish(self, channel: str, data: dict) -> bool:
        """Publish real-time message to Centrifugo channel."""
        try:
            headers = {
                "Authorization": f"apikey {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "channel": channel,
                "data": data
            }
            response = requests.post(f"{self.api_url}/publish", json=payload, headers=headers, timeout=3)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Centrifugo publish error (channel {channel}): {e}")
            return False

    def notify_user(self, user_id: str, event_type: str, payload: dict) -> bool:
        """Publish real-time notification to a user's personal channel."""
        channel = f"personal:#{user_id}"
        message = {
            "type": event_type,
            "payload": payload,
            "timestamp": time.time()
        }
        return self.publish(channel, message)

centrifugo_service = CentrifugoService()
