from dataclasses import dataclass
from os import getenv

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    openai_api_key: str | None = getenv("OPENAI_API_KEY") or None
    neo4j_uri: str = getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_username: str = getenv("NEO4J_USERNAME", "neo4j")
    neo4j_password: str | None = getenv("NEO4J_PASSWORD") or None
    graph_backend: str = getenv("GRAPH_BACKEND", "networkx")


settings = Settings()
