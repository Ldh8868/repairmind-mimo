#!/usr/bin/env bash
set -euo pipefail

curl -s http://localhost:8000/health | python -m json.tool
curl -s http://localhost:8000/api/diagnose \
  -H 'Content-Type: application/json' \
  -d '{
    "category":"router",
    "device_model":"AX3000",
    "issue_description":"Wi-Fi 能连接，但是没有网络，橙色灯一直闪烁。我已经重启过一次。",
    "image_note":"路由器正面橙色灯闪烁，WAN 口网线已插入。",
    "user_language":"zh-CN"
  }' | python -m json.tool
