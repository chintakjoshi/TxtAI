from flask import Request
from twilio.request_validator import RequestValidator

from txtai.config import Settings


def is_valid_twilio_request(req: Request, settings: Settings) -> bool:
    if not settings.verify_twilio_signature:
        return True

    validator = RequestValidator(settings.twilio_auth_token)
    signature = req.headers.get("X-Twilio-Signature", "")
    form_data = req.form.to_dict(flat=True)
    return validator.validate(req.url, form_data, signature)
