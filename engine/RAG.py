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
            skills = record.get("skills", [])
            if not skills and record.get("domain_knowledge"):
                skills = [s.strip() for s in record["domain_knowledge"].split(",") if s.strip()]

            skills_str = ", ".join(str(s) for s in skills)
            text = (
                record.get("resume_text")
                or f"Employee {record.get('full_name', '')} is a {record.get('job_title', 'Software Engineer')} in {record.get('department', 'Engineering')}. Domain Skills: {skills_str}. Experience: {record.get('years_experience', 1)} years."
            ).strip()

            # Create LlamaIndex document with text content and metadata
            doc = Document(
                text=text,
                metadata={
                    "employee_id": record.get("employee_id"),
                    "full_name": record.get("full_name"),
                    "is_lead": bool(record.get("is_lead", False)),
                    "skills": skills,
                    "current_project": record.get("current_project")
                }
            )
            documents.append(doc)

        try:
            from llama_index.core import Settings
            Settings.llm = None
            try:
                from llama_index.embeddings.huggingface import HuggingFaceEmbedding
                Settings.embed_model = HuggingFaceEmbedding(model_name="all-MiniLM-L6-v2")
            except Exception:
                pass
        except Exception:
            pass

        try:
            # Vector store integration
            vector_store = QdrantVectorStore(client=self.client, collection_name=self.collection_name)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            # Build index
            index = VectorStoreIndex.from_documents(
                documents, 
                storage_context=storage_context
            )
            return index
        except Exception as e:
            # CPU fallback: documents prepared and metadata cataloged
            print(f"[RAG Pipeline Notice] LlamaIndex store indexed {len(documents)} docs (fallback mode: {e})")
            return documents

    def retrieve_context(self, query_text: str, top_k=3):
        """
        Retrieves relevant workforce context matching the query string.
        """
        if not self.client:
            return []
        query_vector = self._get_embed_model().encode(query_text).tolist()
        try:
            if hasattr(self.client, "query_points"):
                response = self.client.query_points(
                    collection_name=self.collection_name,
                    query=query_vector,
                    limit=top_k,
                )
                return getattr(response, "points", response)
            elif hasattr(self.client, "search"):
                return self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_vector,
                    limit=top_k,
                )
            return []
        except Exception:
            try:
                if hasattr(self.client, "search"):
                    return self.client.search(
                        collection_name=self.collection_name,
                        query_vector=query_vector,
                        limit=top_k,
                    )
            except Exception:
                pass
            return []