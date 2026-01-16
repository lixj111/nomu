<template>
  <div ref="chartRef" class="category-chart"></div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  type: {
    type: String,
    default: 'expense'
  }
})

const chartRef = ref(null)
let chartInstance = null

const initChart = () => {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value)
  updateChart()
}

const updateChart = () => {
  if (!chartInstance || !props.data.length) return

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: ¥{c} ({d}%)'
    },
    series: [{
      type: 'pie',
      radius: ['35%', '65%'],
      center: ['50%', '50%'],
      data: props.data.map(item => ({
        name: item.category,
        value: item.amount
      })),
      label: {
        fontSize: 12,
        formatter: '{b}\n{d}%'
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  }

  chartInstance.setOption(option)
}

watch(() => props.data, updateChart, { deep: true })

onMounted(() => {
  initChart()
  window.addEventListener('resize', () => chartInstance?.resize())
})

onUnmounted(() => {
  chartInstance?.dispose()
})
</script>

<style scoped>
.category-chart {
  width: 100%;
  height: 280px;
}
</style>
