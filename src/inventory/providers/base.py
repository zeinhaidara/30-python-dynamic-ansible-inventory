"""Common provider interface for inventory sources."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Instance:
    """A single compute instance normalized across providers."""

    id: str
    hostname: str
    provider: str
    tags: dict[str, str] = field(default_factory=dict)
    private_ip: str | None = None
    public_ip: str | None = None


class ProviderError(RuntimeError):
    """Raised when a provider fails to list its instances.

    Callers must never catch this and continue: a provider failure means
    the overall inventory is incomplete and must not be reported as if
    it were complete.
    """


class Provider:
    """Interface every cloud adapter must implement."""

    name: str = "base"

    def list_instances(self) -> list[Instance]:
        raise NotImplementedError
