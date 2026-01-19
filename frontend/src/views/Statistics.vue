<template>
  <div class="statistics-page">
    <!-- 时间范围选择 -->
    <div class="time-tabs">
      <a-segmented
        v-model:value="timeRange"
        :options="timeOptions"
        @change="loadStatistics"
        block
      />
    </div>

    <!-- 概览卡片 -->
    <a-row :gutter="12" class="overview-cards" v-if="overview">
      <a-col :span="8">
        <a-card class="overview-card income" :bordered="false">
          <div class="card-label">总收入</div>
          <div class="card-value">¥{{ overview.total_income.toFixed(2) }}</div>
          <div class="card-sub">本月 ¥{{ overview.month_income.toFixed(2) }}</div>
        </a-card>
      </a-col>
      <a-col :span="8">
        <a-card class="overview-card expense" :bordered="false">
          <div class="card-label">总支出</div>
          <div class="card-value">¥{{ overview.total_expense.toFixed(2) }}</div>
          <div class="card-sub">本月 ¥{{ overview.month_expense.toFixed(2) }}</div>
        </a-card>
      </a-col>
      <a-col :span="8">
        <a-card class="overview-card balance" :bordered="false">
          <div class="card-label">结余</div>
          <div class="card-value" :class="{ negative: overview.balance < 0 }">
            ¥{{ overview.balance.toFixed(2) }}
          </div>
          <div class="card-sub">{{ overview.account_count }} 笔账单</div>
        </a-card>
      </a-col>
    </a-row>

    <!-- 分类统计 -->
    <a-card class="chart-section" v-if="categoryStats" title="分类统计" :bordered="true">
      <CategoryChart :data="categoryStats.expense_by_category" type="expense" />
      <a-divider v-if="categoryStats.income_by_category?.length > 0" />
      <CategoryChart
        :data="categoryStats.income_by_category"
        type="income"
        v-if="categoryStats.income_by_category?.length > 0"
      />
    </a-card>

    <!-- 趋势统计 -->
    <a-card class="chart-section" v-if="trendStats" title="收支趋势" :bordered="true">
      <TrendChart :data="trendStats.trend" />
    </a-card>

    <a-empty v-if="!overview" description="暂无数据" class="empty-state" />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useLedgerStore } from '@/stores'
import { getOverviewStats, getCategoryStats, getTrendStats } from '@/api/statistics'
import CategoryChart from '@/components/CategoryChart.vue'
import TrendChart from '@/components/TrendChart.vue'
import dayjs from 'dayjs'

const ledgerStore = useLedgerStore()

const timeOptions = [
  { label: '本月', value: 'month' },
  { label: '本年', value: 'year' }
]

const timeRange = ref('month')
const overview = ref(null)
const categoryStats = ref(null)
const trendStats = ref(null)

const getDateRange = () => {
  const now = dayjs()
  if (timeRange.value === 'month') {
    return {
      start: now.startOf('month').format('YYYY-MM-DD'),
      end: now.endOf('month').format('YYYY-MM-DD')
    }
  } else {
    return {
      start: now.startOf('year').format('YYYY-MM-DD'),
      end: now.endOf('year').format('YYYY-MM-DD')
    }
  }
}

const loadStatistics = async () => {
  if (!ledgerStore.currentLedgerId) return

  try {
    const { start, end } = getDateRange()

    // 加载概览统计
    const overviewRes = await getOverviewStats(ledgerStore.currentLedgerId)
    overview.value = overviewRes.data

    // 加载分类统计
    const categoryRes = await getCategoryStats(ledgerStore.currentLedgerId, { start_date: start, end_date: end })
    categoryStats.value = categoryRes.data

    // 加载趋势统计
    const groupBy = timeRange.value === 'month' ? 'day' : 'month'
    const trendRes = await getTrendStats(ledgerStore.currentLedgerId, {
      start_date: start,
      end_date: end,
      group_by: groupBy
    })
    trendStats.value = trendRes.data
  } catch (error) {
    console.log('加载统计数据失败:', error.message)
    // 静默处理错误，不显示数据
    overview.value = null
    categoryStats.value = null
    trendStats.value = null
  }
}

onMounted(() => {
  if (ledgerStore.currentLedgerId) {
    loadStatistics()
  }
})

// 监听账本切换
watch(
  () => ledgerStore.currentLedgerId,
  () => {
    loadStatistics()
  }
)
</script>

<style scoped>
.statistics-page {
  flex: 1;
  overflow-y: auto;
  height: 100%;
  background: #f5f5f5;
}

.time-tabs {
  padding: 16px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
}

.overview-cards {
  padding: 16px;
  padding-bottom: 0;
}

.overview-card {
  border-radius: 12px;
  color: #fff;
  overflow: hidden;
}

.overview-card.income {
  background: linear-gradient(135deg, #52c41a, #389e0d);
}

.overview-card.income :deep(.ant-card-body) {
  background: transparent;
}

.overview-card.expense {
  background: linear-gradient(135deg, #ff4d4f, #cf1322);
}

.overview-card.expense :deep(.ant-card-body) {
  background: transparent;
}

.overview-card.balance {
  background: linear-gradient(135deg, #1890ff, #096dd9);
}

.overview-card.balance :deep(.ant-card-body) {
  background: transparent;
}

.card-label {
  font-size: 12px;
  opacity: 0.9;
  margin-bottom: 8px;
}

.card-value {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 4px;
}

.card-value.negative {
  color: #ff4d4f;
}

.card-sub {
  font-size: 11px;
  opacity: 0.8;
}

.chart-section {
  margin: 16px;
  border-radius: 12px;
}

.chart-section :deep(.ant-card-head-title) {
  font-weight: bold;
}

.empty-state {
  margin: 40px 0;
}
</style>
