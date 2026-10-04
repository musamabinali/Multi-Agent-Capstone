"""Configuration module for MAKPA.

Provides Pydantic v2 settings management with mode detection,
LLM provider resolution, vector store resolution, and Google MCP mode resolution.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from enum import Enum
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Mode(str, Enum):
    """Runtime mode enumeration."""

    DEMO = "demo"
    FREE = "free"
    LIVE = "live"


class LLMProvider(str, Enum):
    """LLM provider enumeration."""

    GEMINI = "gemini"
    GROQ = "groq"
    MOCK = "mock"


class VectorStoreType(str, Enum):
    """Vector store type enumeration."""

    PINECONE = "pinecone"
    CHROMA_HTTP = "chroma_http"
    QDRANT = "qdrant"
    CHROMA_LOCAL = "chroma_local"


class GoogleMCPMode(str, Enum):
    """Google MCP mode enumeration."""

    OFFICIAL = "official"
    LOCAL = "local"
    AUTO = "auto"
    MOCK = "mock"


class EmbeddingProvider(str, Enum):
    """Embedding provider enumeration."""

    HUGGINGFACE = "huggingface"
    GEMINI = "gemini"


class GitHubMCPMode(str, Enum):
    """GitHub MCP mode enumeration."""

    AUTO = "auto"
    MOCK = "mock"
    REAL = "real"


class Settings(BaseSettings):  # type: ignore[misc]
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Runtime mode and thread naming
    makpa_mode: Mode = Field(default=Mode.DEMO, validation_alias="MAKPA_MODE")
    thread_id_prefix: str = Field(default="makpa", validation_alias="THREAD_ID_PREFIX")

    # LLM Providers
    llm_provider: LLMProvider = Field(
        default=LLMProvider.MOCK, validation_alias="LLM_PROVIDER"
    )
    gemini_api_key: str | None = Field(default=None, validation_alias="GEMINI_API_KEY")
    gemini_chat_model: str = Field(
        default="gemini-1.5-flash", validation_alias="GEMINI_CHAT_MODEL"
    )
    gemini_embedding_model: str = Field(
        default="text-embedding-004", validation_alias="GEMINI_EMBEDDING_MODEL"
    )
    groq_api_key: str | None = Field(default=None, validation_alias="GROQ_API_KEY")
    groq_chat_model: str = Field(
        default="llama-3.1-70b-versatile", validation_alias="GROQ_CHAT_MODEL"
    )
    llm_temperature: float = Field(default=0.1, validation_alias="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(default=4096, validation_alias="LLM_MAX_TOKENS")

    # LangSmith Tracing
    langchain_api_key: str | None = Field(default=None, validation_alias="LANGCHAIN_API_KEY")
    langchain_project: str = Field(default="makpa", validation_alias="LANGCHAIN_PROJECT")
    langchain_tracing_v2: bool = Field(
        default=True, validation_alias="LANGCHAIN_TRACING_V2"
    )

    # GitHub MCP
    github_mcp_pat: str | None = Field(default=None, validation_alias="GITHUB_MCP_PAT")
    github_mcp_url: str = Field(
        default="https://api.githubcopilot.com/mcp/",
        validation_alias="GITHUB_MCP_URL",
    )
    mcp_tool_timeout_seconds: int = Field(
        default=30, validation_alias="MCP_TOOL_TIMEOUT_SECONDS"
    )
    github_mcp_mode: GitHubMCPMode = Field(
        default=GitHubMCPMode.AUTO, validation_alias="GITHUB_MCP_MODE"
    )

    # Google MCP
    google_client_id: str | None = Field(default=None, validation_alias="GOOGLE_CLIENT_ID")
    google_client_secret: str | None = Field(
        default=None, validation_alias="GOOGLE_CLIENT_SECRET"
    )
    google_redirect_uri: str = Field(
        default="http://localhost:8080/callback", validation_alias="GOOGLE_REDIRECT_URI"
    )
    google_oauth_redirect_port: int = Field(
        default=8080, validation_alias="GOOGLE_OAUTH_REDIRECT_PORT"
    )
    google_calendar_attendee_mode: str = Field(
        default="own_only", validation_alias="GOOGLE_CALENDAR_ATTENDEE_MODE"
    )
    google_oauth_scopes: str = Field(
        default="https://www.googleapis.com/auth/calendar,https://www.googleapis.com/auth/gmail.send,https://www.googleapis.com/auth/gmail.compose,https://www.googleapis.com/auth/gmail.readonly",
        validation_alias="GOOGLE_OAUTH_SCOPES",
    )
    google_token_cache_path: str = Field(
        default="./data/google_token_cache.json",
        validation_alias="GOOGLE_TOKEN_CACHE_PATH",
    )
    google_mcp_mode: GoogleMCPMode = Field(
        default=GoogleMCPMode.AUTO, validation_alias="GOOGLE_MCP_MODE"
    )
    google_calendar_mcp_url: str | None = Field(
        default=None, validation_alias="GOOGLE_CALENDAR_MCP_URL"
    )
    google_gmail_mcp_url: str | None = Field(
        default=None, validation_alias="GOOGLE_GMAIL_MCP_URL"
    )

    # Vector Store
    vector_store: VectorStoreType = Field(
        default=VectorStoreType.CHROMA_LOCAL, validation_alias="VECTOR_STORE"
    )
    pinecone_api_key: str | None = Field(default=None, validation_alias="PINECONE_API_KEY")
    pinecone_index_name: str = Field(
        default="makpa-rag", validation_alias="PINECONE_INDEX_NAME"
    )
    pinecone_environment: str = Field(
        default="us-east-1", validation_alias="PINECONE_ENVIRONMENT"
    )
    pinecone_cloud: str = Field(default="aws", validation_alias="PINECONE_CLOUD")
    pinecone_region: str = Field(default="us-east-1", validation_alias="PINECONE_REGION")
    chroma_host: str = Field(default="localhost", validation_alias="CHROMA_HOST")
    chroma_port: int = Field(default=8000, validation_alias="CHROMA_PORT")
    qdrant_url: str | None = Field(default=None, validation_alias="QDRANT_URL")
    qdrant_api_key: str | None = Field(default=None, validation_alias="QDRANT_API_KEY")
    qdrant_collection_name: str = Field(
        default="makpa-rag", validation_alias="QDRANT_COLLECTION_NAME"
    )

    # Embeddings
    embedding_provider: EmbeddingProvider = Field(
        default=EmbeddingProvider.HUGGINGFACE, validation_alias="EMBEDDING_PROVIDER"
    )
    hf_embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        validation_alias="HF_EMBEDDING_MODEL",
    )
    embedding_batch_size: int = Field(default=32, validation_alias="EMBEDDING_BATCH_SIZE")

    # RAG Parameters
    sample_pdf_path: str = Field(
        default="./data/sample.pdf", validation_alias="SAMPLE_PDF_PATH"
    )
    pdf_loader: str = Field(default="pypdf", validation_alias="PDF_LOADER")
    rag_chunk_size: int = Field(default=1000, validation_alias="RAG_CHUNK_SIZE")
    rag_chunk_overlap: int = Field(default=200, validation_alias="RAG_CHUNK_OVERLAP")
    rag_k: int = Field(default=5, validation_alias="RAG_K")
    rag_fetch_k: int = Field(default=20, validation_alias="RAG_FETCH_K")
    rag_lambda_mult: float = Field(default=0.5, validation_alias="RAG_LAMBDA_MULT")

    # Checkpointer
    checkpointer_backend: str = Field(
        default="memory", validation_alias="CHECKPOINTER_BACKEND"
    )
    checkpointer_sqlite_path: str = Field(
        default="./data/checkpoints.sqlite", validation_alias="CHECKPOINTER_SQLITE_PATH"
    )

    # Audit Log
    audit_log_path: str = Field(default="./data/audit.log", validation_alias="AUDIT_LOG_PATH")

    # Logging
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    log_format: str = Field(default="console", validation_alias="LOG_FORMAT")

    # Resolved fields (computed, not from env)
    resolved_mode: Mode = Field(default=Mode.DEMO, init=False)
    resolved_llm_provider: LLMProvider = Field(default=LLMProvider.MOCK, init=False)
    resolved_vector_store: VectorStoreType = Field(
        default=VectorStoreType.CHROMA_LOCAL, init=False
    )
    resolved_google_mcp_mode: GoogleMCPMode = Field(
        default=GoogleMCPMode.LOCAL, init=False
    )
    resolved_github_mcp_path: str = Field(default="mock", init=False)
    resolved_google_oauth_state: str = Field(default="missing", init=False)
    downgrade_reasons: list[str] = Field(default_factory=list, init=False)

    @field_validator("makpa_mode", mode="before")  # type: ignore[untyped-decorator]
    @classmethod
    def _validate_mode(cls, v: str | Mode) -> Mode:
        if isinstance(v, Mode):
            return v
        return Mode(str(v).lower())

    @field_validator("llm_provider", mode="before")  # type: ignore[untyped-decorator]
    @classmethod
    def _validate_llm_provider(cls, v: str | LLMProvider) -> LLMProvider:
        if isinstance(v, LLMProvider):
            return v
        return LLMProvider(str(v).lower())

    @field_validator("vector_store", mode="before")  # type: ignore[untyped-decorator]
    @classmethod
    def _validate_vector_store(cls, v: str | VectorStoreType) -> VectorStoreType:
        if isinstance(v, VectorStoreType):
            return v
        return VectorStoreType(str(v).lower())

    @field_validator("google_mcp_mode", mode="before")  # type: ignore[untyped-decorator]
    @classmethod
    def _validate_google_mcp_mode(cls, v: str | GoogleMCPMode) -> GoogleMCPMode:
        if isinstance(v, GoogleMCPMode):
            return v
        return GoogleMCPMode(str(v).lower())

    @field_validator("embedding_provider", mode="before")  # type: ignore[untyped-decorator]
    @classmethod
    def _validate_embedding_provider(cls, v: str | EmbeddingProvider) -> EmbeddingProvider:
        if isinstance(v, EmbeddingProvider):
            return v
        return EmbeddingProvider(str(v).lower())

    @field_validator("github_mcp_mode", mode="before")  # type: ignore[untyped-decorator]
    @classmethod
    def _validate_github_mcp_mode(cls, v: str | GitHubMCPMode) -> GitHubMCPMode:
        if isinstance(v, GitHubMCPMode):
            return v
        return GitHubMCPMode(str(v).lower())

    @field_validator("google_calendar_attendee_mode")  # type: ignore[untyped-decorator]
    @classmethod
    def _validate_attendee_mode(cls, v: str) -> str:
        normalized = str(v).lower()
        if normalized not in ("own_only", "all"):
            raise ValueError("GOOGLE_CALENDAR_ATTENDEE_MODE must be own_only or all")
        return normalized

    def resolve_mode(self) -> Mode:
        """Resolve the effective runtime mode based on available credentials."""
        requested_mode = self.makpa_mode
        effective_mode = requested_mode
        reasons = []

        # Downgrade from LIVE to FREE if GitHub or Google credentials missing
        if requested_mode == Mode.LIVE:
            if not self.github_mcp_pat:
                reasons.append("GitHub PAT missing; downgrading LIVE -> FREE")
                effective_mode = Mode.FREE
            if not self.google_client_id:
                reasons.append("Google Client ID missing; downgrading LIVE -> FREE")
                effective_mode = Mode.FREE

        # Downgrade from FREE to DEMO if no LLM key available
        if effective_mode in (Mode.LIVE, Mode.FREE):
            has_gemini = bool(self.gemini_api_key)
            has_groq = bool(self.groq_api_key)
            if not has_gemini and not has_groq:
                reasons.append("No LLM API key (Gemini/Groq); downgrading to DEMO")
                effective_mode = Mode.DEMO

        self.resolved_mode = effective_mode
        self.downgrade_reasons = reasons
        for reason in reasons:
            logger.warning("Mode downgrade: %s", reason)

        return effective_mode

    def resolve_llm_provider(self) -> LLMProvider:
        """Resolve the LLM provider based on available keys."""
        # Priority: Gemini > Groq > Mock
        if self.gemini_api_key:
            self.resolved_llm_provider = LLMProvider.GEMINI
            return LLMProvider.GEMINI
        if self.groq_api_key:
            self.resolved_llm_provider = LLMProvider.GROQ
            return LLMProvider.GROQ
        self.resolved_llm_provider = LLMProvider.MOCK
        return LLMProvider.MOCK

    def resolve_vector_store(self) -> VectorStoreType:
        """Resolve the vector store based on available credentials and configuration."""
        requested = self.vector_store

        # If explicitly requested and available, use it
        if requested == VectorStoreType.PINECONE and self.pinecone_api_key:
            self.resolved_vector_store = VectorStoreType.PINECONE
            return VectorStoreType.PINECONE

        if requested == VectorStoreType.CHROMA_HTTP:
            # Check if Chroma HTTP is reachable (simplified check)
            self.resolved_vector_store = VectorStoreType.CHROMA_HTTP
            return VectorStoreType.CHROMA_HTTP

        if requested == VectorStoreType.QDRANT and self.qdrant_url and self.qdrant_api_key:
            self.resolved_vector_store = VectorStoreType.QDRANT
            return VectorStoreType.QDRANT

        if requested == VectorStoreType.CHROMA_LOCAL:
            self.resolved_vector_store = VectorStoreType.CHROMA_LOCAL
            return VectorStoreType.CHROMA_LOCAL

        # Fallback chain
        if self.pinecone_api_key:
            self.downgrade_reasons.append(
                f"Vector store {requested.value} unavailable; falling back to Pinecone"
            )
            self.resolved_vector_store = VectorStoreType.PINECONE
            return VectorStoreType.PINECONE

        # In demo mode (no keys), use in-process Chroma
        if self.resolved_mode == Mode.DEMO:
            self.resolved_vector_store = VectorStoreType.CHROMA_LOCAL
            return VectorStoreType.CHROMA_LOCAL

        # Try Chroma HTTP
        self.downgrade_reasons.append(
            f"Vector store {requested.value} unavailable; falling back to Chroma HTTP"
        )
        self.resolved_vector_store = VectorStoreType.CHROMA_HTTP
        return VectorStoreType.CHROMA_HTTP

    def resolve_google_mcp_mode(self) -> GoogleMCPMode:
        """Resolve the Google MCP mode based on availability."""
        mode = self.google_mcp_mode

        if mode == GoogleMCPMode.AUTO:
            # Try official first (check if URLs are configured)
            if self.google_calendar_mcp_url and self.google_gmail_mcp_url:
                self.resolved_google_mcp_mode = GoogleMCPMode.OFFICIAL
                logger.info("Google MCP mode: official (auto-detected)")
                return GoogleMCPMode.OFFICIAL
            else:
                self.resolved_google_mcp_mode = GoogleMCPMode.LOCAL
                logger.info("Google MCP mode: local (official URLs not configured)")
                return GoogleMCPMode.LOCAL

        self.resolved_google_mcp_mode = mode
        return mode

    def resolve_github_mcp_path(self) -> str:
        """Resolve the GitHub MCP path: real server or mock STDIO server.

        - ``mock`` mode forces the mock server.
        - ``real`` mode requires a PAT; without one it degrades to mock
          outside live mode and records the downgrade.
        - ``auto`` (default) uses the real server when a PAT is set,
          otherwise the mock server.
        """
        mode = self.github_mcp_mode
        if mode == GitHubMCPMode.MOCK:
            self.resolved_github_mcp_path = "mock"
            return "mock"
        if self.github_mcp_pat:
            self.resolved_github_mcp_path = "real"
            return "real"
        if mode == GitHubMCPMode.REAL and self.resolved_mode == Mode.LIVE:
            logger.warning("GitHub MCP mode=real but GITHUB_MCP_PAT missing in live")
        self.downgrade_reasons.append(
            "GitHub PAT missing; using mock GitHub MCP server"
        )
        self.resolved_github_mcp_path = "mock"
        return "mock"

    def resolve_google_oauth_state(self) -> str:
        """Resolve Google OAuth state from the token cache (no network).

        Returns ``cached`` (valid access token), ``refreshing``
        (refresh token present but access expired/missing), or
        ``missing`` (no usable cache).
        """
        try:
            with open(self.google_token_cache_path, encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, ValueError):
            self.resolved_google_oauth_state = "missing"
            return "missing"
        if not isinstance(data, dict) or not data.get("refresh_token"):
            self.resolved_google_oauth_state = "missing"
            return "missing"
        expiry_raw = data.get("expiry")
        try:
            expired = expiry_raw is None or datetime.fromisoformat(
                str(expiry_raw)
            ) <= datetime.now(timezone.utc)
        except ValueError:
            expired = True
        state = "refreshing" if expired else "cached"
        self.resolved_google_oauth_state = state
        return state

    def resolve_all(self) -> Settings:
        """Resolve all computed settings."""
        self.resolve_mode()
        self.resolve_llm_provider()
        self.resolve_vector_store()
        self.resolve_google_mcp_mode()
        self.resolve_github_mcp_path()
        self.resolve_google_oauth_state()
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get the cached settings instance with all resolutions applied."""
    settings = Settings()
    return settings.resolve_all()


