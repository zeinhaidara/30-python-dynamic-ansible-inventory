"""Aggregates provider instances into the Ansible dynamic inventory shape."""
from __future__ import annotations

import re

from .providers.base import Instance, Provider, ProviderError

_SAFE = re.compile(r"[^A-Za-z0-9_]")


def _sanitize(value: str) -> str:
    return _SAFE.sub("_", value).lower()


def collect_instances(providers: list[Provider]) -> list[Instance]:
    """Runs every provider and concatenates results.

    Any ProviderError propagates immediately: a single failing provider
    must abort the whole run rather than silently yielding a partial list.
    """
    instances: list[Instance] = []
    for provider in providers:
        instances.extend(provider.list_instances())
    return instances


def build_inventory(instances: list[Instance]) -> dict:
    groups: dict[str, set[str]] = {}
    hostvars: dict[str, dict] = {}

    for instance in instances:
        host = instance.hostname

        provider_group = f"provider_{_sanitize(instance.provider)}"
        groups.setdefault(provider_group, set()).add(host)

        for key, value in instance.tags.items():
            tag_group = f"tag_{_sanitize(key)}_{_sanitize(value)}"
            groups.setdefault(tag_group, set()).add(host)

        hostvars[host] = {
            "ansible_host": instance.private_ip or instance.public_ip or host,
            "provider": instance.provider,
            "instance_id": instance.id,
            "tags": dict(instance.tags),
        }

    result: dict = {name: {"hosts": sorted(hosts)} for name, hosts in groups.items()}
    result["_meta"] = {"hostvars": hostvars}
    return result


__all__ = ["collect_instances", "build_inventory", "ProviderError"]
