# MiMo API Notes

本项目默认通过 OpenAI-compatible Chat Completions 调用 MiMo：

```text
POST https://api.xiaomimimo.com/v1/chat/completions
Authorization: Bearer <MIMO_API_KEY>
```

环境变量：

```bash
MIMO_API_KEY=你的_api_key
MIMO_BASE_URL=https://api.xiaomimimo.com/v1
MIMO_MODEL=mimo-v2.5-pro
DEMO_MODE=false
```

如果平台模型名与你账号后台显示不一致，请以 MiMo 控制台为准，更新 `MIMO_MODEL` 即可。

## 为什么先做文本 + 图片备注

当前 MVP 优先保证可运行和可审核：

- 用户可以输入故障照片的观察结果。
- 后端 schema 已保留 `image_note` 字段。
- 后续如 MiMo 多模态 API schema 在你的账号中开放，可把 `mimo_client.py` 的 message content 改成包含图片的 OpenAI-compatible multimodal content。

这能避免因为图片 schema 差异导致评审无法启动项目。
