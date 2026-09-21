import json
import re
from pathlib import Path
from .security import normalized

SUBJECT_NAMES={'math':'Matemáticas','science':'Ciencias','english':'Inglés','programming':'Programación','technology':'Tecnología'}

class Library:
    """Keyword retriever; replace search() with local embeddings later."""
    def __init__(self, root):
        self.root = Path(root).resolve()

    def documents(self):
        result = []
        for path in sorted(self.root.rglob('*')):
            if path.suffix.lower() not in ('.json', '.md', '.txt') or not path.is_file():
                continue
            if not path.resolve().is_relative_to(self.root) or path.stat().st_size > 300_000:
                continue
            try:
                text = path.read_text(encoding='utf-8')
                items = json.loads(text) if path.suffix.lower() == '.json' else [{'title':text.splitlines()[0].lstrip('# ').strip() if text.strip() else path.stem,'content':text}]
                if isinstance(items, dict):
                    items = [items]
                for i, item in enumerate(items):
                    if isinstance(item, dict) and isinstance(item.get('content'), str):
                        result.append(dict(id=f'{path.relative_to(self.root).as_posix()}:{i}', title=str(item.get('title',path.stem))[:200],
                                           subject=str(item.get('subject',SUBJECT_NAMES.get(path.parent.name,path.parent.name)))[:60], content=item['content'][:20000]))
            except (ValueError, OSError, TypeError):
                continue
        return result

    def search(self, query='', limit=30, extra=()):
        words = set(re.findall(r'\w+', normalized(query))) - {'que','como','para','con','una','los','las','del','por','es','de','el','la'}
        scored = []
        for doc in [*self.documents(), *extra]:
            title = normalized(doc['title'] + ' ' + doc['subject'])
            body = normalized(doc['content'])
            score = sum(5*title.count(w)+body.count(w) for w in words)
            if not words or score:
                scored.append((score,doc))
        return [d for _,d in sorted(scored,key=lambda pair:pair[0],reverse=True)[:limit]]
