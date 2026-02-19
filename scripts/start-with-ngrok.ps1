param(
    [int]$TimeoutSeconds = 60
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path ".env")) {
    throw "Missing .env file. Copy .env-sample to .env and add secrets first."
}

$tokenInEnvFile = Select-String -Path ".env" -Pattern "^\s*NGROK_AUTHTOKEN\s*=\s*(.+?)\s*$" | Select-Object -First 1
$hasNonEmptyEnvToken = $null -ne $tokenInEnvFile
if (-not $hasNonEmptyEnvToken -and [string]::IsNullOrWhiteSpace($env:NGROK_AUTHTOKEN)) {
    throw "NGROK_AUTHTOKEN is missing. Add it to .env or set it in your shell environment."
}

docker compose up -d --build

$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
$publicUrl = $null

while ((Get-Date) -lt $deadline) {
    Start-Sleep -Seconds 2
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -Method Get
        $httpsTunnel = $response.tunnels | Where-Object { $_.public_url -like "https://*" } | Select-Object -First 1
        if ($httpsTunnel) {
            $publicUrl = $httpsTunnel.public_url
            break
        }
    } catch {
        # Wait for ngrok agent/API to become ready.
    }
}

if (-not $publicUrl) {
    throw "Could not fetch ngrok forwarding URL within $TimeoutSeconds seconds."
}

$webhookUrl = "$publicUrl/webhook/sms"
Write-Host "ngrok forwarding URL: $publicUrl"
Write-Host "Twilio webhook URL:    $webhookUrl"
Write-Output $webhookUrl
