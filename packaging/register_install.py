"""Installer helper; run once from elevated ALLEN Setup to register and request activation."""
import argparse
import json
import sqlite3
import os
from pathlib import Path

from licensing.runtime import activation_request, data_home


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--install-root', type=Path, required=True)
    parser.add_argument('--version', required=True)
    parser.add_argument('--llama-server', type=Path, required=True)
    parser.add_argument('--model', type=Path, required=True)
    args = parser.parse_args()
    state = data_home()
    state.mkdir(parents=True, exist_ok=True)
    config = {'executable': str(args.llama_server.resolve()), 'model': str(args.model.resolve())}
    config_path = state / 'local_model.json'
    temp = config_path.with_suffix('.tmp')
    temp.write_text(json.dumps(config, indent=2), encoding='utf-8')
    temp.replace(config_path)
    old_db = Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'ALLEN' / 'allen.sqlite3'
    new_db = state / 'allen.sqlite3'
    if old_db.is_file() and not new_db.exists():
        with sqlite3.connect(old_db) as source, sqlite3.connect(new_db) as target:
            source.backup(target)
            check = target.execute('PRAGMA integrity_check').fetchone()
        if not check or check[0] != 'ok':
            new_db.unlink(missing_ok=True)
            raise RuntimeError('La copia de datos locales de ALLEN no pasó integrity_check.')
    request = activation_request(args.install_root, args.version)
    print(json.dumps({'activation_request': str(data_home() / 'activation-request.allen'),
                      'installation_id': request['installation_id']}, ensure_ascii=True))


if __name__ == '__main__':
    main()
