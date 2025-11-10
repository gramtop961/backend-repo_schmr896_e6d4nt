"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# The Fone Buyers app schemas

class Device(BaseModel):
    """
    Devices available for trade-in
    Collection name: "device"
    """
    brand: str = Field(..., description="Device brand, e.g., Apple, Samsung")
    model: str = Field(..., description="Model name, e.g., iPhone 14 Pro")
    storages: List[int] = Field(default_factory=list, description="Available storage options in GB")
    base_price: float = Field(..., ge=0, description="Base price used for quote calculations")
    image: Optional[str] = Field(None, description="Optional image URL")

class QuoteRequest(BaseModel):
    brand: str
    model: str
    storage: int
    condition: str  # Like New, Good, Fair, Broken

class QuoteResponse(BaseModel):
    brand: str
    model: str
    storage: int
    condition: str
    offer: float
    currency: str = "USD"
