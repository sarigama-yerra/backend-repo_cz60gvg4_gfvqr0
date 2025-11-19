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

from pydantic import BaseModel, Field, HttpUrl
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

# App-specific schema for the System Software learning feed
class Systemclip(BaseModel):
    """
    Short, vertical-clip style lesson about system software topics.
    Collection name: "systemclip"
    """
    title: str = Field(..., description="Clip title")
    topic: str = Field(..., description="Area like OS, Compilers, Networking, DBMS, etc.")
    description: Optional[str] = Field(None, description="Brief summary shown on overlay")
    video_url: HttpUrl = Field(..., description="MP4 or streamable URL")
    thumbnail_url: Optional[HttpUrl] = Field(None, description="Optional preview image")
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    difficulty: Optional[str] = Field(None, description="beginner | intermediate | advanced")
    likes: int = Field(0, ge=0, description="Total likes")
    bookmarks: int = Field(0, ge=0, description="Total bookmarks")
    author: Optional[str] = Field(None, description="Display name of the author")

# Add your own schemas here:
# --------------------------------------------------

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
