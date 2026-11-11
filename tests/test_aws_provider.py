import pytest

from src.inventory.providers.aws import AwsProvider
from src.inventory.providers.base import ProviderError

from .conftest import FailingEc2Client


def test_list_instances_paginates_and_filters_stopped(two_page_responses):
    client = _PagedClient(two_page_responses)
    provider = AwsProvider(client=client, region="us-east-1")

    instances = provider.list_instances()

    hostnames = sorted(i.hostname for i in instances)
    assert hostnames == ["db-01.example.com", "web-01.example.com"]


def test_list_instances_captures_tags_and_ips(two_page_responses):
    client = _PagedClient(two_page_responses)
    provider = AwsProvider(client=client, region="us-east-1")

    instances = {i.hostname: i for i in provider.list_instances()}
    web = instances["web-01.example.com"]

    assert web.tags == {"Name": "web-01.example.com", "env": "prod"}
    assert web.private_ip == "10.0.1.11"
    assert web.public_ip == "203.0.113.11"
    assert web.provider == "aws"


def test_list_instances_raises_provider_error_on_client_failure():
    provider = AwsProvider(client=FailingEc2Client(), region="us-east-1")

    with pytest.raises(ProviderError):
        provider.list_instances()


class _PagedClient:
    def __init__(self, pages):
        self._pages = pages
        self._calls = 0

    def describe_instances(self, **kwargs):
        expected_token = self._pages[self._calls - 1].get("NextToken") if self._calls else None
        assert kwargs.get("NextToken") == expected_token
        page = self._pages[self._calls]
        self._calls += 1
        return page
