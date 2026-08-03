<template>
  <div class="ai-chat-page">
    <!-- 顶部标题栏 -->
    <div class="chat-header">
      <a-button type="text" class="menu-btn" @click="sessionsVisible = true">
        <MenuOutlined />
      </a-button>
      <ZhiIcon :size="22" class="header-icon" />
      <div class="header-text">
        <span class="header-title">小智</span>
        <span class="header-sub">分析消费习惯 · 趋势 · 建议</span>
      </div>
      <!-- 开启对话后会话锁定账本：只展示账本名，不再出现选择框 -->
      <div v-if="sessionLocked" class="ledger-tag">
        <BookOutlined class="ledger-tag-icon" />
        <span class="ledger-tag-name">{{ sessionLedgerName || '未指定账本' }}</span>
      </div>
      <a-select
        v-else
        class="ledger-select"
        :value="ledgerStore.currentLedgerId"
        placeholder="选择账本"
        @change="onLedgerChange"
      >
        <a-select-option v-for="l in ledgerStore.ledgers" :key="l.id" :value="l.id">
          {{ l.name }}{{ l.is_default ? '（默认）' : '' }}
        </a-select-option>
      </a-select>
    </div>

    <!-- 消息列表 -->
    <div ref="messageListRef" class="message-list">
      <ChatMessage
        v-for="(msg, index) in messages"
        :key="index"
        :message="msg"
        :role="msg.role"
        :loading="msg.role === 'assistant' && msg.status === 'loading'"
      />
      <a-empty
        v-if="messages.length === 0"
        description="你好，我是小智，你的智能记账分析助手。可以问我：分析消费习惯、本月支出、某分类的花销、消费趋势等。"
        class="empty-state"
      />
    </div>

    <!-- 快捷提问 -->
    <div v-if="messages.length === 0" class="quick-questions">
      <a-button
        v-for="q in quickQuestions"
        :key="q"
        size="small"
        class="quick-btn"
        @click="send(q)"
      >
        {{ q }}
      </a-button>
    </div>

    <!-- 输入区 -->
    <div class="chat-input-bar">
      <a-input
        v-model:value="input"
        placeholder="输入你的问题，例如：分析我最近的消费习惯"
        :disabled="sending"
        @pressEnter="send()"
      />
      <a-button
        v-if="sending"
        type="primary"
        danger
        class="send-btn"
        @click="stopStream"
      >
        停止
      </a-button>
      <a-button
        v-else
        type="primary"
        class="send-btn"
        :disabled="!input.trim()"
        @click="send()"
      >
        发送
      </a-button>
    </div>

    <!-- 会话记录抽屉 -->
    <a-drawer
      v-model:open="sessionsVisible"
      title="会话记录"
      placement="left"
      :width="280"
    >
      <div class="session-list">
        <a-button type="dashed" block class="new-session-btn" @click="newSession">
          <PlusOutlined /> 新建会话
        </a-button>
        <a-empty v-if="sessions.length === 0" description="暂无会话记录" class="session-empty" />
        <div
          v-for="s in sessions"
          :key="s.id"
          class="session-item"
          :class="{ active: s.id === currentSessionId }"
          @click="selectSession(s.id)"
        >
          <div class="session-info">
            <div class="session-title">{{ s.title || '新会话' }}</div>
            <div class="session-meta">{{ s.message_count }} 条消息</div>
          </div>
          <a-button
            type="text"
            size="small"
            class="session-del"
            @click.stop="removeSession(s.id)"
          >
            <DeleteOutlined />
          </a-button>
        </div>
      </div>
    </a-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, computed, nextTick, onMounted } from 'vue'
import { MenuOutlined, PlusOutlined, DeleteOutlined, BookOutlined } from '@ant-design/icons-vue'
import { useLedgerStore } from '@/stores'
import {
  chatStream,
  getSessions,
  createSession,
  getSessionMessages,
  deleteSession
} from '@/api/ai_chat'
import ChatMessage from '@/components/ChatMessage.vue'
import ZhiIcon from '@/components/ZhiIcon.vue'

