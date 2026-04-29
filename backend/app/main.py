from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.schemas import DiagnoseRequest, DiagnoseResponse, TicketRequest, TicketResponse
from app.services.repair_agent import RepairAgent

settings = get_settings()
agent = RepairAgent(settings)

app = FastAPI(
    title="MiMo RepairMind API",
    description="MVP API for a MiMo-powered smart-device repair and after-sales agent.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {
        "ok": True,
        "demo_mode": settings.demo_mode,
        "model": settings.mimo_model,
        "kb_sources": agent.kb.list_sources(),
    }


@app.post("/api/diagnose", response_model=DiagnoseResponse)
async def diagnose(payload: DiagnoseRequest) -> DiagnoseResponse:
    return await agent.diagnose(payload)


@app.post("/api/ticket", response_model=TicketResponse)
def create_ticket(payload: TicketRequest) -> TicketResponse:
    return agent.create_ticket(payload)
