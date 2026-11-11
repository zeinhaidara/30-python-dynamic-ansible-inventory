"""GCP adapter stub. Not implemented against the real GCP SDK."""
from __future__ import annotations

from .base import Instance, Provider


class GcpProvider(Provider):
    """Placeholder adapter: interface-only, no real GCP SDK calls.

    Wiring this up for real would use google-cloud-compute's
    InstancesClient.aggregated_list across zones.
    """

    name = "gcp"

    def list_instances(self) -> list[Instance]:
        raise NotImplementedError("gcp provider is interface-only, see README")
