from qdrant_client import QdrantClient
from qdrant_client.http import models

class WorkforceVectorStore:
    def __init__(self, host="localhost", port=6333):
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = "employee_workforce"

    def hybrid_search_with_lead_immunity(self, query_vector: list, required_skill: str, top_k=5):
       
        lead_immunity_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="is_lead",
                    match=models.MatchValue(value=False)
                ),
                models.FieldCondition(
                    key="skills",
                    match=models.MatchValue(value=required_skill)
                )
            ]
        )

        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=lead_immunity_filter,
            limit=top_k
        )
        return search_result