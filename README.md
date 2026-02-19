# TxtAI - SMS AI Chatbot POC

SMS chatbot proof-of-concept using Flask + Twilio + NVIDIA NIM (OpenAI-compatible API).

## What this app does

1. Twilio receives an inbound SMS and sends a webhook `POST` to this Flask app.
2. The app forwards the incoming message to NVIDIA NIM via the `openai` Python client.
3. The app returns a TwiML SMS response to Twilio.
4. Twilio sends that response back to the sender's phone.

## Project files

- `app.py`: thin entrypoint
- `txtai/__init__.py`: Flask app factory
- `txtai/config.py`: env/config loading and validation
- `txtai/routes/sms.py`: webhook + health routes
- `txtai/services/nim.py`: NVIDIA NIM integration
- `txtai/services/twilio_auth.py`: Twilio signature validation
- `txtai/utils/text_sanitizer.py`: markdown and emoji cleanup
- `Dockerfile`: container image for Flask app
- `docker-compose.yml`: app + ngrok stack
- `scripts/start-with-ngrok.ps1`: start stack and print ngrok HTTPS URL
- `.env`: local secrets/config (ignored by git)
- `.env-sample`: config template

## Environment variables

Copy `.env-sample` to `.env` and fill values:

- `TWILIO_AUTH_TOKEN` (required only when `VERIFY_TWILIO_SIGNATURE=true`)
- `NVIDIA_API_KEY`
- `NVIDIA_BASE_URL` (default `https://integrate.api.nvidia.com/v1`)
- `NVIDIA_MODEL` (pick a model available in your NVIDIA NIM account)
- `SYSTEM_PROMPT` (optional)
- `VERIFY_TWILIO_SIGNATURE` (`true` recommended once webhook URL is fixed)
- `PORT` (default `5000`)
- `NGROK_AUTHTOKEN` (required for containerized ngrok)

Twilio setup values like account SID and phone number are configured in Twilio Console for webhook routing; they are not runtime-required by this app code.

## Run locally

```powershell
# from project root
.\venv\Scripts\Activate.ps1
python app.py
```

Server endpoints:

- Health check: `http://localhost:5000/health`
- Twilio webhook: `http://localhost:5000/webhook/sms`

## Expose local server with ngrok

In a second terminal:

```powershell
ngrok http 5000
```

Copy the HTTPS forwarding URL, e.g. `https://abc123.ngrok-free.app`.

## Dockerized run (app + ngrok)

Assuming Docker Desktop is installed and running:

```powershell
# One-shot start: builds, starts, and prints webhook URL
powershell -ExecutionPolicy Bypass -File .\scripts\start-with-ngrok.ps1
```

This command returns the final URL you should paste into Twilio:

`https://<ngrok-domain>/webhook/sms`

Manual docker commands:

```powershell
docker compose up -d --build
```

Check ngrok API directly for tunnels:

```powershell
Invoke-RestMethod http://localhost:4040/api/tunnels
```

Stop services:

```powershell
docker compose down
```

## Configure Twilio webhook

1. Open Twilio Console -> Phone Numbers -> Manage -> Active numbers.
2. Select your Twilio number.
3. Under **Messaging**, set **A message comes in** to:
   `https://<your-ngrok-domain>/webhook/sms`
4. Method: `HTTP POST`.
5. Save.

Now text your Twilio number and you should receive an AI reply.

## Notes

- If `VERIFY_TWILIO_SIGNATURE=true`, Twilio request signatures are validated.
- Replies are capped to ~1600 chars for SMS practicality.
