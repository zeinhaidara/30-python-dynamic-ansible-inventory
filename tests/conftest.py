import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


class FailingEc2Client:
    def describe_instances(self, **kwargs):
        raise RuntimeError("UnauthorizedOperation: not authorized")


@pytest.fixture
def two_page_responses():
    return [
        load_fixture("describe_instances_page1.json"),
        load_fixture("describe_instances_page2.json"),
    ]
