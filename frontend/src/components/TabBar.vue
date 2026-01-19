<template>
  <a-layout-footer class="tab-bar">
    <div class="tab-item" :class="{ active: activeTab === 'ledger' }" @click="switchTab('ledger')">
      <BookOutlined class="tab-icon" />
      <span class="tab-label">账本</span>
    </div>
    <div class="tab-item" :class="{ active: activeTab === 'schedule' }" @click="switchTab('schedule')">
      <CalendarOutlined class="tab-icon" />
      <span class="tab-label">日程</span>
    </div>
    <div class="tab-item" :class="{ active: activeTab === 'statistics' }" @click="switchTab('statistics')">
      <BarChartOutlined class="tab-icon" />
      <span class="tab-label">统计</span>
    </div>
    <div class="tab-item" :class="{ active: activeTab === 'settings' }" @click="switchTab('settings')">
      <SettingOutlined class="tab-icon" />
      <span class="tab-label">设置</span>
    </div>
  </a-layout-footer>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  BookOutlined,
  CalendarOutlined,
  BarChartOutlined,
  SettingOutlined
} from '@ant-design/icons-vue'

const router = useRouter()
const route = useRoute()

const activeTab = computed(() => {
  const routeName = route.name?.toLowerCase() || ''
  if (routeName.includes('schedule')) return 'schedule'
  if (routeName.includes('statistics')) return 'statistics'
  if (routeName.includes('settings')) return 'settings'
  return 'ledger'
})

const switchTab = (tab) => {
  router.push({ name: tab.charAt(0).toUpperCase() + tab.slice(1) })
}
</script>

<style scoped>
.tab-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: #fff;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 0;
  margin: 0;
  z-index: 999;
}

.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  padding: 8px 0;
}

.tab-item:hover {
  background: #fafafa;
}

.tab-item.active .tab-icon {
  color: #1677ff;
}

.tab-item.active .tab-label {
  color: #1677ff;
  font-weight: 500;
}

.tab-icon {
  font-size: 22px;
  color: #999;
  margin-bottom: 2px;
  transition: color 0.3s;
}

.tab-label {
  font-size: 12px;
  color: #999;
  transition: color 0.3s;
}
</style>
