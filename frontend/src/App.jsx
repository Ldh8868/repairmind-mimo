import React, { useEffect, useMemo, useState } from 'react';
import { createTicket, diagnose, health } from './api.js';

const categoryLabels = {
  router: '路由器 / 网络设备',
  robot_vacuum: '扫地机器人',
  smart_camera: '智能摄像头',
  earbuds_wearable: '耳机 / 穿戴设备',
  tv_projector: '电视 / 投影',
  other: '其他设备',
};

const examples = {
  router: 'Wi-Fi 能连接，但是没有网络，路由器橙色灯一直闪烁。我已经重启过一次。',
  robot_vacuum: '扫地机器人清扫一会儿就提示主刷卡住，底部有很多头发。',
  smart_camera: '摄像头一直配网失败，App 提示找不到设备。',
  earbuds_wearable: '蓝牙耳机只有左耳能连接，右耳没有声音，放回盒子也没恢复。',
};

export default function App() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [ticketLoading, setTicketLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [ticket, setTicket] = useState(null);
  const [error, setError] = useState('');
  const [form, setForm] = useState({
    category: 'router',
    device_model: 'AX3000',
    issue_description: examples.router,
    image_note: '',
    user_language: 'zh-CN',
  });

  useEffect(() => {
    health().then(setStatus).catch(() => setStatus({ ok: false }));
  }, []);

  const riskLabel = useMemo(() => {
    if (!result) return '';
    return {
      low: '低风险',
      medium: '中风险',
      high: '高风险，建议停止自助处理',
    }[result.risk_level] || result.risk_level;
  }, [result]);

  function updateField(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  function applyExample(category) {
    setForm((prev) => ({
      ...prev,
      category,
      issue_description: examples[category] || prev.issue_description,
    }));
  }

  async function onSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);
    setTicket(null);
    try {
      const data = await diagnose(form);
      setResult(data);
    } catch (err) {
      setError(err.message || '诊断失败');
    } finally {
      setLoading(false);
    }
  }

  async function onCreateTicket() {
    if (!result) return;
    setTicketLoading(true);
    setError('');
    try {
      const data = await createTicket({ original_request: form, diagnosis: result });
      setTicket(data);
    } catch (err) {
      setError(err.message || '工单生成失败');
    } finally {
      setTicketLoading(false);
    }
  }

  return (
    <main className="page">
      <section className="hero">
        <div>
          <p className="eyebrow">MiMo Token 补贴申请 Demo</p>
          <h1>MiMo RepairMind</h1>
          <p className="subtitle">
            一个面向智能硬件售后的维修 Agent：理解用户描述，检索说明书知识库，生成安全、可执行的排障步骤，并自动沉淀客服工单。
          </p>
        </div>
        <div className="status-card">
          <span className={status?.ok ? 'dot ok' : 'dot'} />
          <div>
            <strong>{status?.ok ? '后端已连接' : '后端未连接'}</strong>
            <p>{status?.demo_mode ? 'Demo 模式：不消耗 API Token' : 'MiMo API 模式：真实调用模型'}</p>
            <p className="muted">Model: {status?.model || 'unknown'}</p>
          </div>
        </div>
      </section>

      <section className="grid">
        <form className="card form" onSubmit={onSubmit}>
          <h2>故障输入</h2>
          <label>
            设备类型
            <select value={form.category} onChange={(e) => updateField('category', e.target.value)}>
              {Object.entries(categoryLabels).map(([key, label]) => (
                <option key={key} value={key}>{label}</option>
              ))}
            </select>
          </label>
          <div className="quick-examples">
            {Object.keys(examples).map((key) => (
              <button type="button" key={key} onClick={() => applyExample(key)}>
                {categoryLabels[key]}
              </button>
            ))}
          </div>
          <label>
            设备型号
            <input
              value={form.device_model}
              onChange={(e) => updateField('device_model', e.target.value)}
              placeholder="例如 AX3000 / Mijia Robot / Camera 2K"
            />
          </label>
          <label>
            用户描述
            <textarea
              rows="8"
              value={form.issue_description}
              onChange={(e) => updateField('issue_description', e.target.value)}
              placeholder="请描述故障现象、指示灯、错误码、已经尝试过的操作。"
            />
          </label>
          <label>
            图片备注，可选
            <textarea
              rows="3"
              value={form.image_note}
              onChange={(e) => updateField('image_note', e.target.value)}
              placeholder="MVP 先填写图片观察结果，例如：橙色灯闪烁、底部主刷缠绕头发。后续可接入真实多模态图片 schema。"
            />
          </label>
          <button className="primary" disabled={loading}>
            {loading ? '诊断中...' : '生成维修诊断'}
          </button>
          {error && <p className="error">{error}</p>}
        </form>

        <section className="card result">
          <h2>Agent 输出</h2>
          {!result && <p className="empty">提交左侧表单后，这里会显示诊断结果。</p>}
          {result && (
            <>
              <div className="summary">
                <p>{result.summary}</p>
                <div className={`risk ${result.risk_level}`}>{riskLabel}</div>
              </div>

              <h3>最可能问题</h3>
              <p>{result.likely_issue}</p>

              <h3>还需要补充</h3>
              <ul>
                {result.need_more_info.map((item, idx) => <li key={idx}>{item}</li>)}
              </ul>

              <h3>排障步骤</h3>
              <div className="steps">
                {result.steps.map((step, idx) => (
                  <article className="step" key={idx}>
                    <span>{idx + 1}</span>
                    <div>
                      <h4>{step.title}</h4>
                      <p>{step.instruction}</p>
                      <p className="muted">观察：{step.expected_observation}</p>
                      <p className="muted">失败后：{step.next_if_failed}</p>
                      {step.safety_note && <p className="safety">安全：{step.safety_note}</p>}
                    </div>
                  </article>
                ))}
              </div>

              <h3>停止条件</h3>
              <ul>
                {result.stop_conditions.map((item, idx) => <li key={idx}>{item}</li>)}
              </ul>

              <h3>匹配知识库</h3>
              <ul>
                {result.matched_knowledge.map((item, idx) => <li key={idx}>{item}</li>)}
              </ul>

              <button className="secondary" onClick={onCreateTicket} disabled={ticketLoading}>
                {ticketLoading ? '生成中...' : '生成客服工单'}
              </button>
            </>
          )}
        </section>
      </section>

      {ticket && (
        <section className="card ticket">
          <h2>客服工单</h2>
          <div className="ticket-header">
            <strong>{ticket.title}</strong>
            <span>{ticket.priority}</span>
          </div>
          <p><strong>用户摘要：</strong>{ticket.customer_summary}</p>
          <p><strong>技术摘要：</strong>{ticket.technical_summary}</p>
          <p><strong>建议动作：</strong>{ticket.recommended_next_action}</p>
          <h3>已建议步骤</h3>
          <ul>{ticket.tried_steps.map((item, idx) => <li key={idx}>{item}</li>)}</ul>
        </section>
      )}
    </main>
  );
}
