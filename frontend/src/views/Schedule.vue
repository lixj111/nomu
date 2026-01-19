<template>
  <div class="schedule-page">
    <!-- 月份选择 -->
    <div class="month-selector">
      <a-button size="small" @click="prevMonth">
        <template #icon><LeftOutlined /></template>
        上一月
      </a-button>
      <span class="month-title">{{ currentYear }}年{{ currentMonth }}月</span>
      <a-button size="small" @click="nextMonth">
        下一月
        <template #icon><RightOutlined /></template>
      </a-button>
    </div>

    <!-- 按日期分组的账单列表 -->
    <div class="accounts-by-date">
      <a-collapse
        v-for="(items, date) in accountsByDate"
        :key="date"
        :bordered="false"
        class="date-group"
        default-active-key=""
      >
        <template #header>
          <div class="date-header">
            <span class="date-text">{{ formatDate(date) }}</span>
            <span class="date-summary">
              收入 ¥{{ daySummary(items).income }} | 支出 ¥{{ daySummary(items).expense }}
            </span>
          </div>
        </template>
        <template #expandIcon>
          <div></div>
        </template>
        <div class="date-accounts">
          <a-list :data-source="items" class="account-list">
            <template #renderItem="{ item }">
              <a-list-item
                class="account-item"
                @click="showDetail(item)"
              >
                <div class="account-icon">{{ item.category ? item.category[0] : '账' }}</div>
                <div class="account-info">
                  <div class="account-name">{{ item.item_name }}</div>
                  <div class="account-meta">{{ item.category || '未分类' }}</div>
                </div>
                <div
                  class="account-amount"
                  :class="{ expense: item.transaction_type === '支出', income: item.transaction_type === '收入' }"
                >
                  {{ item.transaction_type === '支出' ? '-' : '+' }}¥{{ item.amount }}
                </div>
              </a-list-item>
            </template>
          </a-list>
        </div>
      </a-collapse>

      <a-empty
        v-if="Object.keys(accountsByDate).length === 0"
        description="本月暂无账单"
        class="empty-state"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, h } from 'vue'
import { Modal } from 'ant-design-vue'
import { LeftOutlined, RightOutlined } from '@ant-design/icons-vue'
import dayjs from 'dayjs'
import { useAccountStore, useLedgerStore } from '@/stores'

const accountStore = useAccountStore()
const ledgerStore = useLedgerStore()

const currentYear = ref(new Date().getFullYear())
const currentMonth = ref(new Date().getMonth() + 1)

const accountsByDate = computed(() => accountStore.accountsByDate)

const formatDate = (dateStr) => {
  const date = dayjs(dateStr)
  const today = dayjs()
  const yesterday = today.subtract(1, 'day')

  if (date.isSame(today, 'day')) return '今天'
  if (date.isSame(yesterday, 'day')) return '昨天'

  return date.format('MM月DD日 dddd')
}

const daySummary = (items) => {
  return items.reduce(
    (acc, cur) => {
      if (cur.transaction_type === '收入') {
        acc.income += cur.amount
      } else {
        acc.expense += cur.amount
      }
      return acc
    },
    { income: 0, expense: 0 }
  )
}

const showDetail = (account) => {
  Modal.info({
    title: account.item_name,
    width: 400,
    content: h => h('div', { class: 'detail-content' }, [
      h('p', `金额: ¥${account.amount}`),
      h('p', `分类: ${account.category || '未分类'}`),
      h('p', `日期: ${account.transaction_date}`),
      h('p', `商户: ${account.merchant_name || '-'}`),
      h('p', `支付方式: ${account.payment_method || '-'}`)
    ])
  })
}

const loadMonthData = () => {
  accountStore.fetchAccountsByDate(currentYear.value, currentMonth.value)
}

const prevMonth = () => {
  if (currentMonth.value === 1) {
    currentYear.value--
    currentMonth.value = 12
  } else {
    currentMonth.value--
  }
  loadMonthData()
}

const nextMonth = () => {
  if (currentMonth.value === 12) {
    currentYear.value++
    currentMonth.value = 1
  } else {
    currentMonth.value++
  }
  loadMonthData()
}

onMounted(() => {
  if (ledgerStore.currentLedgerId) {
    loadMonthData()
  }
})

// 监听账本切换
watch(
  () => ledgerStore.currentLedgerId,
  () => {
    loadMonthData()
  }
)
</script>

<style scoped>
.schedule-page {
  flex: 1;
  overflow-y: auto;
  height: 100%;
  background: #f5f5f5;
}

.month-selector {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
}

.month-title {
  font-size: 16px;
  font-weight: bold;
}

.accounts-by-date {
  padding: 8px 0;
}

.date-group {
  margin-bottom: 16px;
  background: #fff;
}

.date-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 8px 16px;
  background: #f5f5f5;
  font-size: 14px;
  color: #666;
}

.date-summary {
  font-size: 12px;
}

.date-accounts {
  background: #fff;
}

.account-list {
  background: #fff;
}

.account-item {
  display: flex !important;
  align-items: center;
  padding: 12px 16px !important;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
}

.account-item:last-child {
  border-bottom: none;
}

.account-item:hover {
  background: #fafafa;
}

.account-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1890ff, #096dd9);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  margin-right: 12px;
}

.account-info {
  flex: 1;
}

.account-name {
  font-size: 15px;
  font-weight: 500;
  margin-bottom: 4px;
}

.account-meta {
  font-size: 12px;
  color: #999;
}

.account-amount {
  font-size: 16px;
  font-weight: bold;
}

.account-amount.expense {
  color: #ff4d4f;
}

.account-amount.income {
  color: #52c41a;
}

.empty-state {
  margin: 40px 0;
}

.detail-content p {
  margin: 8px 0;
}
</style>
