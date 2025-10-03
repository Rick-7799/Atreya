from typing import List, Dict, Any
from ..models.schemas import RecommendRequest, RecommendResponse, HerbSuggestion, DiagnosisRequest, DiagnosisResponse
from .graph import GraphService
from .llm import generate_recommendations, generate_diagnosis

class RecommenderService:
    def __init__(self, graph: GraphService):
        self.graph = graph

    def recommend(self, req: RecommendRequest) -> RecommendResponse:
        facts = self.graph.herbs_for_symptoms(req.symptoms)
        herbs = list({f["herb"] for f in facts})
        avoid_map = self.graph.contraindications(herbs)

        llm_text = generate_recommendations(
            age=req.age,
            gender=req.gender,
            symptoms=req.symptoms,
            lifestyle=req.lifestyle,
            facts=facts,
            avoid_map=avoid_map
        )

        top = {}
        for f in facts:
            h = f["herb"]
            top.setdefault(h, {"why": [], "how": "tea/decoction 1-2x daily"})
            why = f.get("evidence") or f.get("condition")
            if why and why not in top[h]["why"]:
                top[h]["why"].append(why)
        suggestions = []
        for i, (h, v) in enumerate(top.items()):
            if i >= 5: break
            suggestions.append(HerbSuggestion(
                name=h,
                why="; ".join(v["why"]) or "Traditional support",
                how_to_use=v["how"],
                avoid_with=avoid_map.get(h, [])
            ))

        tips = [
            "Prioritize 7–8 hours of consistent sleep.",
            "Hydrate regularly; warm water or herbal tea can support digestion.",
            "Gentle daily movement (e.g., yoga, walking) supports overall balance."
        ]

        return RecommendResponse(
            suggestions=suggestions,
            tips=tips,
            disclaimer="This is an educational demo and not medical advice. Consult a qualified professional.",
            debug={"llm": llm_text[:1200]}
        )

    def diagnose(self, req: DiagnosisRequest) -> DiagnosisResponse:
        conditions = self.graph.conditions_from_symptoms(req.symptoms)
        out = generate_diagnosis(req.symptoms, req.lifestyle, conditions)
        return DiagnosisResponse(
            probable_conditions=conditions[:3],
            confidence=out["confidence"],
            rationale=out["text"],
            disclaimer="This is an educational demo and not medical advice. Consult a qualified professional."
        )
