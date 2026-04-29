import os
from functools import lru_cache

import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


@lru_cache(maxsize=1)
def _get_client() -> genai.Client:
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION")
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not project or not location or not credentials_path:
        raise RuntimeError(
            "Vertex AI settings are missing. Set GOOGLE_CLOUD_PROJECT, "
            "GOOGLE_CLOUD_LOCATION, and GOOGLE_APPLICATION_CREDENTIALS in .env."
        )
    if not os.path.exists(credentials_path):
        raise RuntimeError(
            f"Service account key file not found: {credentials_path}"
        )
    return genai.Client(vertexai=True, project=project, location=location)


def _normalize_task_type(task_type: str) -> str:
    # Vertex AI expects uppercase task types.
    return task_type.upper()


def get_query_embedding(query: str) -> list[float]:
    client = _get_client()
    result = client.models.embed_content(
        model="publishers/google/models/text-multilingual-embedding-002",
        contents=query,
        config=types.EmbedContentConfig(
            task_type=_normalize_task_type("retrieval_query")
        ),
    )
    return result.embeddings[0].values


@lru_cache(maxsize=1)
def _get_collection() -> chromadb.Collection:
    client = chromadb.PersistentClient(path="./chroma_db")
    return client.get_collection("mumzworld_products")


def retrieve_products(query: str, top_k: int = 8) -> list[dict]:
    collection = _get_collection()

    query_emb = get_query_embedding(query)

    results = collection.query(
        query_embeddings=[query_emb],
        n_results=top_k,
        include=["metadatas", "distances"],
    )

    products: list[dict] = []
    for meta, dist in zip(results["metadatas"][0], results["distances"][0]):
        item = dict(meta)
        item["similarity_score"] = round(1 - dist, 3)
        products.append(item)

    return products
