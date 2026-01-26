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
    <!-- 月统计模式：横向滚动月份选择器 -->
    <div class="time-display-bar month-mode" v-if="activeTab === 'month'">
      <div class="year-display">{{ currentYear }}</div>
      <div class="month-divider">|</div>
      <div class="month-scroll-container">
        <div class="month-scroll-content">
          <a-button
            v-for="monthOption in monthOptions"
            :key="monthOption.key"
            size="small"
            :type="isMonthSelected(monthOption) ? 'primary' : 'default'"
            @click="selectMonth(monthOption)"
            class="month-button"
          >
            {{ monthOption.label }}
          </a-button>
        </div>
      </div>
    </div>

    <!-- 年统计模式：横向滚动年份选择器 -->
    <div class="time-display-bar year-mode" v-else-if="activeTab === 'year'">
      <div class="year-scroll-container">
        <div class="year-scroll-content">
          <a-button
            v-for="yearOption in yearOptions"
            :key="yearOption.key"
            size="small"
            :type="isYearSelected(yearOption) ? 'primary' : 'default'"
            @click="selectYear(yearOption)"
            class="year-button"
          >
            {{ yearOption.label }}
          </a-button>
        </div>
      </div>
    </div>

    <!-- 自定义模式：原有左右箭头样式 -->
    <div class="time-display-bar" v-else>
      <a-button size="small" @click="prevPeriod">
        <template #icon><LeftOutlined /></template>
      </a-button>
      <span class="time-title" @click="handleTimeTitleClick" :class="{ clickable: activeTab === 'custom' }">
        {{ timeDisplayTitle }}
      </span>
      <a-button size="small" @click="nextPeriod">
        <template #icon><RightOutlined /></template>
      </a-button>
    </div>

    <!-- 自定义日期范围选择弹窗 -->
    <a-modal v-model:open="showDateRangeModal" title="选择日期范围" :width="400" @ok="handleDateRangeConfirm">
      <a-form layout="vertical">
        <a-form-item label="开始日期">
          <a-date-picker v-model:value="tempStartDate" format="YYYY-MM-DD" style="width: 100%" />
        </a-form-item>
        <a-form-item label="结束日期">
          <a-date-picker v-model:value="tempEndDate" format="YYYY-MM-DD" style="width: 100%" />
        </a-form-item>
      </a-form>
    </a-modal>

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
        <!-- 日均统计：年统计且选择"所有"时不显示 -->
        <div class="summary-row-daily" v-if="summaryExpanded && !(activeTab === 'year' && currentYear === null)">
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
        <div class="toggle-icon-bottom" v-if="!(activeTab === 'year' && currentYear === null)">
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
            <component :is="getCategoryIcon(item.category)" />
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
import {
  LeftOutlined,
  RightOutlined,
  DownOutlined,
  UpOutlined,
  CoffeeOutlined,
  CarOutlined,
  ShoppingOutlined,
  GiftOutlined,
  HomeOutlined,
  BookOutlined,
  HeartOutlined,
  MoreOutlined,
  WalletOutlined,
  TrophyOutlined,
  TeamOutlined,
  SwapOutlined,
  TransactionOutlined,
  DollarOutlined,
  RiseOutlined
} from '@ant-design/icons-vue'
import { useAccountStore, useLedgerStore } from '@/stores'
import * as echarts from 'echarts'
import dayjs from 'dayjs'

const accountStore = useAccountStore()
const ledgerStore = useLedgerStore()

// 支出分类配置
const expenseCategories = [
  { label: '食品餐饮', value: '食品餐饮', color: '#ff6b6b', icon: CoffeeOutlined },
  { label: '出行交通', value: '出行交通', color: '#4dabf7', icon: CarOutlined },
  { label: '购物消费', value: '购物消费', color: '#ff922b', icon: ShoppingOutlined },
  { label: '休闲娱乐', value: '休闲娱乐', color: '#cc5de8', icon: GiftOutlined },
  { label: '居家生活', value: '居家生活', color: '#20c997', icon: HomeOutlined },
  { label: '文化教育', value: '文化教育', color: '#fab005', icon: BookOutlined },
  { label: '健康医疗', value: '健康医疗', color: '#51cf66', icon: HeartOutlined },
  { label: '其他', value: '其他', color: '#adb5bd', icon: MoreOutlined }
]

