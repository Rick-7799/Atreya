from typing import List, Dict
import re
from .graph import GraphService
from .recommender import RecommenderService
from ..models.schemas import RecommendRequest

LIFESTYLE_KEYWORDS = {
    "smoker": ["smoker", "smoking", "cigarette"],
    "alcohol": ["alcohol", "drinking", "drink"],
    "poor sleep": ["poor sleep", "insomnia", "cant sleep", "can't sleep", "late night"],
    "high stress": ["stress", "stressed", "anxiety", "overworked"],
    "sedentary": ["sedentary", "no exercise", "inactive", "sitting all day"],
    "balanced diet": ["balanced diet", "healthy diet", "clean eating"]
}

class ChatService:
    def __init__(self, graph: GraphService, recommender: RecommenderService):
        self.graph = graph
        self.recommender = recommender
        self._symptoms = None

    def _get_symptoms_catalog(self) -> List[str]:
        if self._symptoms is None:
            self._symptoms = self.graph.all_symptoms()
        return self._symptoms

    @staticmethod
    def _normalize(text: str) -> str:
        return re.sub(r"\s+", " ", text.strip().lower())

    def extract(self, message: str) -> Dict[str, List[str]]:
        text = self._normalize(message)

        # Symptoms: match by substring against known symptom names
        syms = []
        for s in self._get_symptoms_catalog():
            s_norm = s.lower()
            if s_norm in text:
                syms.append(s)

        # Lifestyle: keyword buckets
        lifestyle = []
        for label, keys in LIFESTYLE_KEYWORDS.items():
            if any(k in text for k in keys):
                lifestyle.append(label)

        return {"symptoms": list(dict.fromkeys(syms)), "lifestyle": list(dict.fromkeys(lifestyle))}

    def reply(self, message: str) -> Dict[str, any]:
        extracted = self.extract(message)
        # Provide defaults if user didn't state age/gender explicitly
        req = RecommendRequest(
            age=25,
            gender="other",
            symptoms=extracted["symptoms"],
            lifestyle=extracted["lifestyle"],
            conditions_history=[]
        )
        rec = self.recommender.recommend(req)

        # Format a friendly markdown reply
        lines = []
        if extracted["symptoms"]:
            lines.append(f"**Detected symptoms:** {', '.join(extracted['symptoms'])}")
        if extracted["lifestyle"]:
            lines.append(f"**Lifestyle cues:** {', '.join(extracted['lifestyle'])}")
        if not lines:
            lines.append("_I couldn't detect specific symptoms. Here are some general suggestions._")

        lines.append("\n### Suggestions")
        for s in rec.suggestions:
            avoid = f" • **Avoid with:** {', '.join(s.avoid_with)}" if s.avoid_with else ""
            how = f" • **How:** {s.how_to_use}" if s.how_to_use else ""
            lines.append(f"- **{s.name}** — **Why:** {s.why}{how}{avoid}")

        lines.append("\n### Tips")
        for t in rec.tips:
            lines.append(f"- {t}")

        lines.append(f"\n> {rec.disclaimer}")
        return {"reply": "\n".join(lines), "extracted": extracted, "disclaimer": rec.disclaimer}
