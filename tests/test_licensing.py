import base64
import json
from datetime import date
from pathlib import Path
import tempfile
import unittest
import hashlib
from unittest.mock import patch

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from licensing.runtime import canonical_json, register_installation, verify_license, verify_manifest


def sign(payload, key):
    return {'payload': payload, 'signature': base64.b64encode(key.sign(canonical_json(payload))).decode('ascii')}


class OfflineSignatureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.data = self.root / 'programdata'
        self.data.mkdir()
        self.key = Ed25519PrivateKey.generate()
        public = self.key.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
        (self.root / 'license_public_key.pem').write_bytes(public)
        self.public_hash = hashlib.sha256(public).hexdigest()
        self.record = {'installation_id': 'ALLEN-INSTALL-' + 'a' * 32, 'machine_fingerprint': 'b' * 64}

    def save_license(self, payload):
        (self.data / 'license.allen').write_text(json.dumps(sign(payload, self.key)), encoding='utf-8')

    def test_valid_license_is_bound_to_installation_and_machine(self):
        self.save_license({'license_id': 'lic-1', 'customer': 'Colegio', 'edition': 'institutional',
                           'issued_at': '2026-01-01', 'expires_at': '2026-12-31',
                           'installation_id': self.record['installation_id'],
                           'machine_fingerprint': self.record['machine_fingerprint'], 'max_devices': 1})
        with patch('licensing.runtime.data_home', return_value=self.data), patch('licensing.runtime.PUBLIC_KEY_SHA256', self.public_hash):
            result = verify_license(self.root, self.record, today=date(2026, 6, 1))
        self.assertEqual(result['edition'], 'institutional')

    def test_expired_license_is_rejected(self):
        self.save_license({'license_id': 'lic-2', 'customer': 'Colegio', 'edition': 'institutional',
                           'issued_at': '2025-01-01', 'expires_at': '2025-12-31',
                           'installation_id': self.record['installation_id'],
                           'machine_fingerprint': self.record['machine_fingerprint'], 'max_devices': 1})
        with patch('licensing.runtime.data_home', return_value=self.data), patch('licensing.runtime.PUBLIC_KEY_SHA256', self.public_hash), self.assertRaisesRegex(ValueError, 'expirado'):
            verify_license(self.root, self.record, today=date(2026, 1, 1))

    def test_tampered_license_is_rejected(self):
        payload = {'license_id': 'lic-3', 'customer': 'Colegio', 'edition': 'institutional',
                   'issued_at': '2026-01-01', 'expires_at': None,
                   'installation_id': self.record['installation_id'],
                   'machine_fingerprint': self.record['machine_fingerprint'], 'max_devices': 1}
        doc = sign(payload, self.key)
        doc['payload']['customer'] = 'Alterado'
        (self.data / 'license.allen').write_text(json.dumps(doc), encoding='utf-8')
        with patch('licensing.runtime.data_home', return_value=self.data), patch('licensing.runtime.PUBLIC_KEY_SHA256', self.public_hash), self.assertRaises(Exception):
            verify_license(self.root, self.record, today=date(2026, 2, 1))

    def test_manifest_hash_change_is_rejected(self):
        critical = self.root / 'allen_backend.exe'
        critical.write_bytes(b'original')
        payload = {'format': 'ALLEN-MANIFEST-1', 'version': '1.0.0',
                   'files': {'allen_backend.exe': __import__('hashlib').sha256(b'original').hexdigest()}}
        (self.root / 'manifest.allen').write_text(json.dumps(sign(payload, self.key)), encoding='utf-8')
        with patch('licensing.runtime.PUBLIC_KEY_SHA256', self.public_hash):
            self.assertEqual(verify_manifest(self.root)['version'], '1.0.0')
        critical.write_bytes(b'tampered')
        with patch('licensing.runtime.PUBLIC_KEY_SHA256', self.public_hash), self.assertRaisesRegex(ValueError, 'modificados'):
            verify_manifest(self.root)

    def test_registration_uses_uuid4_and_is_stable_only_at_same_path(self):
        app_a = self.root / 'Program Files' / 'ALLEN'
        app_b = self.root / 'Other' / 'ALLEN'
        app_a.mkdir(parents=True)
        app_b.mkdir(parents=True)
        with patch('licensing.runtime.data_home', return_value=self.data), patch('licensing.runtime.machine_fingerprint', return_value='c' * 64):
            first = register_installation(app_a, '1.0.0', write_registry=False)
            second = register_installation(app_a, '1.0.1', write_registry=False)
            relocated = register_installation(app_b, '1.0.1', write_registry=False)
        identifier = first['installation_id'].removeprefix('ALLEN-INSTALL-')
        self.assertEqual(__import__('uuid').UUID(hex=identifier).version, 4)
        self.assertEqual(first['installation_id'], second['installation_id'])
        self.assertNotEqual(first['installation_id'], relocated['installation_id'])


if __name__ == '__main__':
    unittest.main()
