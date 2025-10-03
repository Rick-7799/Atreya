from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

DISCLAIMER = "This is an educational demo and not medical advice. Always consult a qualified professional."

class RecommendRequest(BaseModel):
    age: int = Field(..., ge=0, le=120)
    gender: str = Field(..., description="male/female/other")
    symptoms: List[str] = Field(default_factory=list)
    lifestyle: List[str] = Field(default_factory=list)
    conditions_history: List[str] = Field(default_factory=list)

class HerbSuggestion(BaseModel):
    name: str
    why: str
    how_to_use: Optional[str] = None
    avoid_with: List[str] = Field(default_factory=list)

class RecommendResponse(BaseModel):
    suggestions: List[HerbSuggestion]
    tips: List[str]
    disclaimer: str = DISCLAIMER
    debug: Optional[Dict[str, Any]] = None

class DiagnosisRequest(BaseModel):
    symptoms: List[str] = Field(default_factory=list)
    lifestyle: List[str] = Field(default_factory=list)

class DiagnosisResponse(BaseModel):
    probable_conditions: List[str]
    confidence: float = Field(..., ge=0.0, le=1.0)
    rationale: str
    disclaimer: str = DISCLAIMER

class HerbItem(BaseModel):
    name: str
    properties: List[str] = Field(default_factory=list)

class HerbSearchResponse(BaseModel):
    query: str
    herbs: List[HerbItem]

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    extracted: Dict[str, List[str]] = Field(default_factory=dict)  
    disclaimer: str = DISCLAIMER
