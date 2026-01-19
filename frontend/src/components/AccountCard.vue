<template>
  <div class="account-card" @click="$emit('click', account)">
    <div class="card-icon" :style="{ background: categoryColor }">
      {{ account.category?.[0] || '账' }}
    </div>
    <div class="card-info">
      <div class="card-name">{{ account.item_name }}</div>
      <div class="card-meta">
        <span>{{ account.category || '未分类' }}</span>
        <span v-if="account.merchant_name">{{ account.merchant_name }}</span>
      </div>
    </div>
    <div
      class="card-amount"
      :class="{ expense: account.transaction_type === '支出', income: account.transaction_type === '收入' }"
    >
      {{ account.transaction_type === '支出' ? '-' : '+' }}¥{{ account.amount }}
    </div>
    <div class="card-date">{{ formatDate(account.transaction_date) }}</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import dayjs from 'dayjs'

const props = defineProps({
  account: {
    type: Object,
    required: true
  }
})

defineEmits(['click'])

const categoryColors = {
  '食品餐饮': '#ff6b6b',
  '出行交通': '#4dabf7',
  '购物消费': '#ff922b',
  '休闲娱乐': '#cc5de8',
  '居家生活': '#20c997',
  '文化教育': '#fab005',
  '健康医疗': '#51cf66',
  '其他': '#adb5bd'
}

const categoryColor = computed(() => {
  return categoryColors[props.account.category] || '#1890ff'
})

const formatDate = (dateStr) => {
  const date = dayjs(dateStr)
  const today = dayjs()
  const yesterday = today.subtract(1, 'day')

  if (date.isSame(today, 'day')) return '今天'
  if (date.isSame(yesterday, 'day')) return '昨天'
  return date.format('MM-DD')
}
</script>

<style scoped>
.account-card {
  display: flex;
  align-items: center;
  padding: 14px 16px;
  background: #fff;
  border-bottom: 1px solid #f5f5f5;
  cursor: pointer;
}

.account-card:active {
  background: #f5f5f5;
}

.card-icon {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  margin-right: 12px;
}

.card-info {
  flex: 1;
  min-width: 0;
}

.card-name {
  font-size: 15px;
  font-weight: 500;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-meta {
  font-size: 12px;
  color: #999;
  display: flex;
  gap: 8px;
}

.card-amount {
  font-size: 18px;
  font-weight: bold;
  margin-right: 12px;
}

.card-amount.expense {
  color: #ff4d4f;
}

.card-amount.income {
  color: #52c41a;
}

.card-date {
  font-size: 12px;
  color: #999;
  white-space: nowrap;
}
</style>
