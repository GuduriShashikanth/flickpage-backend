from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# User Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: str = Field(..., min_length=2)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Rating Models
class RatingCreate(BaseModel):
    item_id: int
    item_type: str = Field(..., pattern="^(movie|book)$")
    rating: float = Field(..., ge=0.5, le=5.0)

class RatingResponse(BaseModel):
    id: int
    user_id: int
    item_id: int
    item_type: str
    rating: float
    created_at: datetime

# Interaction Models
class InteractionCreate(BaseModel):
    item_id: int
    item_type: str = Field(..., pattern="^(movie|book)$")
    interaction_type: str = Field(..., pattern="^(view|click|search)$")

class InteractionResponse(BaseModel):
    id: int
    user_id: int
    item_id: int
    item_type: str
    interaction_type: str
    created_at: datetime

# Recommendation Models
class RecommendationResponse(BaseModel):
    item_id: int
    item_type: str
    title: str
    score: float
    reason: str  # "collaborative", "content", "hybrid"
