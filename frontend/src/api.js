const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text}`);
  }
  return res.json();
}

export function diagnose(payload) {
  return request('/api/diagnose', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function createTicket(payload) {
  return request('/api/ticket', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function health() {
  return request('/health');
}
