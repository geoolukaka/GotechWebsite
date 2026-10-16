import os

from dotenv import load_dotenv

load_dotenv()


def _split_csv(value: str) -> list:
    return [v.strip() for v in value.split(",") if v.strip()]


class Config:
    # ------------------------------------------------------------------
    # General
    # ------------------------------------------------------------------
    STORAGE_BACKEND = os.environ.get("STORAGE_BACKEND", "none").lower()  # "none" | "mysql" | "google_sheets"
    ALLOWED_ORIGINS = _split_csv(
        os.environ.get(
            "ALLOWED_ORIGINS",
            "http://localhost:8000,http://127.0.0.1:8000",
        )
    )
    ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY", "")

    # ------------------------------------------------------------------
    # MySQL
    # ------------------------------------------------------------------
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "gotech_contact")

    # ------------------------------------------------------------------
    # Google Sheets
    # ------------------------------------------------------------------
    GOOGLE_SERVICE_ACCOUNT_FILE = os.environ.get(
        "GOOGLE_SERVICE_ACCOUNT_FILE", "service-account.json"
    )
    GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "")
    GOOGLE_SHEET_WORKSHEET = os.environ.get("GOOGLE_SHEET_WORKSHEET", "Submissions")

    # ------------------------------------------------------------------
    # WhatsApp delivery of new inquiries
    # ------------------------------------------------------------------
    WHATSAPP_PROVIDER = os.environ.get("WHATSAPP_PROVIDER", "none").lower()  # "callmebot" | "cloud_api" | "none"
    WHATSAPP_TO = os.environ.get("WHATSAPP_TO", "254707490519")  # 0707490519 in international format

    # callmebot
    CALLMEBOT_API_KEY = os.environ.get("CALLMEBOT_API_KEY", "")

    # Meta WhatsApp Business Cloud API
    WHATSAPP_CLOUD_TOKEN = os.environ.get("WHATSAPP_CLOUD_TOKEN", "")
    WHATSAPP_CLOUD_PHONE_NUMBER_ID = os.environ.get("WHATSAPP_CLOUD_PHONE_NUMBER_ID", "")
    WHATSAPP_CLOUD_TEMPLATE = os.environ.get("WHATSAPP_CLOUD_TEMPLATE", "")
    WHATSAPP_CLOUD_TEMPLATE_LANG = os.environ.get("WHATSAPP_CLOUD_TEMPLATE_LANG", "en")
    WHATSAPP_CLOUD_API_VERSION = os.environ.get("WHATSAPP_CLOUD_API_VERSION", "v21.0")

    # Basic spam protection: max submissions per IP per window
    RATE_LIMIT_MAX = int(os.environ.get("RATE_LIMIT_MAX", 5))
    RATE_LIMIT_WINDOW_SECONDS = int(os.environ.get("RATE_LIMIT_WINDOW_SECONDS", 600))
