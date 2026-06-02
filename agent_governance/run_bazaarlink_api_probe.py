r"""Probe a BazaarLink OpenAI-compatible API key without storing secrets.

Usage:
  $env:BAZAARLINK_API_KEY = Read-Host "Paste BazaarLink API key"
  python agent_governance\run_bazaarlink_api_probe.py
  Remove-Item Env:\BAZAARLINK_API_KEY

This script reads the key only from the environment. It does not write the key
to disk and does not modify benchmark evidence.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://bazaarlink.ai/api/v1"
DEFAULT_MODEL = "auto:free"


def _post_json(url: str, api_key: str, payload: dict[str, object], timeout: float) -> tuple[int, dict[str, object]]:
    body = json.dumps(payload).encode("utf-8")
    request = Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urlopen(request, timeout=timeout) as response:
        status = int(response.status)
        data = json.loads(response.read().decode("utf-8"))
    return status, data


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a minimal BazaarLink API probe.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args()

    api_key = os.environ.get("BAZAARLINK_API_KEY")
    if not api_key:
        print("BAZAARLINK_API_PROBE_SKIPPED")
        print("reason=missing BAZAARLINK_API_KEY environment variable")
        print("secret_policy=do_not_put_api_keys_in_repo_or_command_history")
        return 2

    payload = {
        "model": args.model,
        "messages": [
            {
                "role": "user",
                "content": "Reply with exactly: API_OK",
            }
        ],
        "temperature": 0,
        "max_tokens": 8,
    }

    started = time.perf_counter()
    try:
        status, data = _post_json(
            f"{args.base_url.rstrip('/')}/chat/completions",
            api_key,
            payload,
            args.timeout,
        )
    except HTTPError as exc:
        print("BAZAARLINK_API_PROBE_FAILED")
        print(f"http_status={exc.code}")
        print("error_type=http_error")
        return 1
    except (URLError, TimeoutError) as exc:
        print("BAZAARLINK_API_PROBE_FAILED")
        print(f"error_type={type(exc).__name__}")
        return 1

    elapsed_ms = (time.perf_counter() - started) * 1000.0
    choices = data.get("choices", [])
    content = ""
    if choices and isinstance(choices, list):
        message = choices[0].get("message", {}) if isinstance(choices[0], dict) else {}
        content = str(message.get("content", "")).strip()

    usage = data.get("usage", {}) if isinstance(data.get("usage", {}), dict) else {}

    print("BAZAARLINK_API_PROBE_OK")
    print(f"http_status={status}")
    print(f"model={args.model}")
    print(f"latency_ms={elapsed_ms:.3f}")
    print(f"response={content[:80]}")
    print(f"prompt_tokens={usage.get('prompt_tokens', 'unknown')}")
    print(f"completion_tokens={usage.get('completion_tokens', 'unknown')}")
    print("secret_policy=api_key_read_from_environment_only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
