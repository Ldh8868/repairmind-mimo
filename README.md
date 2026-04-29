# MiMo RepairMind

一个可直接上传 GitHub 的 **MiMo 智能硬件售后与维修 Agent MVP**。

它不是只写概念，而是一个能运行的最小产品：

- FastAPI 后端：负责知识库检索、MiMo 调用、故障诊断、维修步骤生成、工单摘要。
- React 前端：提供用户录入问题、上传故障图片、查看诊断结果和生成工单的界面。
- 本地 Demo 模式：没有 MiMo API Key 也能跑出可演示结果，便于评审快速体验。
- MiMo API 模式：配置 API Key 后走 OpenAI-compatible Chat Completions。

## 适合用来申请 MiMo Token 补贴的理由

这个项目可以真实消耗大量 Token：

1. 说明书/FAQ/售后案例结构化。
2. 多轮维修 Agent 推理。
3. 不同设备类型的大规模回归测试。
4. 多语言版本生成。
5. 工单摘要、客服质检和 Benchmark 数据生成。

首版 MVP 聚焦 4 类设备：路由器、扫地机器人、智能摄像头、耳机/穿戴设备。

## 技术栈

- Backend: Python 3.11+, FastAPI, httpx, Pydantic
- Frontend: Vite, React
- Model API: Xiaomi MiMo OpenAI-compatible endpoint
- Knowledge Base: 本地 Markdown 知识库 + 简单关键词检索，后续可替换成向量数据库

## 目录结构

```text
repairmind-mimo/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── schemas.py
│   │   ├── config.py
│   │   ├── services/
│   │   │   ├── knowledge_base.py
│   │   │   ├── mimo_client.py
│   │   │   └── repair_agent.py
│   │   └── data/manuals/
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api.js
│   │   └── style.css
│   └── package.json
├── docs/
│   ├── PROJECT_APPLICATION.md
│   └── API_NOTES.md
├── scripts/
│   └── smoke_test.sh
├── .env.example
└── README.md
```

## 1. 启动后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp ../.env.example .env
uvicorn app.main:app --reload --port 8000
```

后端健康检查：

```bash
curl http://localhost:8000/health
```

## 2. 配置 MiMo API Key

编辑 `backend/.env`：

```bash
MIMO_API_KEY=你的_api_key
MIMO_BASE_URL=https://api.xiaomimimo.com/v1
MIMO_MODEL=mimo-v2.5-pro
DEMO_MODE=false
```

没有 API Key 时，将 `DEMO_MODE=true`，系统会使用内置规则模拟诊断结果。

## 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

打开 Vite 输出的本地地址，默认通常是：

```text
http://localhost:5173
```

## 4. 一次完整演示

用户输入：

```text
设备：路由器
型号：AX3000
问题：Wi-Fi 能连上，但是没有网络，指示灯一直是橙色闪烁。我已经重启过一次。
```

系统输出：

- 故障类型判断。
- 风险等级。
- 需要用户补充的信息。
- 逐步排障流程。
- 何时停止自助处理。
- 可复制给客服的结构化工单。

## 5. 上传 GitHub

```bash
git init
git add .
git commit -m "feat: add MiMo RepairMind MVP"
git branch -M main
git remote add origin https://github.com/<your-name>/repairmind-mimo.git
git push -u origin main
```

## 6. 后续可以做的真实增强

- 把本地 Markdown 检索替换成向量数据库：Qdrant、Milvus、pgvector。
- 增加 PDF 说明书解析：pymupdf / unstructured。
- 接入真实图片多模态 schema。
- 增加语音 ASR/TTS。
- 增加 Benchmark：同一个故障案例多次跑，统计稳定性和安全性。
- 增加工单系统 Webhook：飞书、企业微信、Zendesk、Freshdesk。

## License

MIT
