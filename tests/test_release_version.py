from fastapi.testclient import TestClient

from backend.app import create_app
from backend.version import ALLEN_VERSION


def test_release_version_is_stable():
    assert ALLEN_VERSION == "1.2.0"


def test_health_exposes_release_version(tmp_path):
    app=create_app(tmp_path/"allen.sqlite3")
    with TestClient(app) as client:
        response=client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["version"] == "1.2.0"
