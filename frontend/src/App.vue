<template>
  <div id="app">
    <a-layout class="app-layout">
      <a-layout-content class="app-content">
        <router-view />
      </a-layout-content>
      <TabBar />
    </a-layout>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useUserStore, useLedgerStore } from '@/stores'
import TabBar from '@/components/TabBar.vue'

const userStore = useUserStore()
const ledgerStore = useLedgerStore()

onMounted(() => {
  // 恢复用户信息
  userStore.restoreUser()

  // 如果已登录，加载账本列表
  if (userStore.isLoggedIn()) {
    ledgerStore.fetchLedgers()
  }
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  width: 100%;
  height: 100%;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background-color: #f5f5f5;
}

#app {
  width: 100%;
  height: 100%;
}

.app-layout {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.app-content {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 60px;
}
</style>
