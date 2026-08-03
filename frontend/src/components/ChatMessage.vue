<template>
  <div class="chat-message" :class="role">
    <div class="bubble">
      <template v-if="role === 'assistant'">
        <ToolCallCard
          v-for="(tc, index) in message.toolCalls"
          :key="index"
          :toolCall="tc"
        />
        <div v-if="message.thinking" class="think-box">
          <div class="think-header" @click="thinkOpen = !thinkOpen">
            <LoadingOutlined v-if="loading && !message.content" class="spin" />
            <span class="think-label">
              {{ loading && !message.content ? '思考中…' : '思考过程' }}
            </span>
            <RightOutlined class="think-arrow" :class="{ open: thinkOpen }" />
          </div>
          <div v-show="thinkOpen" class="think-content">{{ message.thinking }}</div>
        </div>
        <div
          v-if="message.content"
          class="content markdown-body"
          v-html="renderedContent"
        ></div>
        <div v-else-if="!message.thinking && loading" class="thinking">
          <LoadingOutlined class="spin" /> 思考中…
        </div>
      </template>
      <template v-else>
        <div class="content">{{ message.content }}</div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { LoadingOutlined, RightOutlined } from '@ant-design/icons-vue'
import ToolCallCard from './ToolCallCard.vue'

const props = defineProps({
  message: { type: Object, required: true },
  role: { type: String, required: true },
  loading: { type: Boolean, default: false }
})

// 仅 assistant 内容渲染 markdown，且经过 DOMPurify 清洗防 XSS
const renderedContent = computed(() => {
  if (props.role !== 'assistant' || !props.message.content) return ''
  return DOMPurify.sanitize(marked.parse(props.message.content))
})

// 思考过程折叠状态：推理中默认展开，正文出现后自动折叠
const thinkOpen = ref(true)
watch(
  () => props.message.content,
  (c) => {
    if (c) thinkOpen.value = false
  }
)
</script>

<style scoped>
.chat-message {
  display: flex;
  margin: 12px 0;
}

.chat-message.user {
  justify-content: flex-end;
}

.chat-message.assistant {
  justify-content: flex-start;
}

.bubble {
  max-width: 85%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
}

.user .bubble {
  background: #1677ff;
  color: #fff;
  border-top-right-radius: 4px;
}

.assistant .bubble {
  background: #fff;
  color: #262626;
  border: 1px solid #f0f0f0;
  border-top-left-radius: 4px;
}

.content {
  white-space: pre-wrap;
}

/* 助手 markdown 内容：恢复正常换行，交给标记语法排版 */
.assistant .markdown-body {
  white-space: normal;
}

/* marked 渲染后的 markdown 排版样式 */
.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4) {
  margin: 12px 0 8px;
  font-weight: 600;
  line-height: 1.4;
}

.markdown-body :deep(h1) { font-size: 18px; }
.markdown-body :deep(h2) { font-size: 16px; }
.markdown-body :deep(h3) { font-size: 15px; }
.markdown-body :deep(h4) { font-size: 14px; }

.markdown-body :deep(p) {
  margin: 6px 0;
}

.markdown-body :deep(p:first-child) {
  margin-top: 0;
}

.markdown-body :deep(p:last-child) {
  margin-bottom: 0;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  margin: 6px 0;
  padding-left: 22px;
}

.markdown-body :deep(li) {
  margin: 3px 0;
}

.markdown-body :deep(code) {
  background: #f0f0f0;
  border-radius: 4px;
  padding: 1px 5px;
  font-family: Consolas, Monaco, 'Courier New', monospace;
  font-size: 12.5px;
  color: #d4380d;
}

.markdown-body :deep(pre) {
  background: #1f1f1f;
  color: #e6e6e6;
  border-radius: 8px;
  padding: 10px 12px;
  overflow-x: auto;
  margin: 8px 0;
  font-size: 12.5px;
  line-height: 1.5;
}

.markdown-body :deep(pre code) {
  background: transparent;
  color: inherit;
  padding: 0;
  font-size: inherit;
}

.markdown-body :deep(blockquote) {
  margin: 8px 0;
  padding: 4px 12px;
  border-left: 3px solid #1677ff;
  background: #f6f8ff;
  border-radius: 0 6px 6px 0;
  color: #595959;
}

.markdown-body :deep(table) {
  border-collapse: collapse;
  margin: 8px 0;
  width: 100%;
  font-size: 13px;
}

.markdown-body :deep(th),
.markdown-body :deep(td) {
  border: 1px solid #e8e8e8;
  padding: 6px 10px;
  text-align: left;
}

.markdown-body :deep(th) {
  background: #fafafa;
  font-weight: 600;
}

.markdown-body :deep(tr:nth-child(even) td) {
  background: #fafafa;
}

.markdown-body :deep(hr) {
  border: none;
  border-top: 1px solid #f0f0f0;
  margin: 12px 0;
}

.markdown-body :deep(strong) {
  font-weight: 600;
  color: #262626;
}

.markdown-body :deep(a) {
  color: #1677ff;
  text-decoration: none;
}

.markdown-body :deep(img) {
  max-width: 100%;
  border-radius: 6px;
}

.thinking {
  color: #999;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* 推理模型的思考过程展示 */
.think-box {
  margin-bottom: 8px;
  border: 1px solid #ece6ff;
  border-radius: 8px;
  background: #faf8ff;
  overflow: hidden;
}

.think-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  font-size: 12px;
  color: #7c3aed;
  cursor: pointer;
  user-select: none;
}

.think-label {
  flex: 1;
}

.think-arrow {
  font-size: 11px;
  transition: transform 0.2s;
}

.think-arrow.open {
  transform: rotate(90deg);
}

.think-content {
  padding: 8px 12px;
  font-size: 12.5px;
  line-height: 1.6;
  color: #8c8c8c;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 200px;
  overflow-y: auto;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
