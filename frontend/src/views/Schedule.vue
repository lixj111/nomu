<template>
  <div class="schedule-page">
    <!-- 顶部栏 -->
    <div class="schedule-header">
      <!-- 年月显示区（占2/3高度） -->
      <div class="header-year-month">
        <a-button size="small" @click="prevMonth">
          <template #icon><LeftOutlined /></template>
        </a-button>
        <span class="year-month-title">{{ currentYear }}年{{ currentMonth }}月</span>
        <a-button size="small" @click="nextMonth">
          <template #icon><RightOutlined /></template>
        </a-button>
      </div>
      <!-- 月度统计信息区（占1/3高度） -->
      <div class="header-monthly-summary">
        <span class="summary-text">收 <span class="income-amount">{{ monthlySummary.income.toFixed(2) }}</span></span>
        <span class="summary-text">支 <span class="expense-amount">{{ monthlySummary.expense.toFixed(2) }}</span></span>
        <span class="summary-text">余 <span class="balance-amount">{{ monthlySummary.balance.toFixed(2) }}</span></span>
      </div>
    </div>

    <!-- 主体区域 -->
    <div class="schedule-body">
      <!-- 日历区域（占一半高度） -->
      <div class="calendar-section">
        <!-- 星期标题 -->
        <div class="calendar-weekdays">
          <div v-for="day in weekdays" :key="day" class="weekday-item">{{ day }}</div>
        </div>
        <!-- 日期网格 -->
        <div class="calendar-grid">
          <div
            v-for="(dayInfo, index) in calendarDays"
            :key="index"
            class="calendar-day"
            :class="{
              'other-month': dayInfo.isOtherMonth,
              'selected': selectedDate === dayInfo.dateStr,
              'today': dayInfo.isToday
            }"
            @click="selectDate(dayInfo)"
          >
            <div class="day-number">{{ dayInfo.isToday ? '今' : dayInfo.day }}</div>
            <div v-if="dayInfo.hasData" class="day-summary">
              <div v-if="dayInfo.summary.expense > 0" class="day-expense">-{{ dayInfo.summary.expense.toFixed(0) }}</div>
              <div v-if="dayInfo.summary.income > 0" class="day-income">+{{ dayInfo.summary.income.toFixed(0) }}</div>
            </div>
            <div v-else class="day-lunar">{{ dayInfo.lunar }}</div>
          </div>
        </div>
      </div>

      <!-- 选中日期的账单详情区域（占一半高度） -->
      <div class="day-detail-section">
        <div class="day-detail-header">
          <span class="detail-title">{{ selectedDateTitle }}</span>
          <span class="detail-summary">
            收 <span class="income-text">{{ selectedDateSummary.income.toFixed(2) }}</span> 支 <span class="expense-text">{{ selectedDateSummary.expense.toFixed(2) }}</span> 余 <span class="balance-text">{{ (selectedDateSummary.income - selectedDateSummary.expense).toFixed(2) }}</span>
          </span>
        </div>
        <div class="day-detail-content">
          <a-spin :spinning="loading">
            <div v-if="selectedDateAccounts.length === 0" class="empty-state">
              <a-empty description="当天暂无账单" />
            </div>
            <div v-else class="account-list">
              <div
                v-for="account in selectedDateAccounts"
                :key="account.id"
                class="account-item"
                @click="showDetail(account)"
              >
                <div class="account-icon" :style="{ background: getCategoryColor(account.category) }">
                  {{ account.category ? account.category[0] : '账' }}
                </div>
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
          </a-spin>
        </div>
      </div>
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
const selectedDate = ref(dayjs().format('YYYY-MM-DD'))
const loading = ref(false)

const weekdays = ['日', '一', '二', '三', '四', '五', '六']

// 分类颜色
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

const getCategoryColor = (category) => {
  return categoryColors[category] || '#1890ff'
}

const accountsByDate = computed(() => accountStore.accountsByDate)

// 计算月度统计
const monthlySummary = computed(() => {
  let income = 0
  let expense = 0

  Object.values(accountsByDate.value).forEach(items => {
    items.forEach(item => {
      if (item.transaction_type === '收入') {
        income += parseFloat(item.amount)
      } else {
        expense += parseFloat(item.amount)
      }
    })
  })

  return {
    income,
    expense,
    balance: income - expense
  }
})

