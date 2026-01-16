<template>
  <div class="ledger-page">
    <!-- 顶部栏 -->
    <div class="page-header">
      <LedgerSelector @change="handleLedgerChange" />
      <Button size="small" color="primary" @click="showAddModal = true">
        记一笔
      </Button>
    </div>

    <!-- 账单列表 -->
    <PullRefresh v-model="refreshing" @refresh="onRefresh">
      <List
        v-model:loading="loading"
        :finished="finished"
        finished-text="没有更多了"
        @load="onLoad"
      >
        <AccountCard
          v-for="account in accounts"
          :key="account.id"
          :account="account"
          @click="showDetail"
        />
      </List>
    </PullRefresh>

    <!-- 悬浮上传按钮 -->
    <div class="fab-upload" @click="showUploadModal = true">
      <CameraOutlined class="icon" />
    </div>

    <!-- 上传弹窗 -->
    <Popup v-model:show="showUploadModal" position="bottom" :style="{ height: '60%' }">
      <div class="upload-modal">
        <div class="upload-header">
          <span>上传账单</span>
          <CloseOutlined @click="showUploadModal = false" />
        </div>
        <ImageUploader @uploaded="handleUploadSuccess" />
      </div>
    </Popup>

    <!-- 添加账单弹窗 -->
    <Popup v-model:show="showAddModal" position="right" :style="{ width: '100%' }">
      <AccountForm @success="handleAddSuccess" @cancel="showAddModal = false" />
    </Popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Button, List, PullRefresh, Popup, Toast, Dialog } from 'ant-design-mobile-vue'
import { CameraOutlined, CloseOutlined } from '@ant-design/icons-vue'
import { useAccountStore, useLedgerStore } from '@/stores'
import { uploadReceipt } from '@/api/upload'
import AccountCard from '@/components/AccountCard.vue'
import ImageUploader from '@/components/ImageUploader.vue'
import AccountForm from '@/components/AccountForm.vue'
import LedgerSelector from '@/components/LedgerSelector.vue'

const accountStore = useAccountStore()
const ledgerStore = useLedgerStore()

const refreshing = ref(false)
const loading = ref(false)
const finished = ref(false)
const showUploadModal = ref(false)
const showAddModal = ref(false)

const accounts = computed(() => accountStore.accounts)

onMounted(() => {
  if (ledgerStore.currentLedgerId) {
    accountStore.fetchAccounts()
  }
})

const handleLedgerChange = (ledgerId) => {
  ledgerStore.switchLedger(ledgerId)
  accountStore.fetchAccounts()
}

const onRefresh = async () => {
  await accountStore.fetchAccounts()
  refreshing.value = false
  Toast.show('刷新成功')
}

const onLoad = () => {
  // 下拉加载更多（简单实现）
  finished.value = true
}

const showDetail = (account) => {
  Dialog.alert({
    title: account.item_name,
    content: `金额: ¥${account.amount}\n分类: ${account.category || '未分类'}\n日期: ${account.transaction_date}`
  })
}

const handleUploadSuccess = (result) => {
  showUploadModal.value = false
  Toast.show('识别成功')
  accountStore.fetchAccounts()
}

const handleAddSuccess = () => {
  showAddModal.value = false
  Toast.show('添加成功')
  accountStore.fetchAccounts()
}
</script>

<style scoped>
.ledger-page {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 50px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fff;
  border-bottom: 1px solid #eee;
}

.fab-upload {
  position: fixed;
  right: 20px;
  bottom: 80px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1890ff, #096dd9);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.4);
  cursor: pointer;
  z-index: 100;
}

.fab-upload .icon {
  font-size: 24px;
}

.upload-modal {
  padding: 16px;
}

.upload-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-size: 18px;
  font-weight: bold;
}
</style>
