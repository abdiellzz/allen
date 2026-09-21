"""Start ALLEN on the loopback interface only."""
import sys
import threading
import time
import urllib.request
import webbrowser

if __name__ == '__main__':
    try:
        import uvicorn
    except ImportError:
        print('Ejecuta start_allen.bat para instalar las dependencias.')
        sys.exit(1)
    if '--open' in sys.argv:
        def open_when_ready():
            for _ in range(60):
                try:
                    with urllib.request.urlopen('http://127.0.0.1:8787/api/health', timeout=1):
                        webbrowser.open('http://127.0.0.1:8787')
                        return
                except OSError:
                    time.sleep(0.5)
        threading.Thread(target=open_when_ready, daemon=True).start()
    uvicorn.run('backend.app:app', host='127.0.0.1', port=8787, access_log=False)
