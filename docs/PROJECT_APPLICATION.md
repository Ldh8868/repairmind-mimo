# 项目申请文案：MiMo RepairMind

## 项目标题

MiMo RepairMind：Multi-modal Voice Repair Agent for Global Smart Devices

## 项目简介

MiMo RepairMind 是一个面向智能硬件售后的维修 Agent。用户输入设备型号、故障描述和图片观察结果后，系统会检索产品说明书/FAQ/维修知识库，并调用 MiMo 生成安全、可执行、步骤化的排障方案。如果用户无法自助解决，系统会自动生成结构化客服工单，减少客服重复沟通。

## 为什么适合百亿级 Token 补贴

本项目不是单次问答，而是长链路 Agent 产品。后续需要大规模 Token 完成以下任务：

1. 解析大量产品说明书、FAQ、社区案例。
2. 构建多轮故障排查流程。
3. 针对不同语言、地区、设备型号生成本地化版本。
4. 生成和运行 Agent 回归测试集。
5. 生成客服工单、质检报告和 Benchmark。

## 30 天可交付成果

- 可运行 Web Demo。
- GitHub 开源仓库。
- 100 份说明书/FAQ 入库样例。
- 1,000 条故障问答和 300 条多轮排障流程。
- 工单自动摘要 API。
- 技术报告和演示视频。

## 当前 MVP 已完成

- FastAPI 后端。
- React 前端。
- 本地知识库检索。
- MiMo OpenAI-compatible Chat Completions Client。
- 无 API Key 的 Demo fallback。
- 故障诊断 API。
- 客服工单 API。