const ledgerStore = useLedgerStore()

onMounted(() => {
  ledgerStore.fetchLedgers()
  loadSessions(true)
})

// 切换账本：更新全局当前账本，后续提问以新账本为范围
const onLedgerChange = (id) => {
  if (id) ledgerStore.switchLedger(Number(id))
}

const messages = ref([])
const input = ref('')
const sending = ref(false)
const abortController = ref(null)
const messageListRef = ref(null)

// 会话管理
const sessions = ref([])
const sessionsVisible = ref(false)
const currentSessionId = ref(null)
// 当前会话锁定的账本：开启对话后不可切换，顶部只展示名称
const sessionLedgerId = ref(null)
const sessionLocked = computed(() => messages.value.length > 0)
const sessionLedgerName = computed(() => {
  const l = ledgerStore.ledgers.find((x) => x.id === sessionLedgerId.value)
  return l ? `${l.name}${l.is_default ? '（默认）' : ''}` : ''
})

const quickQuestions = [
  '这个月花了多少钱？',
  '分析我的消费习惯',
  '最近30天的支出趋势',
  '上个月最大的一笔支出是什么'
]

const scrollToBottom = () => {
  nextTick(() => {
    const el = messageListRef.value
    if (el) el.scrollTop = el.scrollHeight
  })
}

const stopStream = () => {
  abortController.value?.abort()
}

const loadSessions = async (autoSelect = false) => {
  try {
    const res = await getSessions()
    sessions.value = res.data || []
    if (autoSelect) {
      const latest =
        sessions.value.find((s) => s.id === currentSessionId.value) || sessions.value[0]
      if (latest) await selectSession(latest.id)
    } else if (currentSessionId.value && !sessions.value.some((s) => s.id === currentSessionId.value)) {
      // 当前会话已被删除，重置为新建态
      currentSessionId.value = null
      messages.value = []
    }
  } catch (e) {
    sessions.value = []
  }
}

const selectSession = async (id) => {
  currentSessionId.value = id
  sessionsVisible.value = false
  stopStream()
  // 切换到该会话锁定的账本
  const sess = sessions.value.find((s) => s.id === id)
  sessionLedgerId.value = sess?.ledger_id ?? null
  messages.value = []
  try {
    const res = await getSessionMessages(id)
    messages.value = (res.data || []).map((m) => ({
      role: m.role,
      content: m.content,
      toolCalls: [],
      status: 'done'
    }))
    scrollToBottom()
  } catch (e) {
    // 历史加载失败静默
  }
}

const newSession = () => {
  currentSessionId.value = null
  sessionsVisible.value = false
  stopStream()
  sessionLedgerId.value = null
  messages.value = []
  input.value = ''
}

const removeSession = async (id) => {
  try {
    await deleteSession(id)
  } catch (e) {
    // 删除失败静默
  }
  if (id === currentSessionId.value) {
    currentSessionId.value = null
    messages.value = []
    await loadSessions(true)
  } else {
    sessions.value = sessions.value.filter((s) => s.id !== id)
  }
}

