import logging

from openai import OpenAI

from txtai.config import Settings
from txtai.utils.text_sanitizer import sanitize_sms_reply

LOGGER = logging.getLogger(__name__)


class NIMService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = OpenAI(
            api_key=settings.nvidia_api_key,
            base_url=settings.nvidia_base_url,
        )

    def generate_sms_reply(self, user_message: str) -> str:
        try:
            completion = self.client.chat.completions.create(
                model=self.settings.nvidia_model,
                messages=[
                    {"role": "system", "content": self.settings.system_prompt},
                    {
                        "role": "system",
                        "content": (
                            "Output constraints: reply in plain text only, no markdown formatting, "
                            "and do not use emojis."
                        ),
                    },
                    {"role": "user", "content": user_message},
                ],
                temperature=self.settings.temperature,
                max_tokens=self.settings.max_tokens,
            )
            text = sanitize_sms_reply(completion.choices[0].message.content or "")
            if not text:
                return "I could not generate a response right now. Please try again."
            return text[: self.settings.max_sms_chars]
        except Exception:
            LOGGER.exception("NVIDIA NIM request failed")
            return "Sorry, I hit a temporary error. Please try again in a moment."
