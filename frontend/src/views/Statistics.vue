<template>
  <div class="statistics-page">
    <!-- 时间范围选择 -->
    <div class="time-tabs">
      <Tabs v-model:active="timeRange" @change="loadStatistics">
        <Tab title="本月" value="month" />
        <Tab title="本年" value="year" />
      </Tabs>
    </div>

    <!-- 概览卡片 -->
    <div class="overview-cards" v-if="overview">
      <div class="overview-card income">
        <div class="card-label">总收入</div>
        <div class="card-value">¥{{ overview.total_income.toFixed(2) }}</div>
        <div class="card-sub">本月 ¥{{ overview.month_income.toFixed(2) }}</div>
      </div>
      <div class="overview-card expense">
        <div class="card-label">总支出</div>
        <div class="card-value">¥{{ overview.total_expense.toFixed(2) }}</div>
        <div class="card-sub">本月 ¥{{ overview.month_expense.toFixed(2) }}</div>
      </div>
      <div class="overview-card balance">
        <div class="card-label">结余</div>
        <div class="card-value" :class="{ negative: overview.balance < 0 }">
          ¥{{ overview.balance.toFixed(2) }}
        </div>
        <div class="card-sub">{{ overview.account_count }} 笔账单</div>
      </div>
    </div>

    <!-- 分类统计 -->
    <div class="chart-section" v-if="categoryStats">
      <h3>分类统计</h3>
      <CategoryChart :data="categoryStats.expense_by_category" type="expense" />
      <CategoryChart :data="categoryStats.income_by_category" type="income" v-if="categoryStats.income_by_category.length > 0" />
    </div>

    <!-- 趋势统计 -->
    <div class="chart-section" v-if="trendStats">
      <h3>收支趋势</h3>
      <TrendChart :data="trendStats.trend" />
    </div>

    <Empty v-if="!overview" description="暂无数据" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Tabs, Tab, Empty } from 'ant-design-mobile-vue'
import { useLedgerStore } from '@/stores'
import { getOverviewStats, getCategoryStats, getTrendStats } from '@/api/statistics'
import CategoryChart from '@/components/CategoryChart.vue'
import TrendChart from '@/components/TrendChart.vue'
import dayjs from 'dayjs'

const ledgerStore = useLedgerStore()

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
  padding-bottom: 50px;
  background: #f5f5f5;
}

.time-tabs {
  background: #fff;
  border-bottom: 1px solid #eee;
}

.overview-cards {
  display: flex;
  gap: 12px;
  padding: 16px;
}

.overview-card {
  flex: 1;
  padding: 16px;
  border-radius: 12px;
  color: #fff;
}

.overview-card.income {
  background: linear-gradient(135deg, #52c41a, #389e0d);
}

.overview-card.expense {
  background: linear-gradient(135deg, #ff4d4f, #cf1322);
}

.overview-card.balance {
  background: linear-gradient(135deg, #1890ff, #096dd9);
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
  background: #fff;
  margin: 12px;
  padding: 16px;
  border-radius: 12px;
}

.chart-section h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: bold;
}
</style>
