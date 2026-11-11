from unittest.mock import MagicMock

import api_client
import pytest
from api_client import GitHubAPIError, GitHubClient


class FakeResponse:
    def __init__(self, status_code=200, json_data=None, headers=None, links=None):
        self.status_code = status_code
        self._json = json_data if json_data is not None else []
        self.headers = headers or {}
        self.links = links or {}
        self.text = ""

    def json(self):
        return self._json


@pytest.fixture
def client(monkeypatch):
    # Skip real waiting so the tests run instantly
    monkeypatch.setattr(api_client.time, "sleep", lambda seconds: None)
    return GitHubClient(token="test-token")


def fake_get(client, responses):
    client.session.get = MagicMock(side_effect=responses)


def test_200_returns_the_response(client):
    fake_get(client, [FakeResponse(200, {"full_name": "pallets/flask"})])
    response = client.get("/repos/pallets/flask")
    assert response.json()["full_name"] == "pallets/flask"


def test_404_returns_none(client):
    fake_get(client, [FakeResponse(404)])
    assert client.get("/repos/pallets/not-a-real-repo") is None


def test_401_raises_an_error(client):
    fake_get(client, [FakeResponse(401)])
    with pytest.raises(GitHubAPIError):
        client.get("/repos/pallets/flask")


def test_server_error_is_retried(client):
    fake_get(client, [FakeResponse(500), FakeResponse(200, {"ok": True})])
    response = client.get("/repos/pallets/flask")
    assert response.json() == {"ok": True}
    assert client.session.get.call_count == 2


def test_gives_up_after_max_retries(client):
    fake_get(client, [FakeResponse(500), FakeResponse(500), FakeResponse(500)])
    with pytest.raises(GitHubAPIError):
        client.get("/repos/pallets/flask")


def test_rate_limit_waits_then_retries(client):
    limited = FakeResponse(403, headers={"Retry-After": "1"})
    fake_get(client, [limited, FakeResponse(200, {"ok": True})])
    response = client.get("/repos/pallets/flask")
    assert response.json() == {"ok": True}


def test_pagination_follows_the_next_link(client):
    page1 = FakeResponse(
        200, [1, 2], links={"next": {"url": "https://api.github.com/page2"}}
    )
    page2 = FakeResponse(200, [3, 4])
    fake_get(client, [page1, page2])
    assert list(client.get_paginated("/repos/pallets/flask/commits")) == [1, 2, 3, 4]


def test_pagination_respects_max_pages(client):
    page1 = FakeResponse(
        200, [1, 2], links={"next": {"url": "https://api.github.com/page2"}}
    )
    fake_get(client, [page1])
    assert list(client.get_paginated("/repos/x/y/commits", max_pages=1)) == [1, 2]


def test_missing_token_raises_an_error(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    with pytest.raises(ValueError):
        GitHubClient(token=None)