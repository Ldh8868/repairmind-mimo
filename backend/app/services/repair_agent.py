from __future__ import annotations

import json
from typing import List

from app.config import Settings
from app.schemas import (
    DiagnoseRequest,
    DiagnoseResponse,
    RepairStep,
    TicketRequest,
    TicketResponse,
)
from app.services.knowledge_base import KnowledgeBase, KnowledgeChunk
from app.services.mimo_client import MiMoAPIError, MiMoClient

SYSTEM_PROMPT = """你是 MiMo RepairMind，一个智能硬件售后维修 Agent。
你的目标是：安全、准确、步骤化地帮助普通用户排查智能硬件问题。
必须遵守：
1. 不指导危险拆机、电池穿刺、高压电操作、绕过安全限制。
2. 遇到冒烟、焦味、漏电、异常发热、进水、膨胀电池，立即建议停止使用并联系官方售后。
3. 每一步只给清晰、可执行、低风险的动作。
4. 不确定时要追问，不要编造官方保修政策。
5. 输出必须是 JSON，不要 Markdown。
"""

DIAGNOSIS_JSON_SCHEMA = """
{
  "summary": "一句话总结用户问题",
  "likely_issue": "最可能故障类型",
  "risk_level": "low | medium | high",
  "need_more_info": ["还需要补充的信息"],
  "steps": [
    {
      "title": "步骤标题",
      "instruction": "用户要做什么",
      "expected_observation": "用户要观察什么结果",
      "next_if_failed": "如果失败下一步怎么办",
      "safety_note": "安全提示，可为空"
    }
  ],
  "stop_conditions": ["什么情况下停止自助处理"]
}
"""

HIGH_RISK_KEYWORDS = ["冒烟", "焦味", "漏电", "电击", "进水", "电池鼓包", "膨胀", "烧焦", "火花", "过热"]


