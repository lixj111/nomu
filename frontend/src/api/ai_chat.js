/** AI 对话 SSE 流式请求封装（fetch 读取流，非 axios） */
import request from '@/utils/request'

const BASE = '/api/v1'

// 会话管理（axios 非流式）
export const getSessions = () => request({ url: '/ai/sessions', method: 'get' })
export const createSession = (data = {}) => request({ url: '/ai/sessions', method: 'post', data })
export const getSessionMessages = (id) => request({ url: `/ai/sessions/${id}/messages`, method: 'get' })
export const deleteSession = (id) => request({ url: `/ai/sessions/${id}`, method: 'delete' })

// 按 SSE 帧分隔符 \n\n 解析缓冲区，返回完整事件与剩余半截帧
function parseSseChunk(buffer) {
  const frames = buffer.split('\n\n')
  const events = []
  for (const frame of frames.slice(0, -1)) {
    for (const line of frame.split('\n')) {
      if (line.startsWith('data: ')) {
        try {
          events.push(JSON.parse(line.slice(6)))
        } catch (e) {
          // 忽略解析失败的半截帧
        }
      }
    }
  }
  return { events, rest: frames[frames.length - 1] }
}

function dispatchEvent(evt, handlers) {
  switch (evt.type) {
    case 'tool_call':
      handlers.onToolCall?.(evt)
      break
    case 'tool_result':
      handlers.onToolResult?.(evt)
      break
    case 'delta':
      handlers.onDelta?.(evt.content)
      break
    case 'thinking':
      handlers.onThinking?.(evt.content)
      break
    case 'done':
      handlers.onDone?.(evt.content)
      break
    case 'error':
      handlers.onError?.(evt.message)
      break
  }
}

/**
 * 发送 AI 对话请求并流式读取 SSE 事件
 * @param {object} payload - { messages: [{role, content}], ledger_id }
 * @param {object} handlers - { onToolCall, onToolResult, onDelta, onDone, onError }
 */
export async function chatStream(payload, handlers, signal) {
  const res = await fetch(`${BASE}/ai/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('access_token') || ''}`
    },
    body: JSON.stringify(payload),
    signal
  })

  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`
    try {
      detail = (await res.json()).detail || detail
    } catch (e) {
      // 忽略解析失败
    }
    throw new Error(detail)
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    // TextDecoder 流式解码，跨网络块的中文不乱码
    buffer += decoder.decode(value, { stream: true })
    const { events, rest } = parseSseChunk(buffer)
    buffer = rest
    for (const evt of events) {
      dispatchEvent(evt, handlers)
    }
  }
}
