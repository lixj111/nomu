<template>
  <div class="settings-page">
    <!-- 用户信息 -->
    <div class="user-info">
      <div class="user-avatar">{{ userStore.user?.username?.[0]?.toUpperCase() || 'U' }}</div>
      <div class="user-details">
        <div class="user-name">{{ userStore.user?.username || '未登录' }}</div>
        <div class="user-email">{{ userStore.user?.email || '点击登录' }}</div>
      </div>
    </div>

    <!-- 账本管理 -->
    <CellGroup title="账本管理">
      <Cell
        title="我的账本"
        is-link
        @click="showLedgerManager = true"
      />
      <Cell
        title="创建新账本"
        is-link
        @click="showCreateLedger = true"
      />
    </CellGroup>

    <!-- 数据管理 -->
    <CellGroup title="数据管理">
      <Cell
        title="导出数据"
        is-link
        @click="exportData"
      />
    </Cell>

    <!-- 其他 -->
    <CellGroup title="其他">
      <Cell
        title="关于"
        is-link
        @click="showAbout"
      />
    </CellGroup>

    <!-- 账本管理弹窗 -->
    <Popup v-model:show="showLedgerManager" position="bottom" :style="{ height: '60%' }">
      <div class="ledger-manager">
        <div class="manager-header">
          <span>账本管理</span>
          <CloseOutlined @click="showLedgerManager = false" />
        </div>
        <div class="ledger-list">
          <div
            v-for="ledger in ledgerStore.ledgers"
            :key="ledger.id"
            class="ledger-item"
          >
            <div class="ledger-info">
              <span class="ledger-name">{{ ledger.name }}</span>
              <span v-if="ledger.is_default" class="default-badge">默认</span>
            </div>
            <div class="ledger-actions">
              <Button
                v-if="!ledger.is_default"
                size="mini"
                @click="setDefaultLedger(ledger.id)"
              >
                设为默认
              </Button>
              <Button
                v-if="!ledger.is_default"
                size="mini"
                color="danger"
                @click="confirmDeleteLedger(ledger)"
              >
                删除
              </Button>
            </div>
          </div>
        </div>
      </div>
    </Popup>

    <!-- 创建账本弹窗 -->
    <Dialog v-model:visible="showCreateLedger" title="创建账本" :onConfirm="createLedger">
      <Input v-model="newLedger.name" placeholder="账本名称" />
      <Input v-model="newLedger.description" placeholder="账本描述（可选）" style="margin-top: 12px" />
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { CellGroup, Cell, Button, Popup, Dialog, Input, Toast, Confirm } from 'ant-design-mobile-vue'
import { CloseOutlined } from '@ant-design/icons-vue'
import { useUserStore, useLedgerStore } from '@/stores'

const userStore = useUserStore()
const ledgerStore = useLedgerStore()

const showLedgerManager = ref(false)
const showCreateLedger = ref(false)
const newLedger = ref({ name: '', description: '' })

onMounted(() => {
  ledgerStore.fetchLedgers()
})

const setDefaultLedger = async (id) => {
  await ledgerStore.setDefaultLedger(id)
  Toast.show('已设置为默认账本')
}

const confirmDeleteLedger = (ledger) => {
  Confirm.show({
    content: `确定要删除账本"${ledger.name}"吗？`,
    onConfirm: async () => {
      await ledgerStore.deleteLedger(ledger.id)
      Toast.show('删除成功')
    }
  })
}

const createLedger = async () => {
  if (!newLedger.value.name) {
    Toast.show('请输入账本名称')
    return
  }

  await ledgerStore.createLedger({
    name: newLedger.value.name,
    description: newLedger.value.description
  })

  Toast.show('创建成功')
  showCreateLedger.value = false
  newLedger.value = { name: '', description: '' }
}

const exportData = () => {
  Toast.show('导出功能开发中')
}

const showAbout = () => {
  Dialog.alert({
    content: '自动记账系统 v1.0.0\n基于AI的智能账单识别'
  })
}
</script>

<style scoped>
.settings-page {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 50px;
  background: #f5f5f5;
}

.user-info {
  display: flex;
  align-items: center;
  padding: 24px 16px;
  background: #fff;
  margin-bottom: 12px;
}

.user-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1890ff, #096dd9);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
  margin-right: 16px;
}

.user-details {
  flex: 1;
}

.user-name {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 4px;
}

.user-email {
  font-size: 14px;
  color: #999;
}

.ledger-manager {
  padding: 16px;
}

.manager-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-size: 18px;
  font-weight: bold;
}

.ledger-list {
  max-height: 300px;
  overflow-y: auto;
}

.ledger-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 8px;
  margin-bottom: 8px;
}

.ledger-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ledger-name {
  font-size: 16px;
  font-weight: 500;
}

.default-badge {
  padding: 2px 8px;
  background: #1890ff;
  color: #fff;
  font-size: 12px;
  border-radius: 12px;
}

.ledger-actions {
  display: flex;
  gap: 8px;
}
</style>