class RepairAgent:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.kb = KnowledgeBase()
        self.mimo = MiMoClient(settings)

    async def diagnose(self, request: DiagnoseRequest) -> DiagnoseResponse:
        chunks = self.kb.search(
            query=f"{request.device_model or ''} {request.issue_description} {request.image_note or ''}",
            category=request.category,
            limit=5,
        )
        model_text = await self._call_model_for_diagnosis(request, chunks)
        if model_text:
            parsed = self._parse_diagnosis_json(model_text)
            if parsed:
                return DiagnoseResponse(
                    **parsed,
                    matched_knowledge=self._source_labels(chunks),
                    model_used=self.settings.mimo_model,
                    demo_mode=False,
                )
        return self._fallback_diagnosis(request, chunks)

    async def _call_model_for_diagnosis(
        self,
        request: DiagnoseRequest,
        chunks: List[KnowledgeChunk],
    ) -> str | None:
        if not self.mimo.enabled:
            return None

        kb_context = self.kb.format_chunks(chunks)
        user_prompt = f"""
请基于以下知识库和用户描述进行智能硬件售后诊断。

用户语言：{request.user_language}
设备类型：{request.category}
设备型号：{request.device_model or "未知"}
用户描述：{request.issue_description}
图片备注：{request.image_note or "未提供图片备注"}

可参考知识库：
{kb_context}

请严格输出以下 JSON schema，不要添加 Markdown：
{DIAGNOSIS_JSON_SCHEMA}
"""
        try:
            return await self.mimo.chat(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.15,
                max_tokens=1600,
            )
        except MiMoAPIError:
            # Keep the demo robust. In production, log this with structured logging.
            return None

    def _parse_diagnosis_json(self, raw: str) -> dict | None:
        text = raw.strip()
        if text.startswith("```"):
            text = text.strip("`")
            text = text.replace("json\n", "", 1).replace("JSON\n", "", 1)
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            text = text[start : end + 1]
        try:
            data = json.loads(text)
            # Pydantic will validate structure in DiagnoseResponse.
            return data
        except json.JSONDecodeError:
            return None

    def _fallback_diagnosis(self, request: DiagnoseRequest, chunks: List[KnowledgeChunk]) -> DiagnoseResponse:
        description = request.issue_description
        high_risk = any(keyword in description for keyword in HIGH_RISK_KEYWORDS)
        if high_risk:
            return DiagnoseResponse(
                summary="检测到可能存在安全风险的硬件异常。",
                likely_issue="potential_safety_hazard",
                risk_level="high",
                need_more_info=["设备是否仍在发热、冒烟或有焦味", "是否进水或摔落", "是否仍连接电源"],
                steps=[
                    RepairStep(
                        title="立即断电并停止使用",
                        instruction="请不要继续开机或充电，先断开电源，并把设备放在通风、远离易燃物的位置。",
                        expected_observation="设备不再继续发热、冒烟或出现异味。",
                        next_if_failed="如果异常持续，请远离设备并联系官方售后或专业维修人员。",
                        safety_note="不要拆开电池、电源适配器或高压部件。",
                    )
                ],
                stop_conditions=["冒烟/焦味/漏电/进水/电池鼓包", "用户需要拆机或接触电源板"],
                matched_knowledge=self._source_labels(chunks),
                model_used="local-demo-rules",
                demo_mode=True,
            )

        category = request.category
        if category == "router":
            steps = [
                RepairStep(
                    title="确认外网链路",
                    instruction="检查光猫/上级网线是否正常，重新插紧 WAN 口网线。",
                    expected_observation="WAN 指示灯应常亮或规律闪烁，管理后台应显示已连接。",
                    next_if_failed="更换一根网线，或把电脑直连光猫测试是否能上网。",
                    safety_note="只操作网线和电源适配器，不要拆开路由器外壳。",
                ),
                RepairStep(
                    title="重启网络链路",
                    instruction="先关闭路由器电源，再关闭光猫电源，等待 30 秒后先开光猫，再开路由器。",
                    expected_observation="等待 2-3 分钟后，网络状态应恢复正常。",
                    next_if_failed="进入路由器管理后台检查拨号账号、DHCP 或上网方式配置。",
                    safety_note=None,
                ),
                RepairStep(
                    title="采集客服信息",
                    instruction="记录路由器型号、固件版本、WAN 口状态、错误码和运营商名称。",
                    expected_observation="得到可交给客服定位问题的信息。",
                    next_if_failed="联系运营商或品牌售后，并附上本页生成的工单。",
                    safety_note=None,
                ),
            ]
            issue = "WAN/运营商链路或上网方式配置异常"
        elif category == "robot_vacuum":
            steps = [
                RepairStep(
                    title="清理主刷和边刷",
                    instruction="关闭电源后取出主刷，清理缠绕的头发、线材和异物。",
                    expected_observation="主刷可以顺畅转动，机器重新启动后不再报卡住。",
                    next_if_failed="检查尘盒、滤网、轮组和充电触点。",
                    safety_note="不要在机器运行时触碰刷子或轮组。",
                ),
                RepairStep(
                    title="检查地面环境",
                    instruction="移开电线、地毯流苏、低矮障碍物和门槛附近杂物。",
                    expected_observation="机器能脱困并继续清扫。",
                    next_if_failed="拍摄机器卡住位置和底部照片，提交售后。",
                    safety_note=None,
                ),
            ]
            issue = "机械卡滞或环境障碍导致清扫失败"
        elif category == "smart_camera":
            steps = [
                RepairStep(
                    title="确认供电和网络",
                    instruction="检查电源适配器、数据线和 Wi-Fi 信号，尽量靠近路由器重新配网。",
                    expected_observation="摄像头指示灯进入待配网或在线状态。",
                    next_if_failed="长按重置键恢复配网流程，并确认只使用支持的 Wi-Fi 频段。",
                    safety_note="不要在潮湿环境插拔电源。",
                )
            ]
            issue = "供电、Wi-Fi 或配网状态异常"
        else:
            steps = [
                RepairStep(
                    title="收集基础信息",
                    instruction="确认设备型号、购买时间、固件版本、错误码、是否摔落/进水/改装。",
                    expected_observation="得到足够定位问题的基础信息。",
                    next_if_failed="补充照片或录屏后提交给客服。",
                    safety_note="不要拆机或尝试高风险维修。",
                ),
                RepairStep(
                    title="执行低风险重启",
                    instruction="在不影响数据安全的前提下，断电或重启设备，再观察问题是否复现。",
                    expected_observation="如果是临时软件异常，重启后问题可能消失。",
                    next_if_failed="生成售后工单并联系官方渠道。",
                    safety_note=None,
                ),
            ]
            issue = "需要进一步信息判断的通用设备异常"

        return DiagnoseResponse(
            summary=f"根据描述，当前问题更像是：{issue}。",
            likely_issue=issue,
            risk_level="low",
            need_more_info=["设备完整型号", "指示灯/错误码", "问题出现前是否更新、摔落、进水或断电", "故障照片或短视频"],
            steps=steps,
            stop_conditions=["需要拆机", "出现冒烟、焦味、漏电、异常发热", "多次重置后仍无法恢复"],
            matched_knowledge=self._source_labels(chunks),
            model_used="local-demo-rules",
            demo_mode=True,
        )

    def _source_labels(self, chunks: List[KnowledgeChunk]) -> List[str]:
        return [f"{chunk.source} / {chunk.title}" for chunk in chunks]

    def create_ticket(self, request: TicketRequest) -> TicketResponse:
        priority = "P1-urgent" if request.diagnosis.risk_level == "high" else "P2-normal"
        tried_steps = [step.title for step in request.diagnosis.steps]
        model = request.original_request.device_model or "未知型号"
        return TicketResponse(
            title=f"{request.original_request.category} {model}：{request.diagnosis.likely_issue}",
            priority=priority,
            customer_summary=(
                f"用户反馈：{request.original_request.issue_description}。"
                f"初步判断：{request.diagnosis.summary}"
            ),
            technical_summary=(
                f"设备类型={request.original_request.category}; 型号={model}; "
                f"风险等级={request.diagnosis.risk_level}; "
                f"匹配知识={'; '.join(request.diagnosis.matched_knowledge) or '无'}"
            ),
            tried_steps=tried_steps,
            recommended_next_action="按诊断步骤完成低风险排查；若触发停止条件，转官方售后处理。",
        )
