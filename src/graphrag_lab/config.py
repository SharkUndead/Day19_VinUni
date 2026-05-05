from dataclasses import dataclass
from os import getenv
from pathlib import Path


def load_local_env() -> None:
    current = Path(__file__).resolve()
    project_root = next(
        (
            parent
            for parent in current.parents
            if (parent / ".env").exists() or (parent / "pyproject.toml").exists()
        ),
        current.parents[2],
    )
    env_path = project_root / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            import os

            os.environ[key] = value


load_local_env()


@dataclass(frozen=True)
class Settings:
    openai_api_key: str | None = getenv("OPENAI_API_KEY") or None
    openai_model: str = getenv("OPENAI_MODEL", "gpt-4.1-mini")
    groq_api_key: str | None = getenv("GROQ_API_KEY") or None
    groq_model: str = getenv("GROQ_MODEL", "openai/gpt-oss-20b")
    llm_provider: str = getenv("LLM_PROVIDER", "openai")
    neo4j_uri: str = getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_username: str = getenv("NEO4J_USERNAME", "neo4j")
    neo4j_password: str | None = getenv("NEO4J_PASSWORD") or None
    graph_backend: str = getenv("GRAPH_BACKEND", "networkx")


settings = Settings()
