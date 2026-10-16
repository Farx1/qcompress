# Security policy

## Supported versions

Only the `main` branch is maintained. There are no releases yet.

## Reporting a vulnerability

Please use GitHub's private vulnerability reporting
(**Security > Report a vulnerability** on this repository) rather than a
public issue. Expect a first answer within two weeks; this is a personal
research project with no dedicated security team.

## The web backend is not safe to expose publicly

`backend/` (FastAPI) is a local research tool. Do not run it on a public or
shared network.

- **No authentication.** Every endpoint, including compression, export and
  the WebSocket, is open to whoever can reach the port.
- **Binds to all interfaces by default.** `backend/config.py` defaults
  `API_HOST` to `0.0.0.0`. Set `API_HOST=127.0.0.1` unless you need
  another machine to reach it.
- **Loads arbitrary Hugging Face models.** `model_name` from the request is
  passed to `AutoModelForCausalLM.from_pretrained`. A client can make the
  server download any public repository (disk and bandwidth exhaustion) and
  load its weights. Checkpoints in pickle format (`.bin`, `.pt`) can execute
  code on load depending on the `torch` / `transformers` versions; only
  `.safetensors` checkpoints are data-only.
- **Writes exported models to disk** on request, without quota.

If you need remote access, put it behind an authenticating reverse proxy
and restrict `model_name` to an allow-list.
