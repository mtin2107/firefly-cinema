import csv
import io
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..classifier import classifier, normalize
from ..database import get_db
from ..models import Comment, User
from ..schemas import (
    AdminCommentAction,
    AdminCommentOut,
    AdminCommentPage,
    AdminCommentStats,
    CommentIn,
    CommentOut,
)
from ..security import get_current_user, require_admin
from .movies import get_movie_or_404

router = APIRouter(prefix="/api", tags=["Bình luận"])


def to_out(c: Comment) -> dict:
    reviewed = c.human_label in (0, 1)
    effective_negative = bool(c.human_label) if reviewed else c.is_negative
    return {"id": c.id, "movie_id": c.movie_id, "user_name": c.user.full_name, "content": c.content,
            "is_negative": c.is_negative, "effective_negative": effective_negative, "reviewed": reviewed,
            "negative_score": c.negative_score, "created_at": c.created_at,
            "movie_title": c.movie.title, "model_name": c.model_name,
            "human_label": c.human_label, "reviewed_by": c.reviewed_by,
            "reviewed_by_name": c.reviewer.full_name if c.reviewer else None,
            "reviewed_at": c.reviewed_at, "hidden": c.hidden}


@router.get("/movies/{movie_id}/comments", response_model=list[CommentOut])
def list_comments(movie_id: int, db: Session = Depends(get_db)):
    get_movie_or_404(db, movie_id)
    rows = db.scalars(select(Comment).where(
        Comment.movie_id == movie_id, Comment.hidden.is_(False)
    ).order_by(Comment.created_at.desc())).all()
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


@router.get("/admin/comments", response_model=AdminCommentPage)
def admin_comments(
    label: Literal["negative", "normal"] | None = None,
    reviewed: bool | None = None,
    page: int = Query(1),
    page_size: int = Query(20),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if page < 1:
        raise HTTPException(422, "Trang phải là số nguyên từ 1 trở lên.")
    if not 1 <= page_size <= 100:
        raise HTTPException(422, "Số bình luận mỗi trang phải từ 1 đến 100.")
    filters = []
    if label:
        filters.append(Comment.is_negative == (label == "negative"))
    if reviewed is not None:
        filters.append(Comment.human_label.is_not(None) if reviewed else Comment.human_label.is_(None))
    total = db.scalar(select(func.count()).select_from(Comment).where(*filters)) or 0
    query = (select(Comment).where(*filters).order_by(Comment.created_at.desc(), Comment.id.desc())
             .offset((page - 1) * page_size).limit(page_size))
    return {"items": [to_out(c) for c in db.scalars(query).all()], "total": total}


@router.patch("/admin/comments/{comment_id}", response_model=AdminCommentOut)
def update_admin_comment(
    comment_id: int,
    body: AdminCommentAction,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    comment = db.get(Comment, comment_id)
    if comment is None:
        raise HTTPException(404, "Không tìm thấy bình luận.")

    if body.action == "confirm":
        comment.human_label = int(comment.is_negative)
        comment.reviewed_by = admin.id
        comment.reviewed_at = datetime.now()
    elif body.action == "relabel":
        if body.label not in (0, 1):
            raise HTTPException(422, "Đổi nhãn cần label là 0 hoặc 1.")
        comment.human_label = body.label
        comment.reviewed_by = admin.id
        comment.reviewed_at = datetime.now()
    elif body.action == "hide":
        comment.hidden = True
    else:
        comment.hidden = False

    db.commit()
    db.refresh(comment)
    return to_out(comment)


@router.get("/admin/comments/stats", response_model=AdminCommentStats)
def admin_comment_stats(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    rows = db.scalars(select(Comment).where(Comment.human_label.in_([0, 1]))).all()
    tp = sum(c.is_negative and c.human_label == 1 for c in rows)
    fp = sum(c.is_negative and c.human_label == 0 for c in rows)
    tn = sum(not c.is_negative and c.human_label == 0 for c in rows)
    fn = sum(not c.is_negative and c.human_label == 1 for c in rows)
    reviewed = len(rows)
    agree = tp + tn
    disagree = fp + fn
    return {"reviewed": reviewed, "agree": agree, "disagree": disagree,
            "accuracy": agree / reviewed if reviewed else 0.0,
            "tp": tp, "fp": fp, "tn": tn, "fn": fn}


@router.get("/admin/comments/export.csv")
def export_admin_comments(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    rows = db.scalars(select(Comment).where(Comment.human_label.in_([0, 1])).order_by(Comment.id)).all()
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\r\n")
    writer.writerow(["text", "text_norm", "label"])
    for comment in rows:
        writer.writerow([comment.content, normalize(comment.content), comment.human_label])
    return Response(
        content=output.getvalue().encode("utf-8-sig"),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="firefly_comments_reviewed.csv"'},
    )
