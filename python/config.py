import os
from pathlib import Path


def load_api_key() -> str:
    env_path = Path(__file__).resolve().parent.parent / ".env.football"
    if env_path.exists():
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            if key.strip() == "FOOTBALL_DATA_API_KEY":
                return value.strip().strip('"\'')

    return os.getenv("FOOTBALL_DATA_API_KEY", "").strip()
