"""Canonical server-side answer keys for persistent learning adventures.

The frontend may display the same questions, but progress integrity is decided
here. Client-supplied "correct" flags are never trusted.
"""
from __future__ import annotations

ADVENTURE_ANSWERS: dict[str, tuple[str, ...]] = {
    "recover-network": (
        "192.168.10",
        "255.255.255.0",
        "/26",
        "192.168.10.65",
    ),
    "digital-defender": (
        "Usar una frase larga y única",
        "Añadir otra comprobación de identidad",
        "Verificar por un canal conocido antes de actuar",
        "Tener una copia de seguridad probada",
    ),
    "hidden-bug": (
        "15",
        "edad >= 18",
        "for",
        "Agrupar lógica reutilizable",
    ),
    "ai-lab": (
        "Una unidad de texto que procesa el modelo",
        "Usar un modelo ya entrenado para producir una salida",
        "Verificarlo con una fuente confiable",
        "Puede reducir el envío de contenido a servicios externos",
    ),
    "science-expedition": (
        "Poder ponerse a prueba",
        "La cantidad de luz",
        "Una medición registrada de forma consistente",
        "Cambiar o rechazar la hipótesis",
    ),
}


def adventure_step_count(adventure_id: str) -> int:
    return len(ADVENTURE_ANSWERS.get(adventure_id, ()))


def adventure_answer(adventure_id: str, step: int) -> str | None:
    answers=ADVENTURE_ANSWERS.get(adventure_id)
    if answers is None or step < 0 or step >= len(answers):
        return None
    return answers[step]


def answer_is_correct(adventure_id: str, step: int, answer: str) -> bool:
    expected=adventure_answer(adventure_id,step)
    if expected is None:
        return False
    return str(answer).strip().casefold()==expected.strip().casefold()
