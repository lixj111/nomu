<template>
  <div class="statistics-page">
    <!-- 顶部栏：标签和设置 -->
    <div class="statistics-header">
      <!-- 左侧标签 -->
      <div class="header-tabs">
        <div
          v-for="tab in tabs"
          :key="tab.value"
          class="tab-item"
          :class="{ active: activeTab === tab.value }"
          @click="switchTab(tab.value)"
        >
          {{ tab.label }}
        </div>
      </div>
      <!-- 右侧设置图标 -->
      <div class="header-settings">
        <a-dropdown :trigger="['click']">
          <div class="settings-icon">
            <span></span>
            <span></span>
            <span></span>
          </div>
          <template #overlay>
            <a-menu>
              <a-menu-item @click="showChartSettings">
                <span>图表设置</span>
              </a-menu-item>
              <a-menu-item @click="showMoreSettings">
                <span>更多设置</span>
              </a-menu-item>
            </a-menu>
          </template>
        </a-dropdown>
      </div>
    </div>

    <!-- 时间选择栏 -->
    <div class="time-display-bar">
      <a-button size="small" @click="prevPeriod">
        <template #icon><LeftOutlined /></template>
      </a-button>
      <span class="time-title">{{ timeDisplayTitle }}</span>
      <a-button size="small" @click="nextPeriod">
        <template #icon><RightOutlined /></template>
      </a-button>
    </div>

    <!-- 可滚动内容区域 -->
    <div class="statistics-content">

    <!-- 汇总统计（可折叠） -->
    <div class="summary-section" v-if="periodStats">
      <div class="summary-content" @click="toggleSummary">
        <div class="summary-row-main">
          <div class="summary-item">
            <span class="summary-label">{{ periodLabel }}支出</span>
            <span class="summary-value expense">¥{{ periodStats.totalExpense.toFixed(2) }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">{{ periodLabel }}收入</span>
            <span class="summary-value income">¥{{ periodStats.totalIncome.toFixed(2) }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">{{ periodLabel }}结余</span>
            <span class="summary-value" :class="{ expense: periodStats.balance < 0, income: periodStats.balance >= 0 }">
              ¥{{ periodStats.balance.toFixed(2) }}
            </span>
          </div>
        </div>
        <div class="summary-row-daily" v-if="summaryExpanded">
          <div class="summary-item">
            <span class="summary-label">日均支出</span>
            <span class="summary-value expense">¥{{ periodStats.dailyExpense.toFixed(2) }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">日均收入</span>
            <span class="summary-value income">¥{{ periodStats.dailyIncome.toFixed(2) }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">日均结余</span>
            <span class="summary-value" :class="{ expense: periodStats.dailyBalance < 0, income: periodStats.dailyBalance >= 0 }">
              ¥{{ periodStats.dailyBalance.toFixed(2) }}
            </span>
          </div>
        </div>
        <div class="toggle-icon-bottom">
          <DownOutlined v-if="!summaryExpanded" />
          <UpOutlined v-else />
        </div>
      </div>
    </div>

    <!-- 收支统计柱状图 -->
    <div class="chart-section bar-chart-section">
      <div class="section-header">
        <span class="section-title">收支统计</span>
        <a-radio-group v-model:value="barChartType" button-style="solid" size="small">
          <a-radio-button value="expense">支出</a-radio-button>
          <a-radio-button value="income">收入</a-radio-button>
        </a-radio-group>
      </div>
      <div ref="barChartRef" class="chart-container"></div>
    </div>

    <!-- 收支占比圆环图 -->
    <div class="chart-section pie-chart-section">
      <div class="section-header">
        <span class="section-title">收支占比</span>
        <a-radio-group v-model:value="pieChartType" button-style="solid" size="small">
          <a-radio-button value="expense">支出</a-radio-button>
          <a-radio-button value="income">收入</a-radio-button>
        </a-radio-group>
      </div>
      <div ref="pieChartRef" class="chart-container pie-chart"></div>
    </div>

    <!-- 分类统计数据 -->
    <div class="chart-section category-list-section">
      <div class="section-header">
        <span class="section-title">{{ pieChartType === 'expense' ? '支出' : '收入' }}数据</span>
      </div>
      <div class="category-list">
        <div
          v-for="item in currentCategoryData"
          :key="item.category"
          class="category-item"
        >
          <div class="category-icon" :style="{ background: getCategoryColor(item.category) }">
            {{ item.category[0] }}
          </div>
          <div class="category-info">
            <div class="category-name">{{ item.category }}</div>
            <div class="category-meta">{{ item.count }}笔 · {{ item.percent }}%</div>
          </div>
          <div class="category-amount" :class="{ expense: pieChartType === 'expense', income: pieChartType === 'income' }">
            {{ pieChartType === 'expense' ? '-' : '+' }}¥{{ item.amount.toFixed(2) }}
          </div>
        </div>
      </div>
    </div>

    <!-- 排皮表统计 -->
    <div class="chart-section table-section">
      <div class="section-header">
        <span class="section-title">账单明细</span>
      </div>
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>日期</th>
              <th>收入</th>
              <th>支出</th>
              <th>结余</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in tableData" :key="index">
              <td>{{ row.date }}</td>
              <td class="income-cell">{{ row.income > 0 ? '+' + row.income.toFixed(2) : '-' }}</td>
              <td class="expense-cell">{{ row.expense > 0 ? row.expense.toFixed(2) : '-' }}</td>
              <td :class="row.balance >= 0 ? 'income-cell' : 'expense-cell'">
                {{ row.balance >= 0 ? '+' : '' }}{{ row.balance.toFixed(2) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <a-empty v-if="!periodStats" description="暂无数据" class="empty-state" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { Modal } from 'ant-design-vue'
import { LeftOutlined, RightOutlined, DownOutlined, UpOutlined } from '@ant-design/icons-vue'
import { useAccountStore, useLedgerStore } from '@/stores'
import * as echarts from 'echarts'
import dayjs from 'dayjs'

const accountStore = useAccountStore()
const ledgerStore = useLedgerStore()

// 标签页配置
const tabs = [
  { label: '月统计', value: 'month' },
  { label: '年统计', value: 'year' },
  { label: '自定义', value: 'custom' }
]

const activeTab = ref('month')
const currentYear = ref(new Date().getFullYear())
const currentMonth = ref(new Date().getMonth() + 1)
const customStartDate = ref(dayjs().startOf('month'))
const customEndDate = ref(dayjs().endOf('month'))
const summaryExpanded = ref(false)  // 汇总统计是否展开

// 图表类型
const barChartType = ref('expense')  // expense, income
const pieChartType = ref('expense')  // expense, income

// 图表DOM引用
const barChartRef = ref(null)
const pieChartRef = ref(null)

// 图表实例
let barChart = null
let pieChart = null

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

// 计算时间显示标题
const timeDisplayTitle = computed(() => {
  if (activeTab.value === 'month') {
    return `${currentYear.value}年${currentMonth.value}月`
  } else if (activeTab.value === 'year') {
    return `${currentYear.value}年`
  } else {
    return `${customStartDate.value.format('YYYY-MM-DD')} ~ ${customEndDate.value.format('YYYY-MM-DD')}`
  }
})

// 计算周期标签
const periodLabel = computed(() => {
  if (activeTab.value === 'month') {
    return '月'
  } else if (activeTab.value === 'year') {
    return '年'
  } else {
    return '期间'
  }
})

// 计算周期天数
const periodDays = computed(() => {
  const { start, end } = getDateRange()
  const startDate = dayjs(start)
  const endDate = dayjs(end)
  return endDate.diff(startDate, 'day') + 1
})

// 获取当前时间范围内的账单
const getPeriodAccounts = () => {
  const { start, end } = getDateRange()
  const allAccounts = accountStore.accounts || []
  return allAccounts.filter(account => {
    const accountDate = account.transaction_date
    return accountDate >= start && accountDate <= end
  })
}

// 计算周期统计数据
const periodStats = computed(() => {
  const accounts = getPeriodAccounts()
  if (accounts.length === 0) return null

  let totalExpense = 0
  let totalIncome = 0

  accounts.forEach(account => {
    const amount = parseFloat(account.amount)
    if (account.transaction_type === '收入') {
      totalIncome += amount
    } else {
      totalExpense += amount
    }
  })

  const balance = totalIncome - totalExpense
  const days = periodDays.value

  return {
    totalExpense,
    totalIncome,
    balance,
    dailyExpense: totalExpense / days,
    dailyIncome: totalIncome / days,
    dailyBalance: balance / days
  }
})

// 计算柱状图数据
const barChartData = computed(() => {
  const accounts = getPeriodAccounts()
  if (accounts.length === 0) return { dates: [], expense: [], income: [] }

  // 获取当前周期内的所有日期
  const { start, end } = getDateRange()
  const startDate = dayjs(start)
  const endDate = dayjs(end)
  const allDates = []

  // 生成所有日期
  let currentDate = startDate
  while (currentDate.isBefore(endDate) || currentDate.isSame(endDate, 'day')) {
    allDates.push(currentDate.format('YYYY-MM-DD'))
    currentDate = currentDate.add(1, 'day')
  }

  // 初始化所有日期的数据
  const grouped = {}
  allDates.forEach(date => {
    grouped[date] = { expense: 0, income: 0 }
  })

  // 按日期分组账单
  accounts.forEach(account => {
    const date = account.transaction_date
    if (grouped[date]) {
      const amount = parseFloat(account.amount)
      if (account.transaction_type === '收入') {
        grouped[date].income += amount
      } else {
        grouped[date].expense += amount
      }
    }
  })

  // 生成显示标签和数据
  const dates = []
  const expense = []
  const income = []

  allDates.forEach(date => {
    let label
    if (activeTab.value === 'month') {
      label = dayjs(date).format('M月D日')
    } else if (activeTab.value === 'year') {
      label = dayjs(date).format('M月')
    } else {
      label = dayjs(date).format('MM-DD')
    }

    // 年统计时按月合并
    if (activeTab.value === 'year') {
      const existingIndex = dates.findIndex(d => d === label)
      if (existingIndex >= 0) {
        expense[existingIndex] += grouped[date].expense
        income[existingIndex] += grouped[date].income
      } else {
        dates.push(label)
        expense.push(grouped[date].expense)
        income.push(grouped[date].income)
      }
    } else {
      dates.push(label)
      expense.push(grouped[date].expense)
      income.push(grouped[date].income)
    }
  })

  return { dates, expense, income }
})

// 计算分类统计数据
const categoryStats = computed(() => {
  const accounts = getPeriodAccounts()
  if (accounts.length === 0) return { expense: [], income: [] }

  const expenseByCategory = {}
  const incomeByCategory = {}
  let totalExpense = 0
  let totalIncome = 0

  accounts.forEach(account => {
    const category = account.category || '其他'
    const amount = parseFloat(account.amount)

    if (account.transaction_type === '收入') {
      if (!incomeByCategory[category]) {
        incomeByCategory[category] = { amount: 0, count: 0 }
      }
      incomeByCategory[category].amount += amount
      incomeByCategory[category].count += 1
      totalIncome += amount
    } else {
      if (!expenseByCategory[category]) {
        expenseByCategory[category] = { amount: 0, count: 0 }
      }
      expenseByCategory[category].amount += amount
      expenseByCategory[category].count += 1
      totalExpense += amount
    }
  })

  const formatCategoryData = (data, total) => {
    return Object.entries(data)
      .map(([category, info]) => ({
        category,
        amount: info.amount,
        count: info.count,
        percent: total > 0 ? ((info.amount / total) * 100).toFixed(1) : 0
      }))
      .sort((a, b) => b.amount - a.amount)
  }

  return {
    expense: formatCategoryData(expenseByCategory, totalExpense),
    income: formatCategoryData(incomeByCategory, totalIncome)
  }
})

// 当前选择的分类数据
const currentCategoryData = computed(() => {
  return pieChartType.value === 'expense' ? categoryStats.value.expense : categoryStats.value.income
})

// 计算表格数据
const tableData = computed(() => {
  const accounts = getPeriodAccounts()
  if (accounts.length === 0) return []

  // 按日期分组
  const grouped = {}
  accounts.forEach(account => {
    const date = account.transaction_date
    if (!grouped[date]) {
      grouped[date] = { income: 0, expense: 0 }
    }
    const amount = parseFloat(account.amount)
    if (account.transaction_type === '收入') {
      grouped[date].income += amount
    } else {
      grouped[date].expense += amount
    }
  })

  // 排序并计算累计结余
  const dates = Object.keys(grouped).sort()
  let cumulativeBalance = 0

  return dates.map(date => {
    const row = grouped[date]
    cumulativeBalance += row.income - row.expense
    return {
      date: dayjs(date).format(activeTab.value === 'year' ? 'M月' : 'M月D日'),
      income: row.income,
      expense: row.expense,
      balance: cumulativeBalance
    }
  }).reverse()  // 最新的在上面
})

const getDateRange = () => {
  if (activeTab.value === 'month') {
    const date = dayjs(`${currentYear.value}-${currentMonth.value.toString().padStart(2, '0')}-01`)
    return {
      start: date.startOf('month').format('YYYY-MM-DD'),
      end: date.endOf('month').format('YYYY-MM-DD')
    }
  } else if (activeTab.value === 'year') {
    const date = dayjs(`${currentYear.value}-01-01`)
    return {
      start: date.startOf('year').format('YYYY-MM-DD'),
      end: date.endOf('year').format('YYYY-MM-DD')
    }
  } else {
    return {
      start: customStartDate.value.format('YYYY-MM-DD'),
      end: customEndDate.value.format('YYYY-MM-DD')
    }
  }
}

// 初始化柱状图
const initBarChart = () => {
  console.log('[Statistics] initBarChart 被调用, barChartRef.value:', !!barChartRef.value)
  if (!barChartRef.value) return

  if (barChart) {
    console.log('[Statistics] 销毁旧的柱状图实例')
    barChart.dispose()
  }

  barChart = echarts.init(barChartRef.value)
  console.log('[Statistics] 柱状图实例已创建')
  updateBarChart()
}

// 更新柱状图
const updateBarChart = () => {
  console.log('[Statistics] updateBarChart 被调用')
  if (!barChart) {
    console.log('[Statistics] barChart 实例不存在，跳过更新')
    return
  }

  const data = barChartData.value
  console.log('[Statistics] barChartData:', data)
  const color = barChartType.value === 'expense' ? '#ff4d4f' : '#52c41a'
  const seriesData = barChartType.value === 'expense' ? data.expense : data.income
  const seriesName = barChartType.value === 'expense' ? '支出' : '收入'

  console.log('[Statistics] 当前图表类型:', barChartType.value, '系列名称:', seriesName, '颜色:', color)
  console.log('[Statistics] 系列数据长度:', seriesData.length, '数据:', seriesData)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params) => {
        const param = params[0]
        return `${param.name}<br/>${seriesName}: ¥${param.value.toFixed(2)}`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data.dates,
      axisLabel: { fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      axisLabel: { fontSize: 10 }
    },
    series: [
      {
        name: seriesName,
        type: 'bar',
        data: seriesData,
        itemStyle: { color }
      }
    ]
  }

  // 使用 notMerge: true 强制不合并，完全替换配置
  console.log('[Statistics] 调用 setOption 更新图表')
  barChart.setOption(option, { notMerge: true })
}

// 初始化圆环图
const initPieChart = () => {
  console.log('[Statistics] initPieChart 被调用, pieChartRef.value:', !!pieChartRef.value)
  if (!pieChartRef.value) return

  if (pieChart) {
    console.log('[Statistics] 销毁旧的圆环图实例')
    pieChart.dispose()
  }

  pieChart = echarts.init(pieChartRef.value)
  console.log('[Statistics] 圆环图实例已创建')
  updatePieChart()
}

// 更新圆环图
const updatePieChart = () => {
  console.log('[Statistics] updatePieChart 被调用')
  if (!pieChart) {
    console.log('[Statistics] pieChart 实例不存在，跳过更新')
    return
  }

  const data = pieChartType.value === 'expense' ? categoryStats.value.expense : categoryStats.value.income
  console.log('[Statistics] 当前图表类型:', pieChartType.value, '分类数据:', data)

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      textStyle: { fontSize: 11 }
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['35%', '50%'],
        avoidLabelOverlap: false,
        label: {
          show: true,
          position: 'outside',
          formatter: '{b}\n{d}%',
          fontSize: 11
        },
        labelLine: {
          show: true,
          length: 15,
          length2: 10
        },
        data: data.map(item => ({
          value: item.amount,
          name: item.category,
          itemStyle: { color: getCategoryColor(item.category) }
        }))
      }
    ]
  }

  // 使用 notMerge: true 强制不合并，完全替换配置
  console.log('[Statistics] 调用 setOption 更新圆环图')
  pieChart.setOption(option, { notMerge: true })
}

// 切换汇总统计展开/折叠
const toggleSummary = () => {
  summaryExpanded.value = !summaryExpanded.value
}

// 切换标签
const switchTab = (tab) => {
  activeTab.value = tab
  loadStatistics()
}

// 上一周期
const prevPeriod = () => {
  if (activeTab.value === 'month') {
    if (currentMonth.value === 1) {
      currentYear.value--
      currentMonth.value = 12
    } else {
      currentMonth.value--
    }
  } else if (activeTab.value === 'year') {
    currentYear.value--
  } else {
    // 自定义模式：向前移动一个周期
    const diff = customEndDate.value.diff(customStartDate.value, 'day')
    customStartDate.value = customStartDate.value.subtract(diff + 1, 'day')
    customEndDate.value = customEndDate.value.subtract(diff + 1, 'day')
  }
  loadStatistics()
}

// 下一周期
const nextPeriod = () => {
  if (activeTab.value === 'month') {
    if (currentMonth.value === 12) {
      currentYear.value++
      currentMonth.value = 1
    } else {
      currentMonth.value++
    }
  } else if (activeTab.value === 'year') {
    currentYear.value++
  } else {
    // 自定义模式：向后移动一个周期
    const diff = customEndDate.value.diff(customStartDate.value, 'day')
    customStartDate.value = customStartDate.value.add(diff + 1, 'day')
    customEndDate.value = customEndDate.value.add(diff + 1, 'day')
  }
  loadStatistics()
}

// 图表设置
const showChartSettings = () => {
  Modal.info({
    title: '图表设置',
    content: '图表设置功能即将推出'
  })
}

// 更多设置
const showMoreSettings = () => {
  Modal.info({
    title: '更多设置',
    content: '更多设置功能即将推出'
  })
}

const loadStatistics = async () => {
  if (!ledgerStore.currentLedgerId) return

  try {
    // 重新加载账单数据
    await accountStore.fetchAccounts()

    // 更新图表
    await nextTick()
    updateBarChart()
    updatePieChart()
  } catch (error) {
    console.log('加载统计数据失败:', error.message)
  }
}

onMounted(() => {
  if (ledgerStore.currentLedgerId) {
    accountStore.fetchAccounts().then(() => {
      nextTick(() => {
        initBarChart()
        initPieChart()
      })
    })
  }
})

// 监听图表类型变化
watch(barChartType, (newVal) => {
  console.log('[Statistics] barChartType 变化:', newVal)
  nextTick(() => {
    console.log('[Statistics] 准备更新柱状图, barChart实例:', !!barChart)
    updateBarChart()
  })
})

watch(pieChartType, (newVal) => {
  console.log('[Statistics] pieChartType 变化:', newVal)
  nextTick(() => {
    console.log('[Statistics] 准备更新圆环图, pieChart实例:', !!pieChart)
    updatePieChart()
  })
})

// 监听账本切换
watch(
  () => ledgerStore.currentLedgerId,
  () => {
    loadStatistics()
  }
)

// 监听窗口大小变化
window.addEventListener('resize', () => {
  barChart?.resize()
  pieChart?.resize()
})
</script>

<style scoped>
.statistics-page {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f5f5f5;
  overflow: hidden;
}

.statistics-header {
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  flex-shrink: 0;
  position: sticky;
  top: 0;
  z-index: 10;
}

.header-tabs {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tab-item {
  padding: 6px 16px;
  border-radius: 6px;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-item.active {
  background: #1890ff;
  color: #fff;
  font-weight: 500;
}

.header-settings {
  cursor: pointer;
}

.settings-icon {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 8px;
  border-radius: 4px;
  transition: background 0.2s;
}

.settings-icon:hover {
  background: rgba(82, 196, 26, 0.1);
}

.settings-icon span {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #52c41a;
}

.time-display-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px 16px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  gap: 16px;
  flex-shrink: 0;
  position: sticky;
  top: 49px;
  z-index: 9;
}

/* 可滚动的内容区域 */
.statistics-content {
  overflow-y: auto;
  flex: 1;
  padding-bottom: 16px;
}

.time-title {
  font-size: 16px;
  font-weight: bold;
  min-width: 120px;
  text-align: center;
}

.summary-section {
  background: #fff;
  margin: 12px 16px;
  border-radius: 12px;
  overflow: hidden;
}

.summary-content {
  cursor: pointer;
}

.summary-row-main {
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 16px;
}

.summary-row-daily {
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 0 16px 16px 16px;
  border-top: 1px solid #f0f0f0;
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.summary-label {
  font-size: 13px;
  color: #666;
}

.summary-value {
  font-size: 18px;
  font-weight: bold;
}

.summary-value.income {
  color: #52c41a;
}

.summary-value.expense {
  color: #ff4d4f;
}

.toggle-icon-bottom {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 8px;
  border-top: 1px solid #f0f0f0;
  color: #999;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.toggle-icon-bottom:hover {
  background: #fafafa;
}

.chart-section {
  background: #fff;
  margin: 12px 16px;
  border-radius: 12px;
  padding: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title {
  font-size: 15px;
  font-weight: bold;
  color: #262626;
}

.chart-container {
  width: 100%;
  height: 220px;
}

.chart-container.pie-chart {
  height: 200px;
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.category-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background: #fafafa;
  border-radius: 8px;
}

.category-icon {
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

.category-info {
  flex: 1;
}

.category-name {
  font-size: 14px;
  font-weight: 500;
  color: #262626;
  margin-bottom: 2px;
}

.category-meta {
  font-size: 12px;
  color: #8c8c8c;
}

.category-amount {
  font-size: 16px;
  font-weight: bold;
}

.category-amount.expense {
  color: #ff4d4f;
}

.category-amount.income {
  color: #52c41a;
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.data-table thead {
  background: #fafafa;
}

.data-table th {
  padding: 10px;
  text-align: left;
  font-weight: 500;
  color: #595959;
  border-bottom: 1px solid #f0f0f0;
}

.data-table td {
  padding: 10px;
  border-bottom: 1px solid #f0f0f0;
  color: #262626;
}

.data-table tbody tr:last-child td {
  border-bottom: none;
}

.data-table .income-cell {
  color: #52c41a;
}

.data-table .expense-cell {
  color: #ff4d4f;
}

.empty-state {
  margin: 40px 0;
}
</style>