// 生成日历数据
const calendarDays = computed(() => {
  const days = []
  const firstDay = dayjs(`${currentYear.value}-${currentMonth.value.toString().padStart(2, '0')}-01`)
  const lastDay = firstDay.endOf('month')
  const today = dayjs()

  // 获取当月第一天是星期几（0-6）
  const firstDayOfWeek = firstDay.day()

  // 填充上个月的日期
  const prevMonthDays = firstDay.day()
  for (let i = prevMonthDays - 1; i >= 0; i--) {
    const date = firstDay.subtract(i + 1, 'day')
    days.push({
      day: date.date(),
      dateStr: date.format('YYYY-MM-DD'),
      isOtherMonth: true,
      isToday: date.isSame(today, 'day'),
      hasData: false,
      summary: { income: 0, expense: 0 },
      lunar: getLunarDay(date.date())
    })
  }

  // 填充当月日期
  for (let i = 1; i <= lastDay.date(); i++) {
    const date = dayjs(`${currentYear.value}-${currentMonth.value.toString().padStart(2, '0')}-${i.toString().padStart(2, '0')}`)
    const dateStr = date.format('YYYY-MM-DD')
    const items = accountsByDate.value[dateStr] || []

    let summary = { income: 0, expense: 0 }
    let hasData = false

    if (items.length > 0) {
      hasData = true
      items.forEach(item => {
        if (item.transaction_type === '收入') {
          summary.income += parseFloat(item.amount)
        } else {
          summary.expense += parseFloat(item.amount)
        }
      })
    }

    days.push({
      day: i,
      dateStr,
      isOtherMonth: false,
      isToday: date.isSame(today, 'day'),
      hasData,
      summary,
      lunar: hasData ? '' : getLunarDay(i)
    })
  }

  // 填充下个月的日期，补齐到42天（6行）
  const remainingDays = 42 - days.length
  for (let i = 1; i <= remainingDays; i++) {
    const date = lastDay.add(i, 'day')
    days.push({
      day: date.date(),
      dateStr: date.format('YYYY-MM-DD'),
      isOtherMonth: true,
      isToday: date.isSame(today, 'day'),
      hasData: false,
      summary: { income: 0, expense: 0 },
      lunar: getLunarDay(date.date())
    })
  }

  return days
})

// 简单的农历模拟（实际项目中可使用lunar-javascript等库）
const getLunarDay = (day) => {
  const lunarChars = ['初一', '初二', '初三', '初四', '初五', '初六', '初七', '初八', '初九', '初十',
                      '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
                      '廿一', '廿二', '廿三', '廿四', '廿五', '廿六', '廿七', '廿八', '廿九', '三十']
  const index = (day - 1) % 30
  return lunarChars[index]
}

// 选中日期的账单
const selectedDateAccounts = computed(() => {
  return accountsByDate.value[selectedDate.value] || []
})

// 选中日期的标题
const selectedDateTitle = computed(() => {
  const date = dayjs(selectedDate.value)
  const today = dayjs()

  if (date.isSame(today, 'day')) {
    return '今天'
  }

  return date.format('M月D日')
})

// 选中日期的统计
const selectedDateSummary = computed(() => {
  let income = 0
  let expense = 0

  selectedDateAccounts.value.forEach(item => {
    if (item.transaction_type === '收入') {
      income += parseFloat(item.amount)
    } else {
      expense += parseFloat(item.amount)
    }
  })

  return { income, expense }
})

const selectDate = (dayInfo) => {
  selectedDate.value = dayInfo.dateStr
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
  loading.value = true
  accountStore.fetchAccountsByDate(currentYear.value, currentMonth.value)
    .finally(() => {
      loading.value = false
    })
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
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f5f5f5;
  overflow: hidden;
}

.schedule-header {
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.header-year-month {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 12px 16px;
  height: 40px;
  flex: 2;
}

.year-month-title {
  font-size: 18px;
  font-weight: bold;
  margin: 0 12px;
}

.header-monthly-summary {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 0 16px 8px 16px;
  height: 20px;
  flex: 1;
  gap: 16px;
}

.summary-text {
  font-size: 13px;
  color: #666;
}

.income-amount {
  color: #52c41a;
  font-weight: 500;
}

.expense-amount {
  color: #ff4d4f;
  font-weight: 500;
}

.balance-amount {
  color: #666;
  font-weight: 500;
}

.schedule-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.calendar-section {
  flex: 1;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  flex-direction: column;
  padding: 8px;
}

.calendar-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
  margin-bottom: 4px;
}

.weekday-item {
  text-align: center;
  font-size: 12px;
  color: #666;
  padding: 4px 0;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  grid-template-rows: repeat(6, 1fr);
  gap: 2px;
  flex: 1;
}

.calendar-day {
  border-radius: 4px;
  padding: 4px 2px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  cursor: pointer;
  transition: all 0.2s;
  background: #fff;
}

.calendar-day:hover {
  background: #f5f5f5;
}

.calendar-day.other-month {
  opacity: 0.3;
  background: #fafafa;
}

.calendar-day.selected {
  background: #e6f7ff;
}

.calendar-day.today {
  color: #52c41a;
  font-weight: bold;
}

.day-number {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 2px;
}

.day-summary {
  display: flex;
  flex-direction: column;
  gap: 1px;
  font-size: 10px;
  width: 100%;
  align-items: center;
}

.day-expense {
  color: #ff4d4f;
  font-weight: 500;
}

.day-income {
  color: #52c41a;
  font-weight: 500;
}

.day-lunar {
  font-size: 10px;
  color: #999;
}

.day-detail-section {
  flex: 1;
  background: #f5f5f5;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.day-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
}

.detail-title {
  font-size: 16px;
  font-weight: bold;
}

.detail-summary {
  font-size: 13px;
  color: #666;
}

.income-text {
  color: #52c41a;
  font-weight: 500;
}

.expense-text {
  color: #ff4d4f;
  font-weight: 500;
}

.balance-text {
  color: #666;
  font-weight: 500;
}

.day-detail-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.account-list {
  background: #fff;
}

.account-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
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
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  margin-right: 12px;
}

.account-info {
  flex: 1;
  min-width: 0;
}

.account-name {
  font-size: 15px;
  font-weight: 500;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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
  padding: 40px 0;
  text-align: center;
}

.detail-content p {
  margin: 8px 0;
}
</style>
