from .learning_engine import recommend_next_action

def build_recommendation(db,user_id):
    next_action=recommend_next_action(db,user_id)
    due=db.one("SELECT count(*) n FROM flashcards WHERE user_id=? AND due<=date('now')",(user_id,))["n"]
    active=db.one("SELECT * FROM profile_current_activity WHERE user_id=?",(user_id,))
    if active and active.get("status") in ("active","paused"):
        return dict(kind="continue",title="Continúa donde lo dejaste",reason="Tienes una actividad en curso.",activity=active)
    if next_action:
        return dict(kind="mastery",title="Próxima mejor acción",**next_action)
    if due:
        return dict(kind="flashcards",title="Repaso listo",action="flashcards",reason=f"Tienes {due} tarjetas listas para repasar.",priority=.7)
    return dict(kind="explore",title="Prueba algo ahora",action="explore",reason="Elige un tema y conviértelo en una pequeña práctica.",priority=.4)
