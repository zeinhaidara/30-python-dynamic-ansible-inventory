"""AWS EC2 adapter backed by boto3 describe-instances."""
from __future__ import annotations

from typing import Any

from .base import Instance, Provider, ProviderError


class AwsProvider(Provider):
    """Lists running EC2 instances via a boto3 ec2 client.

    The caller supplies the boto3 client (or a fake implementing the same
    describe_instances contract) so tests never touch real AWS.
    """

    name = "aws"

    def __init__(self, client: Any, region: str = "us-east-1") -> None:
        self._client = client
        self._region = region

    def list_instances(self) -> list[Instance]:
        try:
            pages = self._paginate()
        except Exception as exc:  # noqa: BLE001 - re-raised as ProviderError below
            raise ProviderError(f"aws: describe_instances failed in {self._region}: {exc}") from exc

        instances: list[Instance] = []
        for reservation in pages:
            for raw in reservation.get("Instances", []):
                if raw.get("State", {}).get("Name") != "running":
                    continue
                tags = {t["Key"]: t["Value"] for t in raw.get("Tags", [])}
                hostname = tags.get("Name") or raw["InstanceId"]
                instances.append(
                    Instance(
                        id=raw["InstanceId"],
                        hostname=hostname,
                        provider=self.name,
                        tags=tags,
                        private_ip=raw.get("PrivateIpAddress"),
                        public_ip=raw.get("PublicIpAddress"),
                    )
                )
        return instances

    def _paginate(self) -> list[dict]:
        reservations: list[dict] = []
        kwargs: dict[str, Any] = {}
        while True:
            response = self._client.describe_instances(**kwargs)
            reservations.extend(response.get("Reservations", []))
            token = response.get("NextToken")
            if not token:
                break
            kwargs["NextToken"] = token
        return reservations
