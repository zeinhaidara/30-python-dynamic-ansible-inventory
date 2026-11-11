import pytest

from src.inventory.build import build_inventory, collect_instances
from src.inventory.providers.base import Instance, Provider, ProviderError

WEB = Instance(
    id="i-1",
    hostname="web-01.example.com",
    provider="aws",
    tags={"env": "Prod"},
    private_ip="10.0.1.11",
)
DB = Instance(
    id="i-2",
    hostname="db-01.example.com",
    provider="aws",
    tags={"env": "staging"},
    private_ip="10.0.2.21",
)


def test_groups_by_provider_and_tag():
    inventory = build_inventory([WEB, DB])

    assert inventory["provider_aws"]["hosts"] == ["db-01.example.com", "web-01.example.com"]
    assert inventory["tag_env_prod"]["hosts"] == ["web-01.example.com"]
    assert inventory["tag_env_staging"]["hosts"] == ["db-01.example.com"]


def test_hostvars_populated_for_every_host():
    inventory = build_inventory([WEB])

    hostvars = inventory["_meta"]["hostvars"]["web-01.example.com"]
    assert hostvars["ansible_host"] == "10.0.1.11"
    assert hostvars["provider"] == "aws"
    assert hostvars["instance_id"] == "i-1"
    assert hostvars["tags"] == {"env": "Prod"}


def test_hostvars_falls_back_to_public_ip_then_hostname():
    no_private = Instance(
        id="i-3", hostname="edge.example.com", provider="aws", public_ip="203.0.113.5"
    )
    no_ip = Instance(id="i-4", hostname="legacy.example.com", provider="aws")

    inventory = build_inventory([no_private, no_ip])
    hostvars = inventory["_meta"]["hostvars"]

    assert hostvars["edge.example.com"]["ansible_host"] == "203.0.113.5"
    assert hostvars["legacy.example.com"]["ansible_host"] == "legacy.example.com"


def test_collect_instances_concatenates_providers():
    class StubProvider(Provider):
        name = "stub"

        def __init__(self, items):
            self._items = items

        def list_instances(self):
            return self._items

    result = collect_instances([StubProvider([WEB]), StubProvider([DB])])

    assert result == [WEB, DB]


def test_collect_instances_propagates_provider_error_without_partial_result():
    class FailingProvider(Provider):
        name = "failing"

        def list_instances(self):
            raise ProviderError("failing: boom")

    class GoodProvider(Provider):
        name = "good"

        def list_instances(self):
            return [WEB]

    with pytest.raises(ProviderError):
        collect_instances([GoodProvider(), FailingProvider()])