const send = async (text) => {
  const question = text || input.value.trim()
  if (!question || sending.value) return

  input.value = ''
  // a-input 在 pressEnter 后可能用旧 DOM 值回写 ref（输入法/事件时序），下一拍再次清空兜底
  nextTick(() => {
    input.value = ''
  })
  messages.value.push({ role: 'user', content: question })

  // 用 reactive 创建：onDelta/onThinking 改其字段才能触发响应式更新，实现逐字渲染
  const aiMsg = reactive({ role: 'assistant', content: '', thinking: '', toolCalls: [], status: 'loading', _placeholder: true })
  messages.value.push(aiMsg)
  sending.value = true
  scrollToBottom()

  // 历史消息（排除当前占位）：仅发送对话内容
  const history = messages.value
    .filter((m) => !m._placeholder)
    .map(({ role, content }) => ({ role, content }))

  abortController.value = new AbortController()

  try {
    // 无会话时先新建，并绑定当前选择的账本
    if (currentSessionId.value == null) {
      const res = await createSession({ ledger_id: ledgerStore.currentLedgerId })
      currentSessionId.value = res.data.id
      sessionLedgerId.value = ledgerStore.currentLedgerId
    }
    const sid = currentSessionId.value
    await chatStream(
      {
        messages: history,
        ledger_id: ledgerStore.currentLedgerId,
        session_id: sid,
        user_message: question
      },
      {
        onToolCall: (evt) => {
          aiMsg.toolCalls.push({ tool: evt.tool, args: evt.args, summary: '', ok: true, status: 'running' })
          scrollToBottom()
        },
        onToolResult: (evt) => {
          const card = aiMsg.toolCalls.find((c) => c.tool === evt.tool && c.status === 'running')
          if (card) {
            card.summary = evt.summary
            card.ok = evt.ok
            card.status = evt.ok ? 'done' : 'error'
          }
          scrollToBottom()
        },
        onDelta: (text) => {
          aiMsg.content += text
          scrollToBottom()
        },
        onThinking: (text) => {
          aiMsg.thinking += text
          scrollToBottom()
        },
        onDone: () => {
          aiMsg.status = 'done'
        },
        onError: (msg) => {
          aiMsg.status = 'error'
          if (!aiMsg.content) aiMsg.content = `出错了：${msg}`
        }
      },
      abortController.value.signal
    )
    await loadSessions(false)
  } catch (e) {
    aiMsg.status = 'error'
    if (e.name !== 'AbortError' && !aiMsg.content) {
      aiMsg.content = `请求失败：${e.message}`
    }
  } finally {
    sending.value = false
    input.value = ''
    abortController.value = null
    scrollToBottom()
  }
}
</script>

<style scoped>
.ai-chat-page {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f5f5f5;
}

.chat-header {
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  padding: 8px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.menu-btn {
  padding: 4px 6px;
  font-size: 16px;
  color: #595959;
  flex-shrink: 0;
}

.header-icon {
  display: flex;
}

.header-text {
  display: flex;
  flex-direction: column;
  line-height: 1.3;
  min-width: 0;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
}

.header-sub {
  font-size: 12px;
  color: #999;
}

.ledger-select {
  margin-left: auto;
  width: 130px;
  flex-shrink: 0;
}

/* 锁定后展示的账本名标签 */
.ledger-tag {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 8px;
  background: #f5f0ff;
  color: #7c3aed;
  font-size: 13px;
  flex-shrink: 0;
  max-width: 160px;
}

.ledger-tag-icon {
  font-size: 14px;
  flex-shrink: 0;
}

.ledger-tag-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ledger-select .ant-select-selector {
  border-radius: 8px;
  font-size: 13px;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.empty-state {
  margin-top: 60px;
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 0 16px 12px;
  flex-shrink: 0;
}

.quick-btn {
  border-radius: 16px;
}

.chat-input-bar {
  display: flex;
  gap: 8px;
  padding: 12px 16px 80px;
  background: #fff;
  border-top: 1px solid #f0f0f0;
  flex-shrink: 0;
}

.chat-input-bar .ant-input {
  border-radius: 8px;
}

.send-btn {
  flex-shrink: 0;
}

.session-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.new-session-btn {
  border-radius: 8px;
}

.session-empty {
  margin-top: 40px;
}

.session-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  background: #fafafa;
  border: 1px solid #f0f0f0;
  transition: all 0.2s;
}

.session-item:hover {
  background: #f0f0f0;
}

.session-item.active {
  background: #e6f4ff;
  border-color: #91caff;
}

.session-info {
  flex: 1;
  min-width: 0;
}

.session-title {
  font-size: 14px;
  color: #262626;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-meta {
  font-size: 12px;
  color: #999;
}

.session-del {
  flex-shrink: 0;
  color: #999;
}

.session-del:hover {
  color: #ff4d4f;
}
</style>
