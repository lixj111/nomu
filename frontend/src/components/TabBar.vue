<template>
  <a-layout-footer class="tab-bar">
    <div
      v-for="tab in tabs"
      :key="tab.key"
      class="tab-item"
      :class="{ active: activeTab === tab.key }"
      @click="switchTab(tab)"
    >
      <component :is="tab.icon" class="tab-icon" />
      <span class="tab-label">{{ tab.label }}</span>
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
import ZhiIcon from './ZhiIcon.vue'

const tabs = [
  { key: 'ledger', name: 'Ledger', icon: BookOutlined, label: '账本' },
  { key: 'schedule', name: 'Schedule', icon: CalendarOutlined, label: '日程' },
  { key: 'aichat', name: 'AIChat', icon: ZhiIcon, label: '小智' },
  { key: 'statistics', name: 'Statistics', icon: BarChartOutlined, label: '统计' },
  { key: 'settings', name: 'Settings', icon: SettingOutlined, label: '设置' }
]

const router = useRouter()
const route = useRoute()

const activeTab = computed(() => {
  const routeName = route.name?.toLowerCase() || ''
  return tabs.find((tab) => routeName.includes(tab.key))?.key || 'ledger'
})

const switchTab = (tab) => {
  router.push({ name: tab.name })
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
