"""Apply Prisma migrations and seed against Supabase (repo-root `.env.local`).

Refuses DATABASE_URL / DIRECT_URL that look like local or Docker Postgres unless
ALLOW_LOCAL_MIGRATE=1 is set.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _forbid_local_urls() -> None:
    if os.environ.get("ALLOW_LOCAL_MIGRATE") == "1":
        return
    for label in ("DATABASE_URL", "DIRECT_URL"):
        u = os.environ.get(label, "").lower()
        if not u.strip():
            print(f"Missing {label} in .env.local (or .env).", file=sys.stderr)
            sys.exit(1)
        bad = ("localhost", "127.0.0.1", "@db:", "host.docker.internal")
        if any(b in u for b in bad):
            print(
                f"{label} points at a local or Docker hostname. "
                "Use Supabase connection strings from Project Settings, "
                "or set ALLOW_LOCAL_MIGRATE=1 to override.",
                file=sys.stderr,
            )
            sys.exit(2)


def main() -> None:
    backend = Path(__file__).resolve().parent.parent
    os.chdir(backend)
    if str(backend) not in sys.path:
        sys.path.insert(0, str(backend))

    from app.env_bootstrap import load_repo_environment

    load_repo_environment()
    _forbid_local_urls()

    exe = sys.executable
    subprocess.check_call([exe, "-m", "prisma", "migrate", "deploy"])
    subprocess.check_call([exe, "-m", "prisma", "generate"])
    subprocess.check_call([exe, "-m", "app.seed"])


if __name__ == "__main__":
    main()
