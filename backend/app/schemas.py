from typing import List, Literal, Optional

from pydantic import BaseModel, Field


DeviceCategory = Literal[
    "router",
    "robot_vacuum",
    "smart_camera",
    "earbuds_wearable",
    "tv_projector",
    "other",
]

RiskLevel = Literal["low", "medium", "high"]


class DiagnoseRequest(BaseModel):
    category: DeviceCategory = "other"
    device_model: Optional[str] = Field(default=None, max_length=120)
    issue_description: str = Field(min_length=5, max_length=4000)
    image_note: Optional[str] = Field(default=None, max_length=1000)
    user_language: str = Field(default="zh-CN", max_length=20)


class RepairStep(BaseModel):
    title: str
    instruction: str
    expected_observation: str
    next_if_failed: str
    safety_note: Optional[str] = None


class DiagnoseResponse(BaseModel):
    summary: str
    likely_issue: str
    risk_level: RiskLevel
    need_more_info: List[str]
    steps: List[RepairStep]
    stop_conditions: List[str]
    matched_knowledge: List[str]
    model_used: str
    demo_mode: bool


class TicketRequest(BaseModel):
    original_request: DiagnoseRequest
    diagnosis: DiagnoseResponse


class TicketResponse(BaseModel):
    title: str
    priority: Literal["P3-low", "P2-normal", "P1-urgent"]
    customer_summary: str
    technical_summary: str
    tried_steps: List[str]
    recommended_next_action: str
