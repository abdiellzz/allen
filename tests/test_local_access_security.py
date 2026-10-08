from fastapi.testclient import TestClient

from backend.app import create_app


def test_local_api_requires_ephemeral_launch_secret(tmp_path):
    app = create_app(
        tmp_path / "allen.sqlite3",
        require_license=False,
        require_local_access=True,
    )
    with TestClient(app) as client:
        health = client.get("/api/health")
        assert health.status_code == 200

        blocked = client.get("/api/bootstrap")
        assert blocked.status_code == 403

        wrong = client.get("/?access=wrong-secret", follow_redirects=False)
        assert wrong.status_code == 403

        launch = client.get(
            "/?access=" + app.state.access_key,
            follow_redirects=False,
        )
        assert launch.status_code == 303
        cookie = launch.headers.get("set-cookie", "")
        assert "HttpOnly" in cookie
        assert "SameSite=strict" in cookie

        allowed = client.get("/api/bootstrap")
        assert allowed.status_code == 200
        assert "token" in allowed.json()


def test_security_headers_are_applied_to_blocked_responses(tmp_path):
    app = create_app(
        tmp_path / "allen.sqlite3",
        require_license=False,
        require_local_access=True,
    )
    with TestClient(app) as client:
        response = client.get("/api/bootstrap")
        assert response.status_code == 403
        assert response.headers["x-content-type-options"] == "nosniff"
        assert response.headers["referrer-policy"] == "no-referrer"
        assert response.headers["cache-control"] == "no-store"
        assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
        assert response.headers["permissions-policy"] == "camera=(), microphone=(), geolocation=()"
