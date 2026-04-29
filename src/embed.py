import json
import os

import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


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


def get_embedding(client: genai.Client, text: str) -> list[float]:
    result = client.models.embed_content(
        model="publishers/google/models/text-multilingual-embedding-002",
        contents=text,
        config=types.EmbedContentConfig(
            task_type=_normalize_task_type("retrieval_document")
        ),
    )
    return result.embeddings[0].values


def build_catalog_text(product: dict) -> str:
    return (
        f"{product['name']}. Category: {product['category']}. "
        f"Age: {product['age_range']}. Price: {product['price_aed']} AED. "
        f"Tags: {', '.join(product['tags'])}. {product['description']}"
    )


def ingest_catalog() -> None:
    genai_client = _get_client()

    client = chromadb.PersistentClient(path="./chroma_db")
    collections = client.list_collections()
    collection_names = {c.name for c in collections} if collections else set()
    if "mumzworld_products" in collection_names:
        client.delete_collection("mumzworld_products")

    collection = client.create_collection(
        name="mumzworld_products",
        metadata={"hnsw:space": "cosine"},
    )

    with open("data/catalog.json", encoding="utf-8") as file:
        products = json.load(file)

    ids: list[str] = []
    embeddings: list[list[float]] = []
    documents: list[str] = []
    metadatas: list[dict] = []

    for product in products:
        text = build_catalog_text(product)
        emb = get_embedding(genai_client, text)
        ids.append(product["id"])
        embeddings.append(emb)
        documents.append(text)
        metadatas.append(
            {
                "name": product["name"],
                "name_ar": product["name_ar"],
                "price_aed": product["price_aed"],
                "category": product["category"],
                "age_range": product["age_range"],
                "description": product["description"],
                "description_ar": product["description_ar"],
            }
        )

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )
    print(f"✅ Ingested {len(products)} products into ChromaDB")


if __name__ == "__main__":
    ingest_catalog()