// 收入分类配置
const incomeCategories = [
  { label: '工资', value: '工资', color: '#52c41a', icon: WalletOutlined },
  { label: '奖金', value: '奖金', color: '#faad14', icon: TrophyOutlined },
  { label: '兼职外快', value: '兼职外快', color: '#13c2c2', icon: TeamOutlined },
  { label: '二手闲置', value: '二手闲置', color: '#eb2f96', icon: SwapOutlined },
  { label: '补贴', value: '补贴', color: '#722ed1', icon: TransactionOutlined },
  { label: '红包', value: '红包', color: '#fa541c', icon: DollarOutlined },
  { label: '理财盈利', value: '理财盈利', color: '#2f54eb', icon: RiseOutlined },
  { label: '其他', value: '其他', color: '#adb5bd', icon: MoreOutlined }
]

// 标签页配置
const tabs = [
  { label: '月统计', value: 'month' },
  { label: '年统计', value: 'year' },
  { label: '自定义', value: 'custom' }
]

const activeTab = ref('month')
const currentYear = ref(new Date().getFullYear())
const currentMonth = ref(new Date().getMonth() + 1)

// 生成月份选项列表（包含"本月"和最近12个月）
const monthOptions = computed(() => {
  const now = dayjs()
  const options = []

  // 添加"本月"按钮
  options.push({
    key: 'current',
    label: '本月',
    year: now.year(),
    month: now.month() + 1
  })

  // 添加最近11个月（从上个月往前数，避免与本月重复）
  for (let i = 1; i < 12; i++) {
    const date = now.subtract(i, 'month')
    options.push({
      key: `month-${i}`,
      label: `${date.month() + 1}月`,
      year: date.year(),
      month: date.month() + 1
    })
  }

  return options
})

// 生成年份选项列表（包含"所有"、"今年"、"去年"和最近20年）
const yearOptions = computed(() => {
  const now = dayjs()
  const currentYear = now.year()
  const options = []

  // 添加"所有"按钮（显示全部年份的数据）
  options.push({
    key: 'all',
    label: '所有',
    year: null
  })

  // 添加"今年"按钮
  options.push({
    key: 'current',
    label: '今年',
    year: currentYear
  })

  // 添加"去年"按钮
  options.push({
    key: 'last-year',
    label: '去年',
    year: currentYear - 1
  })

  // 添加最近20年（从前年开始往前数，避免与今年、去年重复）
  for (let i = 2; i < 20; i++) {
    const year = currentYear - i
    options.push({
      key: `year-${i}`,
      label: `${year}年`,
      year: year
    })
  }

  return options
})

const customStartDate = ref(dayjs().startOf('month'))
const customEndDate = ref(dayjs().endOf('month'))
const summaryExpanded = ref(false)  // 汇总统计是否展开

// 日期范围选择弹窗
const showDateRangeModal = ref(false)
const tempStartDate = ref(dayjs().startOf('month'))
const tempEndDate = ref(dayjs().endOf('month'))

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
  '其他': '#adb5bd',
  '工资': '#52c41a',
  '奖金': '#faad14',
  '兼职外快': '#13c2c2',
  '二手闲置': '#eb2f96',
  '补贴': '#722ed1',
  '红包': '#fa541c',
  '理财盈利': '#2f54eb'
}

const getCategoryColor = (category) => {
  return categoryColors[category] || '#1890ff'
}

