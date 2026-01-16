<template>
  <div class="schedule-page">
    <!-- 月份选择 -->
    <div class="month-selector">
      <Button size="small" @click="prevMonth">上一月</Button>
      <span class="month-title">{{ currentYear }}年{{ currentMonth }}月</span>
      <Button size="small" @click="nextMonth">下一月</Button>
    </div>

    <!-- 按日期分组的账单列表 -->
    <div class="accounts-by-date">
      <div v-for="(items, date) in accountsByDate" :key="date" class="date-group">
        <div class="date-header">
          <span class="date-text">{{ formatDate(date) }}</span>
          <span class="date-summary">
            收入 ¥{{ daySummary(items).income }} | 支出 ¥{{ daySummary(items).expense }}
          </span>
        </div>
        <div class="date-accounts">
          <div
            v-for="account in items"
            :key="account.id"
            class="account-item"
            @click="showDetail(account)"
          >
            <div class="account-icon">{{ account.category ? account.category[0] : '账' }}</div>
            <div class="account-info">
              <div class="account-name">{{ account.item_name }}</div>
              <div class="account-meta">{{ account.category || '未分类' }}</div>
            </div>
            <div
              class="account-amount"
              :class="{ expense: account.transaction_type === '支出', income: account.transaction_type === '收入' }"
            >
              {{ account.transaction_type === '支出' ? '-' : '+' }}¥{{ account.amount }}
            </div>
          </div>
        </div>
      </div>

      <Empty v-if="Object.keys(accountsByDate).length === 0" description="本月暂无账单" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Button, Empty, Dialog } from 'ant-design-mobile-vue'
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
  Dialog.alert({
    title: account.item_name,
    content: `金额: ¥${account.amount}\n分类: ${account.category || '未分类'}\n日期: ${account.transaction_date}\n商户: ${account.merchant_name || '-'}\n支付方式: ${account.payment_method || '-'}`
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
  padding-bottom: 50px;
}

.month-selector {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fff;
  border-bottom: 1px solid #eee;
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
}

.date-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.account-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #f5f5f5;
  cursor: pointer;
}

.account-item:last-child {
  border-bottom: none;
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
</style>
