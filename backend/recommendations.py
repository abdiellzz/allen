from .time_utils import local_day_iso
from .learning_engine import recommend_next_action
from .learning_intelligence import due_reviews

def build_recommendation(db,user_id):
    next_action=recommend_next_action(db,user_id)
    topic_reviews=due_reviews(db,user_id,5)
    due=db.one("SELECT count(*) n FROM flashcards WHERE user_id=? AND due<=?",(user_id,local_day_iso()))["n"]
    active=db.one("SELECT * FROM profile_current_activity WHERE user_id=?",(user_id,))
    if active and active.get("status") in ("active","paused"):
        if active.get("activity_type")=="course" and active.get("reference_id"):
            enrollment=db.one("SELECT ce.*,c.id course_id,c.structure_json FROM course_enrollments ce JOIN courses c ON c.id=ce.course_id WHERE ce.id=? AND ce.user_id=?",(active["reference_id"],user_id))
            if enrollment:
                node_id=f"u{enrollment['unit_index']}:t{enrollment['topic_index']}"
                prereqs=db.all("SELECT from_node,reason FROM curriculum_edges WHERE course_id=? AND to_node=? AND relation='prerequisite'",(enrollment["course_id"],node_id))
                try:
                    structure=__import__("json").loads(enrollment["structure_json"])
                except Exception:
                    structure={}
                for edge in prereqs:
                    try:
                        left,right=edge["from_node"].split(":")
                        ui=int(left[1:]); ti=int(right[1:])
                        ptopic=structure["units"][ui]["topics"][ti]["title"]
                        prow=db.one("SELECT mastery_score,status FROM topic_mastery WHERE user_id=? AND subject=? AND topic=?",(user_id,active.get("subject",""),ptopic))
                        if prow and prow["mastery_score"]<50:
                            return dict(kind="prerequisite",title="Refuerza la base antes de seguir",action="review",subject=active.get("subject",""),topic=ptopic,
                                        reason=f"Antes de continuar con {active.get('topic') or 'este tema'}, conviene reforzar {ptopic} ({prow['mastery_score']}% de dominio).",priority=.97,activity=active)
                    except Exception:
                        continue
        return dict(kind="continue",title="Continúa donde lo dejaste",reason="Tienes una actividad en curso.",activity=active)
    if topic_reviews:
        first=topic_reviews[0]
        return dict(kind="review",title="Repaso espaciado",action="review",subject=first["subject"],topic=first["topic"],
                    reason=f"Conviene recuperar {first['topic']} antes de seguir; su revisión ya está programada.",priority=.9,due_reviews=topic_reviews)
    if next_action:
        return dict(kind="mastery",title="Próxima mejor acción",**next_action)
    if due:
        return dict(kind="flashcards",title="Repaso listo",action="flashcards",reason=f"Tienes {due} tarjetas listas para repasar.",priority=.7)
    return dict(kind="explore",title="Prueba algo ahora",action="explore",reason="Elige un tema y conviértelo en una pequeña práctica.",priority=.4)
