"""Azure adapter stub. Not implemented against the real Azure SDK."""
from __future__ import annotations

from .base import Instance, Provider


class AzureProvider(Provider):
    """Placeholder adapter: interface-only, no real Azure SDK calls.

    Wiring this up for real would use azure-mgmt-compute's
    VirtualMachinesOperations.list_all plus a network client for IPs.
    """

    name = "azure"

    def list_instances(self) -> list[Instance]:
        raise NotImplementedError("azure provider is interface-only, see README")
