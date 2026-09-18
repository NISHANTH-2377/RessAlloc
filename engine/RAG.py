from llama_index.core import VectorStoreIndex, Document, StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from sentence_transformers import SentenceTransformer
import os

class WorkforceRAGPipeline:
    def __init__(self, qdrant_client, collection_name="employee_workforce"):
        self.client = qdrant_client
        self.collection_name = collection_name
        self.embed_model = None

    def _get_embed_model(self):
        if self.embed_model is None:
            self.embed_model = SentenceTransformer("all-MiniLM-L6-v2")
        return self.embed_model

    def ingest_employee_documents(self, raw_employee_records: list[dict]):
        """
        Parses employee records, generates vector embeddings, 
        and indexes them with structural metadata into Qdrant.
        """
        documents = []
        for record in raw_employee_records:
            # Create LlamaIndex document with text content and metadata
            doc = Document(
                text=record.get("resume_text", ""),
                metadata={
                    "employee_id": record.get("employee_id"),
                    "is_lead": record.get("is_lead", False),
                    "skills": record.get("skills", []),
                    "current_project": record.get("current_project")
                }
            )
            documents.append(doc)

        # Vector store integration
        vector_store = QdrantVectorStore(client=self.client, collection_name=self.collection_name)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        # Build index
        index = VectorStoreIndex.from_documents(
            documents, 
            storage_context=storage_context
        )
        return index

    def retrieve_context(self, query_text: str, top_k=3):
        """
        Retrieves relevant workforce context matching the query string.
        """
        query_vector = self._get_embed_model().encode(query_text).tolist()
        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k
        )
        return search_results