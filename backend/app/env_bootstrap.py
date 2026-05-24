"""Load repo-root `.env` / `.env.local` and optional `backend/.env` into `os.environ` (for Prisma and Settings)."""

from pathlib import Path

from dotenv import load_dotenv

_REPO_ROOT = Path(__file__).resolve().parents[2]
_BACKEND_ROOT = Path(__file__).resolve().parents[1]


def load_repo_environment() -> None:
    if (_REPO_ROOT / ".env").is_file():
        load_dotenv(_REPO_ROOT / ".env", override=False)
    if (_REPO_ROOT / ".env.local").is_file():
        load_dotenv(_REPO_ROOT / ".env.local", override=True)
    if (_BACKEND_ROOT / ".env").is_file():
        load_dotenv(_BACKEND_ROOT / ".env", override=True)
