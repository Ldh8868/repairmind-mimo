import asyncio

from app.config import Settings
from app.schemas import DiagnoseRequest
from app.services.repair_agent import RepairAgent


def test_router_demo_diagnosis():
    agent = RepairAgent(Settings(DEMO_MODE=True))
    response = asyncio.run(
        agent.diagnose(
            DiagnoseRequest(
                category="router",
                device_model="AX3000",
                issue_description="Wi-Fi 能连接，但是没有网络，橙色灯闪烁，已经重启过。",
            )
        )
    )
    assert response.demo_mode is True
    assert response.risk_level == "low"
    assert len(response.steps) >= 2


def test_high_risk_stop():
    agent = RepairAgent(Settings(DEMO_MODE=True))
    response = asyncio.run(
        agent.diagnose(
            DiagnoseRequest(
                category="earbuds_wearable",
                device_model="unknown",
                issue_description="充电盒有焦味，而且电池鼓包。",
            )
        )
    )
    assert response.risk_level == "high"
    assert "停止" in response.steps[0].instruction
