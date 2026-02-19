import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    nvidia_api_key: str
    nvidia_base_url: str
    nvidia_model: str
    system_prompt: str
    verify_twilio_signature: bool
    twilio_auth_token: str
    port: int
    flask_debug: bool
    max_sms_chars: int = 1600
    max_tokens: int = 300
    temperature: float = 0.6


def _as_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def load_settings() -> Settings:
    settings = Settings(
        nvidia_api_key=os.getenv("NVIDIA_API_KEY", "").strip(),
        nvidia_base_url=os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1").strip(),
        nvidia_model=os.getenv("NVIDIA_MODEL", "meta/llama-3.1-8b-instruct").strip(),
        system_prompt=os.getenv("SYSTEM_PROMPT", "You are a concise and helpful SMS assistant.").strip(),
        verify_twilio_signature=_as_bool(os.getenv("VERIFY_TWILIO_SIGNATURE", "false")),
        twilio_auth_token=os.getenv("TWILIO_AUTH_TOKEN", "").strip(),
        port=int(os.getenv("PORT", "5000")),
        flask_debug=_as_bool(os.getenv("FLASK_DEBUG", "false")),
    )

    if not settings.nvidia_api_key:
        raise RuntimeError("Missing NVIDIA_API_KEY in environment.")

    if settings.verify_twilio_signature and not settings.twilio_auth_token:
        raise RuntimeError(
            "VERIFY_TWILIO_SIGNATURE is true, but TWILIO_AUTH_TOKEN is missing."
        )

    return settings
