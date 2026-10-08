from fastapi.testclient import TestClient

from backend.app import create_app
from backend.version import ALLEN_VERSION


def test_release_version_is_stable():
    assert ALLEN_VERSION == "1.2.3"


def test_bootstrap_exposes_release_version_without_fingerprinting_health(tmp_path):
    app=create_app(tmp_path/"allen.sqlite3")
    with TestClient(app) as client:
        health=client.get("/api/health")
        assert health.status_code == 200
        assert "version" not in health.json()
        response=client.get("/api/bootstrap")
        assert response.status_code == 200
        assert response.json()["version"] == "1.2.3"
