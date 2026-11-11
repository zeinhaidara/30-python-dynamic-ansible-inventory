#!/usr/bin/env python3
"""Fixture inventory script for CI's ansible-inventory validation step.

Produces the same JSON shape as inventory.py but from the checked-in
fixture pages instead of a live boto3 client, so ansible-inventory can
validate the contract without any AWS credentials.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.inventory.build import build_inventory  # noqa: E402
from src.inventory.providers.aws import AwsProvider  # noqa: E402

FIXTURES = Path(__file__).parent


class _FixtureClient:
    def __init__(self, pages):
        self._pages = pages
        self._calls = 0

    def describe_instances(self, **kwargs):
        page = self._pages[self._calls]
        self._calls += 1
        return page


def _load_pages():
    return [
        json.loads((FIXTURES / "describe_instances_page1.json").read_text()),
        json.loads((FIXTURES / "describe_instances_page2.json").read_text()),
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true")
    group.add_argument("--host")
    args = parser.parse_args()
    if args.host:
        print(json.dumps({}))
        return 0

    provider = AwsProvider(client=_FixtureClient(_load_pages()))
    print(json.dumps(build_inventory(provider.list_instances()), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
