from uagents import Model
from typing import List, Dict, Optional
from pydantic import BaseModel

class Review(Model):
    id: str
    userId: str
    rating: float
    comment: str
    date: str

class ProductAttributes(Model):
    # Generic attributes that can be used for any product
    attributes: Dict[str, str]

class Product(Model):
    id: str
    name: str
    price: float
    description: str
    images: List[str]
    reviews: List[Review]
    attributes: ProductAttributes

class ProductRequest(Model):
    type: str = "get_all_products"  # Default request type
    filters: Optional[Dict] = None   # Optional filters like price range, category, etc.

class ProductResponse(Model):
    type: str
    data: List[Dict]
    status: str = "success"

class Query(Model):
    message: str

class SearchResponse(Model):
    status: str
    data: dict = None