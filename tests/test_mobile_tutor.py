"""The optional bridge preserves access controls and never changes learning evidence."""
from fastapi.testclient import TestClient

from backend.app import create_app


class ModelStub:
    def __init__(self):
        self.connected = True
        self.calls = []

    async def status(self, _settings):
        return {'connected': self.connected}

    async def answer(self, request, profile, settings, sources):
        self.calls.append((request, profile, settings, sources))
        yield {'type': 'delta', 'text': 'Busca la idea que une los detalles del texto.'}


def test_bridge_is_explicit_protected_and_context_is_bounded(tmp_path):
    model = ModelStub()
    app = create_app(tmp_path/'local.sqlite3', ai=model, require_license=False,
                     require_local_access=True, require_teacher_auth=False)
    with TestClient(app) as client:
        assert client.get('/api/mobile/bootstrap').status_code == 403
        client.get('/?access='+app.state.issue_launch_token())
        assert client.get('/mobile/').status_code == 200
        config = client.get('/api/mobile/bootstrap').json()
        payload = {'message': 'Dame una analogía', 'topic_id': 'reading-main',
                   'question_id': 'r-1'}
        assert client.post('/api/mobile/tutor', json=payload).status_code == 403
        headers = {'x-allen-token': config['token']}
        response = client.post('/api/mobile/tutor', json=payload, headers=headers)
        assert response.status_code == 200
        assert response.json()['generated'] is True
        request, profile, settings, sources = model.calls[0]
        assert request.use_library is False and request.history == []
        assert settings.save_history is False and settings.max_tokens <= 320
        assert profile['name'] == 'Estudiante'
        assert 'student_answer' not in sources[0]['content']
        assert 'feedback' not in sources[0]['content']
        assert client.post('/api/mobile/tutor', json={**payload, 'question_id': 'py-1'}, headers=headers).status_code == 422
        assert client.post('/api/mobile/tutor', json={**payload, 'last_answer': 'inventada'}, headers=headers).status_code == 422
        assert client.post('/api/mobile/tutor', json={**payload, 'profile_id': 123}, headers=headers).status_code == 422
        model.connected = False
        assert client.post('/api/mobile/tutor', json=payload, headers=headers).status_code == 503
        model.connected = True
        for _ in range(18):
            assert client.post('/api/mobile/tutor', json=payload, headers=headers).status_code == 200
        assert client.post('/api/mobile/tutor', json=payload, headers=headers).status_code == 429


def test_mobile_retains_license_boundary(tmp_path):
    app = create_app(tmp_path/'local.sqlite3', ai=ModelStub(), require_license=True,
                     require_local_access=False, require_teacher_auth=False)
    with TestClient(app) as client:
        assert client.get('/api/mobile/bootstrap').status_code == 402
