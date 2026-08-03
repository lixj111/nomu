<template>
  <div class="tool-call-card" :class="statusClass">
    <div class="tool-call-header" @click="expanded = !expanded">
      <LoadingOutlined v-if="status === 'running'" class="tool-icon loading" />
      <CheckCircleOutlined v-else-if="status === 'done'" class="tool-icon success" />
      <CloseCircleOutlined v-else class="tool-icon error" />
      <span class="tool-name">{{ toolLabel }}</span>
      <span v-if="status === 'running'" class="tool-status running">执行中…</span>
      <DownOutlined v-if="expanded" class="expand-icon" />
      <RightOutlined v-else class="expand-icon" />
    </div>
    <div v-if="expanded" class="tool-call-body">
      <div v-if="argsText" class="tool-args">
        <span class="label">参数</span>{{ argsText }}
      </div>
      <div v-if="summary" class="tool-summary" :class="{ error: status === 'error' }">
        <span class="label">结果</span>{{ summary }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  LoadingOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  DownOutlined,
  RightOutlined
} from '@ant-design/icons-vue'

const props = defineProps({
  toolCall: { type: Object, required: true }
})

const expanded = ref(false)

const TOOL_LABELS = {
  list_ledgers: '查询账本列表',
  get_default_ledger: '获取默认账本',
  get_statistics: '查询收支概览',
  get_category_stats: '查询分类统计',
  get_trend: '查询消费趋势',
  get_accounts: '查询账单明细'
}

const status = computed(() => props.toolCall.status || 'done')
const toolLabel = computed(() => TOOL_LABELS[props.toolCall.tool] || props.toolCall.tool)
const statusClass = computed(() => `status-${status.value}`)

const argsText = computed(() => {
  const args = props.toolCall.args
  if (!args || typeof args !== 'object') return ''
  const parts = []
  for (const [k, v] of Object.entries(args)) {
    if (v !== undefined && v !== null && v !== '') parts.push(`${k}=${v}`)
  }
  return parts.join('，')
})

const summary = computed(() => props.toolCall.summary || '')
</script>

<style scoped>
.tool-call-card {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  background: #fafafa;
  margin: 6px 0;
  font-size: 12px;
  overflow: hidden;
}

.tool-call-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  cursor: pointer;
  user-select: none;
}

.tool-icon {
  font-size: 14px;
  flex-shrink: 0;
}

.tool-icon.loading {
  color: #1677ff;
  animation: spin 1s linear infinite;
}

.tool-icon.success {
  color: #52c41a;
}

.tool-icon.error {
  color: #ff4d4f;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.tool-name {
  flex: 1;
  font-weight: 500;
  color: #262626;
}

.tool-status.running {
  color: #1677ff;
}

.expand-icon {
  color: #999;
  font-size: 10px;
}

.tool-call-body {
  padding: 4px 12px 10px 34px;
  color: #595959;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.label {
  color: #999;
  margin-right: 4px;
}

.tool-summary.error {
  color: #ff4d4f;
}
</style>
