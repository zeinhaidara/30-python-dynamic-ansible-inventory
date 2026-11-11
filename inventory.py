#!/usr/bin/env python3
"""Ansible dynamic inventory script for multi-cloud EC2-style instances.

Implements the Ansible dynamic inventory contract: --list prints the full
inventory as JSON with a top-level _meta.hostvars; --host prints {} since
_meta.hostvars already carries every host's vars from --list.

A failing provider aborts the whole run with a non-zero exit and a message
on stderr. It never prints a partial inventory to stdout.
"""
from __future__ import annotations

import argparse
import json
import sys

import boto3

from src.inventory.build import build_inventory, collect_instances
from src.inventory.providers.aws import AwsProvider
from src.inventory.providers.base import ProviderError


def _default_providers(region: str) -> list:
    return [AwsProvider(client=boto3.client("ec2", region_name=region), region=region)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true", help="print the full inventory")
    group.add_argument("--host", help="print vars for a single host (legacy, see README)")
    parser.add_argument("--region", default="us-east-1", help="AWS region to query")
    args = parser.parse_args(argv)

    if args.host:
        print(json.dumps({}))
        return 0

    try:
        providers = _default_providers(args.region)
        instances = collect_instances(providers)
    except ProviderError as exc:
        print(f"inventory: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001 - any setup failure must abort loudly, never partial output
        print(f"inventory: aws client setup failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(build_inventory(instances), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
