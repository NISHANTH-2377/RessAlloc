from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer


class WorkforceVectorStore:
    def __init__(self, host="localhost", port=6333, collection_name="employee_workforce"):
        self.client = QdrantClient(host=host, port=port, check_compatibility=False)
        self.collection_name = collection_name
        self.embed_model = None

    def _get_embed_model(self):
        if self.embed_model is None:
            self.embed_model = SentenceTransformer("all-MiniLM-L6-v2")
        return self.embed_model

    def _ensure_collection(self):
        try:
            self.client.get_collection(self.collection_name)
            return
        except Exception:
            pass

        try:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
            )
        except Exception:
            pass

    def _embed_text(self, text: str) -> list[float]:
        if not text:
            return [0.0] * 384
        vector = self._get_embed_model().encode(str(text), normalize_embeddings=True)
        return [float(value) for value in vector.tolist()]

    def index_employee_records(self, employee_records: list[dict]) -> int:
        self._ensure_collection()
        points = []

        for index, record in enumerate(employee_records):
            payload = {
                "employee_id": record.get("employee_id"),
                "full_name": record.get("full_name"),
                "job_title": record.get("job_title"),
                "department": record.get("department"),
                "skills": record.get("skills", []),
                "current_project": record.get("current_project"),
                "current_project_weight": record.get("current_project_weight"),
                "project_changes_last_30_days": int(record.get("project_changes_last_30_days", 0)),
                "days_on_current_project": int(record.get("days_on_current_project", 0)),
                "is_lead": bool(record.get("is_lead", False)),
                "availability_hours": float(record.get("availability_hours", 0.0)),
                "ability_score": float(record.get("ability_score", 0.5)),
                "utilization": float(record.get("utilization", 0.0)),
                "resume_text": record.get("resume_text", ""),
            }

            text_source = (
                payload.get("resume_text")
                or " ".join(str(skill) for skill in payload.get("skills", []))
                or payload.get("job_title")
                or payload.get("full_name")
                or str(record.get("employee_id", index))
            )
            point_id = record.get("employee_id") or index + 1
            points.append(
                models.PointStruct(
                    id=str(point_id),
                    vector=self._embed_text(text_source),
                    payload=payload,
                )
            )

        if points:
            self.client.upsert(collection_name=self.collection_name, points=points, wait=True)
        return len(points)

    def search_semantic_candidates(self, project_text: str, top_k: int = 5) -> list[dict]:
        self._ensure_collection()
        query_vector = self._embed_text(project_text)

        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k,
            )
        except Exception:
            return []

        normalized = []
        for item in results:
            payload = getattr(item, "payload", {}) or {}
            normalized.append(
                {
                    "employee_id": payload.get("employee_id"),
                    "name": payload.get("full_name") or payload.get("employee_id"),
                    "score": float(getattr(item, "score", 0.0)),
                    "payload": payload,
                }
            )
        return normalized

    def hybrid_search_with_lead_immunity(self, query_vector: list, required_skill: str, top_k=5):
        lead_immunity_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="is_lead",
                    match=models.MatchValue(value=False),
                ),
                models.FieldCondition(
                    key="skills",
                    match=models.MatchValue(value=required_skill),
                ),
            ]
        )

        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=lead_immunity_filter,
            limit=top_k,
        )
        return search_result