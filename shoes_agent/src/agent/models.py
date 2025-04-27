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
    # Shoe-specific attributes
    attributes: Dict[str, str]  # e.g., size, color, material, style

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
    filters: Optional[Dict] = None   # Optional filters like price range, size, etc.

class ProductResponse(Model):
    type: str
    data: List[Dict]
    status: str = "success" 