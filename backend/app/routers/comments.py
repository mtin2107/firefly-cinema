from typing import Literal

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..classifier import classifier
from ..database import get_db
from ..models import Comment, User
from ..schemas import CommentIn, CommentOut, AdminCommentOut
from ..security import get_current_user, require_admin
from .movies import get_movie_or_404

router = APIRouter(prefix="/api", tags=["Bình luận"])


def to_out(c: Comment) -> dict:
    return {"id": c.id, "movie_id": c.movie_id, "user_name": c.user.full_name, "content": c.content,
            "is_negative": c.is_negative, "negative_score": c.negative_score, "created_at": c.created_at,
            "movie_title": c.movie.title, "model_name": c.model_name}


@router.get("/movies/{movie_id}/comments", response_model=list[CommentOut])
def list_comments(movie_id: int, db: Session = Depends(get_db)):
    get_movie_or_404(db, movie_id)
    rows = db.scalars(select(Comment).where(Comment.movie_id == movie_id).order_by(Comment.created_at.desc())).all()
    return [to_out(c) for c in rows]


@router.post("/movies/{movie_id}/comments", response_model=CommentOut, status_code=201)
def create_comment(movie_id: int, body: CommentIn, user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    get_movie_or_404(db, movie_id)
    text = body.content.strip()
    is_negative, score = classifier.predict(text)  # <-- PhoBERT chấm điểm ở đây
    c = Comment(movie_id=movie_id, user_id=user.id, content=text, is_negative=is_negative,
                negative_score=score, model_name=classifier.name)
    db.add(c)
    db.commit()
    db.refresh(c)
    return to_out(c)


@router.get("/admin/comments", response_model=list[AdminCommentOut])
def admin_comments(label: Literal["negative", "normal"] | None = None,
                   _: User = Depends(require_admin), db: Session = Depends(get_db)):
    query = select(Comment).order_by(Comment.created_at.desc())
    if label:
        query = query.where(Comment.is_negative == (label == "negative"))
    return [to_out(c) for c in db.scalars(query).all()]
