"""Deliver new contact inquiries to the owner's WhatsApp number.

Two delivery methods are supported (pick one with WHATSAPP_PROVIDER):

* callmebot  - free, personal notifications to your own number. Quickest setup.
* cloud_api  - Meta's official WhatsApp Business Cloud API. Best for a business.
"""

import logging
import re

import requests

logger = logging.getLogger("gotech.whatsapp")

TIMEOUT_SECONDS = 10


class NotificationError(Exception):
    """Raised when WhatsApp delivery fails."""


def normalise_number(number: str) -> str:
    """Return digits only, in international format, e.g. 0707490519 -> 254707490519."""
    digits = re.sub(r"\D", "", number or "")
    if digits.startswith("0"):
        digits = "254" + digits[1:]
    return digits


def _one_line(text: str, limit: int) -> str:
    """Meta template variables cannot contain newlines or tabs."""
    text = re.sub(r"\s+", " ", text or "").strip()
    return text if len(text) <= limit else text[: limit - 1] + "…"


def format_inquiry(data: dict) -> str:
    """Multi-line text used by the callmebot and plain-text modes."""
    return (
        "New website inquiry - GoTech Solutions\n"
        f"Name: {data.get('name', '')}\n"
        f"Phone: {data.get('phone') or 'not given'}\n"
        f"Email: {data.get('email', '')}\n"
        f"Service: {data.get('service', '')}\n"
        f"Message: {data.get('message', '')}"
    )


class WhatsAppNotifier:
    def send(self, data: dict) -> None:
        raise NotImplementedError


class NullNotifier(WhatsAppNotifier):
    """Used when WHATSAPP_PROVIDER=none: does nothing."""

    def send(self, data: dict) -> None:
        return None


class CallMeBotNotifier(WhatsAppNotifier):
    URL = "https://api.callmebot.com/whatsapp.php"

    def __init__(self, to_number: str, api_key: str):
        if not to_number or not api_key:
            raise ValueError("callmebot needs WHATSAPP_TO and CALLMEBOT_API_KEY.")
        self.to_number = normalise_number(to_number)
        self.api_key = api_key

    def send(self, data: dict) -> None:
        params = {
            "phone": self.to_number,
            "text": format_inquiry(data),
            "apikey": self.api_key,
        }
        try:
            response = requests.get(self.URL, params=params, timeout=TIMEOUT_SECONDS)
        except requests.RequestException as exc:
            raise NotificationError(f"CallMeBot request failed: {exc}") from exc
        if response.status_code != 200:
            raise NotificationError(
                f"CallMeBot returned {response.status_code}: {response.text[:200]}"
            )


class CloudAPINotifier(WhatsAppNotifier):
    """Meta WhatsApp Business Cloud API.

    Business-initiated messages must use an approved *template*. Create one in
    WhatsApp Manager with 5 body variables, in this order:
        {{1}} name   {{2}} phone   {{3}} email   {{4}} service   {{5}} message
    e.g.  "New GoTech inquiry from {{1}} ({{2}}, {{3}}). Service: {{4}}. Message: {{5}}"

    If WHATSAPP_CLOUD_TEMPLATE is left blank, a plain text message is sent
    instead, which only works inside the 24-hour window after you last messaged
    the business number (useful for testing).
    """

    def __init__(self, to_number, access_token, phone_number_id,
                 template_name="", template_language="en", api_version="v21.0"):
        if not (to_number and access_token and phone_number_id):
            raise ValueError(
                "cloud_api needs WHATSAPP_TO, WHATSAPP_CLOUD_TOKEN and "
                "WHATSAPP_CLOUD_PHONE_NUMBER_ID."
            )
        self.to_number = normalise_number(to_number)
        self.template_name = template_name
        self.template_language = template_language
        self.url = f"https://graph.facebook.com/{api_version}/{phone_number_id}/messages"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    def _payload(self, data: dict) -> dict:
        base = {"messaging_product": "whatsapp", "to": self.to_number}
        if not self.template_name:
            return {**base, "type": "text",
                    "text": {"body": format_inquiry(data), "preview_url": False}}

        values = [
            _one_line(data.get("name"), 100),
            _one_line(data.get("phone") or "not given", 40),
            _one_line(data.get("email"), 120),
            _one_line(data.get("service"), 80),
            _one_line(data.get("message"), 800),
        ]
        return {
            **base,
            "type": "template",
            "template": {
                "name": self.template_name,
                "language": {"code": self.template_language},
                "components": [{
                    "type": "body",
                    "parameters": [{"type": "text", "text": v} for v in values],
                }],
            },
        }

    def send(self, data: dict) -> None:
        try:
            response = requests.post(
                self.url, headers=self.headers, json=self._payload(data),
                timeout=TIMEOUT_SECONDS,
            )
        except requests.RequestException as exc:
            raise NotificationError(f"WhatsApp Cloud API request failed: {exc}") from exc
        if response.status_code >= 300:
            raise NotificationError(
                f"WhatsApp Cloud API returned {response.status_code}: {response.text[:300]}"
            )
