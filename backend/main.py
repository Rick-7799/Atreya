from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from atreya.models.schemas import RecommendRequest, RecommendResponse, DiagnosisRequest, DiagnosisResponse, HerbSearchResponse
from atreya.services.graph import GraphService
from atreya.services.recommender import RecommenderService
from atreya.utils.config import settings
from atreya.models.schemas import RecommendRequest, RecommendResponse, DiagnosisRequest, DiagnosisResponse, HerbSearchResponse, ChatRequest, ChatResponse
from atreya.services.chat import ChatService


app = FastAPI(
    title="Atreya API",
    version="1.0.0",
    description="Educational demo: personalized wellness suggestions using LangChain + Neo4j. Not medical advice."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = GraphService()
recommender = RecommenderService(graph=graph)
chat_service = ChatService(graph=graph, recommender=recommender)


@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/recommendations", response_model=RecommendResponse)
def recommendations(req: RecommendRequest):
    try:
        result = recommender.recommend(req)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/diagnosis", response_model=DiagnosisResponse)
def diagnosis(req: DiagnosisRequest):
    try:
        result = recommender.diagnose(req)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/herbs/search", response_model=HerbSearchResponse)
def herbs_search(q: str = ""):
    try:
        herbs = graph.search_herbs(q)
        return {"query": q, "herbs": herbs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        out = chat_service.reply(req.message)
        return out
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
