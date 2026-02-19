import logging

from flask import Blueprint, current_app, request
from twilio.twiml.messaging_response import MessagingResponse

from txtai.config import Settings
from txtai.services.nim import NIMService
from txtai.services.twilio_auth import is_valid_twilio_request

sms_blueprint = Blueprint("sms", __name__)
LOGGER = logging.getLogger(__name__)


def _get_settings() -> Settings:
    return current_app.config["SETTINGS"]


def _get_nim_service() -> NIMService:
    service = current_app.extensions.get("nim_service")
    if service is None:
        service = NIMService(_get_settings())
        current_app.extensions["nim_service"] = service
    return service


@sms_blueprint.get("/health")
def health_check():
    return {"status": "ok"}, 200


@sms_blueprint.post("/webhook/sms")
def sms_webhook():
    settings = _get_settings()
    if not is_valid_twilio_request(request, settings):
        return "Forbidden", 403

    incoming_body = request.form.get("Body", "").strip()
    sender = request.form.get("From", "unknown")
    LOGGER.info("Incoming SMS from %s", sender)

    if not incoming_body:
        reply_text = "Please send a message so I can help."
    else:
        reply_text = _get_nim_service().generate_sms_reply(incoming_body)

    response = MessagingResponse()
    response.message(reply_text)
    return str(response), 200, {"Content-Type": "application/xml"}
