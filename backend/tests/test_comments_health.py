import csv
import io

from app.models import Comment


def test_comment_score_is_persisted(client, auth_headers, movie, db):
    response = client.post(f"/api/movies/{movie.id}/comments", headers=auth_headers["user"],
                           json={"content": "Phim quá thất vọng"})
    assert response.status_code == 201
    row = db.get(Comment, response.json()["id"])
    assert row.is_negative is True
    assert row.negative_score == 0.91
    assert row.model_name == "fake"


def test_blank_comment_returns_vietnamese_422(client, auth_headers, movie):
    response = client.post(f"/api/movies/{movie.id}/comments", headers=auth_headers["user"],
                           json={"content": "   "})
    assert response.status_code == 422
    assert "không được để trống" in response.json()["detail"]


def test_review_preserves_original_model_result_and_csv_is_safe(
    client, auth_headers, movie, users, db
):
    user, _ = users
    row = Comment(movie_id=movie.id, user_id=user.id, content="=2+2",
                  is_negative=True, negative_score=0.91, model_name="fake",
                  model_version="test-1")
    db.add(row)
    db.commit()
    original = (row.is_negative, row.negative_score, row.model_name, row.model_version, row.content)

    reviewed = client.patch(f"/api/admin/comments/{row.id}", headers=auth_headers["admin"],
                            json={"action": "relabel", "label": 0})
    assert reviewed.status_code == 200
    db.refresh(row)
    assert (row.is_negative, row.negative_score, row.model_name, row.model_version, row.content) == original

    exported = client.get("/api/admin/comments/export.csv", headers=auth_headers["admin"])
    assert exported.status_code == 200
    parsed = list(csv.reader(io.StringIO(exported.content.decode("utf-8-sig"))))
    assert parsed[1][0].startswith("'")
    assert parsed[1][1].startswith("'")
    db.refresh(row)
    assert row.content == "=2+2"


def test_comment_moderation_filter_stats_and_visibility(client, auth_headers, movie, users, db):
    user, _ = users
    row = Comment(movie_id=movie.id, user_id=user.id, content="Bình luận cần duyệt",
                  is_negative=True, negative_score=0.91, model_name="fake",
                  model_version="test-1")
    db.add(row)
    db.commit()

    confirmed = client.patch(f"/api/admin/comments/{row.id}", headers=auth_headers["admin"],
                             json={"action": "confirm"})
    assert confirmed.status_code == 200
    assert confirmed.json()["human_label"] == 1
    stats = client.get("/api/admin/comments/stats", headers=auth_headers["admin"]).json()
    assert stats == {"reviewed": 1, "agree": 1, "disagree": 0, "accuracy": 1.0,
                     "tp": 1, "fp": 0, "tn": 0, "fn": 0}
    reviewed = client.get("/api/admin/comments?reviewed=true",
                          headers=auth_headers["admin"]).json()
    assert reviewed["total"] == 1

    assert client.patch(f"/api/admin/comments/{row.id}", headers=auth_headers["admin"],
                        json={"action": "hide"}).status_code == 200
    public = client.get(f"/api/movies/{movie.id}/comments")
    assert public.status_code == 200
    assert public.json() == []


def test_invalid_review_payload_returns_vietnamese_422(client, auth_headers):
    response = client.patch("/api/admin/comments/1", headers=auth_headers["admin"],
                            json={"action": "relabel", "label": "sai"})
    assert response.status_code == 422
    assert "không hợp lệ" in response.json()["detail"]
    assert "input should be" not in response.json()["detail"].lower()


def test_health_does_not_expose_internal_classifier_errors(client, fake_classifier):
    fake_classifier.error = "FileNotFoundError: C:\\Users\\secret\\model"
    fake_classifier.health = lambda: [{
        "name": "broken", "version": "x", "loaded": False,
        "available": False, "active": False,
        "error": "[WinError 110] C:\\Users\\secret\\model",
    }]
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    serialized = response.text
    assert "C:\\\\Users" not in serialized
    assert "WinError" not in serialized
    assert body["classifier_error"] == "Model được cấu hình không khả dụng."
    assert body["models"][0]["error"] == "Model không khả dụng."


def test_missing_model_falls_back_without_importing_torch(monkeypatch):
    import builtins
    from app import classifier as classifier_module

    imported = []
    original_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        if name == "torch" or name.startswith("transformers"):
            imported.append(name)
            raise AssertionError("Không được import thư viện model khi checkpoint không tồn tại")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(classifier_module, "MODEL_DIR", "tests/__missing__/a")
    monkeypatch.setattr(classifier_module, "MODEL_DIR_B", "tests/__missing__/b")
    monkeypatch.setattr(classifier_module, "SKLEARN_MODELS", "")
    monkeypatch.setattr(classifier_module, "ACTIVE_MODEL", "phobert_b")
    monkeypatch.setattr(builtins, "__import__", guarded_import)
    registry = classifier_module.ModelRegistry()
    assert registry.name == "keyword"
    assert registry.predict("phim chán") == (True, 0.87)
    assert imported == []