def print_startup_banner() -> None:
    """Print a boxed startup banner with resolved configuration."""
    settings = get_settings()

    lines = [
        "   ",
        "   ",
        "+========================================================+",
        "|             MAKPA - Multi-Agent System                 |",
        "+========================================================+",
        f"|  Mode:                  {settings.resolved_mode.value:<52}",
        f"|  LLM Provider:          {settings.resolved_llm_provider.value:<52}",
        f"|  Vector Store:          {settings.resolved_vector_store.value:<52}",
        f"|  Embedding Provider:    {settings.embedding_provider.value:<51}",
        f"|  Google MCP Mode:       {settings.resolved_google_mcp_mode.value:<52}",
        f"|  Google OAuth:          {settings.resolved_google_oauth_state:<51}",
        f"|  GitHub MCP:            {settings.resolved_github_mcp_path:<52}",
        "+========================================================+",
        "   ",
    ]

    if settings.downgrade_reasons:
        lines.append("| Downgrades:")
        for reason in settings.downgrade_reasons:
            lines.append(f"|   - {reason:<63} |")
        lines.append("+========================================================+")

    if settings.resolved_mode == Mode.LIVE:
        note = "Note: live = live LLM; MCP mocked unless credentials present"
        lines.insert(-1, "|  " + note.ljust(71) + " |")

    for line in lines:
        print(line)


__all__ = [
    "Settings",
    "Mode",
    "LLMProvider",
    "VectorStoreType",
    "GoogleMCPMode",
    "EmbeddingProvider",
    "GitHubMCPMode",
    "get_settings",
    "print_startup_banner",
]
