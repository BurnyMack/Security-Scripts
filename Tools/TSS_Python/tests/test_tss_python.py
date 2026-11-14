"""Tests for TSS_Python with the requests layer mocked (no live calls)."""

import importlib.util
from pathlib import Path

import pytest

_MODULE_PATH = Path(__file__).resolve().parents[1] / "TSS_Python.py"
_spec = importlib.util.spec_from_file_location("tss_python", _MODULE_PATH)
tss = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tss)


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def json(self):
        return self._payload


class FakeRequests:
    """Stand-in for the module's `requests`, recording calls."""

    RequestException = Exception

    def __init__(self):
        self.calls = []
        self.token_response = FakeResponse(200, {"access_token": "TOKEN"})
        self.get_response = FakeResponse(
            200,
            {
                "name": "prod-db",
                "items": [
                    {"fieldName": "Username", "itemValue": "svc"},
                    {"fieldName": "Password", "itemValue": "p@ss"},
                ],
            },
        )
        self.put_response = FakeResponse(200, {})

    def post(self, url, data=None, headers=None):
        self.calls.append(("post", url, data))
        return self.token_response

    def get(self, url, headers=None):
        self.calls.append(("get", url))
        return self.get_response

    def put(self, url, headers=None, json=None):
        self.calls.append(("put", url, json))
        return self.put_response


@pytest.fixture
def fake_requests(monkeypatch):
    fake = FakeRequests()
    monkeypatch.setattr(tss, "requests", fake)
    return fake


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("TSS_USERNAME", "admin")
    monkeypatch.setenv("TSS_PASSWORD", "secret")


def test_get_token_success(fake_requests):
    assert tss.GetToken("https://ss/token", "u", "p") == "TOKEN"
    assert fake_requests.calls[0][0] == "post"


def test_get_token_failure_raises(fake_requests):
    fake_requests.token_response = FakeResponse(401, {}, text="bad")
    with pytest.raises(tss.TSSError):
        tss.GetToken("https://ss/token", "u", "p")


def test_get_secret_normalises_fields(fake_requests):
    data = tss.GetSecret("https://ss/secrets", "TOKEN", "42")
    assert data["name"] == "prod-db"
    assert data["user"] == "svc"
    assert data["pass"] == "p@ss"
    assert fake_requests.calls[-1][1].endswith("/42")


def test_get_secret_error_raises(fake_requests):
    fake_requests.get_response = FakeResponse(404, {})
    with pytest.raises(tss.TSSError):
        tss.GetSecret("https://ss/secrets", "TOKEN", "99")


def test_cli_get_success(fake_requests, creds, capsys):
    rc = tss.main(
        [
            "get",
            "--id",
            "42",
            "--token-url",
            "https://ss/token",
            "--server-url",
            "https://ss/secrets",
            "--output-format",
            "json",
        ]
    )
    assert rc == 0
    assert "prod-db" in capsys.readouterr().out


def test_cli_missing_credentials_errors(fake_requests, monkeypatch):
    monkeypatch.delenv("TSS_USERNAME", raising=False)
    monkeypatch.delenv("TSS_PASSWORD", raising=False)
    rc = tss.main(
        ["get", "--id", "1", "--token-url", "https://ss/t", "--server-url", "https://ss/s"]
    )
    assert rc == 1


def test_cli_update_success(fake_requests, creds, monkeypatch):
    monkeypatch.setenv("TSS_NEW_VALUE", "rotated")
    rc = tss.main(
        ["update", "--id", "42", "--token-url", "https://ss/t", "--server-url", "https://ss/s"]
    )
    assert rc == 0
    assert fake_requests.calls[-1][0] == "put"
