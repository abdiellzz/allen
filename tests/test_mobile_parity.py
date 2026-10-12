"""Prevent the browser projection drifting from ALLEN's existing learning engine."""
import json
import random
import subprocess
from pathlib import Path

from backend.learning_engine import compute_mastery, recommend_for_state
from backend.time_utils import local_day_iso

ROOT = Path(__file__).resolve().parent.parent


def test_browser_learning_rules_match_existing_python_engine():
    rng = random.Random(42)
    cases = [dict(attempts=0), dict(attempts=1, correct=1), dict(attempts=12, incorrect=12)]
    for _ in range(100):
        attempts = rng.randrange(1, 45)
        correct = rng.randrange(attempts + 1)
        cases.append(dict(attempts=attempts, correct=correct, incorrect=attempts-correct,
                          hints=rng.randrange(10), practice_count=rng.randrange(5),
                          quiz_count=rng.randrange(5), difficulty=rng.choice(['Fácil', 'Normal', 'Difícil']),
                          last_seen=local_day_iso(), next_review=local_day_iso()))
    out = subprocess.run(['node', str(ROOT/'tests/fixtures/mobile-parity.mjs')],
                         input=json.dumps(dict(cases=cases, now=local_day_iso()+'T12:00:00')),
                         capture_output=True, text=True, encoding='utf-8', check=True)
    actual = json.loads(out.stdout)
    for c, row in zip(cases, actual):
        expected = compute_mastery(**c)
        assert row['mastery'] == expected, c
        assert row['recommendation'] == recommend_for_state(dict(mastery_score=expected['score'],
                                                                  status=expected['status'], topic='Fracciones'))
