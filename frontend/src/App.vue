<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useUserStore, useLedgerStore } from '@/stores'

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
  display: flex;
  flex-direction: column;
}
</style>
