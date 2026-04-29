from pydantic import BaseModel
from typing import Optional


class ProductCard(BaseModel):
    name_en: str
    name_ar: str
    price_aed: int
    category: str
    age_range: str
    description_en: str
    description_ar: str
    reasoning_en: str
    reasoning_ar: str
    confidence: float


class GiftResponse(BaseModel):
    query_understood_en: str
    query_understood_ar: str
    products: list[ProductCard]
    needs_clarification: bool
    clarification_question_en: Optional[str] = None
    clarification_question_ar: Optional[str] = None
    fallback_message_en: Optional[str] = None
    fallback_message_ar: Optional[str] = None