// 获取分类图标
const getCategoryIcon = (category) => {
  const allCategories = [...expenseCategories, ...incomeCategories]
  const found = allCategories.find(c => c.value === category)
  return found ? found.icon : MoreOutlined
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
    // 年统计且选择"所有"时显示"总"，否则显示"年"
    return currentYear.value === null ? '总' : '年'
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

  const { start, end } = getDateRange()
  const startDate = dayjs(start)
  const endDate = dayjs(end)

  // 年统计且选择"所有"时，直接按月分组
  if (activeTab.value === 'year' && currentYear.value === null) {
    const monthlyData = {}

    // 初始化12个月的数据
    for (let i = 1; i <= 12; i++) {
      monthlyData[i] = { expense: 0, income: 0 }
    }

    // 按月统计
    accounts.forEach(account => {
      const date = dayjs(account.transaction_date)
      const month = date.month() + 1  // 1-12
      const amount = parseFloat(account.amount)

      if (account.transaction_type === '收入') {
        monthlyData[month].income += amount
      } else {
        monthlyData[month].expense += amount
      }
    })

    // 生成12个月的数据
    const dates = []
    const expense = []
    const income = []

    for (let i = 1; i <= 12; i++) {
      dates.push(`${i}月`)
      expense.push(monthlyData[i].expense)
      income.push(monthlyData[i].income)
    }

    return { dates, expense, income }
  }

  // 其他情况：生成所有日期
  const allDates = []
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

  // 年统计时按月分组，其他情况按日期分组
  const isYearMode = activeTab.value === 'year'
  const isAllYears = isYearMode && currentYear.value === null
  const grouped = {}

  accounts.forEach(account => {
    const date = account.transaction_date

    // 年统计"所有"：按月分组但需要显示年份（使用 YYYY-MM 作为key）
    // 年统计具体年份：按月分组（使用 YYYY-MM 作为key）
    // 月统计/自定义：按日期分组（使用 YYYY-MM-DD 作为key）
    const key = isYearMode ? date.substring(0, 7) : date

    if (!grouped[key]) {
      grouped[key] = { income: 0, expense: 0 }
    }
    const amount = parseFloat(account.amount)
    if (account.transaction_type === '收入') {
      grouped[key].income += amount
    } else {
      grouped[key].expense += amount
    }
  })

  // 排序
  const keys = Object.keys(grouped).sort()

  return keys.map(key => {
    const row = grouped[key]
    // 年统计"所有"：显示"2024年1月"
    // 年统计具体年份：显示"1月"、"2月"
    // 月统计/自定义：显示"1月15日"
    let dateDisplay
    if (isAllYears) {
      dateDisplay = dayjs(key + '-01').format('YYYY年M月')
    } else if (isYearMode) {
      dateDisplay = dayjs(key + '-01').format('M月')
    } else {
      dateDisplay = dayjs(key).format('M月D日')
    }

    return {
      date: dateDisplay,
      income: row.income,
      expense: row.expense,
      balance: row.income - row.expense
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
    // 如果是"所有"年份（currentYear 为 null），返回所有数据
    if (currentYear.value === null) {
      return {
        start: '1900-01-01',  // 足够早的日期
        end: '2099-12-31'      // 足够晚的日期
      }
    }
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
  if (!barChartRef.value) return

  if (barChart) {
    barChart.dispose()
  }

  barChart = echarts.init(barChartRef.value)
  updateBarChart()
}

// 更新柱状图
const updateBarChart = () => {
  if (!barChart) {
    return
  }

  const data = barChartData.value
  const color = barChartType.value === 'expense' ? '#ff4d4f' : '#52c41a'
  const seriesData = barChartType.value === 'expense' ? data.expense : data.income
  const seriesName = barChartType.value === 'expense' ? '支出' : '收入'

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

  barChart.setOption(option, { notMerge: true })
}

// 初始化圆环图
const initPieChart = () => {
  if (!pieChartRef.value) return

  if (pieChart) {
    pieChart.dispose()
  }

  pieChart = echarts.init(pieChartRef.value)
  updatePieChart()
}

// 更新圆环图
const updatePieChart = () => {
  if (!pieChart) {
    return
  }

  const data = pieChartType.value === 'expense' ? categoryStats.value.expense : categoryStats.value.income

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

  pieChart.setOption(option, { notMerge: true })
}

// 切换汇总统计展开/折叠
const toggleSummary = () => {
  summaryExpanded.value = !summaryExpanded.value
}

// 判断月份选项是否被选中
const isMonthSelected = (monthOption) => {
  return currentYear.value === monthOption.year && currentMonth.value === monthOption.month
}

// 选择月份
const selectMonth = (monthOption) => {
  currentYear.value = monthOption.year
  currentMonth.value = monthOption.month
  loadStatistics()
}

// 判断年份选项是否被选中
const isYearSelected = (yearOption) => {
  if (yearOption.year === null) {
    // "所有"选项：当 currentYear 为 null 时选中
    return currentYear.value === null
  }
  return currentYear.value === yearOption.year
}

// 选择年份
const selectYear = (yearOption) => {
  currentYear.value = yearOption.year
  currentMonth.value = 1  // 重置月份为1月
  loadStatistics()
}

// 切换标签
const switchTab = (tab) => {
  activeTab.value = tab
  // 切换到月统计时，设置为本月
  if (tab === 'month') {
    const now = dayjs()
    currentYear.value = now.year()
    currentMonth.value = now.month() + 1
  }
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

// 点击时间标题打开日期选择（仅自定义模式）
const handleTimeTitleClick = () => {
  if (activeTab.value === 'custom') {
    tempStartDate.value = customStartDate.value
    tempEndDate.value = customEndDate.value
    showDateRangeModal.value = true
  }
}

// 确认日期范围选择
const handleDateRangeConfirm = () => {
  if (!tempStartDate.value || !tempEndDate.value) {
    Modal.warning({
      title: '提示',
      content: '请选择完整的日期范围'
    })
    return
  }

  if (tempStartDate.value.isAfter(tempEndDate.value)) {
    Modal.warning({
      title: '提示',
      content: '开始日期不能晚于结束日期'
    })
    return
  }

  customStartDate.value = tempStartDate.value
  customEndDate.value = tempEndDate.value
  showDateRangeModal.value = false
  loadStatistics()
}

const loadStatistics = async () => {
  if (!ledgerStore.currentLedgerId) return

  try {
    // 获取当前时间范围
    const { start, end } = getDateRange()

    // 统计页面传入时间段参数，让后端筛选数据
    await accountStore.fetchAccounts({
      start_date: start,
      end_date: end
    })

    // 更新图表
    await nextTick()
    updateBarChart()
    updatePieChart()
  } catch (error) {
    // 加载失败，静默处理
  }
}

onMounted(() => {
  if (ledgerStore.currentLedgerId) {
    const { start, end } = getDateRange()
    accountStore.fetchAccounts({
      start_date: start,
      end_date: end
    }).then(() => {
      nextTick(() => {
        initBarChart()
        initPieChart()
      })
    })
  }
})

// 监听图表类型变化
watch(barChartType, () => {
  nextTick(() => {
    updateBarChart()
  })
})

watch(pieChartType, () => {
  nextTick(() => {
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

/* 月统计模式：横向滚动布局 */
.time-display-bar.month-mode {
  justify-content: flex-start;
}

/* 年统计模式：横向滚动布局 */
.time-display-bar.year-mode {
  justify-content: flex-start;
  padding: 12px 0;
}

.time-display-bar .year-display {
  font-size: 16px;
  font-weight: bold;
  color: #262626;
  flex-shrink: 0;
}

.time-display-bar .month-divider {
  font-size: 16px;
  color: #d9d9d9;
  margin: 0 8px;
  flex-shrink: 0;
}

.time-display-bar .month-scroll-container {
  flex: 1;
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
  /* 隐藏滚动条但保留滚动功能 */
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE/Edge */
}

.time-display-bar .month-scroll-container::-webkit-scrollbar {
  display: none; /* Chrome/Safari */
}

.time-display-bar .month-scroll-content {
  display: flex;
  gap: 8px;
  padding: 2px 0;
}

.time-display-bar .month-button {
  flex-shrink: 0;
  min-width: 60px;
}

.time-display-bar .year-scroll-container {
  flex: 1;
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
  /* 隐藏滚动条但保留滚动功能 */
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE/Edge */
}

.time-display-bar .year-scroll-container::-webkit-scrollbar {
  display: none; /* Chrome/Safari */
}

.time-display-bar .year-scroll-content {
  display: flex;
  gap: 8px;
  padding: 2px 16px;
}

.time-display-bar .year-button {
  flex-shrink: 0;
  min-width: 70px;
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

.time-title.clickable {
  cursor: pointer;
  text-decoration: underline;
  text-decoration-style: dashed;
  text-decoration-color: #999;
}

.time-title.clickable:hover {
  color: #1890ff;
  text-decoration-color: #1890ff;
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
