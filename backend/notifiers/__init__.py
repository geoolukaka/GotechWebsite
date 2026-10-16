from .whatsapp import (
    CallMeBotNotifier,
    CloudAPINotifier,
    NullNotifier,
    WhatsAppNotifier,
    format_inquiry,
)


def get_notifier(config) -> WhatsAppNotifier:
    """Pick the WhatsApp delivery method from WHATSAPP_PROVIDER in .env."""
    provider = config["WHATSAPP_PROVIDER"]
    to_number = config["WHATSAPP_TO"]

    if provider == "none":
        return NullNotifier()

    if provider == "callmebot":
        return CallMeBotNotifier(to_number=to_number, api_key=config["CALLMEBOT_API_KEY"])

    if provider == "cloud_api":
        return CloudAPINotifier(
            to_number=to_number,
            access_token=config["WHATSAPP_CLOUD_TOKEN"],
            phone_number_id=config["WHATSAPP_CLOUD_PHONE_NUMBER_ID"],
            template_name=config["WHATSAPP_CLOUD_TEMPLATE"],
            template_language=config["WHATSAPP_CLOUD_TEMPLATE_LANG"],
            api_version=config["WHATSAPP_CLOUD_API_VERSION"],
        )

    raise ValueError(
        f"Unknown WHATSAPP_PROVIDER '{provider}'. Use 'callmebot', 'cloud_api' or 'none'."
    )
